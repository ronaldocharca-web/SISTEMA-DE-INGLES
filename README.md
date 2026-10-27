# Sistema de verificación de exámenes de inglés

Sistema para la carrera de Turismo que permite verificar, a partir del historial académico de un estudiante, si ya cursó o aprobó materias o niveles de inglés.

> **Estado actual:** el proyecto cuenta con un backend FastAPI y un frontend Next.js para analizar el historial académico directamente desde la aplicación.

## Objetivo funcional

El usuario debe poder:

1. Subir su historial académico en formato PDF.
2. Esperar a que el sistema extraiga las materias del documento.
3. Revisar si el historial contiene materias o niveles de inglés.
4. Recibir un resultado claro sobre si puede o no tomar el examen de inglés.

La decisión final debe basarse en reglas configurables de la carrera de Turismo. El sistema no debe decidir solamente por una palabra aislada: debe revisar siglas, nombres de materias, observaciones y, cuando corresponda, la nota obtenida.

## Arquitectura general

El sistema estará dividido en dos aplicaciones independientes:

```text
SISTEMA_de_INGLES/
├── frontend/                         # Next.js, patrón MVC
│   ├── public/                       # Imágenes y archivos públicos
│   ├── app/                          # App Router, layout y estilos globales
│   ├── src/
│   │   ├── components/               # Componentes y coordinadores reutilizables
│   │   │   ├── admin/
│   │   │   └── flows/
│   │   ├── controllers/              # Estado y acciones de la interfaz
│   │   ├── models/                   # Tipos TypeScript
│   │   ├── screens/                  # Una pantalla por archivo
│   │   │   ├── admin/
│   │   │   └── historial/
│   │   └── services/                 # Cliente HTTP de FastAPI
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                          # FastAPI, arquitectura por capas
│   ├── app/
│   │   ├── api/                      # Capa de presentación HTTP
│   │   │   ├── routes/               # Rutas admin, estudiantes e historiales
│   │   │   ├── dependencies.py       # Validación de sesión administrativa
│   │   │   └── router.py             # Router principal de la API
│   │   ├── services/                 # Capa de negocio
│   │   ├── repositories/             # Capa de datos: Supabase/Excel/reglas
│   │   ├── infrastructure/           # Clientes externos, como Supabase
│   │   ├── schemas/                  # Modelos Pydantic
│   │   └── main.py                   # Punto de entrada de FastAPI
│   ├── supabase/                     # Esquema SQL
│   └── requirements.txt
│
└── README.md
```

La estructura está inspirada en la separación mostrada en la referencia, pero
adaptada a las convenciones reales de Next.js y FastAPI. No se añadieron
carpetas propias de React/Vite o Express que estos frameworks no necesitan.

## Frontend: Next.js con MVC

El frontend usará Next.js y separará las responsabilidades así:

- **Model:** tipos TypeScript, por ejemplo `Historial`, `Materia`, `ResultadoEvaluacion` y `ReglaIngles`.
- **View:** páginas y componentes React que muestran el formulario de carga, el progreso, las materias detectadas y el resultado.
- **Controller:** acciones que reciben eventos del usuario, validan el archivo y llaman al servicio HTTP del backend.
- **Service:** módulo que encapsula las peticiones a la API de FastAPI.

La vista no debe analizar el PDF ni contener reglas de negocio. Solo debe presentar el resultado que entrega el backend.

## Backend: FastAPI con tres capas

### 1. Capa de presentación

Responsabilidades:

- Recibir el PDF mediante una ruta HTTP.
- Validar extensión, tipo MIME y tamaño.
- Devolver respuestas JSON claras.
- No incluir reglas de aprobación dentro de las rutas.

### 2. Capa de negocio

Responsabilidades:

- Extraer el texto del PDF.
- Convertir las líneas del historial en materias estructuradas.
- Normalizar nombres, siglas y observaciones.
- Detectar materias relacionadas con inglés.
- Aplicar las reglas académicas de Turismo.
- Generar el resultado: `puede tomar`, `no puede tomar` o `requiere revisión`.

### 3. Capa de datos

Responsabilidades:

- Guardar temporalmente el PDF durante el análisis.
- Consultar reglas configuradas y, posteriormente, una base de datos si se incorpora.
- Persistir auditoría únicamente si el proyecto lo requiere.

La extracción actual con `pdfplumber` pertenece a la capa de negocio. El guardado y lectura de archivos no deben quedar mezclados con las rutas de FastAPI.

## Flujo principal

```text
Usuario
  │
  ▼
Frontend Next.js
  │  Sube historial.pdf
  ▼
API FastAPI: POST /api/v1/historiales/analizar
  │
  ├── Validar PDF
  ├── Extraer texto con pdfplumber
  ├── Identificar materias, notas y observaciones
  ├── Buscar niveles o materias de inglés
  ├── Aplicar reglas de Turismo
  ▼
Respuesta JSON
  │
  ▼
Frontend muestra el resultado y el detalle encontrado
```

## Resultado esperado de la API

Ejemplo de respuesta:

```json
{
  "estado": "NO_PUEDE_TOMAR",
  "mensaje": "El historial registra una materia de inglés aprobada.",
  "ci": "1234567",
  "materias_ingles": [
    {
      "sigla": "ING-101",
      "materia": "Inglés I",
      "nota": 78,
      "observacion": "APROBADO",
      "gestion": "2023",
      "periodo": "SEGUNDO"
    }
  ],
  "advertencias": []
}
```

Estados recomendados:

- `PUEDE_TOMAR`: no se encontró ningún nivel o materia de inglés que impida rendir el examen.
- `NO_PUEDE_TOMAR`: se encontró una materia o nivel aprobado que impide rendirlo.
- `REQUIERE_REVISION`: el PDF no pudo leerse completamente o contiene información ambigua.

## Reglas iniciales de detección

La implementación deberá permitir configurar:

- Siglas de materias de inglés, por ejemplo `ING-101`.
- Palabras del nombre, por ejemplo `INGLES`, `INGLÉS`, `ENGLISH`.
- Niveles: `I`, `II`, `III`, `1`, `2`, `3`.
- Observaciones válidas: `APROBADO`, `REPROBADO`, `ABANDONADO`.
- Nota mínima aprobatoria, si la carrera utiliza una regla numérica.

Estas reglas deben estar en configuración o en una tabla, no escritas directamente en el componente del frontend.

## Dependencias del backend

```text
fastapi
uvicorn[standard]
python-multipart
pdfplumber
pandas
pydantic-settings
openpyxl
supabase
python-dotenv
```

## Despliegue en Vercel

El proyecto se publica como **dos proyectos de Vercel** desde el mismo
repositorio: uno para `backend/` (FastAPI) y otro para `frontend/` (Next.js).

1. Sube este proyecto a un repositorio privado de GitHub. No incluyas
   `backend/.env` ni `frontend/.env.local`.
2. En Vercel, crea un proyecto importando el repositorio y configura el
   **Root Directory** como `backend`.
3. En el proyecto del backend agrega estas variables de entorno:

   ```ini
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
   SUPABASE_SECRET_KEY=sb_secret_...
   CORS_ORIGINS=https://tu-frontend.vercel.app
   ```

   La entrada `backend/index.py` permite que Vercel reconozca la aplicación
   FastAPI.
4. Despliega el backend y copia su URL pública, por ejemplo:
   `https://sistema-ingles-api.vercel.app`.
5. Crea un segundo proyecto en Vercel desde el mismo repositorio, esta vez con
   **Root Directory** igual a `frontend`.
6. En el proyecto del frontend crea esta variable de entorno:

   ```ini
   NEXT_PUBLIC_API_URL=https://sistema-ingles-api.vercel.app/api/v1
   ```

7. Despliega el frontend. Finalmente actualiza `CORS_ORIGINS` del backend con
   la URL final del frontend y vuelve a desplegar el backend.

Nunca publiques las claves `SUPABASE_SECRET_KEY`, `ADMIN_TOKEN` ni contraseñas
en GitHub o en variables que comiencen con `NEXT_PUBLIC_`.

El frontend utilizará Next.js, React y TypeScript.

## Consideraciones importantes

- Los historiales pueden tener formatos distintos; por eso se debe guardar el texto original o un registro de diagnóstico cuando el análisis falle.
- Los PDF escaneados como imagen necesitan OCR; `pdfplumber` por sí solo no extrae texto de imágenes.
- Los archivos con datos personales deben procesarse de forma temporal y eliminarse después del análisis.
- La API debe limitar el tamaño del archivo y aceptar únicamente PDF.
- La interfaz debe mostrar una advertencia cuando el documento no tenga texto seleccionable.
- Cada PDF válido se reserva durante 20 minutos mientras el estudiante completa
  el formulario. Su huella SHA-256, no el archivo, impide usarlo al mismo tiempo
  desde otro equipo o volver a usarlo después del registro.
- Para habilitar ese bloqueo compartido en Supabase, ejecuta
  `backend/supabase/migration_pdf_usos.sql` en el SQL Editor.
- Antes de publicar el sistema, se deben probar historiales reales anonimizados con materias aprobadas, reprobadas, abandonadas y sin inglés.

## Próximos pasos

1. Definir oficialmente las reglas de la carrera de Turismo.
2. Agregar pruebas automatizadas con varios historiales anonimizados.
3. Configurar los dominios permitidos por CORS para producción.
4. Preparar el despliegue separado: frontend en Vercel y backend en un servicio compatible con FastAPI.

## Ejecutar la primera versión funcional

### Backend

Desde la carpeta raíz:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

El backend quedará disponible en `http://localhost:8000`. La documentación interactiva está en `http://localhost:8000/docs`.

### Frontend

En otra ventana de PowerShell:

```powershell
cd frontend
copy .env.local.example .env.local
npm install
npm run dev
```

Abre `http://localhost:3000`, selecciona un PDF y pulsa **Analizar historial**.

La evaluación busca los códigos del cuadro de convalidación de la imagen proporcionada: `TUR 401`, `TUR 402`, `TUR 403`, `TUR 404`, `TUR 3001`, `TUR 3002`, `TUR 3003` y `TUR 3004`. Si encuentra alguno, muestra la pantalla de incumplimiento; si no encuentra ninguno, muestra el formulario de datos del estudiante. Esta regla debe confirmarse con la normativa oficial antes de usar el sistema oficialmente.

## Registro de estudiantes en Excel

Cuando el estudiante cumple los requisitos y envía el formulario, el backend crea o actualiza `backend/data/estudiantes.xlsx` con:

- Fecha y hora.
- Nombre.
- Cédula.
- RU.
- Correo.
- Celular.

El sistema revisa la cédula y el RU antes de guardar. Si alguno ya existe, no crea otra fila y muestra: `Ya llenaste el formulario. Tus datos ya están registrados.` La escritura está protegida con un bloqueo para evitar duplicados por envíos simultáneos dentro de la misma instancia del backend.

Para un despliegue con varios servidores o en Vercel, el archivo Excel local no debe ser la base de datos definitiva porque el almacenamiento local puede ser temporal y las instancias pueden ser independientes. El repositorio ya está preparado para usar Supabase como base de datos compartida. Si no existen las variables de Supabase, mantiene Excel como respaldo local para desarrollo.

## Convocatorias y fechas de inscripción

Desde el panel administrativo se puede definir el nombre de una convocatoria y
la gestión, el semestre y el intervalo exacto de inicio y finalización. La
carga del historial queda
deshabilitada fuera de ese intervalo y el backend vuelve a validar la fecha al
guardar los datos del estudiante.

La gestión acepta un año, por ejemplo `2026`, y el semestre puede ser `Primer
semestre` o `Segundo semestre`. Estos datos aparecen en el encabezado del Word
de clasificación y en la hoja `Convocatoria` del Excel descargado.

Al iniciar una nueva convocatoria, la tabla administrativa comienza vacía y el
estudiante puede volver a inscribirse para ese nuevo período. Los registros de
convocatorias anteriores no se eliminan: permanecen relacionados con su período
en Supabase. El panel muestra las convocatorias cerradas en secciones
desplegables, con sus fechas y estudiantes registrados. El botón **Descargar
datos** genera en memoria un archivo Excel con los estudiantes e incidencias de
la convocatoria actual.

## Configurar Supabase

1. Crea un proyecto en [Supabase](https://supabase.com/).
2. Entra a **SQL Editor**, abre `backend/supabase/schema.sql`, pega todo su contenido y ejecútalo.
3. Copia `backend/.env.example` como `backend/.env`:

```powershell
cd backend
Copy-Item .env.example .env
```

4. Edita `backend/.env` y reemplaza estos valores:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_tu_clave_publicable
SUPABASE_SECRET_KEY=tu_clave_secreta_del_backend
```

La `SUPABASE_SECRET_KEY` es una clave privada del servidor: no debe escribirse en el frontend, no debe subirse a GitHub y no debe compartirse en el navegador. Supabase recomienda usar las nuevas claves `publishable` y `secret`; para este backend se utiliza la clave `secret` del proyecto. Consulta la [documentación oficial de claves de Supabase](https://supabase.com/docs/guides/getting-started/api-keys).

5. Cambia también las credenciales administrativas antes de publicar:

```env
ADMIN_USER=un_usuario_seguro
ADMIN_PASSWORD=una_contraseña_larga
ADMIN_TOKEN=un_token_largo_y_aleatorio
```

6. Reinicia FastAPI:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Desde ese momento, los estudiantes e incidencias se guardarán en las tablas `estudiantes` e `incidencias` de Supabase. El panel administrativo seguirá mostrando los registros y podrá generar el Excel descargable a partir de Supabase.

### Crear el administrador en Supabase

La contraseña administrativa no se guarda en `admin_profiles`. Se guarda de forma segura en **Supabase Auth**:

1. En Supabase entra a **Authentication > Users**.
2. Crea un usuario con su correo y una contraseña segura.
3. Copia el `User UID` del usuario creado.
4. Ejecuta en **SQL Editor**:

```sql
insert into public.admin_profiles (user_id, email, nombre_usuario, rol)
values ('USER_UID_COPIADO', 'correo-del-admin@ejemplo.com', 'admin', 'admin');
```

El usuario podrá ingresar desde la aplicación usando `admin` como nombre de usuario y la contraseña creada en Supabase Auth. El backend valida el token de Supabase y además comprueba que el usuario tenga un registro activo en `admin_profiles`.

El formulario **Cambiar usuario y contraseña** también actualiza el nombre de usuario en `admin_profiles` y la contraseña mediante Supabase Auth.

La integración usa el cliente oficial de Python de Supabase y conserva Excel únicamente como fallback local. La instalación oficial se documenta en [Supabase Python](https://supabase.com/docs/reference/python/installing). La autenticación administrativa actual sigue siendo propia de la aplicación; en una siguiente etapa puede migrarse a Supabase Auth para manejar usuarios, sesiones, recuperación de contraseña y roles administrativos.

## Niveles de acceso

La aplicación tiene dos niveles:

- **Estudiante:** analiza su historial y registra sus datos una sola vez.
- **Administrativo:** inicia sesión, consulta la lista de estudiantes registrados y descarga el archivo Excel.

En producción, el usuario administrativo se gestiona con Supabase Auth y `admin_profiles`. Las variables `ADMIN_USER`, `ADMIN_PASSWORD` y `ADMIN_TOKEN` se conservan únicamente como respaldo para desarrollo cuando Supabase no está configurado.

## Protección del acceso administrativo

El inicio de sesión permite como máximo cinco contraseñas incorrectas por combinación de usuario y origen. Los primeros cuatro errores muestran cuántos intentos quedan. El quinto error bloquea nuevos intentos durante 20 minutos y responde con HTTP `429` y la cabecera `Retry-After`.

En Supabase, el estado se almacena en `admin_login_attempts` usando un hash del usuario y el origen, sin guardar la dirección IP en texto plano. La función `register_admin_login_failure` incrementa el contador de forma atómica para que el límite también funcione cuando existen varias instancias del backend. Un acceso correcto elimina el contador correspondiente.

#   S I S T E M A - D E - I N G L E S  
 
