# Pruebas automáticas

Estas pruebas no crean estudiantes, no cambian convocatorias y no escriben en
Supabase. Validan la lógica local del sistema.

Desde la carpeta `backend` ejecuta:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Cobertura actual:

- Validación de datos del formulario.
- Detección de CI y RU en formatos frecuentes.
- Prevención de confundir una sigla como `TUR-401` con un RU.
- Reglas de detección de materias de inglés.
- Estados del análisis: PDF inválido, ya inscrito, no habilitado y habilitado.
- Rutas básicas de salud y validación de archivos de la API.
- Detección de varios historiales dentro de un mismo PDF.
- Bloqueo del mismo PDF mientras está en uso y después de registrarse.

## Prueba de carga local

Con el backend iniciado, esta prueba consulta solo el estado de inscripción:
no registra personas ni cambia información.

```powershell
.\.venv\Scripts\python.exe tests\benchmark_estado.py --solicitudes 100 --concurrencia 10
```

No uses este script contra producción sin coordinarlo, porque consume consultas
de Supabase.

