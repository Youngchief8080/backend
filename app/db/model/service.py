# app/db/model/service.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class ServiceModel(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String, nullable=True)

    sub_services = relationship("SubService", back_populates="service", cascade="all, delete-orphan")
