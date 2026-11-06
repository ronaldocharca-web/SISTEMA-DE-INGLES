"use client";

import { useAdditionController } from "@/controllers/useAdditionController";
import { AdditionApprovedScreen } from "@/screens/addition/AdditionApprovedScreen";
import { AdditionRejectedScreen } from "@/screens/addition/AdditionRejectedScreen";
import { AdditionUploadScreen } from "@/screens/addition/AdditionUploadScreen";

export function AdditionFlow() {
  const controller = useAdditionController();
  const resultado = controller.resultado;
  if (resultado?.estado === "PUEDE_SOLICITAR") return <AdditionApprovedScreen resultado={resultado} onBack={controller.reiniciar} />;
  if (resultado?.estado === "NO_PUEDE_SOLICITAR") return <AdditionRejectedScreen resultado={resultado} onBack={controller.reiniciar} />;
  if (resultado) return (
    <section className="card">
      <div className="result no_puede_tomar" style={{ marginTop: 0 }}>
        <span className="status"><span className="status-dot" />{resultado.estado === "YA_SOLICITO" ? "SOLICITUD YA REGISTRADA" : "NO SE PUDO CONTINUAR"}</span>
        <h2>{resultado.mensaje}</h2>
        {resultado.advertencias.map((item) => <p key={item}>{item}</p>)}
      </div>
      <button className="secondary" onClick={controller.reiniciar}>← Volver</button>
    </section>
  );
  return <AdditionUploadScreen cargando={controller.cargando} error={controller.error} onUpload={controller.analizar} />;
}
