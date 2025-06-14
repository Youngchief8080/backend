# app/crud/contact.py
from sqlalchemy.orm import Session
from app.db.model.contact import ContactModel
from app.schemas.contact import ContactForm

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