from sqlalchemy.orm import Session, selectinload
from uuid import UUID
from app import models, schemas
from datetime import datetime

def create_project(db: Session, data: schemas.ProjectCreate, owner: str):
    proj = models.Project(
        **data.dict(),
        owner=owner,                   
        created_at=datetime.utcnow()    
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj

def get_projects(db: Session):
    # ✅ This will preload tasks for each project (used for ProjectsPage progress bar)
    return db.query(models.Project).options(selectinload(models.Project.tasks)).all()

def get_project_by_id(db: Session, project_id: UUID):
    # ✅ This will preload tasks for single project (used in ProjectDetailPage)
    return (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .options(selectinload(models.Project.tasks))
        .first()
    )

def update_project(db: Session, project_id: UUID, data: schemas.ProjectCreate):
    proj = get_project_by_id(db, project_id)
    if not proj:
        return None
    for key, val in data.dict().items():
        setattr(proj, key, val)
    db.commit()
    db.refresh(proj)
    return proj

def delete_project(db: Session, project_id: UUID):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return None
    db.delete(project)
    db.commit()
    return project

def update_project_details(db: Session, project_id: UUID, data: schemas.ProjectUpdate):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return None
    project.name = data.name
    project.description = data.description
    project.status = data.status
    project.due_date = data.due_date
    db.commit()
    db.refresh(project)
    return project