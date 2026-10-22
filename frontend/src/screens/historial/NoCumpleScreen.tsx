import { ResultadoAnalisis } from "@/models/historial";

type Props = { resultado: ResultadoAnalisis; onBack: () => void };

export function NoCumpleScreen({ resultado, onBack }: Props) {
  return (
    <section className="card result no_puede_tomar">
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span className="status">
          <span className="status-dot"></span>
          NO CUMPLE LOS REQUISITOS
        </span>
      </div>

      <h2>No puede continuar con la solicitud</h2>
      <p style={{ color: "#fca5a5", fontSize: "15px", lineHeight: "1.6" }}>{resultado.mensaje}</p>

      {resultado.materias_requisito.length > 0 && (
        <>
          <h3>Asignaturas de inglés registradas</h3>
          <ul className="subject-grid">
            {resultado.materias_requisito.map((materia) => (
              <li className="subject-item" key={`${materia.sigla}-${materia.materia}`}>
                <span className="subject-code">{materia.sigla}</span>
                <span className="subject-name">{materia.materia}</span>
                <span className="subject-badge">
                  {materia.observacion} • {materia.nota} pts
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      <button type="button" onClick={onBack} style={{ marginTop: "14px" }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="m15 18-6-6 6-6"></path>
        </svg>
        <span>Analizar otro historial</span>
      </button>
    </section>
  );
}
