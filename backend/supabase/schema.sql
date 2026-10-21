-- Ejecutar en Supabase SQL Editor.
-- La clave secreta solo debe usarse desde FastAPI; nunca desde el frontend.

create table if not exists public.convocatorias (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  nombre text not null,
  inicio timestamptz not null,
  fin timestamptz not null,
  activa boolean not null default true,
  constraint convocatoria_intervalo_valido check (fin > inicio)
);

create unique index if not exists convocatorias_una_activa
  on public.convocatorias (activa)
  where activa = true;

create table if not exists public.estudiantes (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  convocatoria_id uuid not null references public.convocatorias(id),
  nombre text not null,
  ci text not null,
  ru text not null,
  correo text not null,
  celular text not null
);

create table if not exists public.incidencias (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  convocatoria_id uuid references public.convocatorias(id),
  nombre text,
  ci text,
  ru text,
  archivo text not null,
  motivo text not null
);

-- Migración segura para proyectos que ya tenían registros antes de incorporar
-- convocatorias. Los datos anteriores quedan guardados como un período cerrado.
alter table public.estudiantes
  add column if not exists convocatoria_id uuid references public.convocatorias(id);
alter table public.incidencias
  add column if not exists convocatoria_id uuid references public.convocatorias(id);

alter table public.estudiantes drop constraint if exists estudiantes_ci_unique;
alter table public.estudiantes drop constraint if exists estudiantes_ru_unique;

do $$
declare
  legacy_id uuid;
begin
  if exists (select 1 from public.estudiantes where convocatoria_id is null)
     or exists (select 1 from public.incidencias where convocatoria_id is null) then
    insert into public.convocatorias (nombre, inicio, fin, activa)
    values (
      'Registros anteriores',
      '2000-01-01 00:00:00+00',
      '2000-01-02 00:00:00+00',
      false
    )
    returning id into legacy_id;

    update public.estudiantes
      set convocatoria_id = legacy_id
      where convocatoria_id is null;
    update public.incidencias
      set convocatoria_id = legacy_id
      where convocatoria_id is null;
  end if;
end;
$$;

alter table public.estudiantes alter column convocatoria_id set not null;

create unique index if not exists estudiantes_convocatoria_ci_unique
  on public.estudiantes (convocatoria_id, ci);
create unique index if not exists estudiantes_convocatoria_ru_unique
  on public.estudiantes (convocatoria_id, ru);

-- Cierra la convocatoria anterior y crea una nueva en una sola transacción.
create or replace function public.create_exam_convocatoria(
  p_nombre text,
  p_inicio timestamptz,
  p_fin timestamptz
)
returns setof public.convocatorias
language plpgsql
security definer
set search_path = public
as $$
declare
  nueva public.convocatorias;
begin
  if p_fin <= p_inicio then
    raise exception 'La fecha final debe ser posterior a la inicial.';
  end if;

  update public.convocatorias set activa = false where activa = true;
  insert into public.convocatorias (nombre, inicio, fin, activa)
  values (trim(p_nombre), p_inicio, p_fin, true)
  returning * into nueva;

  return next nueva;
end;
$$;

-- La contraseña vive en Supabase Auth. Esta tabla solo guarda el rol.
create table if not exists public.admin_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  email text not null unique,
  nombre_usuario text not null unique,
  rol text not null default 'admin' check (rol = 'admin'),
  activo boolean not null default true,
  created_at timestamptz not null default now()
);

-- Control persistente de intentos fallidos. login_key es un hash del
-- usuario y el origen; no almacena la dirección IP en texto plano.
create table if not exists public.admin_login_attempts (
  login_key text primary key,
  failed_attempts integer not null default 0
    check (failed_attempts between 0 and 5),
  locked_until timestamptz,
  updated_at timestamptz not null default now()
);

-- Incrementa los intentos de forma atómica, incluso con varios servidores.
create or replace function public.register_admin_login_failure(p_login_key text)
returns table(failed_attempts integer, locked_until timestamptz)
language plpgsql
security definer
set search_path = public
as $$
declare
  result_attempts integer;
  result_locked_until timestamptz;
begin
  insert into public.admin_login_attempts as attempts (
    login_key, failed_attempts, locked_until, updated_at
  )
  values (p_login_key, 1, null, now())
  on conflict (login_key) do update
  set
    failed_attempts = case
      when attempts.locked_until is not null
        and attempts.locked_until <= now() then 1
      else least(attempts.failed_attempts + 1, 5)
    end,
    locked_until = case
      when attempts.locked_until is not null
        and attempts.locked_until > now() then attempts.locked_until
      when (
        case
          when attempts.locked_until is not null
            and attempts.locked_until <= now() then 1
          else attempts.failed_attempts + 1
        end
      ) >= 5 then now() + interval '20 minutes'
      else null
    end,
    updated_at = now()
  returning attempts.failed_attempts, attempts.locked_until
  into result_attempts, result_locked_until;

  return query select result_attempts, result_locked_until;
end;
$$;

alter table public.estudiantes enable row level security;
alter table public.incidencias enable row level security;
alter table public.convocatorias enable row level security;
alter table public.admin_profiles enable row level security;
alter table public.admin_login_attempts enable row level security;

-- El backend usará una secret key en un entorno confiable y realizará
-- las comprobaciones de administrador antes de consultar estas tablas.
grant all on public.estudiantes to service_role;
grant all on public.incidencias to service_role;
grant all on public.convocatorias to service_role;
grant all on public.admin_profiles to service_role;
grant all on public.admin_login_attempts to service_role;

revoke all on function public.register_admin_login_failure(text) from public;
revoke all on function public.register_admin_login_failure(text) from anon;
revoke all on function public.register_admin_login_failure(text) from authenticated;
grant execute on function public.register_admin_login_failure(text) to service_role;

revoke all on function public.create_exam_convocatoria(text, timestamptz, timestamptz) from public;
revoke all on function public.create_exam_convocatoria(text, timestamptz, timestamptz) from anon;
revoke all on function public.create_exam_convocatoria(text, timestamptz, timestamptz) from authenticated;
grant execute on function public.create_exam_convocatoria(text, timestamptz, timestamptz) to service_role;
