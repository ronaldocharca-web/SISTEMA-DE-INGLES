import { EstadoInscripciones } from "@/models/admin";
import { ResultadoAnalisis } from "@/models/historial";
import { RegistroEstudiante, RegistroEstudianteResponse } from "@/models/student";
import { API_URL, leerJson, solicitar } from "@/services/apiClient";


export async function analizarHistorial(archivo: File): Promise<ResultadoAnalisis> {
  const formulario = new FormData();
  formulario.append("archivo", archivo);
  const respuesta = await solicitar(`${API_URL}/historiales/analizar`, {
    method: "POST",
    body: formulario,
  });
  return leerJson<ResultadoAnalisis>(respuesta, "No fue posible analizar el PDF.");
}

export async function registrarEstudiante(
  data: RegistroEstudiante,
): Promise<RegistroEstudianteResponse> {
  const respuesta = await solicitar(`${API_URL}/estudiantes/registrar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return leerJson<RegistroEstudianteResponse>(respuesta, "No fue posible registrar los datos.");
}

export async function liberarReservaPdf(token?: string): Promise<void> {
  if (!token) return;
  await solicitar(`${API_URL}/historiales/reserva/${encodeURIComponent(token)}`, {
    method: "DELETE",
  }).catch(() => undefined);
}

export async function obtenerEstadoInscripciones(): Promise<EstadoInscripciones> {
  const respuesta = await solicitar(`${API_URL}/estudiantes/inscripciones/estado`, {
    cache: "no-store",
  });
  return leerJson<EstadoInscripciones>(respuesta, "No fue posible consultar las fechas.");
}
