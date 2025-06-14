
# app/api/routes/contact.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from typing import List, Optional
from app.schemas.contact import ContactForm, ContactResponse
from app.db.session import get_db
from app.crud.contact import create_contact , get_user_messages
from app.services.jwt import get_current_user
from app.schemas.user import UserOut

router = APIRouter()

@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def submit_contact(contact_form: ContactForm, db: Session = Depends(get_db)):
    try:
        contact = create_contact(db, contact_form)
        return contact
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/contacts/me", response_model=List[ContactResponse])
def get_my_messages(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user)
):
    try:
        return get_user_messages(db, current_user.id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch messages")