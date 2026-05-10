from pydantic import BaseModel, EmailStr, field_validator
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
    platform:      str
    sale_price:    str
    regular_price: str
    discount:      str
    url:           Optional[str] = None
    sale_end_date: Optional[str] = None

    @field_validator("sale_price", "regular_price", "discount", mode="before")
    @classmethod
    def coerce_to_str(cls, v):
        return str(v) if v is not None else v


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
    url:           Optional[str] = None
    sale_end_date: Optional[str] = None