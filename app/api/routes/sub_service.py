from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from typing import List   # <-- Add this line
from app.db.session import get_db
from app.db.model.sub_service import SubService
from app.db.model.service import ServiceModel
from app.schemas import sub_service as schemas
from app.crud import crud_sub_services
import shutil
import os
from uuid import uuid4

router = APIRouter(prefix="/sub-services", tags=["Sub Services"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../uploads/sub_services"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_image(image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/uploads/sub_services/{filename}".replace("\\", "/")

# CREATE
@router.post("/")
def create_sub_service(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(...),
    service_id: int = Form(...),
    db: Session = Depends(get_db),
):
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Parent service not found")

    image_url = save_image(image)

    sub_service = SubService(
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        service_id=service_id
    )
    db.add(sub_service)
    db.commit()
    db.refresh(sub_service)

    return {
        "id": sub_service.id,
        "name": sub_service.name,
        "description": sub_service.description,
        "price": sub_service.price,
        "image_url": sub_service.image_url,
        "service_id": sub_service.service_id
    }

# FETCH ALL
@router.get("/manage/")
def get_sub_services(db: Session = Depends(get_db)):
    sub_services = db.query(SubService).options(joinedload(SubService.service)).all()

    return [
        {
            "id": ss.id,
            "name": ss.name,
            "description": ss.description,
            "price": ss.price,
            "image_url": ss.image_url,
            "parent_service": {
                "name": ss.service.name if ss.service else None
            }
        } for ss in sub_services
    ]


# UPDATE
@router.put("/manage/{sub_service_id}")
def update_sub_service(
    sub_service_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    sub_service = db.query(SubService).filter(SubService.id == sub_service_id).first()
    if not sub_service:
        raise HTTPException(status_code=404, detail="Sub-service not found")

    sub_service.name = name
    sub_service.description = description
    sub_service.price = price

    if image:
        image_url = save_image(image)
        sub_service.image_url = image_url

    db.commit()
    db.refresh(sub_service)

    return {
        "id": sub_service.id,
        "name": sub_service.name,
        "description": sub_service.description,
        "price": sub_service.price,
        "image_url": sub_service.image_url,
        "service_id": sub_service.service_id
    }

# DELETE
@router.delete("/manage/{sub_service_id}")
def delete_sub_service(sub_service_id: int, db: Session = Depends(get_db)):
    sub_service = db.query(SubService).filter(SubService.id == sub_service_id).first()
    if not sub_service:
        raise HTTPException(status_code=404, detail="Sub-service not found")

    db.delete(sub_service)
    db.commit()
    return {"detail": "Sub-service deleted successfully"}

@router.get("/services/{service_id}/subservices", response_model=list[schemas.SubServiceOut])
def get_subservices_for_service(service_id: int, db: Session = Depends(get_db)):
    subservices = crud_sub_services.get_subservices_by_service_id(db, service_id)
    if not subservices:
        raise HTTPException(status_code=404, detail="No sub-services found for this service.")
    return subservices


