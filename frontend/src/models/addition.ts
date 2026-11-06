import { AdminIncident, Convocatoria } from "@/models/admin";
import { Materia } from "@/models/historial";

export type EstadoAdicion = "PUEDE_SOLICITAR" | "NO_PUEDE_SOLICITAR" | "REQUIERE_REVISION" | "YA_SOLICITO" | "PDF_NO_VALIDO";

export type ResultadoAdicion = {
  estado: EstadoAdicion;
  mensaje: string;
  motivos: string[];
  ci: string;
  nombre: string;
  ru: string;
  archivo: string;
  promedio: number;
  promedio_minimo: number;
  materias_detectadas: number;
  materias_observadas: Materia[];
  advertencias: string[];
  pdf_token?: string;
};

export type EstadoAdicionInscripciones = {
  habilitada: boolean;
  mensaje: string;
  convocatoria: Convocatoria | null;
  promedio_minimo: number;
};

export type SolicitudAdicion = {
  nombre: string;
  ci: string;
  ru: string;
  correo: string;
  celular: string;
  sigla_materia: string;
  nombre_materia: string;
  semestre_materia: number;
  numero_materia_total: number;
  pdf_token: string;
};

export type AdminAdditionRequest = {
  Fecha: string;
  Nombre: string;
  CI: string;
  RU: string;
  Correo: string;
  Celular: string;
  Sigla: string;
  "Nombre de materia": string;
  "Semestre de materia": string;
  "Carga total": string;
  Promedio: string;
};

export type AdditionClosedCall = Convocatoria & {
  created_at: string;
  total: number;
  solicitudes: AdminAdditionRequest[];
};

export type AdditionAdminResponse = {
  total: number;
  solicitudes: AdminAdditionRequest[];
  incidencias: AdminIncident[];
  convocatoria: Convocatoria | null;
  convocatorias_cerradas: AdditionClosedCall[];
  promedio_minimo: number;
};
