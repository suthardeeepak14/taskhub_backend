from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas
from typing import List

# ✅ Create Project
def create_project(db: Session, project_data: schemas.ProjectCreate, owner: str):
    new_project = models.Project(
        name=project_data.name,
        description=project_data.description,
        status=project_data.status or "pending",
        due_date=project_data.due_date,
        owners=owner  # ✅ First owner = creator username
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# ✅ Get All Projects (For Admins)
def get_all_projects(db: Session):
    return db.query(models.Project).all()


# ✅ Get Projects for Specific User (Owner or Member)
def get_user_related_projects(db: Session, username: str):
    return db.query(models.Project).filter(
        (models.Project.owners.contains(username)) | (models.Project.members.contains(username))
    ).all()


# ✅ Get Single Project By ID
def get_project_by_id(db: Session, project_id: UUID):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


# ✅ Update Project Details (Only by Owner or Admin)
def update_project_details(db: Session, project_id: UUID, project_data: schemas.ProjectUpdate):
    project = get_project_by_id(db, project_id)
    if not project:
        return None

    for field, value in project_data.dict(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


# ✅ Delete Project (Admin or Owner)
def delete_project_by_id(db: Session, project_id: UUID):
    project = get_project_by_id(db, project_id)
    if project:
        db.delete(project)
        db.commit()
    return project


# ✅ Update Project Members (By Owners only)
def update_project_members(db: Session, project_id: UUID, members: List[str]):
    project = get_project_by_id(db, project_id)
    if not project:
        return None

    project.members = ",".join(members)
    db.commit()
    db.refresh(project)
    return {"msg": "Project members updated"}


# ✅ Update Project Owners (By Owners only)
def update_project_owners(db: Session, project_id: UUID, owners: List[str]):
    project = get_project_by_id(db, project_id)
    if not project:
        return None

    project.owners = ",".join(owners)
    db.commit()
    db.refresh(project)
    return {"msg": "Project owners updated"}
