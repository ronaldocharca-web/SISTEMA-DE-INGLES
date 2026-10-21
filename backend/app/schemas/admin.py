from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    usuario: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=150)


class AdminCredentialsUpdate(BaseModel):
    usuario: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=150)
