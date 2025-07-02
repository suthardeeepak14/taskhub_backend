from sqlalchemy.orm import Session
from app import schemas, auth
from app.models import User

def register_user(db: Session, user_data: schemas.UserCreate):
    hashed_pw = auth.hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        role="user" 
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user