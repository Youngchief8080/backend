
# app/api/routes/contact.py
from fastapi import APIRouter, Depends, HTTPException, status , Query
from sqlalchemy.orm import Session

from typing import List, Optional
from app.schemas.contact import ContactForm, ContactResponse , ContactReply
from app.db.session import get_db
from app.crud.contact import create_contact , get_user_messages , get_message_by_id , reply_to_message
from app.services.jwt import get_current_user
from app.schemas.user import UserOut
from app.crud.contact import get_all_messages
from app.services.roles import admin_required
from app.db.model.contact import ContactModel 

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
    

@router.get("/contacts/admin", response_model=List[ContactResponse])
def get_all_user_messages(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: UserOut = Depends(admin_required)  # Enforce admin access
):
    try:
        return get_all_messages(db, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch messages")
    
@router.get("/contacts/{message_id}", response_model=ContactResponse)
def get_single_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_admin: UserOut = Depends(admin_required)
):
    contact = get_message_by_id(db, message_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Message not found")
    return contact


@router.post("/contacts/{contact_id}/reply", response_model=ContactResponse)
def reply_to_contact(
    contact_id: int,
    reply_data: ContactReply,
    db: Session = Depends(get_db),
    current_admin: UserOut = Depends(admin_required)
):
    contact = db.query(ContactModel).filter(ContactModel.id == contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Message not found")

    contact.reply = reply_data.reply
    contact.status = reply_data.status
    db.commit()
    db.refresh(contact)
    return contact

