from __future__ import annotations

from app.repositories.addition_repository import AdditionRepository
from app.schemas.adicion import ResultadoAdicion
from app.services.pdf_extractor import MULTIPLES_HISTORIALES, PdfExtractor


class AdditionAnalysisService:
    def __init__(self) -> None:
        self.extractor = PdfExtractor()
        self.repository = AdditionRepository()

    def analizar(self, contenido: bytes, nombre_archivo: str, convocatoria: dict) -> dict:
        registros, ci, nombre, ru, advertencias, faltantes, promedio_general = self.extractor.extraer(contenido)
        promedio_minimo = self.repository.obtener_promedio_minimo()
        if promedio_general is None:
            faltantes = [*faltantes, "PROM.GRAL. del historial"]
        if faltantes:
            self.repository.registrar_incidencia(
                nombre, ci, ru, nombre_archivo, "PDF rechazado: " + ", ".join(faltantes)
            )
            return ResultadoAdicion(
                estado="PDF_NO_VALIDO",
                mensaje="Este PDF no está permitido." if MULTIPLES_HISTORIALES in faltantes else "Este archivo no es un historial académico válido.",
                ci=ci, nombre=nombre, ru=ru, archivo=nombre_archivo,
                promedio_minimo=promedio_minimo, materias_detectadas=len(registros),
                advertencias=[f"Falta: {item}." for item in faltantes],
            ).model_dump()
        if self.repository.esta_registrado(ci, ru):
            return ResultadoAdicion(
                estado="YA_SOLICITO", mensaje="Ya enviaste una solicitud de adición en esta convocatoria.",
                ci=ci, nombre=nombre, ru=ru, archivo=nombre_archivo,
                promedio_minimo=promedio_minimo, materias_detectadas=len(registros),
            ).model_dump()

        promedio = round(promedio_general, 2)
        gestion = int(convocatoria['gestion'])
        if convocatoria['semestre'] == 'Primer semestre':
            gestion -= 1
            periodo = 'SEGUNDO'
        elif convocatoria['semestre'] == 'Segundo semestre':
            periodo = 'PRIMERO'
        else:
            raise ValueError('El semestre de la convocatoria no es válido.')
        periodo_revisado = f'{periodo.lower()} semestre de {gestion}'
        registros_periodo = [item for item in registros
                            if str(item.get('gestion', '')).strip() == str(gestion)
                            and str(item.get('periodo', '')).strip().upper() == periodo]
        materias_observadas = [
            item for item in registros_periodo
            if str(item.get("observacion", "")).upper() in {"REPROBADO", "ABANDONADO", "ABANDONO"}
        ]
        reprobadas = [item for item in materias_observadas if str(item.get("observacion", "")).upper() == "REPROBADO"]
        abandonadas = [item for item in materias_observadas if str(item.get("observacion", "")).upper() in {"ABANDONADO", "ABANDONO"}]
        motivos: list[str] = []
        if not registros_periodo:
            motivos.append(f'Tu historial debe contener materias del {periodo_revisado}, el período inmediatamente anterior a la convocatoria.')
        if reprobadas:
            motivos.append(f"Tienes {len(reprobadas)} materia(s) reprobada(s) en el {periodo_revisado}.")
        if abandonadas:
            motivos.append(f"Tienes {len(abandonadas)} materia(s) abandonada(s) en el {periodo_revisado}.")
        if promedio < promedio_minimo:
            motivos.append(f"Tu promedio es {promedio:.2f} y el mínimo requerido es {promedio_minimo:.2f}.")

        if motivos:
            estado, mensaje = "NO_PUEDE_SOLICITAR", "No cumples todos los requisitos para adicionar una materia."
        elif advertencias:
            estado, mensaje = "REQUIERE_REVISION", "El historial necesita revisión porque algunas páginas no tienen texto seleccionable."
        else:
            estado, mensaje = "PUEDE_SOLICITAR", "Cumples los requisitos académicos para solicitar la adición de una materia."
        return ResultadoAdicion(
            estado=estado, mensaje=mensaje, motivos=motivos, ci=ci, nombre=nombre, ru=ru,
            archivo=nombre_archivo, promedio=promedio, promedio_minimo=promedio_minimo,
            materias_detectadas=len(registros), materias_observadas=materias_observadas,
            advertencias=advertencias,
        ).model_dump()
