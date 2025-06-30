from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, database
from app.project_router import router as project_router
from app.task_router import router as task_router
from app.comment_router import router as comment_router
app = FastAPI(title="TaskHub API", version="1.0")
from app.auth_router import router as auth_router


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

models.Base.metadata.create_all(bind=database.engine)


app.include_router(auth_router, tags=["Auth"])
app.include_router(project_router, prefix="", tags=["Projects"])
app.include_router(task_router, prefix="", tags=["Tasks"])
app.include_router(comment_router, tags=["comments"])
