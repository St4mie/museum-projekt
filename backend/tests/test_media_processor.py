# backend/tests/test_media_processor.py

import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image

from app.services.media_processor import generate_image_thumbnail, transcode_video
import app.config as config_module
import app.services.media_processor as processor_module  # Zum Patchen von BASE

# Mark all tests to use settings and config_module_settings fixtures
pytestmark = pytest.mark.usefixtures("settings", "config_module_settings")

@pytest.fixture
def config_module_settings():
    """
    Fixture to provide access to config_module.settings
    """
    return config_module.settings


@pytest.fixture(autouse=True)
def tmp_media_dir(tmp_path, monkeypatch, config_module_settings):
    """
    Fixture for a temporary MEDIA_STATIC_PATH:
    1. Creates tmp/static
    2. Patches settings.media_static_path and processor_module.BASE
    """
    test_static = tmp_path / "static"
    shutil.rmtree(test_static, ignore_errors=True)
    test_static.mkdir()

    # 1) Patching the Pydantic settings
    monkeypatch.setattr(
        config_module.settings,
        "media_static_path",
        test_static
    )

    # 2) Patch BASE in the processor module (in case it's hardcoded)
    monkeypatch.setattr(processor_module, "BASE", test_static)

    return test_static


@pytest.fixture
def create_dummy_image():
    def _create_dummy_image(path: Path, size=(400, 300), color=(255, 0, 0)):
        img = Image.new("RGB", size, color)
        img.save(path, format="JPEG")
    return _create_dummy_image


@pytest.fixture
def create_dummy_video():
    def _create_dummy_video(path: Path):
        path.write_bytes(b"\x00\x00\x00")
    return _create_dummy_video


def test_generate_image_thumbnail_creates_thumbnail(tmp_media_dir, create_dummy_image):
    movie_id = 7
    orig_dir = tmp_media_dir / "images" / "movies" / str(movie_id)
    orig_dir.mkdir(parents=True)
    src_path = orig_dir / "cover.jpg"
    create_dummy_image(src_path)

    thumb_path = generate_image_thumbnail(movie_id, "cover.jpg")
    assert thumb_path.exists(), "Thumbnail file was not created"
    with Image.open(thumb_path) as thumb_img:
        w, h = thumb_img.size
        assert w <= 200 and h <= 200, "Thumbnail has incorrect dimensions"


def test_generate_image_thumbnail_missing_source(tmp_media_dir):
    with pytest.raises(FileNotFoundError):
        generate_image_thumbnail(8, "nonexistent.jpg")


def test_transcode_video_invokes_ffmpeg(tmp_media_dir, monkeypatch, create_dummy_video):
    movie_id = 9
    vids_dir = tmp_media_dir / "videos" / "movies" / str(movie_id)
    vids_dir.mkdir(parents=True)
    src_path = vids_dir / "clip.mp4"
    create_dummy_video(src_path)

    # Stub für subprocess.run
    called = {}
    def fake_run(cmd, check):
        called['cmd'] = cmd
        called['check'] = check

    monkeypatch.setattr(subprocess, "run", fake_run)

    out_path = transcode_video(movie_id, "clip.mp4", resolution="480p")

    expected_dir = vids_dir / "480p"
    assert expected_dir.exists(), "Transcoding output directory is missing"
    assert out_path == expected_dir / "clip.mp4", "Return path is incorrect"
    # Check that ffmpeg was called with the correct scale parameter
    assert any("ffmpeg" in part for part in called['cmd']), "ffmpeg was not called"
    assert any("scale=" in part for part in called['cmd']), "Scale parameter is missing in ffmpeg call"


def test_transcode_video_missing_source(tmp_media_dir):
    with pytest.raises(FileNotFoundError):
        transcode_video(10, "absent.mp4")


def test_transcode_video_fallback_on_error(tmp_media_dir, monkeypatch, create_dummy_video):
    """Test that the function falls back to copying when ffmpeg fails."""
    movie_id = 11
    vids_dir = tmp_media_dir / "videos" / "movies" / str(movie_id)
    vids_dir.mkdir(parents=True)
    src_path = vids_dir / "error.mp4"
    create_dummy_video(src_path)

    # Make subprocess.run raise an exception
    def failing_run(cmd, check):
        raise RuntimeError("Simulated ffmpeg failure")

    monkeypatch.setattr(subprocess, "run", failing_run)

    # Spy on shutil.copy2
    original_copy2 = shutil.copy2
    copy_called = {"src": None, "dst": None}

    def spy_copy2(src, dst):
        copy_called["src"] = src
        copy_called["dst"] = dst
        return original_copy2(src, dst)

    monkeypatch.setattr(shutil, "copy2", spy_copy2)

    out_path = transcode_video(movie_id, "error.mp4")

    # Verify fallback was used
    assert copy_called["src"] == src_path, "Source file was not copied as fallback"
    assert copy_called["dst"] == out_path, "Destination file was not correct in fallback"
    assert out_path.exists(), "Output file does not exist after fallback"
