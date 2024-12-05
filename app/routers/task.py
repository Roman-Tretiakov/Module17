from fastapi import APIRouter, Depends, status, HTTPException
from app.models import User, Task
from app.schemas import CreateTask, UpdateTask

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

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_tasks(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Task)).all()


@router.get("/task_id")
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is not None:
        return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Task with id: \'{task_id}\' was not found'
    )


@router.post("/create")
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, task_create: CreateTask):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is not None:
        db.execute(insert(Task).values(title=task_create.title,
                                       content=task_create.content,
                                       priority=task_create.priority,
                                       user_id=user_id,
                                       slug=slugify(task_create.title)))
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'User with id: \'{user_id}\' was not found'
    )


@router.put("/update")
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, task_update: UpdateTask):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is not None:
        db.execute(update(Task).where(Task.id == task_id).values(
            title=task_update.title,
            content=task_update.content,
            priority=task_update.priority,
        ))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task updated successfully'
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Task with id: \'{task_id}\' was not found'
    )


@router.delete("/delete")
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    task = db.scalar(select(Task).where(Task.id == task_id))
    if task is not None:
        db.execute(delete(Task).where(Task.id == task_id))
        db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task deleted successfully'
        }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'Task with id: \'{task_id}\' was not found'
    )

