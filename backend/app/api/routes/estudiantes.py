from fastapi import APIRouter, HTTPException

from app.repositories.convocatoria_repository import (
    ConvocatoriaRepository,
    InscripcionesCerradasError,
)
from app.repositories.student_repository import StudentRepository
from app.repositories.pdf_usage_repository import (
    EXPIRADO,
    INVALIDO,
    REGISTRADO,
    RESERVADO,
    PdfUsageRepository,
)
from app.schemas.student import RegistroEstudianteRequest


router = APIRouter(prefix="/estudiantes", tags=["estudiantes"])
student_repository = StudentRepository()
convocatoria_repository = ConvocatoriaRepository()
pdf_usage_repository = PdfUsageRepository()


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
        convocatoria = convocatoria_repository.exigir_abierta()
        estado_pdf = pdf_usage_repository.validar_reserva(
            estudiante.pdf_token,
            convocatoria["id"],
            estudiante.ci,
            estudiante.ru,
        )
        if estado_pdf == REGISTRADO:
            raise HTTPException(status_code=409, detail="Este PDF ya fue registrado.")
        if estado_pdf == INVALIDO:
            raise HTTPException(
                status_code=409,
                detail="Los datos no corresponden al historial analizado.",
            )
        if estado_pdf == EXPIRADO or estado_pdf != RESERVADO:
            raise HTTPException(
                status_code=409,
                detail="La verificación del PDF expiró. Vuelve a subirlo.",
            )
        registrado, mensaje = student_repository.registrar(estudiante)
        pdf_usage_repository.marcar_registrado(estudiante.pdf_token)
    except InscripcionesCerradasError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    return {
        "registrado": registrado,
        "duplicado": not registrado,
        "mensaje": mensaje,
    }
