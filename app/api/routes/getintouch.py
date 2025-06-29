
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.getintouch import GetintouchCreate, GetintouchOut
from app.crud import getintouch
from app.db.session import get_db

router = APIRouter(
    prefix="/getintouch",
    tags=["Getintouch"]
)

# Submit a new contact message
@router.post("/", response_model=GetintouchOut)
def submit_contact(contact: GetintouchCreate, db: Session = Depends(get_db)):
    return getintouch.create_contact(db, contact)

# Get all contact messages (admin use)
@router.get("/contact-mesages", response_model=List[GetintouchOut])
def read_all_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return getintouch.get_all_contacts(db, skip=skip, limit=limit)

# Get a specific contact message by ID
@router.get("/{contact_id}", response_model=GetintouchOut)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = getintouch.get_contact_by_id(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact message not found")
    return contact

# Delete a contact message
@router.delete("/delete-message/{contact_id}", response_model=GetintouchOut)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = getintouch.delete_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact message not found")
    return contact
