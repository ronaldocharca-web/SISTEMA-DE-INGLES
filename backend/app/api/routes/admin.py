from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
from threading import Lock

from app.api.dependencies import admin_service, exigir_admin
from app.repositories.convocatoria_repository import ConvocatoriaRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.admin import AdminCredentialsUpdate, AdminLoginRequest
from app.schemas.convocatoria import ConvocatoriaFinUpdate, ConvocatoriaRequest
from app.services.admin_service import (
    AdminBloqueadoError,
    AdminCredencialesInvalidasError,
)


router = APIRouter(prefix="/admin", tags=["administración"])
student_repository = StudentRepository()
convocatoria_repository = ConvocatoriaRepository()
dashboard_lock = Lock()


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


@router.get("/estudiantes")
def listar_estudiantes(_: str = Depends(exigir_admin)):
    # El cliente síncrono de Supabase reutiliza conexiones HTTP/2. El bloqueo
    # evita que dos cargas simultáneas del panel compartan el mismo socket.
    with dashboard_lock:
        estudiantes = student_repository.listar()
        incidencias = student_repository.listar_incidencias()
        convocatorias_cerradas = []
        for convocatoria in convocatoria_repository.listar_cerradas():
            estudiantes_anteriores = student_repository.listar(convocatoria["id"])
            convocatorias_cerradas.append(
                {
                    **convocatoria,
                    "total": len(estudiantes_anteriores),
                    "estudiantes": estudiantes_anteriores,
                }
            )
        return {
            "total": len(estudiantes),
            "estudiantes": estudiantes,
            "incidencias": incidencias,
            "convocatoria": convocatoria_repository.obtener_actual(),
            "convocatorias_cerradas": convocatorias_cerradas,
        }


@router.put("/convocatoria")
def crear_convocatoria(
    datos: ConvocatoriaRequest,
    _: str = Depends(exigir_admin),
):
    convocatoria = convocatoria_repository.crear(datos)
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


@router.get("/convocatorias/cerradas")
def listar_convocatorias_cerradas(_: str = Depends(exigir_admin)):
    convocatorias = convocatoria_repository.listar_cerradas()
    resultado = []
    for convocatoria in convocatorias:
        estudiantes = student_repository.listar(convocatoria["id"])
        resultado.append(
            {
                **convocatoria,
                "total": len(estudiantes),
                "estudiantes": estudiantes,
            }
        )
    return {"convocatorias": resultado}


@router.get("/convocatorias/{convocatoria_id}/exportar")
def exportar_convocatoria(convocatoria_id: str, _: str = Depends(exigir_admin)):
    try:
        contenido = student_repository.generar_excel(convocatoria_id)
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el Excel: {error}",
        ) from error
    return StreamingResponse(
        BytesIO(contenido),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="estudiantes_convocatoria_{convocatoria_id}.xlsx"'
            )
        },
    )


@router.get("/estudiantes/exportar")
def exportar_estudiantes(_: str = Depends(exigir_admin)):
    """Descarga el Excel de la convocatoria actual."""
    try:
        contenido = student_repository.generar_excel()
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"No fue posible generar el Excel: {error}",
        ) from error
    return StreamingResponse(
        BytesIO(contenido),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="estudiantes_convocatoria_actual.xlsx"'},
    )
