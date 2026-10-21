import { ResultadoAnalisis } from "@/models/historial";

type Props = { resultado: ResultadoAnalisis; onBack: () => void };

export function YaInscritoScreen({ resultado, onBack }: Props) {
  return <section className="card result no_puede_tomar"><span className="status">INSCRIPCIÓN EXISTENTE</span><h2>Tú ya te inscribiste antes</h2><p>{resultado.mensaje}</p><button type="button" onClick={onBack}>Analizar otro historial</button></section>;
}
