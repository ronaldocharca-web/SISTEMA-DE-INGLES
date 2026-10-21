from __future__ import annotations

import unicodedata

from app.repositories.rules_repository import RulesRepository
from app.repositories.student_repository import StudentRepository
from app.schemas.historial import ResultadoAnalisis
from app.services.pdf_extractor import PdfExtractor


def normalizar(valor: str) -> str:
    texto = unicodedata.normalize("NFD", valor.upper())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


class AnalisisService:
    def __init__(self) -> None:
        self.extractor = PdfExtractor()
        self.rules = RulesRepository()
        self.students = StudentRepository()

    def analizar(self, contenido: bytes, nombre_archivo: str) -> dict:
        registros, ci, nombre_estudiante, ru, advertencias, faltantes = self.extractor.extraer(contenido)
        if faltantes:
            self.students.registrar_incidencia(
                nombre_estudiante,
                ci,
                ru,
                nombre_archivo,
                "PDF rechazado: " + ", ".join(faltantes),
            )
            return ResultadoAnalisis(
                estado="PDF_NO_VALIDO",
                mensaje="Este archivo no es válido. Solo se aceptan historiales del estudiante.",
                ci=ci,
                nombre=nombre_estudiante,
                ru=ru,
                archivo=nombre_archivo,
                materias_detectadas=len(registros),
                advertencias=[f"Falta: {item}." for item in faltantes],
            ).model_dump()
        if self.students.esta_registrado(ci, ru):
            return ResultadoAnalisis(
                estado="YA_INSCRITO",
                mensaje="Tú ya te inscribiste antes. No necesitas volver a llenar el formulario.",
                ci=ci,
                nombre=nombre_estudiante,
                ru=ru,
                archivo=nombre_archivo,
                materias_detectadas=len(registros),
            ).model_dump()
        codigos = tuple(normalizar(item) for item in self.rules.english_codes())
        materias_requisito = [
            registro for registro in registros
            if any(normalizar(str(registro["sigla"])) == codigo for codigo in codigos)
        ]
        if materias_requisito:
            estado, mensaje = "NO_PUEDE_TOMAR", "El historial contiene una asignatura de inglés del cuadro de convalidación."
        elif advertencias:
            estado, mensaje = "REQUIERE_REVISION", "Se extrajeron materias, pero algunas páginas no tenían texto seleccionable."
        else:
            estado, mensaje = "PUEDE_TOMAR", "No se encontraron materias o niveles de inglés en el historial."
        return ResultadoAnalisis(
            estado=estado, mensaje=mensaje, ci=ci, nombre=nombre_estudiante, ru=ru, archivo=nombre_archivo,
            materias_requisito=materias_requisito,
            codigos_buscados=list(self.rules.english_codes()),
            materias_detectadas=len(registros),
            advertencias=advertencias,
        ).model_dump()
