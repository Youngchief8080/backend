from sqlalchemy.orm import Session
from app.db.model.service import ServiceModel
from app.schemas.service import ServiceCreate

def create_service(db: Session, service: ServiceCreate):
    new_service = ServiceModel(**service.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

def get_all_services(db: Session, skip: int = 0, limit: int = 10, search: str = ""):
    query = db.query(ServiceModel)
    if search:
        query = query.filter(ServiceModel.name.ilike(f"%{search}%"))
    total = query.count()
    services = query.offset(skip).limit(limit).all()
    return {"total": total, "services": services}

def get_service_by_id(db: Session, service_id: int):
    return db.query(ServiceModel).filter(ServiceModel.id == service_id).first()

def update_service(db: Session, service_id: int, updated_data: ServiceCreate):
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        return None
    for key, value in updated_data.dict().items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service

def delete_service(db: Session, service_id: int):
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        return False
    db.delete(service)
    db.commit()
    return True
