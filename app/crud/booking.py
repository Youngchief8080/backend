from sqlalchemy.orm import Session
from app.db.model.booking import Booking, BookingItem
from app.schemas.booking import BookingCreate


def create_booking(db: Session, booking_data: BookingCreate):
    booking = Booking(
        user_id=booking_data.user_id,
        contact_info=booking_data.contact_info,
        date=booking_data.date,
        time=booking_data.time,
        total_amount=booking_data.total_amount,
    )
    db.add(booking)
    db.flush()

    for item in booking_data.items:
        booking_item = BookingItem(
            booking_id=booking.id,
            sub_service_id=item.sub_service_id,
            name=item.name,
            price=item.price,
            quantity=item.quantity,
        )
        db.add(booking_item)

    db.commit()
    db.refresh(booking)
    return booking


def get_bookings_by_user(db: Session, user_id: str):
    return db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.date.desc()).all()
