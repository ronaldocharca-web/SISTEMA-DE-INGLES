-- Conserva los datos anteriores; las nuevas solicitudes ya no piden semestre.
alter table public.solicitudes_adicion alter column semestre_materia drop not null;
