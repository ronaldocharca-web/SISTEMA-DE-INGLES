"use client";

import { DragEvent, useState } from "react";

type Props = {
  archivo: File | null;
  cargando: boolean;
  habilitada: boolean;
  onChange: (archivo: File | null) => void;
};

function formatearTamano(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function PdfDropzone({ archivo, cargando, habilitada, onChange }: Props) {
  const [arrastrando, setArrastrando] = useState(false);

  function manejarDrag(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.stopPropagation();
    if (!habilitada) return;
    setArrastrando(event.type === "dragover");
  }

  function manejarDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    event.stopPropagation();
    setArrastrando(false);
    if (!habilitada) return;
    const archivoNuevo = event.dataTransfer.files?.[0];
    if (archivoNuevo?.type === "application/pdf") onChange(archivoNuevo);
  }

  return (
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
          onChange={(event) => onChange(event.target.files?.[0] ?? null)}
        />
        <div className="dropzone-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <path d="M12 18v-6" /><path d="m9 15 3-3 3 3" />
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
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <div className="file-card-details">
              <span className="file-card-name">{archivo.name}</span>
              <span className="file-card-size">{formatearTamano(archivo.size)}</span>
            </div>
          </div>
          <button type="button" className="file-card-remove" title="Quitar archivo" onClick={() => onChange(null)}>✕</button>
        </div>
      )}
    </div>
  );
}
