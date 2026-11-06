"use client";

import { useState } from "react";

import { ResultadoAdicion } from "@/models/addition";
import { analizarHistorialAdicion } from "@/services/additionService";

const KEY = "sistema-adicion-reserva-pdf";

export function useAdditionController() {
  const [resultado, setResultado] = useState<ResultadoAdicion | null>(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  async function analizar(archivo: File) {
    setCargando(true);
    setError("");
    try {
      const nuevo = await analizarHistorialAdicion(archivo, window.sessionStorage.getItem(KEY) ?? undefined);
      if (nuevo.pdf_token) window.sessionStorage.setItem(KEY, nuevo.pdf_token);
      setResultado(nuevo);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "Ocurrió un error.");
    } finally {
      setCargando(false);
    }
  }

  function reiniciar() {
    window.sessionStorage.removeItem(KEY);
    setResultado(null);
    setError("");
  }

  return { resultado, cargando, error, analizar, reiniciar };
}
