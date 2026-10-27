import { AdminStudentsResponse } from "@/models/admin";


export function AdminDashboardStats({ datos }: { datos: AdminStudentsResponse }) {
  const convocatoria = datos.convocatoria;
  return (
    <div className="dashboard-stats">
      <article>
        <span>Estado</span>
        <strong className={convocatoria?.abierta ? "stat-open" : "stat-closed"}>
          {convocatoria?.abierta ? "Abierta" : "Cerrada"}
        </strong>
        <small>
          {convocatoria
            ? `${convocatoria.nombre} · Gestión ${convocatoria.gestion} · ${convocatoria.semestre}`
            : "Sin convocatoria"}
        </small>
      </article>
      <article><span>Inscritos actuales</span><strong>{datos.total}</strong><small>estudiantes</small></article>
      <article><span>Convocatorias anteriores</span><strong>{datos.convocatorias_cerradas.length}</strong><small>períodos guardados</small></article>
    </div>
  );
}
