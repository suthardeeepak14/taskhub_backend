from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app import models, schemas, database
from app.database import get_db
from app.models import Task, Comment
from app.schemas import CommentCreate, Comment
from datetime import datetime

router = APIRouter()

@router.get("/projects/{project_id}/tasks/{task_id}/comments", response_model=List[schemas.Comment])
def get_comments(project_id: UUID, task_id: UUID, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.query(models.Comment).filter(models.Comment.task_id == task_id).all()

@router.post("/projects/{project_id}/tasks/{task_id}/comments", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
def create_comment(project_id: UUID, task_id: UUID, comment: schemas.CommentCreate, db: Session = Depends(database.get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
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


