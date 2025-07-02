from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, models
from app.auth import hash_password, verify_password, create_access_token
from app.schemas import UserResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Register User (Default role: user)
@router.post("/register", response_model=UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role="user"  # ✅ Default role is user
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user  # ✅ This will auto return role via UserResponse schema

# ✅ Login Route (return user with role)
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)  # ✅ Returns full user with role
    }
