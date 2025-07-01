from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func  # ✅ REQUIRED for count aggregation
from typing import List
from uuid import UUID
from app import models, schemas, database
from app.database import get_db
from app.models import Task, Comment
from app.schemas import CommentCreate, Comment
from datetime import datetime

router = APIRouter()

# ------------------ Get Comments for a Task ------------------
@router.get("/projects/{project_id}/tasks/{task_id}/comments", response_model=List[schemas.Comment])
def get_comments(project_id: UUID, task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.query(models.Comment).filter(models.Comment.task_id == task_id).all()

# ------------------ Create a New Comment ------------------
@router.post("/projects/{project_id}/tasks/{task_id}/comments", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
def create_comment(project_id: UUID, task_id: UUID, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    new_comment = models.Comment(
        content=comment.content,
        author=comment.author,
        task_id=task_id,
        created_at=datetime.utcnow()
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

# ------------------ Get Tasks + Comment Count for a Project ------------------
@router.get("/projects/{project_id}/tasks-with-comment-count")
def get_tasks_with_comment_counts(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    results = (
        db.query(
            models.Task,
            func.count(models.Comment.id).label("comment_count")
        )
        .outerjoin(models.Comment, models.Comment.task_id == models.Task.id)
        .filter(models.Task.project_id == project_id)
        .group_by(models.Task.id)
        .all()
    )

    tasks_with_counts = []
    for task, comment_count in results:
        task_dict = task.__dict__.copy()
        task_dict.pop("_sa_instance_state", None)
        task_dict["comment_count"] = comment_count
        tasks_with_counts.append(task_dict)

    return tasks_with_counts
