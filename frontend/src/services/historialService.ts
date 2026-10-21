import { AdminStudentsResponse, Convocatoria, EstadoInscripciones } from "@/models/admin";
import { ResultadoAnalisis } from "@/models/historial";
import { RegistroEstudiante, RegistroEstudianteResponse } from "@/models/student";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function analizarHistorial(archivo: File): Promise<ResultadoAnalisis> {
  const formulario = new FormData();
  formulario.append("archivo", archivo);
  const respuesta = await fetch(`${API_URL}/historiales/analizar`, { method: "POST", body: formulario });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible analizar el PDF.");
  return datos as ResultadoAnalisis;
}

export async function registrarEstudiante(data: RegistroEstudiante): Promise<RegistroEstudianteResponse> {
  const respuesta = await fetch(`${API_URL}/estudiantes/registrar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible registrar los datos.");
  return datos as RegistroEstudianteResponse;
}

export async function obtenerEstadoInscripciones(): Promise<EstadoInscripciones> {
  const respuesta = await fetch(`${API_URL}/estudiantes/inscripciones/estado`, {
    cache: "no-store",
  });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible consultar las fechas.");
  return datos as EstadoInscripciones;
}

export async function iniciarSesionAdmin(usuario: string, password: string): Promise<string> {
  const respuesta = await fetch(`${API_URL}/admin/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ usuario, password }) });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible iniciar sesión.");
  return datos.token as string;
}

export async function obtenerEstudiantesAdmin(token: string): Promise<AdminStudentsResponse> {
  const respuesta = await fetch(`${API_URL}/admin/estudiantes`, { headers: { "X-Admin-Token": token } });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible cargar los registros.");
  return datos as AdminStudentsResponse;
}

export async function descargarExcelAdmin(token: string): Promise<void> {
  const url = `${API_URL}/admin/estudiantes/exportar`;
  const respuesta = await fetch(url, { headers: { "X-Admin-Token": token } });
  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => ({}));
    throw new Error(datos.detail ?? "No fue posible descargar el Excel.");
  }
  const blob = await respuesta.blob();
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(blob);
  enlace.download = "estudiantes_convocatoria.xlsx";
  enlace.click();
  URL.revokeObjectURL(enlace.href);
}

export async function descargarExcelConvocatoriaAdmin(token: string, convocatoriaId: string): Promise<void> {
  const respuesta = await fetch(`${API_URL}/admin/convocatorias/${convocatoriaId}/exportar`, {
    headers: { "X-Admin-Token": token },
  });
  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => ({}));
    throw new Error(datos.detail ?? "No fue posible descargar el Excel de la convocatoria.");
  }
  const blob = await respuesta.blob();
  const enlace = document.createElement("a");
  enlace.href = URL.createObjectURL(blob);
  enlace.download = `estudiantes_convocatoria_${convocatoriaId}.xlsx`;
  enlace.click();
  URL.revokeObjectURL(enlace.href);
}

export async function crearConvocatoriaAdmin(
  token: string,
  nombre: string,
  inicio: string,
  fin: string,
): Promise<Convocatoria> {
  const respuesta = await fetch(`${API_URL}/admin/convocatoria`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "X-Admin-Token": token },
    body: JSON.stringify({ nombre, inicio, fin }),
  });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible guardar las fechas.");
  return datos.convocatoria as Convocatoria;
}

export async function actualizarFinConvocatoriaAdmin(
  token: string,
  fin: string,
): Promise<Convocatoria> {
  const respuesta = await fetch(`${API_URL}/admin/convocatoria/fin`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", "X-Admin-Token": token },
    body: JSON.stringify({ fin }),
  });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible actualizar la fecha de cierre.");
  return datos.convocatoria as Convocatoria;
}

export async function actualizarCredencialesAdmin(token: string, usuario: string, password: string): Promise<string> {
  const respuesta = await fetch(`${API_URL}/admin/credenciales`, { method: "PUT", headers: { "Content-Type": "application/json", "X-Admin-Token": token }, body: JSON.stringify({ usuario, password }) });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible actualizar las credenciales.");
  return datos.mensaje as string;
}
