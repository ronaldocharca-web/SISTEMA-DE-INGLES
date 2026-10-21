type Props = { onBack: () => void };

export function InvalidPdfScreen({ onBack }: Props) {
  return <section className="card result no_puede_tomar"><span className="status">PDF NO VÁLIDO</span><h2>Este archivo no es válido</h2><p>Solo se aceptan historiales del estudiante.</p><button type="button" onClick={onBack}>Subir otro PDF</button></section>;
}
