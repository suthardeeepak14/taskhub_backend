from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas
# from app.core.security import hash_password, verify_password
from schemas import UserOut
from fastapi import APIRouter, Depends
from app.database import get_db


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()