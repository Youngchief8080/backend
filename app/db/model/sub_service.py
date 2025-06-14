from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base  # Adjust import as necessary

class SubService(Base):
    __tablename__ = "sub_services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)

    service_id = Column(Integer, ForeignKey("services.id"))  # Foreign key to services table

    service = relationship("ServiceModel", back_populates="sub_services")  # String reference to ServiceModel
