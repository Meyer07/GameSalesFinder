from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ── Auth ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    email:              EmailStr
    password:           str
    notification_email: Optional[EmailStr] = None
    pushover_key:       Optional[str] = None
    platforms:          Optional[str] = "ps"  # default to PlayStation only


class UserLogin(BaseModel):
    email:    EmailStr
    password: str


class UserResponse(BaseModel):
    id:                 int
    email:              EmailStr
    notification_email: Optional[EmailStr]
    pushover_key:       Optional[str]
    platforms:          str
    is_active:          bool
    created_at:         datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type:   str


# ── Wishlist ───────────────────────────────────────────────

class WishlistItemCreate(BaseModel):
    game_title: str


class WishlistItemResponse(BaseModel):
    id:         int
    game_title: str
    added_at:   datetime

    class Config:
        from_attributes = True


# ── User Settings Update ───────────────────────────────────

class UserUpdate(BaseModel):
    notification_email: Optional[EmailStr] = None
    pushover_key:       Optional[str] = None
    password:           Optional[str] = None
    platforms:          Optional[str] = None  # e.g. "ps,steam,switch"