"use client";

import { useState } from "react";

import { descargarExcelAdmin, descargarPdfAdmin, descargarWordAdmin } from "@/services/adminExportService";

type Props = {
  token: string;
  onBack: () => void;
  onError: (mensaje: string) => void;
};

type Formato = "excel" | "word" | "pdf";

const descargas = {
  excel: { ejecutar: descargarExcelAdmin, etiqueta: "Descargar Excel" },
  word: { ejecutar: descargarWordAdmin, etiqueta: "Descargar Word" },
  pdf: { ejecutar: descargarPdfAdmin, etiqueta: "Descargar PDF" },
} satisfies Record<Formato, { ejecutar: (token: string) => Promise<void>; etiqueta: string }>;

export function AdminDashboardHeader({ token, onBack, onError }: Props) {
  const [descargando, setDescargando] = useState<Formato | null>(null);

  async function descargar(formato: Formato) {
    setDescargando(formato);
    onError("");
    try {
      await descargas[formato].ejecutar(token);
    } catch (exception) {
      onError(exception instanceof Error ? exception.message : `No fue posible descargar el ${formato}.`);
    } finally {
      setDescargando(null);
    }
  }

  return (
    <header className="dashboard-header">
      <div>
        <span className="status">ADMINISTRACIÓN</span>
        <h2>Panel de inscripciones</h2>
        <p>Gestiona la convocatoria, los estudiantes y el historial.</p>
      </div>
      <div className="admin-actions">
        {(Object.keys(descargas) as Formato[]).map((formato) => (
          <button
            className={formato === "excel" ? undefined : "secondary"}
            disabled={descargando !== null}
            key={formato}
            onClick={() => void descargar(formato)}
          >
            {descargando === formato ? "Generando..." : descargas[formato].etiqueta}
          </button>
        ))}
        <button className="logout-button" onClick={onBack}>Salir</button>
      </div>
    </header>
  );
}
