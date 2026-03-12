from pydantic import BaseModel
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: str
    custom_alias: str | None = None
    expires_at: datetime | None = None
    project: str | None = None

class LinkUpdate(BaseModel):
    original_url: str

class UserCreate(BaseModel):
    email: str
    password: str