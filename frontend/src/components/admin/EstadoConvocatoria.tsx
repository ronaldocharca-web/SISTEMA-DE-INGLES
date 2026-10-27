"use client";

import { FormEvent, useState } from "react";

import { Convocatoria } from "@/models/admin";
import { actualizarFinConvocatoriaAdmin } from "@/services/adminService";
import { fechaParaInput, mostrarFecha } from "@/utils/date";

type Props = {
  token: string;
  convocatoria: Convocatoria | null;
  onSaved: () => Promise<void>;
};

export function EstadoConvocatoria({ token, convocatoria, onSaved }: Props) {
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  async function actualizar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!convocatoria) return;
    const fin = new Date(String(new FormData(event.currentTarget).get("fin")));
    if (fin <= new Date(convocatoria.inicio)) {
      setError("La fecha de cierre debe ser posterior al inicio de la convocatoria.");
      return;
    }
    setCargando(true);
    setMensaje("");
    setError("");
    try {
      await actualizarFinConvocatoriaAdmin(token, fin.toISOString());
      setMensaje("Fecha de cierre actualizada. Las inscripciones permanecerán habilitadas hasta ese momento.");
      await onSaved();
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible actualizar la fecha.");
    } finally {
      setCargando(false);
    }
  }

  if (!convocatoria) {
    return <div className="dashboard-section"><h3>Estado de la convocatoria</h3><p className="empty-state">No existe una convocatoria activa. Crea una desde la pestaña “Nueva convocatoria”.</p></div>;
  }

  return (
    <div className="dashboard-section convocatoria-state">
      <span className="status">{convocatoria.abierta ? "CONVOCATORIA ACTUAL" : "ÚLTIMA CONVOCATORIA"}</span>
      <h3>{convocatoria.nombre}</h3>
      <p className="convocatoria-meta">Gestión {convocatoria.gestion} · {convocatoria.semestre}</p>
      <div className={`convocatoria-status ${convocatoria.abierta ? "open" : "closed"}`}>
        <strong>{convocatoria.abierta ? "Inscripciones abiertas" : "Inscripciones cerradas"}</strong>
        <small>Desde {mostrarFecha(convocatoria.inicio)} hasta {mostrarFecha(convocatoria.fin)}</small>
      </div>
      <form className="student-form close-date-form" onSubmit={actualizar}>
        <label>Extender o modificar fecha de cierre<input required name="fin" type="datetime-local" defaultValue={fechaParaInput(convocatoria.fin)} /></label>
        <button disabled={cargando} type="submit">{cargando ? "Actualizando..." : "Actualizar cierre"}</button>
      </form>
      {mensaje && <div className="alert success">{mensaje}</div>}
      {error && <div className="alert error">{error}</div>}
    </div>
  );
}
