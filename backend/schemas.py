from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class userCreate(BaseModel):
    email: EmailStr
    password: str
    notificationEmail:Optional[EmailStr]=None
    pushoverKey:Optional[str]=None


class userLogin(BaseModel):
    email:EmailStr
    password:str



class userResponse(BaseModel):
    id: int
    email: EmailStr
    notificationEmail:Optional[EmailStr]
    pushoverKey:Optional[str]
    isActive:bool
    createdAt:datetime

    class config:
        fromConfig=True


class token(BaseModel):
    accessToken:str
    tokenType:str


class wishListItemCreate(BaseModel):
    gameTitle:str


class wishListItemResponse(BaseModel):
    id: int
    gameTitle:str
    addedAt:datetime

    class Config:
        fromAttributes=True


class userUpdate(BaseModel):
    notificationEmail:Optional[EmailStr]=None
    pushoverTolen:Optional[EmailStr]=None
    password:Optional[EmailStr]=None
    