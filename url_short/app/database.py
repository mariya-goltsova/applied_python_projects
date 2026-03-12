from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "postgresql://user:password@postgres:5432/shortener"
DATABASE_URL = "postgresql://postgres:postgres@postgres:5432/shortener"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()