from fastapi import APIRouter

from app.api.v1.endpoints import auth

v1_router = APIRouter()

v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
