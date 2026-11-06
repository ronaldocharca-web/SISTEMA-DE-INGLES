"use client";

import { FormEvent, useEffect, useState } from "react";

import { ConvocatoriaBanner } from "@/components/historial/ConvocatoriaBanner";
import { PdfDropzone } from "@/components/historial/PdfDropzone";
import { EstadoAdicionInscripciones } from "@/models/addition";
import { obtenerEstadoAdicion } from "@/services/additionService";

type Props = { cargando: boolean; error: string; onUpload: (archivo: File) => Promise<void> };

export function AdditionUploadScreen({ cargando, error, onUpload }: Props) {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [estado, setEstado] = useState<EstadoAdicionInscripciones | null>(null);
  const [errorFechas, setErrorFechas] = useState("");

  useEffect(() => {
    obtenerEstadoAdicion().then(setEstado).catch((exception) => setErrorFechas(
      exception instanceof Error ? exception.message : "No fue posible consultar la convocatoria.",
    ));
  }, []);

  async function enviar(event: FormEvent) {
    event.preventDefault();
    if (archivo && estado?.habilitada) await onUpload(archivo);
  }

  return (
    <section className="card addition-card">
      {estado?.convocatoria && estado.habilitada && <ConvocatoriaBanner convocatoria={estado.convocatoria} />}
      <div className="requirements-box">
        <span className="status">REQUISITOS ACADÉMICOS</span>
        <ul>
          <li>No tener materias reprobadas.</li>
          <li>No tener materias abandonadas.</li>
          <li>Promedio mínimo: <strong>{estado?.promedio_minimo ?? 75}</strong>.</li>
        </ul>
      </div>
      {errorFechas && <div className="alert error">{errorFechas}</div>}
      {estado && !estado.habilitada && (
        <div className="availability-notice" role="status">
          <span className="availability-icon" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
          </span>
          <span>
            <strong>Convocatoria aún no habilitada</strong>
            <small>{estado.mensaje}</small>
          </span>
        </div>
      )}
      {!estado && !errorFechas && <p className="hint">Verificando convocatoria activa...</p>}
      <form onSubmit={enviar}>
        <label>Historial académico digital</label>
        <PdfDropzone archivo={archivo} cargando={cargando} habilitada={estado?.habilitada === true} onChange={setArchivo} />
        <button disabled={!archivo || cargando || !estado?.habilitada} type="submit" style={{ width: "100%" }}>
          {cargando ? "Analizando requisitos..." : "Verificar si puedo adicionar"}
        </button>
      </form>
      {error && <div className="alert error">{error}</div>}
    </section>
  );
}
