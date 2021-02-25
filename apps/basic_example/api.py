import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
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


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# When you declare a path operation function with normal def instead of async
# def, it is run in an external threadpool that is then awaited, instead of
# being called directly (as it would block the server).
# https://github.com/tiangolo/fastapi/issues/260#issuecomment-495945630
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
    # Making sync library/ function async.
    loop = asyncio.get_running_loop()
    is_secure = await loop.run_in_executor(None, if_password_secure, user.password)
    if not is_secure:
        raise HTTPException(status_code=400, detail="The password is unsafe!")

    # Use this carefully the above works fine.
    # with ThreadPoolExecutor(1) as pool2:
    #     is_secure = await loop.run_in_executor(
    #           None, if_password_secure, user.password
    #     )
    # OR
    #     password_hash = await loop.run_in_executor(
    #           pool2, get_password_hash, user.password
    #     )
    password_hash = await loop.run_in_executor(None, get_password_hash, user.password)

    # culprit
    # password_hash = get_password_hash(user.password)

    user_obj = await User.create(password_hash=password_hash,
                                 **user.dict(exclude_unset=True))
    return user_obj


@router.delete("/user/{user_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(user_id: int):
    deleted_count = await User.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")
