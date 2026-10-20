"use client";

import { FormEvent, useState } from "react";

type Props = { cargando: boolean; error: string; onUpload: (archivo: File) => Promise<void> };

export function UploadScreen({ cargando, error, onUpload }: Props) {
  const [archivo, setArchivo] = useState<File | null>(null);
  async function enviar(event: FormEvent) { event.preventDefault(); if (archivo) await onUpload(archivo); }
  return <section className="card"><form onSubmit={enviar}><label htmlFor="archivo">Historial académico en PDF</label><input id="archivo" type="file" accept="application/pdf,.pdf" onChange={(event) => setArchivo(event.target.files?.[0] ?? null)} /><p className="hint">Máximo 4 MB. El documento debe tener texto seleccionable.</p><button disabled={!archivo || cargando} type="submit">{cargando ? "Analizando..." : "Analizar historial"}</button></form>{error && <div className="alert error">{error}</div>}</section>;
}
