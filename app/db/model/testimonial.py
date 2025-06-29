


# app/db/model/service.py
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class TestimonialModel(Base):
    __tablename__ = "testimonial"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String, nullable=True)