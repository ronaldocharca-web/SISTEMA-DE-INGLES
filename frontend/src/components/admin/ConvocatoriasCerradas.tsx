import { useState } from "react";

import { ConvocatoriaCerrada } from "@/models/admin";
import { descargarExcelConvocatoriaAdmin } from "@/services/historialService";

type Props = { convocatorias: ConvocatoriaCerrada[]; token: string };

function mostrarFecha(fecha: string): string {
  return new Intl.DateTimeFormat("es-BO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(fecha));
}

export function ConvocatoriasCerradas({ convocatorias, token }: Props) {
  const [descargando, setDescargando] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function descargar(id: string) {
    setDescargando(id);
    setError("");
    try {
      await descargarExcelConvocatoriaAdmin(token, id);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible descargar el Excel.");
    } finally {
      setDescargando(null);
    }
  }

  return (
    <section className="closed-calls">
      <h3>Convocatorias cerradas</h3>
      {error && <div className="alert error">{error}</div>}
      {convocatorias.length === 0 ? (
        <p className="hint">Todavía no hay convocatorias anteriores.</p>
      ) : convocatorias.map((convocatoria) => (
        <details className="closed-call" key={convocatoria.id}>
          <summary>
            <span><strong>{convocatoria.nombre}</strong><small>{mostrarFecha(convocatoria.inicio)} — {mostrarFecha(convocatoria.fin)}</small></span>
            <span className="closed-call-actions"><b>{convocatoria.total} estudiante{convocatoria.total === 1 ? "" : "s"}</b><button type="button" className="secondary" onClick={(event) => { event.preventDefault(); void descargar(convocatoria.id); }} disabled={descargando === convocatoria.id}>{descargando === convocatoria.id ? "Generando..." : "Descargar Excel"}</button></span>
          </summary>
          {convocatoria.estudiantes.length === 0 ? (
            <p className="hint">No hubo estudiantes registrados en esta convocatoria.</p>
          ) : (
            <div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Nombre</th><th>CI</th><th>RU</th><th>Correo</th><th>Celular</th></tr></thead><tbody>
              {convocatoria.estudiantes.map((estudiante) => <tr key={`${convocatoria.id}-${estudiante.CI}-${estudiante.RU}`}><td>{estudiante.Fecha}</td><td>{estudiante.Nombre}</td><td>{estudiante.CI}</td><td>{estudiante.RU}</td><td>{estudiante.Correo}</td><td>{estudiante.Celular}</td></tr>)}
            </tbody></table></div>
          )}
        </details>
      ))}
    </section>
  );
}
