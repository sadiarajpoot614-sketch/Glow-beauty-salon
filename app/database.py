import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


# PostgreSQL configuration
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://postgres:{quote_plus(DB_PASSWORD)}"
    f"@localhost:5432/beauty_salon_db"
)


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()