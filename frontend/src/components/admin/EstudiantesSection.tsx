import { AdminIncident, AdminStudent, AdminStudentsResponse } from "@/models/admin";


function EstudiantesTable({ estudiantes }: { estudiantes: AdminStudent[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Fecha</th><th>Nombre</th><th>CI</th><th>RU</th><th>Correo</th><th>Celular</th></tr></thead>
        <tbody>
          {estudiantes.map((estudiante) => (
            <tr key={`${estudiante.CI}-${estudiante.RU}`}>
              <td>{estudiante.Fecha}</td><td>{estudiante.Nombre}</td><td>{estudiante.CI}</td>
              <td>{estudiante.RU}</td><td>{estudiante.Correo}</td><td>{estudiante.Celular}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function IncidenciasTable({ incidencias }: { incidencias: AdminIncident[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Fecha</th><th>Nombre</th><th>CI</th><th>RU</th><th>Archivo</th><th>Motivo</th></tr></thead>
        <tbody>
          {incidencias.map((incidencia, index) => (
            <tr key={`${incidencia.Fecha}-${incidencia.CI}-${index}`}>
              <td>{incidencia.Fecha}</td><td>{incidencia.Nombre || "No detectado"}</td>
              <td>{incidencia.CI || "No detectada"}</td><td>{incidencia.RU || "No detectado"}</td>
              <td>{incidencia.Archivo}</td><td>{incidencia.Motivo}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function EstudiantesSection({ datos }: { datos: AdminStudentsResponse }) {
  return (
    <div className="dashboard-section">
      <div className="section-heading">
        <div><span className="status">CONVOCATORIA ACTUAL</span><h3>Estudiantes registrados</h3></div>
        <strong>{datos.total}</strong>
      </div>
      {datos.estudiantes.length === 0
        ? <p className="empty-state">Todavía no hay estudiantes en esta convocatoria.</p>
        : <EstudiantesTable estudiantes={datos.estudiantes} />}

      <div className="section-heading secondary-heading">
        <div><h3>PDF rechazados</h3><p>Archivos que no pudieron validarse.</p></div>
        <strong>{datos.incidencias.length}</strong>
      </div>
      {datos.incidencias.length === 0
        ? <p className="empty-state">No hay PDF rechazados en esta convocatoria.</p>
        : <IncidenciasTable incidencias={datos.incidencias} />}
    </div>
  );
}
