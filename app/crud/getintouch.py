from sqlalchemy.orm import Session
from app.db.model.getintouch import GetintouchModel
from app.schemas.getintouch import GetintouchCreate

# Create a new contact message
def create_contact(db: Session, contact: GetintouchCreate):
    db_contact = GetintouchModel(
        name=contact.name,
        email=contact.email,
        message=contact.message
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

# Get all contact messages
def get_all_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(GetintouchModel).offset(skip).limit(limit).all()

# Get a specific contact message by ID
def get_contact_by_id(db: Session, contact_id: int):
    return db.query(GetintouchModel).filter(GetintouchModel.id == contact_id).first()

# Delete a contact message
def delete_contact(db: Session, contact_id: int):
    contact = db.query(GetintouchModel).filter(GetintouchModel.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact
