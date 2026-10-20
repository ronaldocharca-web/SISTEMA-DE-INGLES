import { ResultadoAnalisis } from "../models/historial";

type Props = { resultado: ResultadoAnalisis; onBack: () => void };

export function NoCumpleScreen({ resultado, onBack }: Props) {
  return <section className="card result no_puede_tomar"><span className="status">NO CUMPLE LOS REQUISITOS</span><h2>No puede continuar con la solicitud</h2><p>{resultado.mensaje}</p><h3>Asignaturas encontradas</h3><ul>{resultado.materias_requisito.map((materia) => <li key={`${materia.sigla}-${materia.materia}`}><strong>{materia.sigla}</strong> — {materia.materia} ({materia.observacion}, nota {materia.nota})</li>)}</ul><button type="button" onClick={onBack}>Analizar otro historial</button></section>;
}
