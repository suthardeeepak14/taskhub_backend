from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app import schemas, models
from app.database import get_db
from app.services import project_service
from app.schemas import ProjectOut
from app.dependencies import get_current_user  # ✅ Import
from app.models import User  # ✅ Import
from app.dependencies import require_admin  # ✅ Import for admin-only routes

router = APIRouter()

# ✅ Create Project with real owner
@router.post("/projects", response_model=schemas.Project)
def create_project(
    p: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return project_service.create_project(db, p, owner=current_user.username)


# ✅ Get All Projects (with tasks preloaded via selectinload in repository)
@router.get("/projects", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return project_service.get_all_projects(db)


# ✅ Get Single Project By ID (Detailed view with tasks)
@router.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project_by_id(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ✅ Update Project
@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: UUID,
    updated_data: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    project = project_service.update_project_details(db, project_id, updated_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ✅ Delete Project
@router.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(project_id: UUID, db: Session = Depends(get_db),current_user: models.User = Depends(require_admin), ):
    deleted_project = project_service.delete_project_by_id(db, project_id)

    if not deleted_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted_project
