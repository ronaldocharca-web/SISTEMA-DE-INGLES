-- Ejecutar una sola vez en Supabase SQL Editor.
-- Agrega el bloqueo contra el uso simultáneo o repetido de un PDF.

create table if not exists public.pdf_usos (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  convocatoria_id uuid not null references public.convocatorias(id) on delete cascade,
  hash_sha256 text not null check (length(hash_sha256) = 64),
  token uuid not null unique,
  estado text not null default 'reservado'
    check (estado in ('reservado', 'registrado')),
  reservado_hasta timestamptz,
  ci text,
  ru text,
  unique (convocatoria_id, hash_sha256)
);

create unique index if not exists pdf_usos_convocatoria_ci_unique
  on public.pdf_usos (convocatoria_id, ci)
  where ci is not null and ci <> '';

create unique index if not exists pdf_usos_convocatoria_ru_unique
  on public.pdf_usos (convocatoria_id, ru)
  where ru is not null and ru <> '';

alter table public.pdf_usos enable row level security;
grant all on public.pdf_usos to service_role;
