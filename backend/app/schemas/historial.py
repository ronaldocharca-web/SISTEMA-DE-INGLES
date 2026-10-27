from typing import Literal

from pydantic import BaseModel, Field

class Materia(BaseModel):
    ci: str = ""
    gestion: str = ""
    periodo: str = ""
    numero: int
    sigla: str
    materia: str
    paralelo: str = ""
    nota: int
    folio: str = ""
    libro: str = ""
    observacion: str = ""
    docente: str = ""

class ResultadoAnalisis(BaseModel):
    estado: Literal["PUEDE_TOMAR", "NO_PUEDE_TOMAR", "REQUIERE_REVISION", "YA_INSCRITO", "PDF_NO_VALIDO", "INSCRIPCIONES_CERRADAS"]
    mensaje: str
    ci: str = ""
    nombre: str = ""
    ru: str = ""
    archivo: str
    materias_requisito: list[Materia] = Field(default_factory=list)
    codigos_buscados: list[str] = Field(default_factory=list)
    materias_detectadas: int
    advertencias: list[str] = Field(default_factory=list)
    convocatoria: dict | None = None
    pdf_token: str | None = None
