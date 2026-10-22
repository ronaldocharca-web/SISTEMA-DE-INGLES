type Props = { mensaje: string; onBack: () => void };

export function RevisionScreen({ mensaje, onBack }: Props) {
  return (
    <section className="card result requiere_revision">
      <span className="status">
        <span className="status-dot"></span>
        REVISIÓN NECESARIA
      </span>
      <h2>Atención con el documento</h2>
      <p style={{ color: "#fef08a", fontSize: "15px", lineHeight: "1.6" }}>{mensaje}</p>
      <p className="hint">Por favor verifica que el PDF sea original, nítido y cuente con texto seleccionable.</p>
      
      <button type="button" onClick={onBack} style={{ marginTop: "18px" }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="m15 18-6-6 6-6"></path>
        </svg>
        <span>Intentar nuevamente</span>
      </button>
    </section>
  );
}
