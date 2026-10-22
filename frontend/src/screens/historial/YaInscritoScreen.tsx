import { ResultadoAnalisis } from "@/models/historial";

type Props = { resultado: ResultadoAnalisis; onBack: () => void };

export function YaInscritoScreen({ resultado, onBack }: Props) {
  return (
    <section className="card result no_puede_tomar">
      <span className="status">
        <span className="status-dot"></span>
        REGISTRO EXISTENTE
      </span>
      <h2>Inscripción previa detectada</h2>
      <p style={{ color: "#fca5a5", fontSize: "15px", lineHeight: "1.6" }}>{resultado.mensaje}</p>

      <button type="button" onClick={onBack} style={{ marginTop: "18px" }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="m15 18-6-6 6-6"></path>
        </svg>
        <span>Analizar otro historial</span>
      </button>
    </section>
  );
}
