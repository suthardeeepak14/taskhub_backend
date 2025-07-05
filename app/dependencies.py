from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.auth import decode_access_token, oauth2_scheme
from app.models import User, Project, Task

# ✅ Get current user from token
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ✅ Admin Check
def require_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user


# ✅ Helper: Check if user is project owner
def is_project_owner(project: Project, current_user: User):
    owners = project.owners or []
    return current_user.username in owners



# ✅ Helper: Check if user is project member
def is_project_member(project: Project, current_user: User):
    members = project.members or []
    return current_user.username in members


# ✅ Admin or Owner check (For edit, delete project)
def require_admin_or_owner(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role == "admin" or is_project_owner(project, current_user):
        return current_user

    raise HTTPException(status_code=403, detail="Only admin or project owner can perform this action")


# ✅ View access check (Admin, Owner, or Member)
def require_project_view_access(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if (
        current_user.role == "admin"
        or is_project_owner(project, current_user)
        or is_project_member(project, current_user)
    ):
        return current_user

    raise HTTPException(status_code=403, detail="You are not authorized to view this project")


# ✅ Only project owners can modify members or owners
def require_owner_for_membership_change(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # ✅ Allow if admin or owner
    if current_user.role != "admin" and not is_project_owner(project, current_user):
        raise HTTPException(
            status_code=403,
            detail="Only project owners or admins can modify members or owners"
        )

    return current_user


def require_task_update_access(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role == "admin":
        return current_user

    if task.assignee != current_user.username and not is_project_owner(project, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to update this task")

    return current_user

# ✅ Only Admin or Project Owner can delete task
def require_admin_or_owner_by_task_id(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user.role != "admin" and not is_project_owner(project, current_user):
        raise HTTPException(status_code=403, detail="Only admin or project owner can delete this task")

    return current_user



def require_project_participant(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if (
        current_user.role == "admin"
        or is_project_owner(project, current_user)
        or is_project_member(project, current_user)
    ):
        return current_user

    raise HTTPException(status_code=403, detail="Only project participants can create tasks")
