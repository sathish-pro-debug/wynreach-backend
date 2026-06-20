from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_main_db
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class ListCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/")
def get_lists(db: Session = Depends(get_main_db)):
    return []

@router.post("/")
def create_list(payload: ListCreate, db: Session = Depends(get_main_db)):
    return {"message": "List created", "name": payload.name}
