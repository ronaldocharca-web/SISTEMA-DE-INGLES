from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from threading import Lock

from openpyxl import Workbook, load_workbook

from app.infrastructure.supabase_client import get_supabase_client
from app.repositories.convocatoria_repository import ConvocatoriaRepository
from app.schemas.adicion import SolicitudAdicionRequest


class AdditionRepository:
    """Solicitudes de adición, separadas de las inscripciones de inglés."""

    _lock = Lock()
    _headers = [
        "Fecha", "Nombre", "CI", "RU", "Correo", "Celular", "Sigla",
        "Nombre de materia", "Semestre de materia", "Carga total", "Promedio",
    ]
    _incident_headers = ["Fecha", "Nombre", "CI", "RU", "Archivo", "Motivo"]

    def __init__(self) -> None:
        data_dir = Path(__file__).resolve().parents[2] / "data"
        self.path = data_dir / "solicitudes_adicion.xlsx"
        self.config_path = data_dir / "configuracion_adicion.json"
        self.convocatorias = ConvocatoriaRepository("adicion")
        self._supabase_verificado = False
        self._usar_fallback_local = False

    @property
    def supabase(self):
        if self._usar_fallback_local:
            return None
        cliente = get_supabase_client()
        if cliente is None or self._supabase_verificado:
            return cliente
        try:
            cliente.table("configuracion_adicion").select("id").limit(1).execute()
            self._supabase_verificado = True
        except Exception as error:
            texto = str(error).lower()
            if any(marca in texto for marca in ("does not exist", "schema cache", "could not find", "relation")):
                self._usar_fallback_local = True
                return None
            raise
        return cliente

    @staticmethod
    def _normalizar(valor: str) -> str:
        return "".join(valor.upper().split())

    @staticmethod
    def _columnas_solicitud_faltantes(error: Exception) -> bool:
        texto = str(error).lower()
        columnas = ("sigla_materia", "nombre_materia", "semestre_materia", "numero_materia_total")
        return any(columna in texto for columna in columnas) and any(
            marca in texto for marca in ("schema cache", "could not find", "column")
        )

    def obtener_promedio_minimo(self) -> float:
        if self.supabase is not None:
            filas = (
                self.supabase.table("configuracion_adicion")
                .select("promedio_minimo")
                .eq("id", 1)
                .limit(1)
                .execute()
                .data
                or []
            )
            if filas:
                return float(filas[0]["promedio_minimo"])
        if self.config_path.exists():
            try:
                return float(json.loads(self.config_path.read_text(encoding="utf-8")).get("promedio_minimo", 75))
            except (OSError, ValueError, json.JSONDecodeError):
                pass
        return 75.0

    def actualizar_promedio_minimo(self, valor: float) -> float:
        valor = round(float(valor), 2)
        if self.supabase is not None:
            self.supabase.table("configuracion_adicion").upsert(
                {"id": 1, "promedio_minimo": valor}
            ).execute()
        else:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(
                json.dumps({"promedio_minimo": valor}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return valor

    def _crear_libro(self) -> None:
        if self.path.exists():
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        libro = Workbook()
        solicitudes = libro.active
        solicitudes.title = "Solicitudes"
        solicitudes.append(self._headers)
        incidencias = libro.create_sheet("Incidencias")
        incidencias.append(self._incident_headers)
        for hoja in (solicitudes, incidencias):
            hoja.freeze_panes = "A2"
            for celda in hoja[1]:
                celda.font = celda.font.copy(bold=True)
        libro.save(self.path)

    @staticmethod
    def _separar_materia(valor: str) -> tuple[str, str]:
        partes = [parte.strip() for parte in str(valor or "").split(" - ", 1)]
        return (partes[0], partes[1]) if len(partes) == 2 else ("", partes[0])

    def _asegurar_formato_local(self) -> None:
        self._crear_libro()
        libro = load_workbook(self.path)
        hoja = libro["Solicitudes"]
        encabezados = [str(celda.value or "") for celda in hoja[1]]
        if "Materia a adicionar" not in encabezados:
            if "Semestre de materia" in encabezados:
                libro.close()
                return
        else:
            for fila in range(2, hoja.max_row + 1):
                sigla, nombre = self._separar_materia(str(hoja.cell(fila, 7).value or ""))
                promedio = hoja.cell(fila, 8).value
                hoja.cell(fila, 7, sigla)
                hoja.cell(fila, 8, nombre)
                hoja.cell(fila, 9, promedio)
        encabezados = [str(celda.value or "") for celda in hoja[1]]
        if "Semestre de materia" not in encabezados:
            for fila in range(2, hoja.max_row + 1):
                promedio = hoja.cell(fila, 9).value
                hoja.cell(fila, 9, "")
                hoja.cell(fila, 10, "")
                hoja.cell(fila, 11, promedio)
        for columna, titulo in enumerate(self._headers, 1):
            hoja.cell(1, columna, titulo)
        libro.save(self.path)

    def registrar(self, solicitud: SolicitudAdicionRequest, promedio: float) -> tuple[bool, str]:
        convocatoria = self.convocatorias.exigir_abierta()
        if self.supabase is not None:
            existente = (
                self.supabase.table("solicitudes_adicion")
                .select("id")
                .eq("convocatoria_id", convocatoria["id"])
                .or_(f"ci.eq.{solicitud.ci},ru.eq.{solicitud.ru}")
                .limit(1)
                .execute()
                .data
            )
            if existente:
                return False, "Ya enviaste una solicitud de adición en esta convocatoria."
            materia_completa = f"{solicitud.sigla_materia} - {solicitud.nombre_materia}"
            datos = {
                "convocatoria_id": convocatoria["id"],
                "nombre": solicitud.nombre,
                "ci": solicitud.ci,
                "ru": solicitud.ru,
                "correo": solicitud.correo,
                "celular": solicitud.celular,
                "materia_adicionar": materia_completa,
                "sigla_materia": solicitud.sigla_materia,
                "nombre_materia": solicitud.nombre_materia,
                "semestre_materia": solicitud.semestre_materia,
                "numero_materia_total": solicitud.numero_materia_total,
                "promedio": promedio,
            }
            try:
                self.supabase.table("solicitudes_adicion").insert(datos).execute()
            except Exception as error:
                if not self._columnas_solicitud_faltantes(error):
                    raise
                datos.pop("sigla_materia")
                datos.pop("nombre_materia")
                datos.pop("semestre_materia")
                datos.pop("numero_materia_total")
                self.supabase.table("solicitudes_adicion").insert(datos).execute()
            return True, "Tu solicitud de adición fue registrada correctamente."

        with self._lock:
            self._asegurar_formato_local()
            libro = load_workbook(self.path)
            hoja = libro["Solicitudes"]
            ci, ru = self._normalizar(solicitud.ci), self._normalizar(solicitud.ru)
            for fila in hoja.iter_rows(min_row=2, values_only=True):
                if (ci and ci == self._normalizar(str(fila[2] or ""))) or (ru and ru == self._normalizar(str(fila[3] or ""))):
                    return False, "Ya enviaste una solicitud de adición en esta convocatoria."
            hoja.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), solicitud.nombre, solicitud.ci,
                solicitud.ru, solicitud.correo, solicitud.celular, solicitud.sigla_materia,
                solicitud.nombre_materia, solicitud.semestre_materia,
                solicitud.numero_materia_total,
                promedio,
            ])
            libro.save(self.path)
        return True, "Tu solicitud de adición fue registrada correctamente."

    def esta_registrado(self, ci: str, ru: str) -> bool:
        convocatoria = self.convocatorias.obtener_actual()
        if convocatoria is None:
            return False
        if self.supabase is not None:
            for columna, valor in (("ci", ci.strip()), ("ru", ru.strip())):
                if valor and (
                    self.supabase.table("solicitudes_adicion").select("id")
                    .eq("convocatoria_id", convocatoria["id"]).eq(columna, valor)
                    .limit(1).execute().data
                ):
                    return True
            return False
        if not self.path.exists():
            return False
        with self._lock:
            libro = load_workbook(self.path, read_only=True)
            for fila in libro["Solicitudes"].iter_rows(min_row=2, values_only=True):
                if (ci and self._normalizar(ci) == self._normalizar(str(fila[2] or ""))) or (ru and self._normalizar(ru) == self._normalizar(str(fila[3] or ""))):
                    return True
        return False

    def registrar_incidencia(self, nombre: str, ci: str, ru: str, archivo: str, motivo: str) -> None:
        convocatoria = self.convocatorias.obtener_actual()
        if self.supabase is not None:
            self.supabase.table("incidencias_adicion").insert({
                "convocatoria_id": convocatoria["id"] if convocatoria else None,
                "nombre": nombre.strip(), "ci": ci.strip(), "ru": ru.strip(),
                "archivo": archivo.strip(), "motivo": motivo.strip(),
            }).execute()
            return
        with self._lock:
            self._crear_libro()
            libro = load_workbook(self.path)
            libro["Incidencias"].append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), nombre, ci, ru, archivo, motivo,
            ])
            libro.save(self.path)

    def listar(self, convocatoria_id: str | None = None) -> list[dict[str, str]]:
        if self.supabase is not None:
            if convocatoria_id is None:
                convocatoria = self.convocatorias.obtener_actual()
                convocatoria_id = convocatoria["id"] if convocatoria else None
            if not convocatoria_id:
                return []
            consulta = self.supabase.table("solicitudes_adicion")
            try:
                filas = (
                    consulta.select("created_at,nombre,ci,ru,correo,celular,materia_adicionar,sigla_materia,nombre_materia,semestre_materia,numero_materia_total,promedio")
                    .eq("convocatoria_id", convocatoria_id).order("created_at", desc=True)
                    .execute().data or []
                )
            except Exception as error:
                if not self._columnas_solicitud_faltantes(error):
                    raise
                filas = (
                    self.supabase.table("solicitudes_adicion")
                    .select("created_at,nombre,ci,ru,correo,celular,materia_adicionar,promedio")
                    .eq("convocatoria_id", convocatoria_id).order("created_at", desc=True)
                    .execute().data or []
                )
            resultado = []
            for f in filas:
                sigla_legacy, nombre_legacy = self._separar_materia(f.get("materia_adicionar", ""))
                resultado.append({
                "Fecha": f.get("created_at", ""), "Nombre": f.get("nombre", ""),
                "CI": f.get("ci", ""), "RU": f.get("ru", ""), "Correo": f.get("correo", ""),
                "Celular": f.get("celular", ""), "Sigla": f.get("sigla_materia") or sigla_legacy,
                "Nombre de materia": f.get("nombre_materia") or nombre_legacy,
                "Semestre de materia": str(f.get("semestre_materia") or ""),
                "Carga total": str(f.get("numero_materia_total") or ""),
                "Promedio": str(f.get("promedio", "")),
                })
            return resultado
        if not self.path.exists():
            return []
        with self._lock:
            self._asegurar_formato_local()
            libro = load_workbook(self.path, read_only=True, data_only=True)
            return [dict(zip(self._headers, [str(v or "") for v in fila])) for fila in libro["Solicitudes"].iter_rows(min_row=2, values_only=True)]

    def listar_incidencias(self, convocatoria_id: str | None = None) -> list[dict[str, str]]:
        if self.supabase is not None:
            if convocatoria_id is None:
                convocatoria = self.convocatorias.obtener_actual()
                convocatoria_id = convocatoria["id"] if convocatoria else None
            if not convocatoria_id:
                return []
            filas = self.supabase.table("incidencias_adicion").select(
                "created_at,nombre,ci,ru,archivo,motivo"
            ).eq("convocatoria_id", convocatoria_id).order("created_at", desc=True).execute().data or []
            return [{
                "Fecha": f.get("created_at", ""), "Nombre": f.get("nombre", ""), "CI": f.get("ci", ""),
                "RU": f.get("ru", ""), "Archivo": f.get("archivo", ""), "Motivo": f.get("motivo", ""),
            } for f in filas]
        if not self.path.exists():
            return []
        with self._lock:
            libro = load_workbook(self.path, read_only=True, data_only=True)
            return [dict(zip(self._incident_headers, [str(v or "") for v in fila])) for fila in libro["Incidencias"].iter_rows(min_row=2, values_only=True)]

    def generar_excel(self, convocatoria_id: str | None = None, convocatoria: dict | None = None) -> bytes:
        libro = Workbook()
        hoja = libro.active
        hoja.title = "Solicitudes"
        hoja.append(self._headers)
        for fila in self.listar(convocatoria_id):
            hoja.append([fila[campo] for campo in self._headers])
        datos = libro.create_sheet("Convocatoria", 0)
        datos.append(["Campo", "Valor"])
        convocatoria = convocatoria or {}
        for campo in ("nombre", "gestion", "semestre", "inicio", "fin"):
            datos.append([campo.capitalize(), convocatoria.get(campo, "")])
        salida = BytesIO()
        libro.save(salida)
        return salida.getvalue()
