from fastapi import Depends, HTTPException, status
from app.services.jwt import get_current_user
from app.db.model.user import User

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action",
        )
    return current_user
