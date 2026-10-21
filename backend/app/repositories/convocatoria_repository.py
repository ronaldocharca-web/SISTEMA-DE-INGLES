from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.infrastructure.supabase_client import get_supabase_client
from app.schemas.convocatoria import ConvocatoriaFinUpdate, ConvocatoriaRequest


class InscripcionesCerradasError(Exception):
    pass


class ConvocatoriaRepository:
    """Gestiona la convocatoria vigente en Supabase o en JSON local."""

    _lock = Lock()

    def __init__(self) -> None:
        self.path = Path(__file__).resolve().parents[2] / "data" / "convocatoria.json"

    @property
    def supabase(self):
        """Obtiene un cliente aislado para evitar reutilizar sockets entre solicitudes."""
        return get_supabase_client()

    @staticmethod
    def _fecha(valor: str | datetime) -> datetime:
        if isinstance(valor, datetime):
            fecha = valor
        else:
            fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        return fecha.astimezone(timezone.utc)

    def obtener_actual(self) -> dict | None:
        if self.supabase is not None:
            filas = (
                self.supabase.table("convocatorias")
                .select("id,nombre,inicio,fin,activa")
                .eq("activa", True)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
                .data
            )
            convocatoria = filas[0] if filas else None
        else:
            if not self.path.exists():
                return None
            convocatoria = json.loads(self.path.read_text(encoding="utf-8"))

        if convocatoria is None:
            return None
        inicio = self._fecha(convocatoria["inicio"])
        fin = self._fecha(convocatoria["fin"])
        ahora = datetime.now(timezone.utc)
        return {
            **convocatoria,
            "inicio": inicio.isoformat(),
            "fin": fin.isoformat(),
            "abierta": inicio <= ahora <= fin,
        }

    def exigir_abierta(self) -> dict:
        convocatoria = self.obtener_actual()
        if convocatoria is None:
            raise InscripcionesCerradasError(
                "Las inscripciones todavía no tienen una fecha habilitada."
            )
        if not convocatoria["abierta"]:
            raise InscripcionesCerradasError(
                "Las inscripciones están cerradas para la convocatoria actual."
            )
        return convocatoria

    def listar_cerradas(self) -> list[dict]:
        if self.supabase is None:
            return []
        filas = (
            self.supabase.table("convocatorias")
            .select("id,nombre,inicio,fin,activa,created_at")
            .eq("activa", False)
            .order("created_at", desc=True)
            .execute()
            .data
            or []
        )
        return [
            {
                **fila,
                "inicio": self._fecha(fila["inicio"]).isoformat(),
                "fin": self._fecha(fila["fin"]).isoformat(),
                "abierta": False,
            }
            for fila in filas
        ]

    def crear(self, datos: ConvocatoriaRequest) -> dict:
        inicio = self._fecha(datos.inicio).isoformat()
        fin = self._fecha(datos.fin).isoformat()
        if self.supabase is not None:
            filas = (
                self.supabase.rpc(
                    "create_exam_convocatoria",
                    {
                        "p_nombre": datos.nombre.strip(),
                        "p_inicio": inicio,
                        "p_fin": fin,
                    },
                )
                .execute()
                .data
            )
            if not filas:
                raise RuntimeError("Supabase no devolvió la convocatoria creada.")
            return {**filas[0], "abierta": self._esta_abierta(inicio, fin)}

        convocatoria = {
            "id": str(uuid4()),
            "nombre": datos.nombre.strip(),
            "inicio": inicio,
            "fin": fin,
            "activa": True,
            "abierta": self._esta_abierta(inicio, fin),
        }
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(convocatoria, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return convocatoria

    def actualizar_fin(self, datos: ConvocatoriaFinUpdate) -> dict:
        convocatoria = self.obtener_actual()
        if convocatoria is None:
            raise ValueError("No existe una convocatoria activa para actualizar.")

        fin = self._fecha(datos.fin)
        inicio = self._fecha(convocatoria["inicio"])
        if fin <= inicio:
            raise ValueError("La fecha final debe ser posterior a la fecha inicial.")

        if self.supabase is not None:
            filas = (
                self.supabase.table("convocatorias")
                .update({"fin": fin.isoformat()})
                .eq("id", convocatoria["id"])
                .execute()
                .data
            )
            if not filas:
                raise RuntimeError("No fue posible actualizar la fecha de cierre.")
        else:
            with self._lock:
                convocatoria["fin"] = fin.isoformat()
                self.path.write_text(
                    json.dumps(convocatoria, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

        return {
            **convocatoria,
            "fin": fin.isoformat(),
            "abierta": self._esta_abierta(convocatoria["inicio"], fin.isoformat()),
        }

    def _esta_abierta(self, inicio: str, fin: str) -> bool:
        ahora = datetime.now(timezone.utc)
        return self._fecha(inicio) <= ahora <= self._fecha(fin)
