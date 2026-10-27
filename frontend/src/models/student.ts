export type RegistroEstudiante = {
  nombre: string;
  ci: string;
  ru: string;
  correo: string;
  celular: string;
  pdf_token: string;
};

export type RegistroEstudianteResponse = {
  registrado: boolean;
  duplicado: boolean;
  mensaje: string;
};
