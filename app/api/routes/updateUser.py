from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil
from typing import Optional
import logging
from datetime import datetime
from uuid import uuid4

from app.db.session import get_db
from app.db.model.user import User
from app.schemas.user import UserOut
from pathlib import Path

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload directory
UPLOAD_BASE = Path("uploads")  # Relative to project root
UPLOAD_DIR = UPLOAD_BASE / "profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def save_profile_image(user_id: int, image: UploadFile) -> str:
    """Save profile image and return relative path"""
    try:
        # Validate image type
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
            )

        # Validate file size
        file_size = 0
        for chunk in image.file:
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {MAX_FILE_SIZE//(1024*1024)}MB"
                )
        image.file.seek(0)

        # Generate unique filename
        ext = os.path.splitext(image.filename)[1]
        filename = f"user_{user_id}_{uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Return relative path for storage in DB
        return f"/uploads/profile_images/{filename}"
        # return f"/uploads/profile_images/{filename}".replace("\\", "/")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving profile image: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to save profile image"
        )

@router.put("/update/{user_id}", response_model=UserOut)
async def update_user_profile(
    user_id: int,
    full_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    role: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    street: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    linkedin: Optional[str] = Form(None),
    twitter: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Update user profile information"""
    try:
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with ID {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")

        # Track updated fields
        updates = {}
        fields_to_update = {
            'full_name': full_name,
            'phone': phone,
            'role': role,
            'bio': bio,
            'street': street,
            'city': city,
            'state': state,
            'country': country,
            'linkedin': linkedin,
            'twitter': twitter
        }

        # Process text fields
        for field, value in fields_to_update.items():
            if value is not None and getattr(user, field) != value:
                setattr(user, field, value)
                updates[field] = value

        # Process profile image
        if profile_image is not None:  # Explicit None check
            try:
                # Handle case when image should be removed (empty string sent)
                if profile_image.filename == '':
                    if user.profile_image:
                        old_image_path = os.path.join(UPLOAD_DIR, os.path.basename(user.profile_image))
                        if os.path.exists(old_image_path):
                            os.unlink(old_image_path)
                            logger.info(f"Deleted old profile image for user {user_id}")
                    user.profile_image = None
                    updates['profile_image'] = None
                # Handle new image upload
                elif profile_image.filename:
                    # Delete old image if exists
                    if user.profile_image:
                        old_image_path = os.path.join(UPLOAD_DIR, os.path.basename(user.profile_image))
                        if os.path.exists(old_image_path):
                            os.unlink(old_image_path)
                            logger.info(f"Deleted old profile image for user {user_id}")

                    # Save new image
                    image_path = save_profile_image(user_id, profile_image)
                    user.profile_image = image_path
                    updates['profile_image'] = image_path
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing profile image: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Failed to process profile image"
                )

        if not updates:
            logger.warning(f"No valid updates provided for user {user_id}")
            raise HTTPException(
                status_code=400,
                detail="No valid updates provided"
            )

        # Commit changes
        db.commit()
        db.refresh(user)
        
        logger.info(f"Successfully updated user {user_id}. Updated fields: {list(updates.keys())}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the profile"
        )