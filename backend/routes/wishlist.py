from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import getCurrentUser
import models
import schemas


router= APIRouter(prefix="/wishlist",tags=["wishlist"])


@router.get("/", response_model=List[schemas.WishlistItemResponse])
def getWishlist(
        db: Session = Depends(get_db),
    current_user: models.User = Depends(getCurrentUser)
):
    return current_user.wishlist

@router.post("/", response_model=schemas.WishlistItemResponse)
def add_to_wishlist(
    item: schemas.WishlistItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(getCurrentUser)
):

    existing = db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id    == current_user.id,
        models.WishlistItem.game_title == item.game_title
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Game already in wishlist")

    wishlist_item = models.WishlistItem(
        user_id    = current_user.id,
        game_title = item.game_title,
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

@router.delete("/{item_id}")
def remove_from_wishlist(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(getCurrentUser)
):
    item = db.query(models.WishlistItem).filter(
        models.WishlistItem.id      == item_id,
        models.WishlistItem.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": f"Removed '{item.game_title}' from wishlist"}

