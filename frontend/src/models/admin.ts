export type AdminStudent = {
  Fecha: string;
  Nombre: string;
  CI: string;
  RU: string;
  Correo: string;
  Celular: string;
};

export type AdminStudentsResponse = {
  total: number;
  estudiantes: AdminStudent[];
  incidencias: AdminIncident[];
  convocatoria: Convocatoria | null;
  convocatorias_cerradas: ConvocatoriaCerrada[];
};

export type Convocatoria = {
  id: string;
  nombre: string;
  gestion: number;
  semestre: "Primer semestre" | "Segundo semestre";
  inicio: string;
  fin: string;
  activa: boolean;
  abierta: boolean;
};

export type ConvocatoriaCerrada = Convocatoria & {
  created_at: string;
  total: number;
  estudiantes: AdminStudent[];
};

export type EstadoInscripciones = {
  habilitada: boolean;
  mensaje: string;
  convocatoria: Convocatoria | null;
};

export type AdminIncident = {
  Fecha: string;
  Nombre: string;
  CI: string;
  RU: string;
  Archivo: string;
  Motivo: string;
};
