

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.model.pastevent import PastEventModel
import shutil
import os
from uuid import uuid4
from typing import List

router = APIRouter(prefix="/pastevents", tags=["Pastevents"])

# Set up the upload directory relative to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../uploads/pastevents"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_image(image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/uploads/pastevents/{filename}".replace("\\", "/")

# ------------------ Create Service ------------------
@router.post("/")
def create_service(
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    image_url = save_image(image)

    new_service = PastEventModel(
        name=name,
        description=description,
        image_url=image_url
    )
    db.add(new_service)
    db.commit()
    db.refresh(new_service)

    return {
        "id": new_service.id,
        "name": new_service.name,
        "description": new_service.description,
        "image_url": new_service.image_url,
    }

# ------------------ Get All Services ------------------
@router.get("/")
def get_all_services(page: int = 1, limit: int = 5, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    services = db.query(PastEventModel).offset(skip).limit(limit).all()
    total_count = db.query(PastEventModel).count()

    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "image_url": s.image_url,
            } for s in services
        ],
        "totalCount": total_count
    }

# ------------------ Get Single Service ------------------
@router.get("/{service_id}")
def get_service_by_id(service_id: int, db: Session = Depends(get_db)):
    service = db.query(PastEventModel).filter(PastEventModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "image_url": service.image_url,
    }

# ------------------ Update Service ------------------
@router.put("/{service_id}")
def update_service(
    service_id: int,
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = db.query(PastEventModel).filter(PastEventModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.name = name
    service.description = description

    if image:
        service.image_url = save_image(image)

    db.commit()
    db.refresh(service)

    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "image_url": service.image_url,
    }

# ------------------ Delete Service ------------------
@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(PastEventModel).filter(PastEventModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()

    return {"detail": "Service deleted successfully"}
