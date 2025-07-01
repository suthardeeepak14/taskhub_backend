from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas, repository

def create_project(db: Session, data: schemas.ProjectCreate, owner: str):
    return repository.project.create_project(db, data, owner)

def get_all_projects(db: Session):
    return repository.project.get_projects(db)

def get_project_by_id(db: Session, project_id: str):
    return repository.project.get_project_by_id(db, project_id)

def update_project_details(db: Session, project_id: UUID, data: schemas.ProjectUpdate):
    return repository.project.update_project_details(db, project_id, data)

def delete_project_by_id(db: Session, project_id: UUID):
    return repository.project.delete_project(db, project_id)
