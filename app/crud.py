from sqlalchemy.orm import Session
from app.models import Project 
from uuid import UUID

def get_project_detail(db: Session, project_id: UUID):
    return db.query(Project).filter(Project.id == project_id).first()
