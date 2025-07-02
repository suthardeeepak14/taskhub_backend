from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

router = APIRouter()

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()