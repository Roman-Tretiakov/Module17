from fastapi import APIRouter, Depends, status, HTTPException
from app.models import User, Task
from app.schemas import CreateUser, UpdateUser

# Сессия БД:
from sqlalchemy.orm import Session
# Функция подключения к БД:
from app.backend.db_depends import get_db
# Аннотации, Модели БД и Pydantic:
from typing import Annotated
# Функции работы с записями:
from sqlalchemy import insert, select, update, delete
# Функция создания slug-строки
from slugify import slugify


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/")
async def all_users(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(User)).all()


@router.get("/user_id")
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with id: \'{user_id}\' was not found'
    )


@router.get("/user_id/tasks")
async def tasks_by_user_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is not None:
        return db.scalars(select(Task).where(Task.user_id == user_id)).all()
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with id: \'{user_id}\' was not found'
    )


@router.post("/create")
async def create_user(db: Annotated[Session, Depends(get_db)], user_create: CreateUser):
    user = db.scalar(select(User).where(User.username == user_create.username))
    if user is None:
        db.execute(insert(User).values(username=user_create.username,
                                       firstname=user_create.firstname,
                                       lastname=user_create.lastname,
                                       age=user_create.age,
                                       slug=slugify(user_create.username)))
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with this user name: \'{user_create.username}\' exists'
    )


@router.put("/update")
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, user_update: UpdateUser):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is not None:
        db.execute(update(User).where(User.id == user_id).values(
            firstname=user_update.firstname,
            lastname=user_update.lastname,
            age=user_update.age))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'User updated successfully'
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with id: \'{user_id}\' was not found'
    )


@router.delete("/delete")
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is not None:
        db.execute(delete(User).where(User.id == user_id))
        if db.scalar(select(Task).where(Task.user_id == user_id)):
            db.execute(delete(Task).where(Task.user_id == user_id))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'User deleted successfully'
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with id: \'{user_id}\' was not found'
    )
