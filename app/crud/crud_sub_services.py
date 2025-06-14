
from sqlalchemy.orm import Session
from app.db.model.sub_service import SubService

def get_subservices_by_service_id(db: Session, service_id: int):
    return db.query(SubService).filter(SubService.service_id == service_id).all()
