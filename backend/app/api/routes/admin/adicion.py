from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.dependencies import exigir_admin
from app.repositories.addition_repository import AdditionRepository
from app.repositories.convocatoria_repository import ConvocatoriaRepository
from app.schemas.adicion import ConfiguracionAdicionUpdate
from app.schemas.convocatoria import ConvocatoriaFinUpdate, ConvocatoriaRequest
from app.services.pdf_service import generar_pdf_solicitudes_adicion
from app.services.word_service import generar_word_solicitudes_adicion


router = APIRouter(prefix="/adicion")
repository = AdditionRepository()
convocatorias = ConvocatoriaRepository("adicion")


def _cerradas_con_solicitudes() -> list[dict]:
    return [
        {**item, "solicitudes": repository.listar(item["id"]), "total": len(repository.listar(item["id"]))}
        for item in convocatorias.listar_cerradas()
    ]


def _convocatoria_cerrada(convocatoria_id: str) -> dict | None:
    return next(
        (item for item in convocatorias.listar_cerradas() if item["id"] == convocatoria_id),
        None,
    )


def _descarga(contenido: bytes, media_type: str, nombre: str) -> StreamingResponse:
    return StreamingResponse(
        BytesIO(contenido),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@router.get("/resumen")
def obtener_resumen(_: str = Depends(exigir_admin)):
    solicitudes = repository.listar()
    return {
        "total": len(solicitudes),
        "solicitudes": solicitudes,
        "incidencias": repository.listar_incidencias(),
        "convocatoria": convocatorias.obtener_actual(),
        "convocatorias_cerradas": _cerradas_con_solicitudes(),
        "promedio_minimo": repository.obtener_promedio_minimo(),
    }


@router.put("/convocatoria")
def crear_convocatoria(datos: ConvocatoriaRequest, _: str = Depends(exigir_admin)):
    try:
        convocatoria = convocatorias.crear(datos)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"mensaje": "Convocatoria de adición configurada.", "convocatoria": convocatoria}


@router.patch("/convocatoria/fin")
def actualizar_fin(datos: ConvocatoriaFinUpdate, _: str = Depends(exigir_admin)):
    try:
        convocatoria = convocatorias.actualizar_fin(datos)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"mensaje": "Fecha actualizada.", "convocatoria": convocatoria}


@router.put("/configuracion")
def actualizar_configuracion(datos: ConfiguracionAdicionUpdate, _: str = Depends(exigir_admin)):
    promedio = repository.actualizar_promedio_minimo(datos.promedio_minimo)
    return {"mensaje": "Promedio mínimo actualizado.", "promedio_minimo": promedio}


@router.get("/exportar")
def exportar(_: str = Depends(exigir_admin)):
    try:
        contenido = repository.generar_excel(convocatoria=convocatorias.obtener_actual())
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"No fue posible generar el Excel: {error}") from error
    return _descarga(contenido, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "solicitudes_adicion_convocatoria_actual.xlsx")


@router.get("/exportar-word")
def exportar_word(_: str = Depends(exigir_admin)):
    try:
        convocatoria = convocatorias.obtener_actual()
        contenido = generar_word_solicitudes_adicion(repository.listar(), convocatoria)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"No fue posible generar el Word: {error}") from error
    return _descarga(contenido, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "solicitudes_adicion_convocatoria_actual.docx")


@router.get("/exportar-pdf")
def exportar_pdf(_: str = Depends(exigir_admin)):
    try:
        convocatoria = convocatorias.obtener_actual()
        contenido = generar_pdf_solicitudes_adicion(repository.listar(), convocatoria)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"No fue posible generar el PDF: {error}") from error
    return _descarga(contenido, "application/pdf", "solicitudes_adicion_convocatoria_actual.pdf")


@router.get("/convocatorias/{convocatoria_id}/exportar")
def exportar_convocatoria(convocatoria_id: str, _: str = Depends(exigir_admin)):
    convocatoria = _convocatoria_cerrada(convocatoria_id)
    if convocatoria is None:
        raise HTTPException(status_code=404, detail="No se encontró la convocatoria.")
    try:
        contenido = repository.generar_excel(convocatoria_id, convocatoria)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"No fue posible generar el Excel: {error}") from error
    return _descarga(contenido, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", f"solicitudes_adicion_{convocatoria_id}.xlsx")


@router.get("/convocatorias/{convocatoria_id}/exportar-word")
def exportar_word_convocatoria(convocatoria_id: str, _: str = Depends(exigir_admin)):
    convocatoria = _convocatoria_cerrada(convocatoria_id)
    if convocatoria is None:
        raise HTTPException(status_code=404, detail="No se encontró la convocatoria.")
    try:
        contenido = generar_word_solicitudes_adicion(repository.listar(convocatoria_id), convocatoria)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"No fue posible generar el Word: {error}") from error
    return _descarga(contenido, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"solicitudes_adicion_{convocatoria_id}.docx")


@router.get("/convocatorias/{convocatoria_id}/exportar-pdf")
def exportar_pdf_convocatoria(convocatoria_id: str, _: str = Depends(exigir_admin)):
    convocatoria = _convocatoria_cerrada(convocatoria_id)
    if convocatoria is None:
        raise HTTPException(status_code=404, detail="No se encontró la convocatoria.")
    try:
        contenido = generar_pdf_solicitudes_adicion(repository.listar(convocatoria_id), convocatoria)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"No fue posible generar el PDF: {error}") from error
    return _descarga(contenido, "application/pdf", f"solicitudes_adicion_{convocatoria_id}.pdf")
