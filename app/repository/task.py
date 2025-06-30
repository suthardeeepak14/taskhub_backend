from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas
from fastapi import HTTPException

def create_task(db: Session, data: schemas.TaskCreate):
    task_data = data.dict()
    if task_data.get("project_id"):
        task_data["project_id"] = UUID(str(task_data["project_id"]))

    task = models.Task(**task_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks(db: Session, status: str = None, assignee: str = None):
    q = db.query(models.Task)
    if status: q = q.filter(models.Task.status == status)
    if assignee: q = q.filter(models.Task.assignee == assignee)
    return q.all()

def get_task_by_id(db: Session, task_id: UUID):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def update_task(db: Session, task_id: UUID, data: schemas.TaskCreate):
    task = get_task_by_id(db, task_id)
    if not task: return None
    for k, v in data.dict().items(): setattr(task, k, v)
    db.commit(); db.refresh(task); return task

def delete_task(db: Session, task_id: UUID):
    task = get_task_by_id(db, task_id)
    if not task: return None
    db.delete(task); db.commit(); return task

def get_tasks_by_project(db: Session, project_id: UUID):
    return db.query(models.Task).filter(models.Task.project_id == project_id).all()


def get_task_by_project_and_id(db: Session, project_id: UUID, task_id: UUID):
    return (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.project_id == project_id)
        .first()
    )


