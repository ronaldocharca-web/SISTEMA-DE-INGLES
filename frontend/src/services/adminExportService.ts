import { descargarArchivo } from "@/services/apiClient";


export function descargarExcelAdmin(token: string): Promise<void> {
  return descargarArchivo("/admin/estudiantes/exportar", token, "estudiantes_convocatoria.xlsx", "No fue posible descargar el Excel.");
}

export function descargarWordAdmin(token: string): Promise<void> {
  return descargarArchivo("/admin/estudiantes/exportar-word", token, "examen_clasificacion_ingles.docx", "No fue posible descargar el Word.");
}

export function descargarPdfAdmin(token: string): Promise<void> {
  return descargarArchivo("/admin/estudiantes/exportar-pdf", token, "examen_clasificacion_ingles.pdf", "No fue posible descargar el PDF.");
}

export function descargarExcelConvocatoriaAdmin(token: string, convocatoriaId: string): Promise<void> {
  return descargarArchivo(`/admin/convocatorias/${convocatoriaId}/exportar`, token, `estudiantes_convocatoria_${convocatoriaId}.xlsx`, "No fue posible descargar el Excel de la convocatoria.");
}

export function descargarWordConvocatoriaAdmin(token: string, convocatoriaId: string): Promise<void> {
  return descargarArchivo(`/admin/convocatorias/${convocatoriaId}/exportar-word`, token, `examen_clasificacion_ingles_${convocatoriaId}.docx`, "No fue posible descargar el Word de la convocatoria.");
}

export function descargarPdfConvocatoriaAdmin(token: string, convocatoriaId: string): Promise<void> {
  return descargarArchivo(`/admin/convocatorias/${convocatoriaId}/exportar-pdf`, token, `examen_clasificacion_ingles_${convocatoriaId}.pdf`, "No fue posible descargar el PDF de la convocatoria.");
}
