from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends

from .links import router
from .database import SessionLocal
from .models import Link
from .cache import get_link
from .database import engine
from .models import Base
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):

    cached = get_link(short_code)

    if cached:
        return RedirectResponse(cached)

    link = db.query(Link).filter(Link.short_code == short_code).first()

    if not link:
        return {"error": "Not found"}

    link.click_count += 1
    db.commit()

    return RedirectResponse(link.original_url)