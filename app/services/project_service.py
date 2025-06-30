from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, repository

def create_project(db: Session, data: schemas.ProjectCreate, owner: str):
    return repository.project.create_project(db, data, owner)

def get_all_projects(db: Session): return repository.project.get_projects(db)

def update_project(db: Session, project_id: UUID, data: schemas.ProjectCreate, user: str):
    proj = repository.project.get_project_by_id(db, project_id)
    if not proj: return None
    if proj.owner != user: raise PermissionError
    return repository.project.update_project(db, project_id, data)

def delete_project(db: Session, project_id: UUID, user: str):
    proj = repository.project.get_project_by_id(db, project_id)
    if not proj: return None
    if proj.owner != user: raise PermissionError
    return repository.project.delete_project(db, project_id)
