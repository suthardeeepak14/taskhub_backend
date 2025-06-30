from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app import schemas, models
from app.database import get_db
from app.repository import task as task_repo

router = APIRouter()

# ------------------- Create Task -------------------
@router.post("/tasks", response_model=schemas.Task)
def create_task(t: schemas.TaskCreate, db: Session = Depends(get_db)):
    return task_repo.create_task(db, t)

# ------------------- List All Tasks -------------------
@router.get("/tasks", response_model=List[schemas.Task])
def list_tasks(status: Optional[str] = None, assignee: Optional[str] = None, db: Session = Depends(get_db)):
    return task_repo.get_tasks(db, status=status, assignee=assignee)

# ------------------- Get Task by ID -------------------
@router.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task_by_id(task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ------------------- Get Task by Project and Task ID -------------------
@router.get("/projects/{project_id}/tasks/{task_id}", response_model=schemas.Task)
def get_task_by_project_and_task_id(project_id: UUID, task_id: UUID, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in this project")

    return task

# ------------------- Update Task -------------------


@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: UUID, t: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = task_repo.update_task(db, task_id, t)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ------------------- Delete Task -------------------
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, db: Session = Depends(get_db)):
    task = task_repo.delete_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return

# ------------------- List Tasks by Project -------------------
@router.get("/projects/{project_id}/tasks", response_model=List[schemas.Task])
def get_tasks_by_project(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return task_repo.get_tasks_by_project(db, project_id)


@router.put("/projects/{project_id}/tasks/{task_id}", response_model=schemas.Task)
def update_task_in_project(
    project_id: UUID,
    task_id: UUID,
    t: schemas.TaskUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    task = db.query(models.Task).filter(
        models.Task.id == task_id, models.Task.project_id == project_id
    ).first()
    if not task:
        raise HTTPException(404, "Task not found in this project")

    # apply any fields present
    for field, value in t.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task