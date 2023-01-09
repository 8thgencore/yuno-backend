from fastapi import APIRouter

from app.api.v1.endpoints import auth, project, role, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
