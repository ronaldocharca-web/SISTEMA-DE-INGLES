from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.infrastructure.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)

RESERVADO = "RESERVADO"
EN_USO = "EN_USO"
REGISTRADO = "REGISTRADO"
EXPIRADO = "EXPIRADO"
INVALIDO = "INVALIDO"


class PdfUsageRepository:
    """Reserva cada PDF para impedir reutilizaciones y carreras entre equipos."""

    _lock = Lock()
    _duracion_reserva = timedelta(minutes=20)

    def __init__(self) -> None:
        self.path = Path(__file__).resolve().parents[2] / "data" / "pdf_usos.json"
        self._usar_fallback_local = False

    @property
    def supabase(self):
        if self._usar_fallback_local:
            return None
        return get_supabase_client()

    @staticmethod
    def calcular_hash(contenido: bytes) -> str:
        return hashlib.sha256(contenido).hexdigest()

    @staticmethod
    def _normalizar_identificador(valor: str) -> str:
        return "".join(valor.upper().split())

    @staticmethod
    def _fecha(valor: str | None) -> datetime | None:
        if not valor:
            return None
        fecha = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        return fecha.astimezone(timezone.utc)

    @staticmethod
    def _es_duplicado(error: Exception) -> bool:
        texto = str(error).lower()
        return "23505" in texto or "duplicate" in texto or "unique" in texto

    @staticmethod
    def _es_tabla_faltante(error: Exception) -> bool:
        texto = str(error).lower()
        return "pdf_usos" in texto and any(
            marca in texto
            for marca in ("does not exist", "schema cache", "could not find", "relation")
        )

    def _activar_fallback(self, error: Exception) -> None:
        self._usar_fallback_local = True
        logger.warning(
            "La tabla pdf_usos todavía no existe en Supabase; se usará el control local: %s",
            error,
        )

    def _cargar_local(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            datos = json.loads(self.path.read_text(encoding="utf-8"))
            return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def _guardar_local(self, filas: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(filas, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def reservar(self, contenido: bytes, convocatoria_id: str) -> tuple[str, str | None]:
        hash_sha256 = self.calcular_hash(contenido)
        token = str(uuid4())
        ahora = datetime.now(timezone.utc)
        reservado_hasta = ahora + self._duracion_reserva
        cliente = self.supabase
        if cliente is None:
            return self._reservar_local(hash_sha256, token, convocatoria_id, ahora, reservado_hasta)

        fila = {
            "convocatoria_id": convocatoria_id,
            "hash_sha256": hash_sha256,
            "token": token,
            "estado": "reservado",
            "reservado_hasta": reservado_hasta.isoformat(),
        }
        try:
            cliente.table("pdf_usos").insert(fila).execute()
            return RESERVADO, token
        except Exception as error:
            if self._es_tabla_faltante(error):
                self._activar_fallback(error)
                return self._reservar_local(hash_sha256, token, convocatoria_id, ahora, reservado_hasta)
            if not self._es_duplicado(error):
                raise

        existente = self._obtener_por_hash(cliente, convocatoria_id, hash_sha256)
        if existente and existente.get("estado") == "registrado":
            return REGISTRADO, None
        if existente and self._fecha(existente.get("reservado_hasta")):
            if self._fecha(existente.get("reservado_hasta")) > ahora:
                return EN_USO, None

        if existente:
            actualizado = (
                cliente.table("pdf_usos")
                .update(
                    {
                        "token": token,
                        "estado": "reservado",
                        "reservado_hasta": reservado_hasta.isoformat(),
                        "ci": None,
                        "ru": None,
                        "updated_at": ahora.isoformat(),
                    }
                )
                .eq("convocatoria_id", convocatoria_id)
                .eq("hash_sha256", hash_sha256)
                .eq("token", existente["token"])
                .execute()
                .data
            )
            if actualizado:
                return RESERVADO, token
        return EN_USO, None

    def _reservar_local(
        self,
        hash_sha256: str,
        token: str,
        convocatoria_id: str,
        ahora: datetime,
        reservado_hasta: datetime,
    ) -> tuple[str, str | None]:
        with self._lock:
            filas = self._cargar_local()
            existente = next(
                (
                    fila
                    for fila in filas
                    if fila.get("convocatoria_id") == convocatoria_id
                    and fila.get("hash_sha256") == hash_sha256
                ),
                None,
            )
            if existente and existente.get("estado") == "registrado":
                return REGISTRADO, None
            if existente:
                fin = self._fecha(existente.get("reservado_hasta"))
                if fin and fin > ahora:
                    return EN_USO, None
                existente.update(
                    token=token,
                    estado="reservado",
                    reservado_hasta=reservado_hasta.isoformat(),
                    ci=None,
                    ru=None,
                    updated_at=ahora.isoformat(),
                )
            else:
                filas.append(
                    {
                        "convocatoria_id": convocatoria_id,
                        "hash_sha256": hash_sha256,
                        "token": token,
                        "estado": "reservado",
                        "reservado_hasta": reservado_hasta.isoformat(),
                        "ci": None,
                        "ru": None,
                        "created_at": ahora.isoformat(),
                        "updated_at": ahora.isoformat(),
                    }
                )
            self._guardar_local(filas)
            return RESERVADO, token

    def asociar_identidad(self, token: str, convocatoria_id: str, ci: str, ru: str) -> str:
        ci_normalizado = self._normalizar_identificador(ci)
        ru_normalizado = self._normalizar_identificador(ru)
        cliente = self.supabase
        if cliente is None:
            return self._asociar_identidad_local(token, convocatoria_id, ci_normalizado, ru_normalizado)

        try:
            actualizado = (
                cliente.table("pdf_usos")
                .update(
                    {
                        "ci": ci_normalizado or None,
                        "ru": ru_normalizado or None,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                .eq("token", token)
                .eq("convocatoria_id", convocatoria_id)
                .eq("estado", "reservado")
                .execute()
                .data
            )
            return RESERVADO if actualizado else EXPIRADO
        except Exception as error:
            if self._es_tabla_faltante(error):
                self._activar_fallback(error)
                return self._asociar_identidad_local(token, convocatoria_id, ci_normalizado, ru_normalizado)
            if not self._es_duplicado(error):
                raise

        existente = self._buscar_identidad(cliente, convocatoria_id, ci_normalizado, ru_normalizado)
        self.liberar(token)
        return REGISTRADO if existente and existente.get("estado") == "registrado" else EN_USO

    def _asociar_identidad_local(
        self,
        token: str,
        convocatoria_id: str,
        ci: str,
        ru: str,
    ) -> str:
        with self._lock:
            filas = self._cargar_local()
            actual = next((fila for fila in filas if fila.get("token") == token), None)
            if not actual or actual.get("estado") != "reservado":
                return EXPIRADO
            ahora = datetime.now(timezone.utc)
            fin = self._fecha(actual.get("reservado_hasta"))
            if not fin or fin <= ahora:
                return EXPIRADO
            otro = next(
                (
                    fila
                    for fila in filas
                    if fila is not actual
                    and fila.get("convocatoria_id") == convocatoria_id
                    and ((ci and fila.get("ci") == ci) or (ru and fila.get("ru") == ru))
                ),
                None,
            )
            if otro:
                filas.remove(actual)
                self._guardar_local(filas)
                return REGISTRADO if otro.get("estado") == "registrado" else EN_USO
            actual.update(ci=ci or None, ru=ru or None, updated_at=ahora.isoformat())
            self._guardar_local(filas)
            return RESERVADO

    def validar_reserva(self, token: str, convocatoria_id: str, ci: str, ru: str) -> str:
        cliente = self.supabase
        if cliente is None:
            return self._validar_reserva_local(token, convocatoria_id, ci, ru)
        try:
            filas = (
                cliente.table("pdf_usos")
                .select("estado,reservado_hasta,ci,ru")
                .eq("token", token)
                .eq("convocatoria_id", convocatoria_id)
                .limit(1)
                .execute()
                .data
                or []
            )
        except Exception as error:
            if self._es_tabla_faltante(error):
                self._activar_fallback(error)
                return self._validar_reserva_local(token, convocatoria_id, ci, ru)
            raise
        return self._validar_fila(filas[0] if filas else None, ci, ru)

    def _validar_reserva_local(self, token: str, convocatoria_id: str, ci: str, ru: str) -> str:
        with self._lock:
            fila = next(
                (
                    item
                    for item in self._cargar_local()
                    if item.get("token") == token
                    and item.get("convocatoria_id") == convocatoria_id
                ),
                None,
            )
            return self._validar_fila(fila, ci, ru)

    def _validar_fila(self, fila: dict | None, ci: str, ru: str) -> str:
        if not fila:
            return EXPIRADO
        if fila.get("estado") == "registrado":
            return REGISTRADO
        fin = self._fecha(fila.get("reservado_hasta"))
        if fila.get("estado") != "reservado" or not fin or fin <= datetime.now(timezone.utc):
            return EXPIRADO
        ci_guardado = self._normalizar_identificador(str(fila.get("ci") or ""))
        ru_guardado = self._normalizar_identificador(str(fila.get("ru") or ""))
        if ci_guardado != self._normalizar_identificador(ci) or ru_guardado != self._normalizar_identificador(ru):
            return INVALIDO
        return RESERVADO

    def marcar_registrado(self, token: str) -> None:
        cliente = self.supabase
        ahora = datetime.now(timezone.utc).isoformat()
        if cliente is None:
            with self._lock:
                filas = self._cargar_local()
                fila = next((item for item in filas if item.get("token") == token), None)
                if fila:
                    fila.update(estado="registrado", reservado_hasta=None, updated_at=ahora)
                    self._guardar_local(filas)
            return
        try:
            (
                cliente.table("pdf_usos")
                .update({"estado": "registrado", "reservado_hasta": None, "updated_at": ahora})
                .eq("token", token)
                .execute()
            )
        except Exception as error:
            if self._es_tabla_faltante(error):
                self._activar_fallback(error)
                self.marcar_registrado(token)
                return
            raise

    def liberar(self, token: str) -> None:
        cliente = self.supabase
        if cliente is None:
            with self._lock:
                filas = self._cargar_local()
                nuevas = [
                    fila
                    for fila in filas
                    if not (fila.get("token") == token and fila.get("estado") == "reservado")
                ]
                if len(nuevas) != len(filas):
                    self._guardar_local(nuevas)
            return
        try:
            (
                cliente.table("pdf_usos")
                .delete()
                .eq("token", token)
                .eq("estado", "reservado")
                .execute()
            )
        except Exception as error:
            if self._es_tabla_faltante(error):
                self._activar_fallback(error)
                self.liberar(token)
                return
            raise

    @staticmethod
    def _obtener_por_hash(cliente, convocatoria_id: str, hash_sha256: str) -> dict | None:
        filas = (
            cliente.table("pdf_usos")
            .select("token,estado,reservado_hasta")
            .eq("convocatoria_id", convocatoria_id)
            .eq("hash_sha256", hash_sha256)
            .limit(1)
            .execute()
            .data
            or []
        )
        return filas[0] if filas else None

    @staticmethod
    def _buscar_identidad(cliente, convocatoria_id: str, ci: str, ru: str) -> dict | None:
        for columna, valor in (("ci", ci), ("ru", ru)):
            if not valor:
                continue
            filas = (
                cliente.table("pdf_usos")
                .select("estado")
                .eq("convocatoria_id", convocatoria_id)
                .eq(columna, valor)
                .limit(1)
                .execute()
                .data
                or []
            )
            if filas:
                return filas[0]
        return None
