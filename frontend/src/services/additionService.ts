import { AdditionAdminResponse, EstadoAdicionInscripciones, ResultadoAdicion, SolicitudAdicion } from "@/models/addition";
import { Convocatoria } from "@/models/admin";
import { API_URL, descargarArchivo, headersAdmin, leerJson, solicitar } from "@/services/apiClient";

export async function obtenerEstadoAdicion(): Promise<EstadoAdicionInscripciones> {
  const respuesta = await solicitar(`${API_URL}/adicion/inscripciones/estado`, { cache: "no-store" });
  return leerJson(respuesta, "No fue posible consultar la convocatoria de adición.");
}

export async function analizarHistorialAdicion(archivo: File, token?: string): Promise<ResultadoAdicion> {
  const data = new FormData();
  data.append("archivo", archivo);
  const respuesta = await solicitar(`${API_URL}/adicion/historiales/analizar`, {
    method: "POST",
    body: data,
    headers: token ? { "X-PDF-Reservation": token } : undefined,
  });
  return leerJson(respuesta, "No fue posible analizar el historial.");
}

export async function registrarSolicitudAdicion(data: SolicitudAdicion) {
  const respuesta = await solicitar(`${API_URL}/adicion/solicitudes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return leerJson<{ registrado: boolean; duplicado: boolean; mensaje: string }>(respuesta, "No fue posible registrar la solicitud.");
}

export async function liberarReservaAdicion(token?: string) {
  if (!token) return;
  await solicitar(`${API_URL}/adicion/historiales/reserva/${encodeURIComponent(token)}`, { method: "DELETE" }).catch(() => undefined);
}

export async function obtenerAdminAdicion(token: string): Promise<AdditionAdminResponse> {
  const respuesta = await solicitar(`${API_URL}/admin/adicion/resumen`, { headers: headersAdmin(token) });
  return leerJson(respuesta, "No fue posible cargar el panel de adición.");
}

export async function crearConvocatoriaAdicion(token: string, data: { nombre: string; gestion: number; semestre: string; inicio: string; fin: string }): Promise<Convocatoria> {
  const respuesta = await solicitar(`${API_URL}/admin/adicion/convocatoria`, {
    method: "PUT", headers: headersAdmin(token, true), body: JSON.stringify(data),
  });
  return (await leerJson<{ convocatoria: Convocatoria }>(respuesta, "No fue posible crear la convocatoria.")).convocatoria;
}

export async function actualizarFinAdicion(token: string, fin: string): Promise<Convocatoria> {
  const respuesta = await solicitar(`${API_URL}/admin/adicion/convocatoria/fin`, {
    method: "PATCH", headers: headersAdmin(token, true), body: JSON.stringify({ fin }),
  });
  return (await leerJson<{ convocatoria: Convocatoria }>(respuesta, "No fue posible actualizar la fecha.")).convocatoria;
}

export async function actualizarPromedioAdicion(token: string, promedio_minimo: number): Promise<number> {
  const respuesta = await solicitar(`${API_URL}/admin/adicion/configuracion`, {
    method: "PUT", headers: headersAdmin(token, true), body: JSON.stringify({ promedio_minimo }),
  });
  return (await leerJson<{ promedio_minimo: number }>(respuesta, "No fue posible actualizar el promedio.")).promedio_minimo;
}

export async function descargarExcelSolicitudesAdicion(token: string) {
  await descargarArchivo(
    "/admin/adicion/exportar",
    token,
    "solicitudes_adicion_convocatoria_actual.xlsx",
    "No fue posible descargar el Excel de solicitudes.",
  );
}

export async function descargarWordSolicitudesAdicion(token: string) {
  await descargarArchivo(
    "/admin/adicion/exportar-word",
    token,
    "solicitudes_adicion_convocatoria_actual.docx",
    "No fue posible descargar el Word de solicitudes.",
  );
}

export async function descargarPdfSolicitudesAdicion(token: string) {
  await descargarArchivo(
    "/admin/adicion/exportar-pdf",
    token,
    "solicitudes_adicion_convocatoria_actual.pdf",
    "No fue posible descargar el PDF de solicitudes.",
  );
}

export async function descargarExcelConvocatoriaAdicion(token: string, convocatoriaId: string) {
  await descargarArchivo(
    `/admin/adicion/convocatorias/${encodeURIComponent(convocatoriaId)}/exportar`,
    token,
    `solicitudes_adicion_${convocatoriaId}.xlsx`,
    "No fue posible descargar el Excel de la convocatoria.",
  );
}

export async function descargarWordConvocatoriaAdicion(token: string, convocatoriaId: string) {
  await descargarArchivo(
    `/admin/adicion/convocatorias/${encodeURIComponent(convocatoriaId)}/exportar-word`,
    token,
    `solicitudes_adicion_${convocatoriaId}.docx`,
    "No fue posible descargar el Word de la convocatoria.",
  );
}

export async function descargarPdfConvocatoriaAdicion(token: string, convocatoriaId: string) {
  await descargarArchivo(
    `/admin/adicion/convocatorias/${encodeURIComponent(convocatoriaId)}/exportar-pdf`,
    token,
    `solicitudes_adicion_${convocatoriaId}.pdf`,
    "No fue posible descargar el PDF de la convocatoria.",
  );
}
