from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id                 = Column(Integer, primary_key=True, index=True)
    email              = Column(String, unique=True, index=True, nullable=False)
    hashed_password    = Column(String, nullable=False)
    notification_email = Column(String, nullable=True)
    pushover_key       = Column(String, nullable=True)
    platforms          = Column(String, nullable=False, default="ps")  # comma-separated: "ps,steam,switch,xbox"
    is_active          = Column(Boolean, default=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    wishlist           = relationship("WishlistItem", back_populates="user", cascade="all, delete")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_title = Column(String, nullable=False)
    added_at   = Column(DateTime(timezone=True), server_default=func.now())
    user       = relationship("User", back_populates="wishlist")


class StoreDeal(Base):
    __tablename__="store_deals"

    id=Column(Integer, primary_key=True,index=True)
    game_title=Column(String,nullable=False,index=True)
    platform=Column(String,nullable=False)
    sale_price=Column(String,nullable=False)
    regular_price=Column(String,nullable=False)
    discount=Column(String,nullable=False)
    url = Column(String, nullable=True)
    sale_end_date=Column(String,nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

