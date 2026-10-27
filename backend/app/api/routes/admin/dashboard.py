from fastapi import APIRouter, Depends

from app.api.dependencies import exigir_admin
from app.api.routes.admin.context import (
    convocatoria_repository,
    dashboard_lock,
    student_repository,
)


router = APIRouter()


def _convocatorias_con_estudiantes() -> list[dict]:
    resultado = []
    for convocatoria in convocatoria_repository.listar_cerradas():
        estudiantes = student_repository.listar(convocatoria["id"])
        resultado.append(
            {
                **convocatoria,
                "total": len(estudiantes),
                "estudiantes": estudiantes,
            }
        )
    return resultado


@router.get("/estudiantes")
def listar_estudiantes(_: str = Depends(exigir_admin)):
    # Evita compartir el mismo socket HTTP/2 de Supabase entre dos cargas del panel.
    with dashboard_lock:
        estudiantes = student_repository.listar()
        return {
            "total": len(estudiantes),
            "estudiantes": estudiantes,
            "incidencias": student_repository.listar_incidencias(),
            "convocatoria": convocatoria_repository.obtener_actual(),
            "convocatorias_cerradas": _convocatorias_con_estudiantes(),
        }


@router.get("/convocatorias/cerradas")
def listar_convocatorias_cerradas(_: str = Depends(exigir_admin)):
    return {"convocatorias": _convocatorias_con_estudiantes()}
