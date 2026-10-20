"use client";
import { useState } from "react";
import { ResultadoAnalisis } from "../models/historial";
import { analizarHistorial } from "../services/historialService";

export function useHistorialController() {
  const [resultado, setResultado] = useState<ResultadoAnalisis | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  async function analizar(archivo: File) {
    setCargando(true); setError(""); setResultado(null);
    try { setResultado(await analizarHistorial(archivo)); }
    catch (exception) { setError(exception instanceof Error ? exception.message : "Ocurrió un error."); }
    finally { setCargando(false); }
  }
  function reiniciar() { setResultado(null); setError(""); }
  return { resultado, cargando, error, analizar, reiniciar };
}
