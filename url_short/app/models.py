from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True)
    password = Column(String)

class Link(Base):
    __tablename__ = "links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    short_code = Column(String, unique=True)
    original_url = Column(String)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    project = Column(String, nullable=True)

    click_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)