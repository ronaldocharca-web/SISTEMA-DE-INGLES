type Props = { mensaje: string; onBack: () => void };

export function RevisionScreen({ mensaje, onBack }: Props) {
  return <section className="card"><div className="alert error"><strong>Revisión necesaria.</strong><p>{mensaje}</p><p>Verifica que el PDF tenga texto seleccionable.</p></div><button type="button" onClick={onBack}>Intentar nuevamente</button></section>;
}
