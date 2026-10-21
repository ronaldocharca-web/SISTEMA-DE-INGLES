"use client";

import { FormEvent, useEffect, useState } from "react";

import { EstadoInscripciones } from "@/models/admin";
import { obtenerEstadoInscripciones } from "@/services/historialService";

type Props = { cargando: boolean; error: string; onUpload: (archivo: File) => Promise<void> };

function mostrarFecha(fecha: string): string {
  return new Intl.DateTimeFormat("es-BO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(fecha));
}

export function UploadScreen({ cargando, error, onUpload }: Props) {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [estado, setEstado] = useState<EstadoInscripciones | null>(null);
  const [errorFechas, setErrorFechas] = useState("");

  useEffect(() => {
    obtenerEstadoInscripciones()
      .then(setEstado)
      .catch((exception) => setErrorFechas(exception instanceof Error ? exception.message : "No fue posible consultar las fechas."));
  }, []);

  async function enviar(event: FormEvent) {
    event.preventDefault();
    if (archivo && estado?.habilitada) await onUpload(archivo);
  }

  const habilitada = estado?.habilitada === true;

  return (
    <section className="card">
      {estado?.convocatoria && (
        <div className={`convocatoria-publica ${habilitada ? "open" : "closed"}`}>
          <span className="status">{estado.convocatoria.nombre}</span>
          <h2>{habilitada ? "Inscripciones abiertas" : "Inscripciones cerradas"}</h2>
          <p>Desde {mostrarFecha(estado.convocatoria.inicio)} hasta {mostrarFecha(estado.convocatoria.fin)}</p>
        </div>
      )}
      {estado && !estado.convocatoria && <div className="alert error">{estado.mensaje}</div>}
      {errorFechas && <div className="alert error">{errorFechas}</div>}
      {!estado && !errorFechas && <p className="hint">Consultando fechas de inscripción...</p>}

      <form onSubmit={enviar}>
        <label htmlFor="archivo">Historial académico en PDF</label>
        <input disabled={!habilitada} id="archivo" type="file" accept="application/pdf,.pdf" onChange={(event) => setArchivo(event.target.files?.[0] ?? null)} />
        <p className="hint">Máximo 4 MB. El documento debe tener texto seleccionable.</p>
        <button disabled={!archivo || cargando || !habilitada} type="submit">{cargando ? "Analizando..." : "Analizar historial"}</button>
      </form>
      {error && <div className="alert error">{error}</div>}
    </section>
  );
}
