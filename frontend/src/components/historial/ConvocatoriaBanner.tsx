import { Convocatoria } from "@/models/admin";
import { mostrarFecha } from "@/utils/date";


export function ConvocatoriaBanner({ convocatoria }: { convocatoria: Convocatoria }) {
  return (
    <div className="convocatoria-publica open">
      <span className="status"><span className="status-dot" />CONVOCATORIA ACTUAL</span>
      <h2>{convocatoria.nombre}</h2>
      <small className="convocatoria-meta">
        Gestión {convocatoria.gestion} · {convocatoria.semestre}
      </small>
      <p>
        Inscripciones habilitadas. Vigencia: {mostrarFecha(convocatoria.inicio)} — {mostrarFecha(convocatoria.fin)}
      </p>
    </div>
  );
}
