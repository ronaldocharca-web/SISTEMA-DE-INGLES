-- Ejecutar una sola vez en Supabase para actualizar instalaciones existentes.

alter table public.convocatorias add column if not exists gestion integer;
alter table public.convocatorias add column if not exists semestre text;

update public.convocatorias
set gestion = coalesce(gestion, extract(year from inicio)::integer),
    semestre = coalesce(semestre, 'Segundo semestre');

alter table public.convocatorias alter column gestion set default 2026;
alter table public.convocatorias alter column gestion set not null;
alter table public.convocatorias alter column semestre set default 'Segundo semestre';
alter table public.convocatorias alter column semestre set not null;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conname = 'convocatoria_semestre_valido'
  ) then
    alter table public.convocatorias
      add constraint convocatoria_semestre_valido
      check (semestre in ('Primer semestre', 'Segundo semestre'));
  end if;
end $$;

drop function if exists public.create_exam_convocatoria(text, timestamptz, timestamptz);

create or replace function public.create_exam_convocatoria(
  p_nombre text,
  p_gestion integer,
  p_semestre text,
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
  if p_gestion < 2000 or p_gestion > 2100 then
    raise exception 'La gestión no es válida.';
  end if;
  if p_semestre not in ('Primer semestre', 'Segundo semestre') then
    raise exception 'El semestre no es válido.';
  end if;

  update public.convocatorias set activa = false where activa = true;
  insert into public.convocatorias (nombre, gestion, semestre, inicio, fin, activa)
  values (trim(p_nombre), p_gestion, p_semestre, p_inicio, p_fin, true)
  returning * into nueva;

  return next nueva;
end;
$$;

revoke all on function public.create_exam_convocatoria(text, integer, text, timestamptz, timestamptz) from public;
revoke all on function public.create_exam_convocatoria(text, integer, text, timestamptz, timestamptz) from anon;
revoke all on function public.create_exam_convocatoria(text, integer, text, timestamptz, timestamptz) from authenticated;
grant execute on function public.create_exam_convocatoria(text, integer, text, timestamptz, timestamptz) to service_role;
