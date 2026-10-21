from fastapi import Header, HTTPException

from app.services.admin_service import AdminService


admin_service = AdminService()


def exigir_admin(x_admin_token: str | None = Header(default=None)) -> str:
    """Valida la sesión administrativa y devuelve el token recibido."""
    if not admin_service.token_valido(x_admin_token):
        raise HTTPException(status_code=401, detail="Sesión administrativa no válida.")
    return x_admin_token
