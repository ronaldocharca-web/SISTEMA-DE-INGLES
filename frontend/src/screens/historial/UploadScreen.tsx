"use client";

import { DragEvent, FormEvent, useEffect, useState } from "react";

import { EstadoInscripciones } from "@/models/admin";
import { obtenerEstadoInscripciones } from "@/services/historialService";

type Props = { cargando: boolean; error: string; onUpload: (archivo: File) => Promise<void> };

function mostrarFecha(fecha: string): string {
  return new Intl.DateTimeFormat("es-BO", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(fecha));
}

function formatearTamano(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function UploadScreen({ cargando, error, onUpload }: Props) {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [arrastrando, setArrastrando] = useState(false);
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

  function manejarDrag(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    e.stopPropagation();
    if (!habilitada) return;
    if (e.type === "dragover") setArrastrando(true);
    if (e.type === "dragleave") setArrastrando(false);
  }

  function manejarDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    e.stopPropagation();
    setArrastrando(false);
    if (!habilitada) return;
    const file = e.dataTransfer.files?.[0];
    if (file && file.type === "application/pdf") {
      setArchivo(file);
    }
  }

  const habilitada = estado?.habilitada === true;

  return (
    <section className="card">
      {estado?.convocatoria && (
        <div className={`convocatoria-publica ${habilitada ? "open" : "closed"}`}>
          <span className="status">
            <span className="status-dot"></span>
            {estado.convocatoria.nombre}
          </span>
          <h2>{habilitada ? "Inscripciones habilitadas" : "Inscripciones cerradas"}</h2>
          <p>
            Vigencia: {mostrarFecha(estado.convocatoria.inicio)} — {mostrarFecha(estado.convocatoria.fin)}
          </p>
        </div>
      )}

      {estado && !estado.convocatoria && <div className="alert error">{estado.mensaje}</div>}
      {errorFechas && <div className="alert error">{errorFechas}</div>}
      {!estado && !errorFechas && <p className="hint">Verificando convocatoria activa...</p>}

      <form onSubmit={enviar}>
        <label>Historial académico digital</label>

        <div className="dropzone-container">
          <div
            className={`dropzone ${arrastrando ? "active" : ""} ${!habilitada ? "disabled" : ""}`}
            onDragOver={manejarDrag}
            onDragLeave={manejarDrag}
            onDrop={manejarDrop}
          >
            <input
              disabled={!habilitada || cargando}
              id="archivo"
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setArchivo(event.target.files?.[0] ?? null)}
            />
            <div className="dropzone-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <path d="M12 18v-6"></path>
                <path d="m9 15 3-3 3 3"></path>
              </svg>
            </div>
            <div>
              <div className="dropzone-title">Arrastra tu PDF aquí o haz clic para buscar</div>
              <div className="dropzone-subtitle">Solo archivos PDF oficiales con texto seleccionable (Máximo 4 MB)</div>
            </div>
          </div>

          {archivo && (
            <div className="file-card">
              <div className="file-card-info">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <div className="file-card-details">
                  <span className="file-card-name">{archivo.name}</span>
                  <span className="file-card-size">{formatearTamano(archivo.size)}</span>
                </div>
              </div>
              <button
                type="button"
                className="file-card-remove"
                title="Quitar archivo"
                onClick={() => setArchivo(null)}
              >
                ✕
              </button>
            </div>
          )}
        </div>

        <button disabled={!archivo || cargando || !habilitada} type="submit" style={{ width: "100%" }}>
          {cargando ? (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="animate-spin" style={{ animation: "spin 1s linear infinite" }}>
                <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
              </svg>
              <span>Analizando historial académico...</span>
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="m5 12 5 5L20 7"></path>
              </svg>
              <span>Verificar historial</span>
            </>
          )}
        </button>
      </form>

      {error && <div className="alert error">{error}</div>}

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </section>
  );
}
