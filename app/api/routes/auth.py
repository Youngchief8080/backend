from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from typing import List

from app.schemas.user import UserCreate, UserOut, AdminCreateUser, UserUpdate , TechnicianMinimalOut , UserProfileOut
from app.crud.user import get_user_by_email, get_user_by_id
from app.db.session import get_db
from app.core.security import get_password_hash, verify_password
from app.db.model.user import User
from app.services.email import send_verification_email
from app.utils.token import generate_verification_token, verify_token
from app.services.jwt import create_access_token
from app.api.deps import get_current_admin_user  # Admin-only route dependenc

router = APIRouter()

# ------------------------ Registration & Login ------------------------

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    verification_token = generate_verification_token(user_in.email)
    hashed_password = get_password_hash(user_in.password)

    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        verification_token=verification_token
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    send_verification_email(to_email=user.email, token=verification_token)

    return user


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"success": False, "detail": "Email already verified"}

    user.is_verified = True
    db.commit()

    return {"success": True, "message": "Email verified successfully"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
           
        },
    }

# ------------------------ Admin Create Technician ------------------------

@router.post("/create-user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(user_in: AdminCreateUser, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db=db, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user_in.password)

    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
        phone=user_in.phone,
        role=user_in.role,
        is_verified=True  # Admin-created users are auto-verified
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

# ------------------------ Admin View All Technicians ------------------------

@router.get("/technicians", response_model=List[UserOut])
def get_technicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin-only route dependency
):
    return db.query(User).filter(User.role == "technician").all()

# ------------------------ Admin Update Technician ------------------------

@router.put("/update-technician/{user_id}", response_model=UserOut)
def update_technician(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = user_update.full_name or user.full_name
    user.phone = user_update.phone or user.phone

    # Handle role safely
    if user_update.role is None:
        user.role = user.role or "user"  # fallback if existing role is also None
    else:
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    return user


# ------------------------ Admin Delete Technician ------------------------

@router.delete("/delete-technician/{technician_id}", response_model=UserOut)
def delete_technician(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_technician = get_user_by_id(db, technician_id)
    if not db_technician:
        raise HTTPException(status_code=404, detail="Technician not found")

    db.delete(db_technician)
    db.commit()
    return db_technician

# ------------------------ Admin to view Users ------------------------
@router.get("/users", response_model=List[UserOut])
def get_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # Admin-only route dependency
):
    return db.query(User).filter(User.role == "user").all()

# ------------------------ Admin Delete users ------------------------
@router.delete("/delete-users/{user_id}", response_model=UserOut)
def delete_users(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return db_user

# ------------------------ Admin Update Technician ------------------------

@router.put("/update-users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name = user_update.full_name or user.full_name
    user.phone = user_update.phone or user.phone

    # Handle role safely
    if user_update.role is None:
        user.role = user.role or "user"  # fallback if existing role is also None
    else:
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    return user


# Add these endpoints to your existing router

@router.get("/counts/technicians")
def count_technicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    count = db.query(User).filter(User.role == "technician").count()
    return {"count": count}

@router.get("/counts/users")
def count_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    count = db.query(User).filter(User.role == "user").count()
    return {"count": count}

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/user/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/profile-image/{user_id}", response_model=UserProfileOut)
def get_user_profile_image(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "profile_image": user.profile_image,
    }







