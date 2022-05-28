from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, utils
from sqlalchemy.orm import Session
from ..database import get_db
from ..pydantic_models.user_model import UserCreate
from ..pydantic_models.user_model import UserCreateResponse
from ..pydantic_models.user_model import UserGetResponse


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


# User registration
@router.post("/", status_code=status.HTTP_201_CREATED,
             response_model=UserCreateResponse)
async def create_user(user: UserCreate,
                      db: Session = Depends(get_db)):
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Get user information
@router.get("/{id}", response_model=UserGetResponse)
async def users(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with the userID: {id} does not exist.")
    return user
