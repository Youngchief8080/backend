
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form , Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.model.gallery import GalleryModel
import shutil
import os
from uuid import uuid4
from typing import List

router = APIRouter(prefix="/gallery", tags=["Gallery"])

# Set up the upload directory relative to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../uploads/gallery"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_image(image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/uploads/gallery/{filename}".replace("\\", "/")

# ------------------ Create Service ------------------
@router.post("/")
def create_gallery_items(
    title: str = Form(...),
    description: str = Form(None),
    category: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    try:
        new_items = []

        for image in images:
            if not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"{image.filename} is not a valid image")

            image_url = save_image(image)

            gallery_item = GalleryModel(
                title=title,
                description=description or "",
                category=category,
                image_url=image_url
            )
            db.add(gallery_item)
            db.flush()  # prepares object with id before commit

            new_items.append({
                "id": gallery_item.id,
                "title": gallery_item.title,
                "description": gallery_item.description,
                "category": gallery_item.category,
                "image_url": gallery_item.image_url,
                "created_at": gallery_item.created_at,
            })

        db.commit()
        return new_items

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

    # Add this to your existing FastAPI routes
@router.get("/getallgallerry")
def get_gallery_images(db: Session = Depends(get_db)):
    try:
        # Order by created_at in descending order (newest first)
        images = db.query(GalleryModel).order_by(GalleryModel.created_at.desc()).all()
        
        return [
            {
                "id": img.id,
                "title": img.title,
                "description": img.description,
                "image_url": img.image_url,
                "category": img.category,
                "created_at": img.created_at.isoformat() if img.created_at else None,
            }
            for img in images
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # ------------------ Delete Service ------------------
@router.delete("/{gallery_id}", status_code=204)
def delete_service(gallery_id: int, db: Session = Depends(get_db)):
    service = db.query(GalleryModel).filter(GalleryModel.id == gallery_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return Response(status_code=204)  # No content response for DELETE

# ------------------ Update Service ------------------
@router.put("/{gallery_id}")
def update_service(
    gallery_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = db.query(GalleryModel).filter(GalleryModel.id == gallery_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.title = title
    service.description = description
    service.category = category

    if image:
        service.image_url = save_image(image)
    db.commit()
    db.refresh(service)
    return {
        "id": service.id,
        "title": service.title,
        "description": service.description,
        "category": service.category,
        "image_url": service.image_url,
    }
# 
