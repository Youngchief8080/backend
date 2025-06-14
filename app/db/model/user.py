from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    role = Column(String, default="user")  # roles: user, admin, technician
    loyalty_points = Column(Integer, default=0, nullable=False)
    bio = Column(Text, nullable=True)
    profile_image = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    linkedin = Column(String, nullable=True)
    twitter = Column(String, nullable=True)
    street = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer_bookings = relationship(
        "Booking", 
        foreign_keys="Booking.user_id",
        back_populates="customer"
    )
    technician_bookings = relationship(
        "Booking",
        foreign_keys="Booking.technician_id", 
        back_populates="technician"
    )

    point_transactions = relationship(
    "LoyaltyPointTransaction",
    back_populates="user",
    cascade="all, delete-orphan"
    )


    # In your User model
# contacts = relationship("ContactModel", back_populates="user", cascade="all, delete-orphan")