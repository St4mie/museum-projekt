# backend/tests/test_media_processor.py

import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from app.services.media_processor import generate_image_thumbnail, transcode_video
import app.config as config_module
import app.services.media_processor as processor_module  # Zum Patchen von BASE


@pytest.fixture(autouse=True)
def tmp_media_dir(tmp_path, monkeypatch):
    """
    Fixture, die für jeden Test ein temporäres MEDIA_STATIC_PATH-Verzeichnis anlegt:
    1. Entfernt tmp/static, legt es neu an.
    2. Patcht config.MEDIA_STATIC_PATH und processor_module.BASE.
    """
    test_static = tmp_path / "static"
    shutil.rmtree(test_static, ignore_errors=True)
    test_static.mkdir()

    # ENV & config
    monkeypatch.setenv("MEDIA_STATIC_PATH", str(test_static))
    monkeypatch.setattr(config_module, "MEDIA_STATIC_PATH", test_static)
    # BASE im Processor-Module anpassen
    monkeypatch.setattr(processor_module, "BASE", test_static)

    return test_static


def create_dummy_image(path: Path, size=(400, 300), color=(255, 0, 0)):
    img = Image.new("RGB", size, color)
    img.save(path, format="JPEG")


def create_dummy_video(path: Path):
    path.write_bytes(b"\x00\x00\x00")


def test_generate_image_thumbnail_creates_thumbnail(tmp_media_dir):
    movie_id = 7
    orig_dir = tmp_media_dir / "images" / "movies" / str(movie_id)
    orig_dir.mkdir(parents=True)
    src_path = orig_dir / "cover.jpg"
    create_dummy_image(src_path)

    thumb_path = generate_image_thumbnail(movie_id, "cover.jpg")
    assert thumb_path.exists()
    with Image.open(thumb_path) as thumb_img:
        w, h = thumb_img.size
        assert w <= 200 and h <= 200


def test_generate_image_thumbnail_missing_source(tmp_media_dir):
    with pytest.raises(FileNotFoundError):
        generate_image_thumbnail(8, "nonexistent.jpg")


def test_transcode_video_invokes_ffmpeg(tmp_media_dir, monkeypatch):
    movie_id = 9
    vids_dir = tmp_media_dir / "videos" / "movies" / str(movie_id)
    vids_dir.mkdir(parents=True)
    src_path = vids_dir / "clip.mp4"
    create_dummy_video(src_path)

    called = {}
    def fake_run(cmd, check):
        called['cmd'] = cmd
        called['check'] = check

    monkeypatch.setattr(subprocess, "run", fake_run)

    out_path = transcode_video(movie_id, "clip.mp4", resolution="480p")

    expected_dir = vids_dir / "480p"
    assert expected_dir.exists()
    assert out_path == expected_dir / "clip.mp4"
    assert "ffmpeg" in called['cmd'][0]
    assert "scale=854:480" in called['cmd']


def test_transcode_video_missing_source(tmp_media_dir):
    with pytest.raises(FileNotFoundError):
        transcode_video(10, "absent.mp4")
