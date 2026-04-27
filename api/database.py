import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from api.models import Base

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in .env file")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(" Database connected successfully to Neon")
        Base.metadata.create_all(bind=engine)
        logger.info(" All tables created / verified")
    except Exception as e:
        logger.error(f" Database connection failed: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()