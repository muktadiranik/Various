from fastapi import FastAPI
from app.api.v1 import auth, projects, tasks, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
