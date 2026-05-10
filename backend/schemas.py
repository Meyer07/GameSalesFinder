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


#store_deals database

class StoreDealCreate(BaseModel):
    game_title:    str
    platform:      str        # "ps" or "xbox"
    sale_price:    str        # e.g. "$29.99"
    regular_price: str        # e.g. "$59.99"
    discount:      str        # e.g. "50"
    sale_end_date: Optional[str] = None


class StoreDealResponse(BaseModel):
    id: int
    game_title:str
    platform: str
    sale_price:str
    regular_price:str
    discount: str
    sale_end_date: Optional[str]
    updated_at:    datetime
 
    class Config:
        from_attributes = True

class StoreDealUpdate(BaseModel):
    game_title:    Optional[str] = None
    platform:      Optional[str] = None
    sale_price:    Optional[str] = None
    regular_price: Optional[str] = None
    discount:      Optional[str] = None
    sale_end_date: Optional[str] = None