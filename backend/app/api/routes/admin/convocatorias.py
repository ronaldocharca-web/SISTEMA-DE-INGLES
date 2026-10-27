from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import exigir_admin
from app.api.routes.admin.context import convocatoria_repository
from app.schemas.convocatoria import ConvocatoriaFinUpdate, ConvocatoriaRequest


router = APIRouter()


@router.put("/convocatoria")
def crear_convocatoria(
    datos: ConvocatoriaRequest,
    _: str = Depends(exigir_admin),
):
    try:
        convocatoria = convocatoria_repository.crear(datos)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {
        "mensaje": "Nueva convocatoria configurada correctamente.",
        "convocatoria": convocatoria,
    }


@router.patch("/convocatoria/fin")
def actualizar_fin_convocatoria(
    datos: ConvocatoriaFinUpdate,
    _: str = Depends(exigir_admin),
):
    try:
        convocatoria = convocatoria_repository.actualizar_fin(datos)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {
        "mensaje": "La fecha de cierre fue actualizada correctamente.",
        "convocatoria": convocatoria,
    }
