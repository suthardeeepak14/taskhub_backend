from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app import schemas,models
from app.database import get_db
from app.services import project_service
from app.models import Project 
from app.schemas import ProjectOut
from app.repository import project as project_repo
from sqlalchemy.orm import selectinload
router = APIRouter()

@router.post("/projects", response_model=schemas.Project)
def create_project(p: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, p, owner="test_user")

@router.get("/projects", response_model=List[schemas.Project])
def list_projects(db: Session = Depends(get_db)):
    return project_service.get_all_projects(db)

@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project_by_id(project_id: str, db: Session = Depends(get_db)):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .options(selectinload(Project.tasks))  # ✅ This loads tasks from DB
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: UUID, updated_data: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.name = updated_data.name
    project.description = updated_data.description
    project.status = updated_data.status
    project.due_date = updated_data.due_date

    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return project

def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).options(
        selectinload(Project.tasks)  # ✅ This loads related tasks with project
    ).first()