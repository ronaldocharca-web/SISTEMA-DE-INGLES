from fastapi import APIRouter, HTTPException

from app.repositories.convocatoria_repository import (
    ConvocatoriaRepository,
    InscripcionesCerradasError,
)
from app.repositories.student_repository import StudentRepository
from app.schemas.student import RegistroEstudianteRequest


router = APIRouter(prefix="/estudiantes", tags=["estudiantes"])
student_repository = StudentRepository()
convocatoria_repository = ConvocatoriaRepository()


@router.get("/inscripciones/estado")
def estado_inscripciones():
    convocatoria = convocatoria_repository.obtener_actual()
    if convocatoria is None:
        return {
            "habilitada": False,
            "mensaje": "Las inscripciones todavía no tienen una fecha habilitada.",
            "convocatoria": None,
        }
    mensaje = (
        "Las inscripciones están abiertas."
        if convocatoria["abierta"]
        else "Las inscripciones están cerradas en este momento."
    )
    return {
        "habilitada": convocatoria["abierta"],
        "mensaje": mensaje,
        "convocatoria": convocatoria,
    }


@router.post("/registrar")
def registrar_estudiante(estudiante: RegistroEstudianteRequest):
    try:
        registrado, mensaje = student_repository.registrar(estudiante)
    except InscripcionesCerradasError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    return {
        "registrado": registrado,
        "duplicado": not registrado,
        "mensaje": mensaje,
    }
