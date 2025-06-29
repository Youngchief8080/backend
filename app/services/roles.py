
# app/services/roles.py
from fastapi import Depends, HTTPException, status
from app.services.jwt import get_current_user
from app.schemas.user import UserOut

def admin_required(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this resource"
        )
    return current_user
