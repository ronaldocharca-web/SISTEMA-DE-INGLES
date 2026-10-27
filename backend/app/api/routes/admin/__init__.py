from fastapi import APIRouter

from app.api.routes.admin import auth, convocatorias, dashboard, exports


router = APIRouter(prefix="/admin", tags=["administración"])
router.include_router(auth.router)
router.include_router(dashboard.router)
router.include_router(convocatorias.router)
router.include_router(exports.router)
