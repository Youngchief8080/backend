

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Time, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    contact_info = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    notes = Column(Text, nullable=True)
    points_used = Column(Integer, default=0, nullable=False)


    # Relationships
    items = relationship("BookingItem", back_populates="booking")
    customer = relationship("User", foreign_keys=[user_id], back_populates="customer_bookings")
    technician = relationship("User", foreign_keys=[technician_id], back_populates="technician_bookings")

class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    sub_service_id = Column(Integer)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)

    booking = relationship("Booking", back_populates="items")

    
