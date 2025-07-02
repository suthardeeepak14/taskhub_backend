from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List
from datetime import date, datetime

# ✅ Tasks Schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    due_date: Optional[date] = None
    assignee: Optional[str] = None
    project_id: Optional[UUID] = None 

class Task(TaskCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None

class TaskRead(BaseModel):
    id: UUID
    title: str
    status: str
    assignee: Optional[str]
    priority: Optional[str]

    class Config:
        from_attributes = True

# ✅ Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    due_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None

class Project(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: Optional[str]
    due_date: Optional[date]
    owners: Optional[str]
    members: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: str
    due_date: Optional[date]
    owners: Optional[str]
    members: Optional[str]
    tasks: List[TaskRead] = []

    class Config:
        from_attributes = True

class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: str
    owners: Optional[str]
    members: Optional[str]
    due_date: Optional[date]
    created_at: datetime
    tasks: List[TaskRead] = []

    class Config:
        from_attributes = True

class ProjectMembersUpdate(BaseModel):
    members: List[str]

class ProjectOwnersUpdate(BaseModel):
    owners: List[str]

# ✅ Comment Schemas
class CommentBase(BaseModel):
    content: str
    author: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: UUID
    created_at: datetime
    task_id: UUID
    class Config:
        from_attributes = True

# ✅ User Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    class Config:
        form_attributes = True
