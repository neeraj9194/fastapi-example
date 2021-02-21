from typing import Optional

from pydantic.main import BaseModel
from tortoise.contrib.pydantic import PydanticModel


class UserResponse(PydanticModel):
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    category: Optional[str]


class UserCreate(PydanticModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    category: Optional[str]
    password: str

    class Config:
        orm_mode = True


class Status(BaseModel):
    message: str
