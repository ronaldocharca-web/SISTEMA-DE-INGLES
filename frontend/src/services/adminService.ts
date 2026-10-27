import { AdminStudentsResponse, Convocatoria } from "@/models/admin";
import { API_URL, headersAdmin, leerJson, solicitar } from "@/services/apiClient";


export async function iniciarSesionAdmin(usuario: string, password: string): Promise<string> {
  const respuesta = await solicitar(`${API_URL}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ usuario, password }),
  });
  const datos = await leerJson<{ token: string }>(respuesta, "No fue posible iniciar sesión.");
  return datos.token;
}

export async function obtenerEstudiantesAdmin(token: string): Promise<AdminStudentsResponse> {
  const respuesta = await solicitar(`${API_URL}/admin/estudiantes`, {
    headers: headersAdmin(token),
  });
  return leerJson<AdminStudentsResponse>(respuesta, "No fue posible cargar los registros.");
}

export async function crearConvocatoriaAdmin(
  token: string,
  nombre: string,
  gestion: number,
  semestre: "Primer semestre" | "Segundo semestre",
  inicio: string,
  fin: string,
): Promise<Convocatoria> {
  const respuesta = await solicitar(`${API_URL}/admin/convocatoria`, {
    method: "PUT",
    headers: headersAdmin(token, true),
    body: JSON.stringify({ nombre, gestion, semestre, inicio, fin }),
  });
  const datos = await leerJson<{ convocatoria: Convocatoria }>(respuesta, "No fue posible guardar las fechas.");
  return datos.convocatoria;
}

export async function actualizarFinConvocatoriaAdmin(
  token: string,
  fin: string,
): Promise<Convocatoria> {
  const respuesta = await solicitar(`${API_URL}/admin/convocatoria/fin`, {
    method: "PATCH",
    headers: headersAdmin(token, true),
    body: JSON.stringify({ fin }),
  });
  const datos = await leerJson<{ convocatoria: Convocatoria }>(respuesta, "No fue posible actualizar la fecha de cierre.");
  return datos.convocatoria;
}

export async function actualizarCredencialesAdmin(
  token: string,
  usuario: string,
  password: string,
): Promise<string> {
  const respuesta = await solicitar(`${API_URL}/admin/credenciales`, {
    method: "PUT",
    headers: headersAdmin(token, true),
    body: JSON.stringify({ usuario, password }),
  });
  const datos = await leerJson<{ mensaje: string }>(respuesta, "No fue posible actualizar las credenciales.");
  return datos.mensaje;
}
