from __future__ import annotations

import hashlib
import json
import math
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock

from supabase_auth.errors import AuthApiError

from app.infrastructure.supabase_client import get_supabase_auth_client, get_supabase_client
from app.schemas.admin import AdminCredentialsUpdate


MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 20


class AdminBloqueadoError(Exception):
    def __init__(self, segundos_restantes: int) -> None:
        self.segundos_restantes = min(
            MINUTOS_BLOQUEO * 60, max(1, segundos_restantes)
        )
        self.minutos_restantes = max(1, math.ceil(self.segundos_restantes / 60))
        super().__init__(
            f"Demasiados intentos fallidos. Inténtalo nuevamente en "
            f"{self.minutos_restantes} minutos."
        )


class AdminCredencialesInvalidasError(Exception):
    def __init__(self, intentos_restantes: int) -> None:
        self.intentos_restantes = max(0, intentos_restantes)
        palabra = "intento" if self.intentos_restantes == 1 else "intentos"
        super().__init__(
            "Usuario o contraseña incorrectos. "
            f"Te quedan {self.intentos_restantes} {palabra}."
        )


class AdminService:
    """Autenticación administrativa con límite persistente de intentos."""

    _lock = Lock()
    _intentos_locales: dict[str, tuple[int, datetime | None]] = {}

    def __init__(self) -> None:
        self.path = Path(__file__).resolve().parents[2] / "data" / "admin_credentials.json"
        self.usuario = os.getenv("ADMIN_USER", "admin")
        self.password = os.getenv("ADMIN_PASSWORD", "cambiar-esta-clave")
        self._cargar()
        self.token = os.getenv("ADMIN_TOKEN", secrets.token_urlsafe(32))

    @property
    def supabase(self):
        return get_supabase_client()

    @property
    def supabase_auth(self):
        return get_supabase_auth_client()

    @property
    def usa_supabase(self) -> bool:
        return self.supabase is not None and self.supabase_auth is not None

    @staticmethod
    def _clave_intento(usuario: str, origen: str) -> str:
        identificador = f"{usuario.strip().lower()}|{origen.strip().lower()}"
        return hashlib.sha256(identificador.encode("utf-8")).hexdigest()

    @staticmethod
    def _fecha(valor: str | None) -> datetime | None:
        if not valor:
            return None
        return datetime.fromisoformat(valor.replace("Z", "+00:00"))

    def _cargar(self) -> None:
        if not self.path.exists():
            return
        try:
            datos = json.loads(self.path.read_text(encoding="utf-8"))
            self.usuario = str(datos.get("usuario", self.usuario))
            self.password = str(datos.get("password", self.password))
        except (OSError, json.JSONDecodeError):
            return

    def _comprobar_bloqueo(self, clave: str) -> None:
        ahora = datetime.now(timezone.utc)
        if self.usa_supabase:
            filas = (
                self.supabase.table("admin_login_attempts")
                .select("locked_until")
                .eq("login_key", clave)
                .limit(1)
                .execute()
                .data
            )
            bloqueo = self._fecha(filas[0].get("locked_until")) if filas else None
        else:
            with self._lock:
                bloqueo = self._intentos_locales.get(clave, (0, None))[1]
        if bloqueo and bloqueo > ahora:
            raise AdminBloqueadoError(math.ceil((bloqueo - ahora).total_seconds()))

    def _registrar_fallo(self, clave: str) -> None:
        ahora = datetime.now(timezone.utc)
        if self.usa_supabase:
            resultado = (
                self.supabase.rpc(
                    "register_admin_login_failure", {"p_login_key": clave}
                )
                .execute()
                .data
            )
            fila = resultado[0] if resultado else {"failed_attempts": 1, "locked_until": None}
            intentos = int(fila["failed_attempts"])
            bloqueo = self._fecha(fila.get("locked_until"))
        else:
            with self._lock:
                intentos_anteriores, bloqueo_anterior = self._intentos_locales.get(
                    clave, (0, None)
                )
                if bloqueo_anterior and bloqueo_anterior <= ahora:
                    intentos_anteriores = 0
                    bloqueo_anterior = None
                intentos = min(intentos_anteriores + 1, MAX_INTENTOS)
                bloqueo = (
                    ahora + timedelta(minutes=MINUTOS_BLOQUEO)
                    if intentos >= MAX_INTENTOS
                    else bloqueo_anterior
                )
                self._intentos_locales[clave] = (intentos, bloqueo)
        if bloqueo and bloqueo > ahora:
            raise AdminBloqueadoError(math.ceil((bloqueo - ahora).total_seconds()))
        raise AdminCredencialesInvalidasError(MAX_INTENTOS - intentos)

    def _limpiar_intentos(self, clave: str) -> None:
        if self.usa_supabase:
            self.supabase.table("admin_login_attempts").delete().eq(
                "login_key", clave
            ).execute()
            return
        with self._lock:
            self._intentos_locales.pop(clave, None)

    def iniciar_sesion(self, usuario: str, password: str, origen: str = "unknown") -> str:
        clave = self._clave_intento(usuario, origen)
        self._comprobar_bloqueo(clave)
        token: str | None = None

        if self.usa_supabase:
            perfil = (
                self.supabase.table("admin_profiles")
                .select("user_id,email,activo")
                .eq("nombre_usuario", usuario.strip())
                .eq("activo", True)
                .limit(1)
                .execute()
                .data
            )
            if perfil:
                try:
                    sesion = self.supabase_auth.auth.sign_in_with_password(
                        {"email": perfil[0]["email"], "password": password}
                    )
                    token = sesion.session.access_token if sesion.session else None
                except AuthApiError:
                    token = None
        elif secrets.compare_digest(usuario, self.usuario) and secrets.compare_digest(
            password, self.password
        ):
            token = self.token

        if not token:
            self._registrar_fallo(clave)
        self._limpiar_intentos(clave)
        return token

    def token_valido(self, token: str | None) -> bool:
        if not token:
            return False
        if not self.usa_supabase:
            return secrets.compare_digest(token, self.token)
        try:
            usuario = self.supabase_auth.auth.get_user(token).user
            if usuario is None:
                return False
            perfil = (
                self.supabase.table("admin_profiles")
                .select("id")
                .eq("user_id", str(usuario.id))
                .eq("activo", True)
                .limit(1)
                .execute()
                .data
            )
            return bool(perfil)
        except Exception:
            return False

    def actualizar(self, credenciales: AdminCredentialsUpdate, token: str | None = None) -> None:
        if self.usa_supabase:
            if not token:
                raise ValueError("Sesión administrativa no válida.")
            usuario = self.supabase_auth.auth.get_user(token).user
            if usuario is None:
                raise ValueError("Sesión administrativa no válida.")
            with self._lock:
                self.supabase.table("admin_profiles").update(
                    {"nombre_usuario": credenciales.usuario.strip()}
                ).eq("user_id", str(usuario.id)).execute()
                self.supabase.auth.admin.update_user_by_id(
                    str(usuario.id), {"password": credenciales.password}
                )
            return

        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(credenciales.model_dump(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self.usuario = credenciales.usuario
            self.password = credenciales.password
