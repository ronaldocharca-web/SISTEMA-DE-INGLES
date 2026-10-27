"use client";

import { FormEvent, useEffect, useState } from "react";

import { ConvocatoriaBanner } from "@/components/historial/ConvocatoriaBanner";
import { PdfDropzone } from "@/components/historial/PdfDropzone";
import { EstadoInscripciones } from "@/models/admin";
import { obtenerEstadoInscripciones } from "@/services/historialService";

type Props = {
  cargando: boolean;
  error: string;
  onUpload: (archivo: File) => Promise<void>;
};

export function UploadScreen({ cargando, error, onUpload }: Props) {
  const [archivo, setArchivo] = useState<File | null>(null);
  const [estado, setEstado] = useState<EstadoInscripciones | null>(null);
  const [errorFechas, setErrorFechas] = useState("");

  useEffect(() => {
    obtenerEstadoInscripciones()
      .then(setEstado)
      .catch((exception) => {
        setErrorFechas(
          exception instanceof Error
            ? exception.message
            : "No fue posible consultar las fechas.",
        );
      });
  }, []);

  const habilitada = estado?.habilitada === true;

  async function enviar(event: FormEvent) {
    event.preventDefault();
    if (archivo && habilitada) await onUpload(archivo);
  }

  return (
    <section className="card">
      {estado?.convocatoria && habilitada && (
        <ConvocatoriaBanner convocatoria={estado.convocatoria} />
      )}
      {estado && !estado.convocatoria && <div className="alert error">{estado.mensaje}</div>}
      {errorFechas && <div className="alert error">{errorFechas}</div>}
      {!estado && !errorFechas && <p className="hint">Verificando convocatoria activa...</p>}

      <form onSubmit={enviar}>
        <label>Historial académico digital</label>
        <PdfDropzone
          archivo={archivo}
          cargando={cargando}
          habilitada={habilitada}
          onChange={setArchivo}
        />
        <button disabled={!archivo || cargando || !habilitada} type="submit" style={{ width: "100%" }}>
          {cargando ? (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="animate-spin" style={{ animation: "spin 1s linear infinite" }}>
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              <span>Analizando historial académico...</span>
            </>
          ) : (
            <>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="m5 12 5 5L20 7" />
              </svg>
              <span>Verificar historial</span>
            </>
          )}
        </button>
      </form>

      {error && <div className="alert error">{error}</div>}
      <style jsx>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </section>
  );
}
