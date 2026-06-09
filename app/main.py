from fastapi import FastAPI

from app.api.routers import charity_project, donation
from app.api.routers.users import auth_router, register_router, users_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version="0.1.0"
)

app.include_router(auth_router, prefix="/auth/jwt", tags=["auth"])

app.include_router(register_router, prefix="/auth", tags=["auth"])

app.include_router(users_router, prefix="/users", tags=["users"])

app.include_router(donation.router)
app.include_router(charity_project.router)