from __future__ import annotations

import os

from supabase import Client, ClientOptions, create_client


def get_supabase_client() -> Client | None:
    url = os.getenv("SUPABASE_URL", "").strip()
    secret_key = os.getenv("SUPABASE_SECRET_KEY", "").strip()
    if not url or not secret_key:
        return None
    return create_client(
        url,
        secret_key,
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )


def get_supabase_auth_client() -> Client | None:
    """Cliente de Auth con la clave publicable, solo para iniciar sesión."""
    url = os.getenv("SUPABASE_URL", "").strip()
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if not url or not publishable_key:
        return None
    return create_client(
        url,
        publishable_key,
        options=ClientOptions(auto_refresh_token=False, persist_session=False),
    )
