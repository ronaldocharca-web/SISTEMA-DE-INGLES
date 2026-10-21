from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.analysis_service import AnalisisService


router = APIRouter(prefix="/historiales", tags=["historiales"])
service = AnalisisService()


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
        return service.analizar(contenido, nombre)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
