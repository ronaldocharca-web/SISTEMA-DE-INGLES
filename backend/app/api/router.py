from fastapi import APIRouter

from app.api.routes import admin, estudiantes, historiales


api_router = APIRouter()
api_router.include_router(historiales.router)
api_router.include_router(estudiantes.router)
api_router.include_router(admin.router)
