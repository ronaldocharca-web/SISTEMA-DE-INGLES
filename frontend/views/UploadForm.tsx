"use client";

import { useHistorialController } from "../controllers/useHistorialController";
import { CumpleScreen } from "../screens/CumpleScreen";
import { NoCumpleScreen } from "../screens/NoCumpleScreen";
import { RevisionScreen } from "../screens/RevisionScreen";
import { UploadScreen } from "../screens/UploadScreen";

/** Coordinador de navegación entre las pantallas del flujo. */
export function UploadForm() {
  const controller = useHistorialController();
  if (controller.resultado?.estado === "NO_PUEDE_TOMAR") return <NoCumpleScreen resultado={controller.resultado} onBack={controller.reiniciar} />;
  if (controller.resultado?.estado === "PUEDE_TOMAR") return <CumpleScreen resultado={controller.resultado} onBack={controller.reiniciar} />;
  if (controller.resultado?.estado === "REQUIERE_REVISION") return <RevisionScreen mensaje={controller.resultado.mensaje} onBack={controller.reiniciar} />;
  return <UploadScreen cargando={controller.cargando} error={controller.error} onUpload={controller.analizar} />;
}
