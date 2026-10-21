"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { AdminCredentialsForm } from "@/components/admin/AdminCredentialsForm";
import { ConvocatoriaForm } from "@/components/admin/ConvocatoriaForm";
import { ConvocatoriasCerradas } from "@/components/admin/ConvocatoriasCerradas";
import { EstadoConvocatoria } from "@/components/admin/EstadoConvocatoria";
import { AdminIncident, AdminStudent, AdminStudentsResponse } from "@/models/admin";
import { descargarExcelAdmin, obtenerEstudiantesAdmin } from "@/services/historialService";

type Props = { token: string; onBack: () => void };
type Section = "estado" | "convocatoria" | "estudiantes" | "historial" | "seguridad";

export function AdminDashboardScreen({ token, onBack }: Props) {
  const [datos, setDatos] = useState<AdminStudentsResponse | null>(null);
  const [section, setSection] = useState<Section>("estado");
  const [error, setError] = useState("");
  const [descargando, setDescargando] = useState(false);
  const cargaInicialRealizada = useRef(false);

  const cargarDatos = useCallback(async () => {
    setError("");
    try {
      setDatos(await obtenerEstudiantesAdmin(token));
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible cargar los datos.");
    }
  }, [token]);

  useEffect(() => {
    if (cargaInicialRealizada.current) return;
    cargaInicialRealizada.current = true;
    void cargarDatos();
  }, [cargarDatos]);

  async function descargar() {
    setDescargando(true);
    setError("");
    try {
      await descargarExcelAdmin(token);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible descargar los datos.");
    } finally {
      setDescargando(false);
    }
  }

  return (
    <section className="admin-dashboard">
      <header className="dashboard-header">
        <div><span className="status">ADMINISTRACIÓN</span><h2>Panel de inscripciones</h2><p>Gestiona la convocatoria, los estudiantes y el historial.</p></div>
        <div className="admin-actions">
          <button disabled={descargando} onClick={descargar}>{descargando ? "Generando..." : "Descargar Excel"}</button>
          <button className="logout-button" onClick={onBack}>Salir</button>
        </div>
      </header>

      {datos && (
        <div className="dashboard-stats">
          <article><span>Estado</span><strong className={datos.convocatoria?.abierta ? "stat-open" : "stat-closed"}>{datos.convocatoria?.abierta ? "Abierta" : "Cerrada"}</strong><small>{datos.convocatoria?.nombre ?? "Sin convocatoria"}</small></article>
          <article><span>Inscritos actuales</span><strong>{datos.total}</strong><small>estudiantes</small></article>
          <article><span>Convocatorias anteriores</span><strong>{datos.convocatorias_cerradas.length}</strong><small>períodos guardados</small></article>
        </div>
      )}

      <nav className="dashboard-tabs" aria-label="Secciones administrativas">
        <button className={section === "estado" ? "active" : ""} onClick={() => setSection("estado")}>Estado</button>
        <button className={section === "convocatoria" ? "active" : ""} onClick={() => setSection("convocatoria")}>Nueva convocatoria</button>
        <button className={section === "estudiantes" ? "active" : ""} onClick={() => setSection("estudiantes")}>Estudiantes</button>
        <button className={section === "historial" ? "active" : ""} onClick={() => setSection("historial")}>Historial</button>
        <button className={section === "seguridad" ? "active" : ""} onClick={() => setSection("seguridad")}>Seguridad</button>
      </nav>

      {error && <div className="alert error dashboard-error">{error}<button className="secondary" onClick={() => void cargarDatos()}>Reintentar</button></div>}
      {!datos && !error && <div className="dashboard-loading">Cargando panel...</div>}

      {datos && <div className="dashboard-content">
        {section === "estado" && <EstadoConvocatoria token={token} convocatoria={datos.convocatoria} onSaved={cargarDatos} />}
        {section === "convocatoria" && <ConvocatoriaForm token={token} actual={datos.convocatoria} onSaved={cargarDatos} />}

        {section === "estudiantes" && <div className="dashboard-section">
          <div className="section-heading"><div><span className="status">CONVOCATORIA ACTUAL</span><h3>Estudiantes registrados</h3></div><strong>{datos.total}</strong></div>
          {datos.estudiantes.length === 0 ? <p className="empty-state">Todavía no hay estudiantes en esta convocatoria.</p> : (
            <div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Nombre</th><th>CI</th><th>RU</th><th>Correo</th><th>Celular</th></tr></thead><tbody>
              {datos.estudiantes.map((estudiante: AdminStudent) => <tr key={`${estudiante.CI}-${estudiante.RU}`}><td>{estudiante.Fecha}</td><td>{estudiante.Nombre}</td><td>{estudiante.CI}</td><td>{estudiante.RU}</td><td>{estudiante.Correo}</td><td>{estudiante.Celular}</td></tr>)}
            </tbody></table></div>
          )}
          <div className="section-heading secondary-heading"><div><h3>PDF rechazados</h3><p>Archivos que no pudieron validarse.</p></div><strong>{datos.incidencias.length}</strong></div>
          {datos.incidencias.length === 0 ? <p className="empty-state">No hay PDF rechazados en esta convocatoria.</p> : (
            <div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Nombre</th><th>CI</th><th>RU</th><th>Archivo</th><th>Motivo</th></tr></thead><tbody>
              {datos.incidencias.map((incidencia: AdminIncident, index) => <tr key={`${incidencia.Fecha}-${incidencia.CI}-${index}`}><td>{incidencia.Fecha}</td><td>{incidencia.Nombre || "No detectado"}</td><td>{incidencia.CI || "No detectada"}</td><td>{incidencia.RU || "No detectado"}</td><td>{incidencia.Archivo}</td><td>{incidencia.Motivo}</td></tr>)}
            </tbody></table></div>
          )}
        </div>}

        {section === "historial" && <div className="dashboard-section"><ConvocatoriasCerradas token={token} convocatorias={datos.convocatorias_cerradas} /></div>}
        {section === "seguridad" && <div className="dashboard-section security-section"><h3>Seguridad administrativa</h3><p>Cambia el usuario y la contraseña de acceso.</p><AdminCredentialsForm token={token} /></div>}
      </div>}
    </section>
  );
}
