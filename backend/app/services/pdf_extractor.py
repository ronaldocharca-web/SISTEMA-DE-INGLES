from __future__ import annotations

import io
import re

import pdfplumber

PATRON_PERIODO = re.compile(r"^(\d{4})\s+(PRIMERO|SEGUNDO|VERANO|INVIERNO)$", re.IGNORECASE)
PATRON_MATERIA = re.compile(
    r"^(\d+)\s+([A-Z]+(?:[- ]\d+)+)\s+(.+?)\s+(?:([A-Z])\s+)?(\d{1,3})\s+"
    r"(?:(\d+)\s+)?(?:(\d+)\s+)?(APROBADO|REPROBADO|ABANDONADO|ABANDONO)\s*(.*)$",
    re.IGNORECASE,
)
PATRON_CI = re.compile(r"C[eé]dula\s*:\s*(\d+)", re.IGNORECASE)
PATRON_NOMBRE = re.compile(r"Nombre\(s\)\s*(.*?)\s+Fecha\s*[.:]", re.IGNORECASE)
PATRON_RU = re.compile(r"Reg\.?\s*\.??\s*Univ\.?\s*:\s*(\d+)", re.IGNORECASE)


class PdfExtractor:
    def extraer(self, contenido: bytes) -> tuple[list[dict[str, object]], str, str, str, list[str]]:
        registros: list[dict[str, object]] = []
        advertencias: list[str] = []
        gestion = ""
        periodo = ""
        ci = ""
        nombre = ""
        ru = ""
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            for pagina in pdf.pages:
                texto = pagina.extract_text() or ""
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
        return registros, ci, nombre, ru, sorted(set(advertencias))
