from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, utils, oauth2
from fastapi.security import OAuth2PasswordRequestForm
from ..pydantic_models.auth_model import Token

router = APIRouter(
    tags=['Authentication']
)


@router.post("/login", response_model=Token)
async def login_authentication(
        user_credentials: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid credentials.")
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    return {"token_type": "bearer",
            "access_token": access_token}
