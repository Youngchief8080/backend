from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import cast, Integer
from typing import List, Optional

from app.db.session import get_db
from app.db.model.booking import Booking, BookingItem
from app.db.model.user import User
from app.schemas.booking import (
    BookingCreate, 
    BookingResponse,
    BookingItemBase,
    BookingItemResponse,
    BookingUpdate
)
from app.db.model.loyalty_point import LoyaltyPointTransaction

router = APIRouter()

@router.post("/bookings/", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    try:
        new_booking = Booking(
            user_id=booking.user_id,
            contact_info=booking.contact_info,
            date=booking.date,
            time=booking.time,
            total_amount=booking.total_amount,
            notes=booking.notes,
            status="pending"
        )
        db.add(new_booking)
        db.flush()

        for item in booking.items:
            db_item = BookingItem(
                booking_id=new_booking.id,
                sub_service_id=item.sub_service_id,
                name=item.name,
                price=item.price,
                quantity=item.quantity
            )
            db.add(db_item)

         # Add this after creating new_booking and before commit
        user = db.query(User).filter(User.id == booking.user_id).first()
        if user:
            # Award standard points
            earned = 10
            user.loyalty_points = (user.loyalty_points or 0) + earned

            db.add(LoyaltyPointTransaction(
                user_id=user.id,
                points=earned,
                reason="booking",
                related_id=new_booking.id
            ))

            # Handle redemption
            if booking.points_used and booking.points_used > 0:
                if user.loyalty_points < booking.points_used:
                    raise HTTPException(status_code=400, detail="Not enough points")
                user.loyalty_points -= booking.points_used

                db.add(LoyaltyPointTransaction(
                    user_id=user.id,
                    points=-booking.points_used,
                    reason="redeem",
                    related_id=new_booking.id
                ))

            new_booking.points_used = booking.points_used or 0


        db.commit()
        db.refresh(new_booking)
        return new_booking
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings/", response_model=List[BookingResponse])
def get_bookings(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Booking).options(joinedload(Booking.items))
    if status:
        query = query.filter(Booking.status == 'pending')
    bookings = query.order_by(Booking.date.desc(), Booking.time.desc()).all()
    return bookings


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking)\
        .options(joinedload(Booking.items))\
        .filter(Booking.id == booking_id)\
        .first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.get("/bookings/user/{user_id}", response_model=List[BookingResponse])
def get_user_bookings(user_id: str, db: Session = Depends(get_db)):
    bookings = db.query(Booking)\
        .options(joinedload(Booking.items))\
        .filter(Booking.user_id == user_id)\
        .order_by(Booking.date.desc(), Booking.time.desc())\
        .all()
    return bookings


@router.get("/booking-users/")
def get_users_with_bookings(db: Session = Depends(get_db)):
    users = db.query(
        User.id,
        User.full_name,
        User.email
    ).join(Booking, User.id == cast(Booking.user_id, Integer))\
     .distinct()\
     .all()
    
    return [{
        "user_id": user.id,
        "user_name": user.full_name,
        "email": user.email
    } for user in users]


@router.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking_status(
    booking_id: int, 
    booking_update: BookingUpdate, 
    db: Session = Depends(get_db)
):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not db_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    for field, value in booking_update.dict(exclude_unset=True).items():
        setattr(db_booking, field, value)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.query(BookingItem).filter(BookingItem.booking_id == booking_id).delete()
    db.delete(booking)
    db.commit()
    
    return {"message": "Booking deleted successfully"}


@router.get("/counts/pending")
def count_pending_bookings(db: Session = Depends(get_db)):
    count = db.query(Booking).filter(Booking.status == "pending").count()
    return {"count": count}


@router.get("/counts/assigned")
def count_assigned_bookings(db: Session = Depends(get_db)):
    count = db.query(Booking).filter(Booking.status == "assigned").count()
    return {"count": count}