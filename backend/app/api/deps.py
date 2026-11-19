from typing import Iterator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models, security
from app.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db() -> Iterator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> models.User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could_not_validate_token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise ValueError("missing subject")
    except ValueError:
        raise credentials_error

    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
    finally:
        db.close()

    if user is None:
        raise credentials_error
    request.state.user = user
    return user


def require_role(role: str):
    """Dependency factory: enforce that the current user has at least `role`."""

    def _check(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="insufficient_permissions",
            )
        return user

    return _check
