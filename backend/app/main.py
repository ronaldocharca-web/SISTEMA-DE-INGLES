# Punto de entrada de FastAPI; las variables se cargan antes de las rutas.
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Carga backend/.env antes de importar las rutas, porque las rutas crean
# los repositorios al iniciar la aplicación.
load_dotenv()

from app.api.router import api_router

app = FastAPI(title="Sistema de verificación de inglés", version="0.1.0")
origenes_permitidos = [
    origen.strip().rstrip("/")
    for origen in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origen.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
