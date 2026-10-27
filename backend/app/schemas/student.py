import re

from pydantic import BaseModel, Field
from pydantic import field_validator


class RegistroEstudianteRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    ci: str = Field(min_length=3, max_length=30)
    ru: str = Field(min_length=3, max_length=30)
    correo: str = Field(min_length=5, max_length=150)
    celular: str = Field(min_length=5, max_length=30)
    pdf_token: str = Field(
        min_length=36,
        max_length=36,
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
    )

    @field_validator("nombre", "ci", "ru", "correo", "celular", "pdf_token", mode="before")
    @classmethod
    def validar_campo_obligatorio(cls, valor: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("Todos los campos son obligatorios.")
        return valor.strip()

    @field_validator("celular")
    @classmethod
    def validar_celular(cls, valor: str) -> str:
        digitos = re.sub(r"\D", "", valor)
        if len(digitos) < 7 or len(digitos) > 15:
            raise ValueError("Ingresa un número de celular válido.")
        return valor
