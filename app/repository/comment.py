

from app.models import Comment
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas import CommentCreate

def create_comment(db: Session, task_id: UUID, comment_data: CommentCreate):
    comment = Comment(task_id=task_id, **comment_data.dict())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def get_comments_by_task(db: Session, task_id: UUID):
    return db.query(Comment).filter(Comment.task_id == task_id).all()
