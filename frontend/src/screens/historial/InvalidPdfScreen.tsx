type Props = { onBack: () => void };

export function InvalidPdfScreen({ onBack }: Props) {
  return (
    <section className="card result no_puede_tomar">
      <span className="status">
        <span className="status-dot"></span>
        DOCUMENTO NO VÁLIDO
      </span>
      <h2>Archivo no reconocido</h2>
      <p style={{ color: "#fca5a5", fontSize: "15px", lineHeight: "1.6" }}>
        El archivo cargado no corresponde a un historial académico oficial o el formato no es compatible. Solo se admiten historiales académicos con texto legible.
      </p>

      <button type="button" onClick={onBack} style={{ marginTop: "18px" }}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="m15 18-6-6 6-6"></path>
        </svg>
        <span>Subir otro archivo PDF</span>
      </button>
    </section>
  );
}
