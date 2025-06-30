
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, repository

def add_comment_to_task(db: Session, task_id: UUID, comment_data: schemas.CommentCreate):
    return repository.comment.create_comment(db, task_id, comment_data)

def get_comments_for_task(db: Session, task_id: UUID):
    return repository.comment.get_comments_by_task(db, task_id)
