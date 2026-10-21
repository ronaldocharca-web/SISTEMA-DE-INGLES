from pydantic import BaseModel, Field


class RegistroEstudianteRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    ci: str = Field(min_length=3, max_length=30)
    ru: str = Field(min_length=3, max_length=30)
    correo: str = Field(min_length=5, max_length=150)
    celular: str = Field(min_length=5, max_length=30)
