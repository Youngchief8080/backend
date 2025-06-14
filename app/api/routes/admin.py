
from fastapi import status
from app.schemas.user import AdminCreateUser  # You'll define this below
from app.crud.user import create_user  # We'll make sure this exists too

@router.post("/create-user", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_by_admin(user_in: AdminCreateUser, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin_user)):
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
        # is_active=True  # Admin-created users are auto-verified
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
