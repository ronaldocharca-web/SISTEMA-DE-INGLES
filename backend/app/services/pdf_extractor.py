from __future__ import annotations

import io
import re
import unicodedata

import pdfplumber

PATRON_PERIODO = re.compile(r"^(\d{4})\s+(PRIMERO|SEGUNDO|VERANO|INVIERNO)$", re.IGNORECASE)
PATRON_MATERIA = re.compile(
    r"^(\d+)\s+([A-Z]+(?:[- ]\d+)+)\s+(.+?)\s+(?:([A-Z])\s+)?(\d{1,3})\s+"
    r"(?:(\d+)\s+)?(?:(\d+)\s+)?(APROBADO|REPROBADO|ABANDONADO|ABANDONO)\s*(.*)$",
    re.IGNORECASE,
)
PATRON_CI = re.compile(
    r"\b(?:C[eé]dula|C\.\s*I\.?|CI)(?:\s+de\s+identidad)?\s*[:#-]?\s*(\d{5,})",
    re.IGNORECASE,
)
PATRON_NOMBRE = re.compile(r"Nombre\(s\)\s*(.*?)\s+Fecha\s*[.:]", re.IGNORECASE)
PATRON_RU = re.compile(
    r"\b(?:Reg\.?\s*\.?\s*Univ\.?|R\.\s*U\.?|RU)\s*[:#-]?\s*(\d{3,})",
    re.IGNORECASE,
)

MULTIPLES_HISTORIALES = "más de un historial académico"


def _normalizar_identidad(valor: str) -> str:
    texto = unicodedata.normalize("NFD", valor.upper())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return " ".join(texto.split())


def contiene_multiples_historiales(texto: str) -> bool:
    cis = {coincidencia for coincidencia in PATRON_CI.findall(texto) if coincidencia}
    rus = {coincidencia for coincidencia in PATRON_RU.findall(texto) if coincidencia}
    nombres = {
        _normalizar_identidad(coincidencia)
        for coincidencia in PATRON_NOMBRE.findall(texto)
        if coincidencia.strip()
    }
    return len(cis) > 1 or len(rus) > 1 or len(nombres) > 1


class PdfExtractor:
    def extraer(self, contenido: bytes) -> tuple[list[dict[str, object]], str, str, str, list[str], list[str]]:
        registros: list[dict[str, object]] = []
        advertencias: list[str] = []
        gestion = ""
        periodo = ""
        ci = ""
        nombre = ""
        ru = ""
        texto_completo = ""
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text() or ""
                texto_completo += f"\n{texto}"
                if not texto.strip():
                    advertencias.append(f"La página {pagina.page_number} no contiene texto seleccionable.")
                    continue
                if not ci:
                    coincidencia_ci = PATRON_CI.search(texto)
                    if coincidencia_ci:
                        ci = coincidencia_ci.group(1)
                if not nombre:
                    coincidencia_nombre = PATRON_NOMBRE.search(texto)
                    if coincidencia_nombre:
                        nombre = coincidencia_nombre.group(1).strip()
                if not ru:
                    coincidencia_ru = PATRON_RU.search(texto)
                    if coincidencia_ru:
                        ru = coincidencia_ru.group(1)
                ultima: dict[str, object] | None = None
                for linea in texto.splitlines():
                    linea = linea.strip()
                    if not linea:
                        continue
                    encabezado = PATRON_PERIODO.fullmatch(linea)
                    if encabezado:
                        gestion, periodo = encabezado.groups()
                        periodo = periodo.upper()
                        ultima = None
                        continue
                    coincidencia = PATRON_MATERIA.match(linea)
                    if coincidencia:
                        numero, sigla, materia, paralelo, nota, folio, libro, observacion, docente = coincidencia.groups()
                        ultima = {
                            "ci": ci, "gestion": gestion, "periodo": periodo,
                            "numero": int(numero), "sigla": " ".join(sigla.upper().replace("-", " ").split()), "materia": materia.strip(),
                            "paralelo": paralelo or "", "nota": int(nota), "folio": folio or "",
                            "libro": libro or "", "observacion": observacion.upper().strip(),
                            "docente": docente.strip(),
                        }
                        registros.append(ultima)
                        continue
                    if ultima is not None and ultima["sigla"] == "INF-332" and linea.upper() == "SISTEMAS)":
                        ultima["materia"] = f"{ultima['materia']} {linea}"
        normalizado = unicodedata.normalize("NFD", texto_completo.upper())
        normalizado = "".join(c for c in normalizado if unicodedata.category(c) != "Mn")
        marcadores = {
            "HISTORIAL ACADEMICO": "título HISTORIAL ACADEMICO",
            "SIGLA": "columna SIGLA",
            "MATERIA": "columna MATERIA",
            "NOTA": "columna NOTA",
            "OBSERVACION": "columna OBSERVACION",
        }
        faltantes = [descripcion for marcador, descripcion in marcadores.items() if marcador not in normalizado]
        if not registros:
            faltantes.append("filas de materias académicas")
        if contiene_multiples_historiales(texto_completo):
            faltantes.append(MULTIPLES_HISTORIALES)
        return registros, ci, nombre, ru, sorted(set(advertencias)), faltantes
