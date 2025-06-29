# app/crud/contact.py
from sqlalchemy.orm import Session
from app.db.model.contact import ContactModel
from app.schemas.contact import ContactForm , ContactReply
from typing import Optional, List

def create_contact(db: Session, contact_data: ContactForm):
    contact = ContactModel(**contact_data.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def get_user_messages(db: Session, user_id: int, status: str = None):
    query = db.query(ContactModel).filter(ContactModel.user_id == user_id)
    
    if status and status != 'all':
        query = query.filter(ContactModel.status == status)

    return query.order_by(ContactModel.created_at.desc()).all()

def get_all_messages(db: Session, status: Optional[str] = None) -> List[ContactModel]:
    query = db.query(ContactModel)

    if status and status != 'all':
        query = query.filter(ContactModel.status == status)

    return query.order_by(ContactModel.created_at.desc()).all()

def reply_to_contact(db: Session, contact_id: int, response: str, status: str):
    contact = db.query(ContactModel).filter(ContactModel.id == contact_id).first()

    if not contact:
        return None

    contact.admin_response = response
    contact.status = status
    db.commit()
    db.refresh(contact)
    return contact

def get_message_by_id(db: Session, message_id: int) -> Optional[ContactModel]:
    return db.query(ContactModel).filter(ContactModel.id == message_id).first()

def reply_to_message(db: Session, message_id: int, reply_data: ContactReply) -> Optional[ContactModel]:
    message = db.query(ContactModel).filter(ContactModel.id == message_id).first()
    if not message:
        return None

    message.response = reply_data.response
    message.status = reply_data.status
    db.commit()
    db.refresh(message)
    return message
