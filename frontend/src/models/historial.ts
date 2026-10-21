export type Estado = "PUEDE_TOMAR" | "NO_PUEDE_TOMAR" | "REQUIERE_REVISION" | "YA_INSCRITO" | "PDF_NO_VALIDO";
export type Materia = { sigla: string; materia: string; nota: number; observacion: string; gestion: string; periodo: string };
export type ResultadoAnalisis = { estado: Estado; mensaje: string; ci: string; nombre: string; ru: string; archivo: string; materias_requisito: Materia[]; codigos_buscados: string[]; materias_detectadas: number; advertencias: string[] };
