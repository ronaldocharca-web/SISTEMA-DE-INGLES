"use client";
import { useState } from "react";
import { ResultadoAnalisis } from "@/models/historial";
import { analizarHistorial } from "@/services/historialService";

const RESERVA_PDF_KEY = "sistema-ingles-reserva-pdf";

export function useHistorialController() {
  const [resultado, setResultado] = useState<ResultadoAnalisis | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  async function analizar(archivo: File) {
    setCargando(true); setError(""); setResultado(null);
    try {
      const tokenReserva = window.sessionStorage.getItem(RESERVA_PDF_KEY) ?? undefined;
      const resultadoNuevo = await analizarHistorial(archivo, tokenReserva);
      if (resultadoNuevo.pdf_token) {
        window.sessionStorage.setItem(RESERVA_PDF_KEY, resultadoNuevo.pdf_token);
      }
      setResultado(resultadoNuevo);
    }
    catch (exception) { setError(exception instanceof Error ? exception.message : "Ocurrió un error."); }
    finally { setCargando(false); }
  }
  function reiniciar() {
    window.sessionStorage.removeItem(RESERVA_PDF_KEY);
    setResultado(null);
    setError("");
  }
  return { resultado, cargando, error, analizar, reiniciar };
}
