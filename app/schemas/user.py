from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None

class UserCreate(UserBase):
    password: str
    bio: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None

class UserOut(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role: str
    loyalty_points: int  # ✅ Must be included
    
    # Profile fields
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    
    # Timestamps
    # created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AdminCreateUser(UserBase):
    password: str
    role: str  # Required for admin-created users
    
    # Optional profile fields
    bio: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    is_active: bool = True
    is_verified: bool = True

class UserUpdate(BaseModel):  # Note: Not inheriting from UserBase
    # Basic info
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    
    # Profile info
    bio: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    
    # Don't include email in updates (should be separate endpoint if needed)
    # Don't include profile_image here - handled separately via UploadFile

    class Config:
        orm_mode = True

        # schemas/user.py



class TechnicianMinimalOut(BaseModel):
    id: int
    full_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserProfileOut(BaseModel):
    id: str
    full_name: str
    role: str
    is_active: bool
    profile_image: str

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
