"use client";

import { useHistorialController } from "@/controllers/useHistorialController";
import { CumpleScreen } from "@/screens/historial/CumpleScreen";
import { InvalidPdfScreen } from "@/screens/historial/InvalidPdfScreen";
import { NoCumpleScreen } from "@/screens/historial/NoCumpleScreen";
import { RevisionScreen } from "@/screens/historial/RevisionScreen";
import { UploadScreen } from "@/screens/historial/UploadScreen";
import { YaInscritoScreen } from "@/screens/historial/YaInscritoScreen";

/** Coordinador de navegación entre las pantallas del flujo. */
export function HistorialFlow() {
  const controller = useHistorialController();
  if (controller.resultado?.estado === "NO_PUEDE_TOMAR") return <NoCumpleScreen resultado={controller.resultado} onBack={controller.reiniciar} />;
  if (controller.resultado?.estado === "PUEDE_TOMAR") return <CumpleScreen resultado={controller.resultado} onBack={controller.reiniciar} />;
  if (controller.resultado?.estado === "REQUIERE_REVISION") return <RevisionScreen mensaje={controller.resultado.mensaje} onBack={controller.reiniciar} />;
  if (controller.resultado?.estado === "YA_INSCRITO") return <YaInscritoScreen resultado={controller.resultado} onBack={controller.reiniciar} />;
  if (controller.resultado?.estado === "PDF_NO_VALIDO") return <InvalidPdfScreen onBack={controller.reiniciar} />;
  return <UploadScreen cargando={controller.cargando} error={controller.error} onUpload={controller.analizar} />;
}
