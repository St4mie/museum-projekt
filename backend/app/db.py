# backend/app/db.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# .env-Datei laden (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

# Verbindungs-URL für MariaDB
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Engine & Session factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basisklasse für ORM-Modelle
Base = declarative_base()
