import { ResultadoAdicion } from "@/models/addition";

export function AdditionRejectedScreen({ resultado, onBack }: { resultado: ResultadoAdicion; onBack: () => void }) {
  return (
    <section className="card">
      <div className="result no_puede_tomar" style={{ marginTop: 0 }}>
        <span className="status"><span className="status-dot" />NO CUMPLE LOS REQUISITOS</span>
        <h2>No puedes solicitar la adición de materia</h2>
        <p className="result-message">{resultado.mensaje}</p>
      </div>
      <div className="reasons-list">
        <h3>Razones</h3>
        <ul>{resultado.motivos.map((motivo) => <li key={motivo}>{motivo}</li>)}</ul>
      </div>
      <div className="average-summary">
        <span>Promedio detectado <strong>{resultado.promedio.toFixed(2)}</strong></span>
        <span>Mínimo requerido <strong>{resultado.promedio_minimo.toFixed(2)}</strong></span>
      </div>
      {resultado.materias_observadas.length > 0 && (
        <div className="table-wrap">
          <table><thead><tr><th>Sigla</th><th>Materia</th><th>Nota</th><th>Observación</th></tr></thead>
            <tbody>{resultado.materias_observadas.map((materia, index) => (
              <tr key={`${materia.sigla}-${index}`}><td>{materia.sigla}</td><td>{materia.materia}</td><td>{materia.nota}</td><td>{materia.observacion}</td></tr>
            ))}</tbody>
          </table>
        </div>
      )}
      <button className="secondary" onClick={onBack}>← Volver a verificar</button>
    </section>
  );
}
