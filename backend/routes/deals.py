from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from auth import get_current_user
import models
import schemas
import os


router=APIRouter(prefix="/deals",tags=["deals"])

ADMIN_EMAIL=os.getenv("ADMIN_EMAIL","")


def require_admin(current_user:models.User=Depends(get_current_user)):
    if current_user!=ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user



@router.get("/", response_model=List[schemas.StoreDealResponse])
def get_deals(platform:str=None,db:Session=Depends(get_db)):
    query=db.query(models.store_deal)
    if platform:
        query=query.filter(models.store_deal.platform==platform)
    return query.order_by(models.store_deal.game_title).all()



@router.post("/", response_model=schemas.StoreDealResponse)
def add_deal(deal: schemas.StoreDealCreate,db: Session = Depends(get_db),admin: models.User = Depends(require_admin)):
    new_deal = models.StoreDeal(
        game_title    = deal.game_title,
        platform      = deal.platform,
        sale_price    = deal.sale_price,
        regular_price = deal.regular_price,
        discount      = deal.discount,
        sale_end_date = deal.sale_end_date,
    )
    db.add(new_deal)
    db.commit()
    db.refresh()
    return new_deal


@router.put("/{deal_id}", response_model=schemas.StoreDealResponse)
def update_deal(
    deal_id: int,
    updates: schemas.StoreDealUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Update an existing store deal."""
    deal = db.query(models.StoreDeal).filter(models.StoreDeal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
 
    if updates.game_title is not None: deal.game_title= updates.game_title
    if updates.platform is not None: deal.platform= updates.platform
    if updates.sale_price is not None: deal.sale_price= updates.sale_price
    if updates.regular_price is not None: deal.regular_price = updates.regular_price
    if updates.discount is not None: deal.discount= updates.discount
    if updates.sale_end_date is not None: deal.sale_end_date = updates.sale_end_date
    db.commit()
    db.refresh(deal)
    return deal
 
 
@router.delete("/{deal_id}")
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Delete a store deal."""
    deal = db.query(models.StoreDeal).filter(models.StoreDeal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
 
    db.delete(deal)
    db.commit()
    return {"message": f"Deleted deal: {deal.game_title}"}
 
 
@router.delete("/clear/{platform}")
def clear_platform_deals(
    platform: str,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin)
):
    """Clear all deals for a platform — use this before adding fresh weekly deals."""
    count = db.query(models.StoreDeal).filter(models.StoreDeal.platform == platform).delete()
    db.commit()
    return {"message": f"Cleared {count} {platform} deals"}