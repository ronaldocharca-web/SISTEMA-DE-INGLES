import { ResultadoAnalisis } from "../models/historial";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export async function analizarHistorial(archivo: File): Promise<ResultadoAnalisis> {
  const formulario = new FormData();
  formulario.append("archivo", archivo);
  const respuesta = await fetch(`${API_URL}/historiales/analizar`, { method: "POST", body: formulario });
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.detail ?? "No fue posible analizar el PDF.");
  return datos as ResultadoAnalisis;
}
