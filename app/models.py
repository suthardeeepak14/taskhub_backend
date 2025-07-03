from sqlalchemy import Column, String, Date, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy.dialects.postgresql import ARRAY

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")
    due_date = Column(Date, nullable=True)
    members = Column(ARRAY(String), default=[])
    owners = Column(ARRAY(String), default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ Store all owners as comma-separated usernames (Example: "admin,deepak")
    

    # ✅ Relationship with Tasks
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    
    description = Column(Text)
    status = Column(String, default="pending")
    priority = Column(String, default="medium")
    due_date = Column(Date)
    assignee = Column(String)

    created_by = Column(String, nullable=False) 
    
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"),nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    project = relationship("Project", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    task = relationship("Task", back_populates="comments")




class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
