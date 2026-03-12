from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from .database import SessionLocal
from .models import Link
from .schemas import LinkCreate, LinkUpdate
from .cache import set_link, delete_link

import random
import string

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@router.post("/links/shorten")
def create_link(data: LinkCreate, db : Session = Depends(get_db)):
    code = data.custom_alias if data.custom_alias else generate_code()
    link = Link(
        short_code = code,
        original_url = data.original_url,
        expires_at = data.expires_at,
        project = data.project
    )
    db.add(link)
    db.commit()
    set_link(code, data.original_url)
    return {"short_url": f"http://localhost:8000/{code}"}


@router.get("/links/{short_code}/stats")
def get_stats(short_code: str, db : Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code  == short_code).first()
    if not link:
        return {"error": "Link not found"}
    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "click_count": link.click_count,
        "last_used_at": link.last_used_at}

@router.delete("/links/cleanup")
def cleanup_links_extra_func(days: int = 30, db : Session = Depends(get_db)):
    threshold = datetime.utcnow() - timedelta(days=days)
    links = db.query(Link).filter(Link.last_used_at < threshold).all()
    count = 0
    for link in links:
        delete_link(link.short_code)
        db.delete(link)
        count += 1
    db.commit()
    return {"deleted_links": count}

@router.delete("/links/{short_code}")
def delete_link_endpoint(short_code: str, db : Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        return {"error": "Link not found"}
    db.delete(link)
    db.commit()
    delete_link(short_code)
    return {"message": "Link deleted"}


@router.put("/links/{short_code}")
def update_link(short_code: str, data: LinkUpdate, db : Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if not link:
        return {"error": "Link not found"}
    link.original_url = data.original_url
    db.commit()

    delete_link(short_code)

    set_link(short_code, data.original_url)
    return {"message": "Link updated"}


@router.get("/links/search")
def search_link(original_url: str, db : Session = Depends(get_db)):
    link = db.query(Link).filter(Link.original_url == original_url).first()

    if not link:
        return {"error": "Link not found"}

    return {
        "short_code": link.short_code,
        "original_url": link.original_url}

@router.get("/links/expired")
def get_expired_links_extra_func(db : Session = Depends(get_db)):
    now = datetime.utcnow()
    links = db.query(Link).filter(Link.expires_at < now).all()
    result = []

    for link in links:
        result.append({
            "short_code": link.short_code,
            "original_url": link.original_url,
            "expires_at": link.expires_at,
            "project": link.project
        })
    return result

# extra func to get grouped links by project
@router.get("/links/project/{project_name}")
def get_project_links_extra_func(project_name: str, db : Session = Depends(get_db)):
    links = db.query(Link).filter(Link.project == project_name).all()
    return links

# extra func to get all links
@router.get("/links")
def get_all_links_extra_func(db : Session = Depends(get_db)):

    links = db.query(Link).all()

    result = []

    for link in links:
        result.append({
            "short_code": link.short_code,
            "original_url": link.original_url,
            "created_at": link.created_at,
            "click_count": link.click_count,
            "last_used_at": link.last_used_at,
            'project': link.project
        })

    return result