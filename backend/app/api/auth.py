from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, security
from app.api.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: schemas.UserCreateStrict, db: Session = Depends(get_db)) -> schemas.UserRead:
    """DEV ONLY: open registration for prototyping. Admin/viewer roles assigned later."""
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email_already_registered")

    user = models.User(
        email=payload.email,
        hashed_password=security.hash_password(payload.password),
        role="viewer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserRead(id=user.id, email=user.email, role=user.role)


@router.post("/login")
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)) -> schemas.Token:
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user is None or not security.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")

    access_token = security.create_access_token(data={"sub": user.email, "role": user.role})
    return schemas.Token(access_token=access_token, token_type="bearer")
