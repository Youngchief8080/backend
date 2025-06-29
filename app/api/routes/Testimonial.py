from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.model.testimonial import TestimonialModel
from app.schemas.testimonial import TestimonialOut
import shutil
import os
from uuid import uuid4
from typing import List

router = APIRouter(prefix="/testimonials", tags=["Testimonials"])

# Upload directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../uploads/testimonial"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_image(image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/uploads/testimonial/{filename}".replace("\\", "/")

# ------------------ Get Hero Banner ------------------
@router.get("/hero", response_model=TestimonialOut)
def get_hero_banner(db: Session = Depends(get_db)):
    banner = db.query(TestimonialModel).first()
    if not banner:
        raise HTTPException(status_code=404, detail="No Testimonial found")
    return banner

# ------------------ Create Banner ------------------
@router.post("/")
def create_service(
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    image_url = save_image(image)

    new_service = TestimonialModel(
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

# ------------------ Get All Banners ------------------
@router.get("/")
def get_all_services(page: int = 1, limit: int = 5, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    services = db.query(TestimonialModel).offset(skip).limit(limit).all()
    total_count = db.query(TestimonialModel).count()
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

# ------------------ Get Single Banner ------------------
@router.get("/{service_id}")
def get_service_by_id(service_id: int, db: Session = Depends(get_db)):
    service = db.query(TestimonialModel).filter(TestimonialModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "image_url": service.image_url,
    }

# ------------------ Update Banner ------------------
@router.put("/{service_id}")
def update_service(
    service_id: int,
    name: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = db.query(TestimonialModel).filter(TestimonialModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Testimonial not found")

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

# ------------------ Delete Banner ------------------
@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(TestimonialModel).filter(TestimonialModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Teams not found")

    db.delete(service)
    db.commit()

    return {"detail": "Testimonial deleted successfully"}
