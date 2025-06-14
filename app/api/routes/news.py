
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form , Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.model.news import NewsModel
import shutil
import os
from uuid import uuid4
from typing import List

router = APIRouter(prefix="/news", tags=["News"])

# Set up the upload directory relative to project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.normpath(os.path.join(BASE_DIR, "../../../uploads/news"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_image(image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, filename)

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/uploads/news/{filename}".replace("\\", "/")

# ------------------ Create Service ------------------
@router.post("/")
def create_service(
    title: str = Form(...),
    description: str = Form(None),
    category: str = Form(...),
    image: UploadFile = File(...),
    content: str = File(...),
    db: Session = Depends(get_db),
):
    try:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_url = save_image(image)

        new_service = NewsModel(
            title=title,
            description=description or "",
            category=category,
            image_url=image_url,
            content=content,
        )
        db.add(new_service)
        db.commit()
        db.refresh(new_service)

        return {
            "id": new_service.id,
            "title": new_service.title,
            "description": new_service.description,
            "category": new_service.category,
            "image_url": new_service.image_url,
            "content": new_service.content,
            "created_at": new_service.created_at,  # Changed from 'created' to 'created_at'
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

#     # Add this to your existing FastAPI routes
@router.get("/getAllNews")
def get_gallery_images(db: Session = Depends(get_db)):
    try:
        # Order by created_at in descending order (newest first)
        images = db.query(NewsModel).order_by(NewsModel.created_at.desc()).all()
        
        return [
            {
                "id": img.id,
                "title": img.title,
                "description": img.description,
                "image_url": img.image_url,
                "category": img.category,
                "content": img.content,
                "created_at": img.created_at.isoformat() if img.created_at else None,
            }
            for img in images
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    #for Delete
    
@router.delete("/{news_id}", status_code=204)
def delete_service(news_id: int, db: Session = Depends(get_db)):
    service = db.query(NewsModel).filter(NewsModel.id == news_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()
    return Response(status_code=204)  # No content response for DELETE


# ------------------ Update Service ------------------
@router.put("/{news_id}")
def update_service(
    news_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    service = db.query(NewsModel).filter(NewsModel.id == news_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.title = title
    service.description = description
    service.category = category
    service.content = content

    if image:
        service.image_url = save_image(image)
    db.commit()
    db.refresh(service)
    return {
        "id": service.id,
        "title": service.title,
        "description": service.description,
        "category": service.category,
        "content": service.content,
        "image_url": service.image_url,
    }
# 
