from fastapi import APIRouter, File, HTTPException, UploadFile
from uuid import UUID

from app.repositories.convocatoria_repository import (
    ConvocatoriaRepository,
    InscripcionesCerradasError,
)
from app.repositories.pdf_usage_repository import (
    EN_USO,
    REGISTRADO,
    RESERVADO,
    PdfUsageRepository,
)
from app.services.analysis_service import AnalisisService


router = APIRouter(prefix="/historiales", tags=["historiales"])
service = AnalisisService()
convocatoria_repository = ConvocatoriaRepository()
pdf_usage_repository = PdfUsageRepository()


@router.post("/analizar")
async def analizar_historial(archivo: UploadFile = File(...)):
    nombre = archivo.filename or "archivo"
    if not nombre.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF.")

    contenido = await archivo.read()
    if not contenido:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")
    if len(contenido) > 4 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="El PDF supera el límite local de 4 MB.",
        )

    try:
        convocatoria = convocatoria_repository.exigir_abierta()
    except InscripcionesCerradasError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error

    estado_reserva, token = pdf_usage_repository.reservar(
        contenido,
        convocatoria["id"],
    )
    if estado_reserva == EN_USO:
        raise HTTPException(status_code=409, detail="El PDF está usándose.")
    if estado_reserva == REGISTRADO:
        raise HTTPException(status_code=409, detail="Este PDF ya fue registrado.")
    if estado_reserva != RESERVADO or token is None:
        raise HTTPException(status_code=503, detail="No fue posible reservar el PDF.")

    try:
        resultado = service.analizar(contenido, nombre)
        estado = resultado["estado"]
        if estado == "PUEDE_TOMAR":
            estado_identidad = pdf_usage_repository.asociar_identidad(
                token,
                convocatoria["id"],
                resultado.get("ci", ""),
                resultado.get("ru", ""),
            )
            if estado_identidad == EN_USO:
                raise HTTPException(status_code=409, detail="El PDF está usándose.")
            if estado_identidad == REGISTRADO:
                raise HTTPException(status_code=409, detail="Este PDF ya fue registrado.")
            if estado_identidad != RESERVADO:
                raise HTTPException(status_code=409, detail="La verificación del PDF expiró. Vuelve a subirlo.")
            resultado["pdf_token"] = token
        elif estado == "YA_INSCRITO":
            pdf_usage_repository.asociar_identidad(
                token,
                convocatoria["id"],
                resultado.get("ci", ""),
                resultado.get("ru", ""),
            )
            pdf_usage_repository.marcar_registrado(token)
        else:
            pdf_usage_repository.liberar(token)
        return resultado
    except HTTPException:
        pdf_usage_repository.liberar(token)
        raise
    except ValueError as error:
        pdf_usage_repository.liberar(token)
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception:
        pdf_usage_repository.liberar(token)
        raise


@router.delete("/reserva/{token}", status_code=204)
def liberar_reserva(token: UUID):
    pdf_usage_repository.liberar(str(token))
    return None
