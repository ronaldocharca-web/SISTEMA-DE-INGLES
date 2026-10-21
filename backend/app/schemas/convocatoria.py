from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ConvocatoriaRequest(BaseModel):
    nombre: str = Field(min_length=3, max_length=120)
    inicio: datetime
    fin: datetime

    @model_validator(mode="after")
    def validar_intervalo(self):
        if self.fin <= self.inicio:
            raise ValueError("La fecha final debe ser posterior a la fecha inicial.")
        return self


class ConvocatoriaFinUpdate(BaseModel):
    fin: datetime


class ConvocatoriaResponse(BaseModel):
    id: str
    nombre: str
    inicio: datetime
    fin: datetime
    activa: bool = True
    abierta: bool
