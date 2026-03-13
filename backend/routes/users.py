from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import hash_password, verify_password, create_access_token, getCurrentUser
import models
import schemas


router = APIRouter(prefix="/auth", tags=["auth"])




@router.post("/signup", response_model=schemas.UserResponse)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email              = user_data.email,
        hashed_password    = hash_password(user_data.password),
        notification_email = user_data.notification_email or user_data.email, 
        pushover_key       = user_data.pushover_key,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.put("/me", response_model=schemas.UserResponse)
def updateMe(
    updates: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(getCurrentUser)
):
    if updates.notification_email is not None:
        current_user.notification_email = updates.notification_email
    if updates.pushover_key is not None:
        current_user.pushover_key = updates.pushover_key
    if updates.password is not None:
        current_user.hashed_password = hash_password(updates.password)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me", response_model=schemas.UserResponse)
def getMe(current_user: models.User = Depends(getCurrentUser)):
    return current_user