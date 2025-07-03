from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app import schemas, models
from app.database import get_db
from app.repository import task as task_repo
from app.dependencies import (
    get_current_user,
    require_admin_or_owner,
    require_task_update_access,
    require_admin_or_owner_by_task_id,
    require_project_participant,
)

router = APIRouter()


# --- Create Task ---
@router.post("/tasks", response_model=schemas.Task)
def create_task(
    t: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_project_participant(t.project_id, db, current_user)
    return task_repo.create_task(db, t)


# --- List Tasks: Admin, Owner, Member, or Assignee only ---
@router.get("/tasks", response_model=List[schemas.Task])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    all_tasks = task_repo.get_tasks(db)
    visible_tasks = []

    for task in all_tasks:
        project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
        if not project:
            continue

       
        is_admin = current_user.role == "admin"
        is_owner = current_user.username in (project.owners or "").split(",")
        is_member = current_user.username in (project.members or "").split(",")
        is_assignee = task.assignee == current_user.username

        if is_admin or is_owner or is_member or is_assignee:
            visible_tasks.append(task)

    return visible_tasks


# --- Get Task by ID ---
@router.get("/tasks/{task_id}", response_model=schemas.Task)
def get_task_by_id(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = (
        db.query(models.Project).filter(models.Project.id == task.project_id).first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_admin = current_user.role == "admin"
    is_owner = current_user.username in (project.owners or "").split(",")
    is_member = current_user.username in (project.members or "").split(",")
    is_assignee = task.assignee == current_user.username

    if not (is_admin or is_owner or is_member or is_assignee):
        raise HTTPException(status_code=403, detail="Access denied")

    return task


# --- Get Tasks by Project ---
@router.get("/projects/{project_id}/tasks", response_model=List[schemas.Task])
def get_tasks_by_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    is_admin = current_user.role == "admin"
    is_owner = current_user.username in (project.owners or "").split(",")
    is_member = current_user.username in (project.members or "").split(",")

    if not (is_admin or is_owner or is_member):
        raise HTTPException(status_code=403, detail="Not authorized to view tasks")

    return task_repo.get_tasks_by_project(db, project_id)


# --- Get Specific Task in Project ---
@router.get(
    "/projects/{project_id}/tasks/{task_id}", response_model=schemas.Task
)
def get_task_by_project_and_task_id(
    project_id: UUID,
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    task = (
        db.query(models.Task)
        .filter(
            models.Task.id == task_id,
            models.Task.project_id == project_id,
        )
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    is_admin = current_user.role == "admin"
    is_owner = current_user.username in (project.owners or "").split(",")
    is_member = current_user.username in (project.members or "").split(",")
    is_assignee = task.assignee == current_user.username

    if not (is_admin or is_owner or is_member or is_assignee):
        raise HTTPException(status_code=403, detail="Access denied")

    return task


# --- Update Task ---
@router.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: UUID,
    t: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_task_update_access(task_id, db, current_user)
    task = task_repo.update_task(db, task_id, t)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# --- Update Task in Project ---
@router.put("/projects/{project_id}/tasks/{task_id}", response_model=schemas.Task)
def update_task_in_project(
    project_id: UUID,
    task_id: UUID,
    t: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_task_update_access(task_id, db, current_user)

    task = db.query(models.Task).filter(
        models.Task.id == task_id, models.Task.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in t.dict(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# --- Delete Task ---
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin_or_owner_by_task_id(task_id, db, current_user)
    deleted = task_repo.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return
