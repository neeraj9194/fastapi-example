from typing import List

import pwnedpasswords
from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from tortoise.contrib.fastapi import HTTPNotFoundError

from .models import User
from .schemas import UserResponse, UserCreate, Status

router = APIRouter(tags=['Users'])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    return await pwd_context.hash(password)


def if_password_secure(password: str) -> bool:
    """
    accept password, but only if it is safe.
    """
    # Call external API to check password.
    result = pwnedpasswords.check(password)
    if result > 0:
        return False
    return True


@router.get("/users/", response_model=List[UserResponse])
async def get_users():
    return await User.all()


@router.post("/user/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # This is external API and is sync.
    is_secure = if_password_secure(user.password)
    if not is_secure:
        raise HTTPException(status_code=400, detail="The password is unsafe!")
    user.password = get_password_hash(user.password)
    user_obj = await User.create(**user.dict(exclude_unset=True))
    return user_obj


@router.delete("/user/{user_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(user_id: int):
    deleted_count = await User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")
