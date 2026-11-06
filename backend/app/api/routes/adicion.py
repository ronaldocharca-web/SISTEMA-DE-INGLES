from uuid import UUID

from fastapi import APIRouter, File, Header, HTTPException, UploadFile

from app.repositories.addition_repository import AdditionRepository
from app.repositories.convocatoria_repository import ConvocatoriaRepository, InscripcionesCerradasError
from app.repositories.pdf_usage_repository import EN_USO, EXPIRADO, INVALIDO, REGISTRADO, RESERVADO, PdfUsageRepository
from app.schemas.adicion import SolicitudAdicionRequest
from app.services.addition_analysis_service import AdditionAnalysisService


router = APIRouter(prefix="/adicion", tags=["adición de materia"])
repository = AdditionRepository()
convocatorias = ConvocatoriaRepository("adicion")
pdf_usos = PdfUsageRepository("adicion")
service = AdditionAnalysisService()


@router.get("/inscripciones/estado")
def estado_inscripciones():
    convocatoria = convocatorias.obtener_actual()
    promedio_minimo = repository.obtener_promedio_minimo()
    if convocatoria is None:
        return {
            "habilitada": False,
            "mensaje": "Las solicitudes de adición todavía no tienen una convocatoria habilitada.",
            "convocatoria": None,
            "promedio_minimo": promedio_minimo,
        }
    return {
        "habilitada": convocatoria["abierta"],
        "mensaje": "Las solicitudes están abiertas." if convocatoria["abierta"] else "Las solicitudes están cerradas.",
        "convocatoria": convocatoria,
        "promedio_minimo": promedio_minimo,
    }


@router.post("/historiales/analizar")
async def analizar_historial(
    archivo: UploadFile = File(...),
    x_pdf_reservation: str | None = Header(default=None),
):
    nombre = archivo.filename or "archivo"
    if not nombre.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF.")
    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    if len(contenido) > 4 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="El PDF supera el límite de 4 MB.")
    try:
        convocatoria = convocatorias.exigir_abierta()
    except InscripcionesCerradasError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error

    estado_reserva, token = pdf_usos.reservar(contenido, convocatoria["id"], x_pdf_reservation)
    if estado_reserva == EN_USO:
        raise HTTPException(status_code=409, detail="El PDF está usándose.")
    if estado_reserva == REGISTRADO:
        raise HTTPException(status_code=409, detail="Este PDF ya fue registrado.")
    if estado_reserva != RESERVADO or not token:
        raise HTTPException(status_code=503, detail="No fue posible reservar el PDF.")
    try:
        resultado = service.analizar(contenido, nombre, convocatoria)
        if resultado["estado"] == "PUEDE_SOLICITAR":
            identidad = pdf_usos.asociar_identidad(token, convocatoria["id"], resultado.get("ci", ""), resultado.get("ru", ""))
            if identidad != RESERVADO:
                raise HTTPException(status_code=409, detail="El estudiante ya tiene una solicitud o la verificación expiró.")
            pdf_usos.guardar_contexto(token, {"promedio": resultado["promedio"]})
            resultado["pdf_token"] = token
        elif resultado["estado"] == "YA_SOLICITO":
            pdf_usos.marcar_registrado(token)
        else:
            pdf_usos.liberar(token)
        return resultado
    except HTTPException:
        pdf_usos.liberar(token)
        raise
    except ValueError as error:
        pdf_usos.liberar(token)
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception:
        pdf_usos.liberar(token)
        raise


@router.post("/solicitudes")
def registrar_solicitud(solicitud: SolicitudAdicionRequest):
    try:
        convocatoria = convocatorias.exigir_abierta()
        estado = pdf_usos.validar_reserva(solicitud.pdf_token, convocatoria["id"], solicitud.ci, solicitud.ru)
        if estado == REGISTRADO:
            raise HTTPException(status_code=409, detail="Este PDF ya fue registrado.")
        if estado == INVALIDO:
            raise HTTPException(status_code=409, detail="Los datos no corresponden al historial analizado.")
        if estado == EXPIRADO or estado != RESERVADO:
            raise HTTPException(status_code=409, detail="La verificación del PDF expiró. Vuelve a subirlo.")
        contexto = pdf_usos.obtener_contexto(solicitud.pdf_token)
        if "promedio" not in contexto:
            raise HTTPException(status_code=409, detail="No se encontró la evaluación del historial. Vuelve a subirlo.")
        registrado, mensaje = repository.registrar(solicitud, float(contexto["promedio"]))
        pdf_usos.marcar_registrado(solicitud.pdf_token)
    except InscripcionesCerradasError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    return {"registrado": registrado, "duplicado": not registrado, "mensaje": mensaje}


@router.delete("/historiales/reserva/{token}", status_code=204)
def liberar_reserva(token: UUID):
    pdf_usos.liberar(str(token))
    return None
