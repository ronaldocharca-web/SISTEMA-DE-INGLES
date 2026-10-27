from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.dependencies import admin_service, exigir_admin
from app.schemas.admin import AdminCredentialsUpdate, AdminLoginRequest
from app.services.admin_service import (
    AdminBloqueadoError,
    AdminCredencialesInvalidasError,
)


router = APIRouter()


@router.post("/login")
def admin_login(datos: AdminLoginRequest, request: Request):
    origen = request.client.host if request.client else "unknown"
    try:
        token = admin_service.iniciar_sesion(datos.usuario, datos.password, origen)
    except AdminBloqueadoError as error:
        raise HTTPException(
            status_code=429,
            detail=str(error),
            headers={"Retry-After": str(error.segundos_restantes)},
        ) from error
    except AdminCredencialesInvalidasError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return {"token": token}


@router.put("/credenciales")
def actualizar_credenciales(
    credenciales: AdminCredentialsUpdate,
    token: str = Depends(exigir_admin),
):
    admin_service.actualizar(credenciales, token)
    return {"mensaje": "Credenciales actualizadas correctamente."}
