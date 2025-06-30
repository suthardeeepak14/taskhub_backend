from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas

def create_project(db: Session, data: schemas.ProjectCreate, owner: str):
    proj = models.Project(**data.dict(), owner=owner)
    db.add(proj); db.commit(); db.refresh(proj)
    return proj

def get_projects(db: Session):
    return db.query(models.Project).all()

def get_project_by_id(db: Session, project_id: UUID):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def update_project(db: Session, project_id: UUID, data: schemas.ProjectCreate):
    proj = get_project_by_id(db, project_id)
    if not proj: return None
    for key, val in data.dict().items(): setattr(proj, key, val)
    db.commit(); db.refresh(proj); return proj

def delete_project(db: Session, project_id: UUID):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return None
    db.delete(project)
    db.commit()
    return project
