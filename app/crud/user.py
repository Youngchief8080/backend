import secrets
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.model.user import User
from app.schemas.user import UserCreate, AdminCreateUser
from app.core.security import get_password_hash

# Set up logging for CRUD operations
logger = logging.getLogger(__name__)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def create_user(db: Session, user_in: UserCreate):
    try:
        verification_token = secrets.token_urlsafe(32)
        user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            verification_token=verification_token
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created: {user.email}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

def create_user_by_admin(db: Session, user_in: AdminCreateUser):
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        logger.warning(f"Attempt to create a user with an already registered email: {user_in.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    try:
        user = User(
            full_name=user_in.full_name,
            email=user_in.email,
            phone=user_in.phone,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role,
            is_verified=True,
            verification_token=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Admin created user: {user.email} with role {user.role}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user by admin: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user by admin")
