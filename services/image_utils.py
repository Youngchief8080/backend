
# backend/services/image_utils.py
import os
import shutil
from uuid import uuid4
from fastapi import UploadFile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "uploads", "services")  # Go up one level

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_service_image(image: UploadFile) -> str:
    ext = os.path.splitext(image.filename)[-1]
    filename = f"{uuid4().hex}{ext}"

    image_path = os.path.join(UPLOAD_DIR, filename)
    image_path = image_path.replace("\\", "/")

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return f"/uploads/services/{filename}".replace("\\", "/")
