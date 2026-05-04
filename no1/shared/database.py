import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


load_dotenv()


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "aegis")


def _build_database_url() -> str:
    # Switched to SQLite to avoid MySQL connection issues and the need for sudo passwords
    return "sqlite:///./aegis.db"


engine = create_engine(
    _build_database_url(),
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print(f"[DB] Connection successful: AsteroidCollision ({DB_HOST}:{DB_PORT}/{DB_NAME})")
        return True
    except Exception as exc:
        print(f"[DB] Connection failed for AsteroidCollision ({DB_HOST}:{DB_PORT}/{DB_NAME}): {exc}")
        return False


if __name__ == "__main__":
    test_connection()