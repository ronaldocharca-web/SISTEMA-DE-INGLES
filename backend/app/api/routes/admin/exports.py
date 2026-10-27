from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.dependencies import exigir_admin
from app.api.routes.admin.context import convocatoria_repository, student_repository
from app.services.pdf_service import generar_pdf_estudiantes
from app.services.word_service import generar_word_estudiantes


router = APIRouter()

EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
WORD_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _descarga(contenido: bytes, media_type: str, nombre: str) -> StreamingResponse:
    return StreamingResponse(
        BytesIO(contenido),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


def _convocatoria_cerrada(convocatoria_id: str) -> dict | None:
    return next(
        (
            item
            for item in convocatoria_repository.listar_cerradas()
            if item["id"] == convocatoria_id
        ),
        None,
    )


@router.get("/convocatorias/{convocatoria_id}/exportar")
def exportar_convocatoria(convocatoria_id: str, _: str = Depends(exigir_admin)):
    try:
        contenido = student_repository.generar_excel(
            convocatoria_id,
            _convocatoria_cerrada(convocatoria_id),
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el Excel: {error}",
        ) from error
    return _descarga(
        contenido,
        EXCEL_MEDIA_TYPE,
        f"estudiantes_convocatoria_{convocatoria_id}.xlsx",
    )


@router.get("/estudiantes/exportar")
def exportar_estudiantes(_: str = Depends(exigir_admin)):
    try:
        contenido = student_repository.generar_excel(
            convocatoria=convocatoria_repository.obtener_actual()
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el Excel: {error}",
        ) from error
    return _descarga(
        contenido,
        EXCEL_MEDIA_TYPE,
        "estudiantes_convocatoria_actual.xlsx",
    )


@router.get("/estudiantes/exportar-word")
def exportar_estudiantes_word(_: str = Depends(exigir_admin)):
    try:
        convocatoria = convocatoria_repository.obtener_actual()
        contenido = generar_word_estudiantes(student_repository.listar(), convocatoria)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el Word: {error}",
        ) from error
    return _descarga(contenido, WORD_MEDIA_TYPE, "examen_clasificacion_ingles.docx")


@router.get("/estudiantes/exportar-pdf")
def exportar_estudiantes_pdf(_: str = Depends(exigir_admin)):
    try:
        convocatoria = convocatoria_repository.obtener_actual()
        contenido = generar_pdf_estudiantes(student_repository.listar(), convocatoria)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el PDF: {error}",
        ) from error
    return _descarga(contenido, "application/pdf", "examen_clasificacion_ingles.pdf")


@router.get("/convocatorias/{convocatoria_id}/exportar-word")
def exportar_word_convocatoria(
    convocatoria_id: str,
    _: str = Depends(exigir_admin),
):
    try:
        convocatoria = _convocatoria_cerrada(convocatoria_id) or {
            "nombre": "Convocatoria"
        }
        contenido = generar_word_estudiantes(
            student_repository.listar(convocatoria_id),
            convocatoria,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el Word de la convocatoria: {error}",
        ) from error
    return _descarga(
        contenido,
        WORD_MEDIA_TYPE,
        f"examen_clasificacion_ingles_{convocatoria_id}.docx",
    )


@router.get("/convocatorias/{convocatoria_id}/exportar-pdf")
def exportar_pdf_convocatoria(
    convocatoria_id: str,
    _: str = Depends(exigir_admin),
):
    try:
        convocatoria = _convocatoria_cerrada(convocatoria_id) or {
            "nombre": "Convocatoria"
        }
        contenido = generar_pdf_estudiantes(
            student_repository.listar(convocatoria_id),
            convocatoria,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el PDF de la convocatoria: {error}",
        ) from error
    return _descarga(
        contenido,
        "application/pdf",
        f"examen_clasificacion_ingles_{convocatoria_id}.pdf",
    )
