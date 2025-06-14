

# app/db/model/service.py
from sqlalchemy import Column, Integer, String , DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class GalleryModel(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    category = Column(String, index=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)