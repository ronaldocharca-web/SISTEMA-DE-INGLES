import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.historial import Materia


class SolicitudAdicionRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    ci: str = Field(min_length=3, max_length=30)
    ru: str = Field(min_length=3, max_length=30)
    correo: str = Field(min_length=5, max_length=150)
    celular: str = Field(min_length=5, max_length=30)
    sigla_materia: str = Field(min_length=2, max_length=30)
    nombre_materia: str = Field(min_length=2, max_length=150)
    semestre_materia: int | None = Field(default=None, ge=1, le=10)
    numero_materia_total: int = Field(ge=7, le=8)
    pdf_token: str = Field(
        min_length=36,
        max_length=36,
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
    )

    @field_validator(
        "nombre", "ci", "ru", "correo", "celular", "sigla_materia", "nombre_materia", "pdf_token",
        mode="before",
    )
    @classmethod
    def validar_obligatorio(cls, valor: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("Todos los campos son obligatorios.")
        return valor.strip()

    @field_validator("sigla_materia")
    @classmethod
    def normalizar_sigla(cls, valor: str) -> str:
        return " ".join(valor.upper().replace("-", " ").split())

    @field_validator("celular")
    @classmethod
    def validar_celular(cls, valor: str) -> str:
        digitos = re.sub(r"\D", "", valor)
        if len(digitos) < 7 or len(digitos) > 15:
            raise ValueError("Ingresa un número de celular válido.")
        return valor


class ConfiguracionAdicionUpdate(BaseModel):
    promedio_minimo: float = Field(ge=0, le=100)


class ResultadoAdicion(BaseModel):
    estado: Literal[
        "PUEDE_SOLICITAR", "NO_PUEDE_SOLICITAR", "REQUIERE_REVISION",
        "YA_SOLICITO", "PDF_NO_VALIDO",
    ]
    mensaje: str
    motivos: list[str] = Field(default_factory=list)
    ci: str = ""
    nombre: str = ""
    ru: str = ""
    archivo: str
    promedio: float = 0
    promedio_minimo: float = 75
    materias_detectadas: int = 0
    materias_observadas: list[Materia] = Field(default_factory=list)
    advertencias: list[str] = Field(default_factory=list)
    pdf_token: str | None = None
