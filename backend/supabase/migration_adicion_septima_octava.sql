-- Limita las nuevas solicitudes de adición a la séptima u octava materia.
-- NOT VALID conserva solicitudes históricas que hayan registrado una sexta materia,
-- pero la nueva regla se aplica inmediatamente a cada inserción o actualización.
alter table public.solicitudes_adicion
  drop constraint if exists solicitudes_adicion_numero_materia_total_check;

alter table public.solicitudes_adicion
  add constraint solicitudes_adicion_numero_materia_total_check
  check (numero_materia_total between 7 and 8) not valid;
