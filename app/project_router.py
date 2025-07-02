from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app import models, schemas
from app.database import get_db
from app.services import project_service
from app.schemas import ProjectOut
from app.dependencies import (
    get_current_user,
    require_admin_or_owner,
    require_project_view_access,
    require_owner_for_membership_change,
)
from fastapi.encoders import jsonable_encoder

router = APIRouter()


# ✅ Create Project (Any logged-in user can create)
@router.post("/projects", response_model=schemas.Project)
def create_project(
    p: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return project_service.create_project(db, p, owner=current_user.username)


# ✅ Get All Projects (Admin sees all, users see only where owner/member)
@router.get("/projects", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role == "admin":
        return project_service.get_all_projects(db)
    return project_service.get_user_related_projects(db, current_user.username)


# ✅ Get Single Project (Admin / Owner / Member)
@router.get("/projects/{project_id}", response_model=schemas.ProjectOut)
def get_project_by_id(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_project_view_access(project_id, db, current_user)
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ✅ Update Project (Only Admin or Owner)
@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: UUID,
    updated_data: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin_or_owner(project_id, db, current_user)
    project = project_service.update_project_details(db, project_id, updated_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ✅ Delete Project (Only Admin or Owner)
@router.delete("/projects/{project_id}", response_model=schemas.Project)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_admin_or_owner(project_id, db, current_user)
    deleted_project = project_service.delete_project_by_id(db, project_id)
    if not deleted_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted_project


# ✅ Update Project Members (Only Owners)
@router.put("/projects/{project_id}/members")
def update_project_members(
    project_id: UUID,
    members_update: schemas.ProjectMembersUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_owner_for_membership_change(project_id, db, current_user)
    return project_service.update_project_members(db, project_id, members_update.members)


# ✅ Update Project Owners (Only Owners)
@router.put("/projects/{project_id}/owners")
def update_project_owners(
    project_id: UUID,
    owners_update: schemas.ProjectOwnersUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    require_owner_for_membership_change(project_id, db, current_user)
    return project_service.update_project_owners(db, project_id, owners_update.owners)
