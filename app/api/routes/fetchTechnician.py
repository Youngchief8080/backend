from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.user import TechnicianMinimalOut
from app.db.session import get_db
from app.db.model.user import User
from app.db.model.booking import Booking

router = APIRouter()

class AssignTechnicianRequest(BaseModel):
    technician_id: int  # Changed to match User.id type

class AssignTechnicianResponse(BaseModel):
    success: bool
    message: str
    booking_id: int
    technician_id: int
    technician_name: str

@router.get("/technicians-minimal", response_model=List[TechnicianMinimalOut])
def get_minimal_technicians(db: Session = Depends(get_db)):
    return db.query(User).filter(User.role == "technician").all()

@router.post("/auth/assign-technician/{booking_id}", response_model=AssignTechnicianResponse)
def assign_technician(
    booking_id: int,
    request: AssignTechnicianRequest,
    db: Session = Depends(get_db)
):
    # 1. Verify booking exists
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_id} not found"
        )

    # 2. Verify technician exists and has correct role
    technician = db.query(User).filter(
        User.id == request.technician_id,
        User.role == "technician"
    ).first()
    
    if not technician:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a technician or doesn't exist"
        )

    # 3. Update booking
    booking.technician_id = technician.id
    booking.status = "assigned"  # Optional: Update status
    db.commit()

    return {
        "success": True,
        "message": f"Technician {technician.full_name} assigned successfully",
        "booking_id": booking.id,
        "technician_id": technician.id,
        "technician_name": technician.full_name
    }