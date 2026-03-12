from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional



class UserCreate(BaseModel):
    email:              EmailStr
    password:           str
    notification_email: Optional[EmailStr] = None
    pushover_key:       Optional[str] = None


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserResponse(BaseModel):
    id:                 int
    email:              EmailStr
    notification_email: Optional[EmailStr]
    pushover_key:       Optional[str]
    is_active:          bool
    created_at:         datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type:   str


class WishlistItemCreate(BaseModel):
    game_title: str


class WishlistItemResponse(BaseModel):
    id:         int
    game_title: str
    added_at:   datetime

    class Config:
        from_attributes = True




class UserUpdate(BaseModel):
    notification_email: Optional[EmailStr] = None
    pushover_key:       Optional[str] = None
    password:           Optional[str] = None