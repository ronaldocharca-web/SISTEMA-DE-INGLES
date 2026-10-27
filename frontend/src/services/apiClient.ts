export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type ErrorDetail = string | Array<{ msg?: string }>;

function mensajeError(detail: ErrorDetail | undefined, fallback: string): string {
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg ?? "Dato inválido").join(" ");
  }
  return detail ?? fallback;
}

export async function solicitar(
  entrada: RequestInfo | URL,
  opciones?: RequestInit,
): Promise<Response> {
  try {
    return await fetch(entrada, opciones);
  } catch {
    throw new Error("No se pudo conectar con el servidor. Verifica que el backend esté encendido.");
  }
}

export async function leerJson<T>(respuesta: Response, fallback: string): Promise<T> {
  const datos = await respuesta.json().catch(() => ({})) as { detail?: ErrorDetail };
  if (!respuesta.ok) throw new Error(mensajeError(datos.detail, fallback));
  return datos as T;
}

export function headersAdmin(token: string, json = false): HeadersInit {
  return {
    "X-Admin-Token": token,
    ...(json ? { "Content-Type": "application/json" } : {}),
  };
}

export async function descargarArchivo(
  ruta: string,
  token: string,
  nombre: string,
  fallback: string,
): Promise<void> {
  const respuesta = await solicitar(`${API_URL}${ruta}`, {
    headers: headersAdmin(token),
  });
  if (!respuesta.ok) {
    await leerJson(respuesta, fallback);
    return;
  }
  const url = URL.createObjectURL(await respuesta.blob());
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombre;
  enlace.click();
  URL.revokeObjectURL(url);
}
