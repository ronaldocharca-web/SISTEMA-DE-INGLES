"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import { AdminCredentialsForm } from "@/components/admin/AdminCredentialsForm";
import { AdditionAdminResponse, AdminAdditionRequest } from "@/models/addition";
import { actualizarFinAdicion, actualizarPromedioAdicion, crearConvocatoriaAdicion, descargarExcelConvocatoriaAdicion, descargarExcelSolicitudesAdicion, descargarPdfConvocatoriaAdicion, descargarPdfSolicitudesAdicion, descargarWordConvocatoriaAdicion, descargarWordSolicitudesAdicion, obtenerAdminAdicion } from "@/services/additionService";
import { fechaParaInput, mostrarFecha } from "@/utils/date";

type Section = "estado" | "convocatoria" | "solicitudes" | "historial" | "configuracion" | "seguridad";

function RequestsTable({ solicitudes }: { solicitudes: AdminAdditionRequest[] }) {
  if (!solicitudes.length) return <p className="empty-state">Todavía no hay solicitudes registradas.</p>;
  return <div className="table-wrap"><table><thead><tr><th>Fecha</th><th>Nombre</th><th>CI</th><th>RU</th><th>Sigla</th><th>Nombre de materia</th><th>Semestre</th><th>Carga total</th><th>Promedio</th><th>Correo</th><th>Celular</th></tr></thead>
    <tbody>{solicitudes.map((item, index) => <tr key={`${item.CI}-${item.RU}-${index}`}><td>{item.Fecha}</td><td>{item.Nombre}</td><td>{item.CI}</td><td>{item.RU}</td><td>{item.Sigla}</td><td>{item["Nombre de materia"]}</td><td>{item["Semestre de materia"] ? `${item["Semestre de materia"]}.º` : "—"}</td><td>{item["Carga total"] ? `${item["Carga total"]}.ª materia` : "—"}</td><td>{item.Promedio}</td><td>{item.Correo}</td><td>{item.Celular}</td></tr>)}</tbody>
  </table></div>;
}

export function AdditionAdminDashboardScreen({ token, onBack }: { token: string; onBack: () => void }) {
  const [datos, setDatos] = useState<AdditionAdminResponse | null>(null);
  const [section, setSection] = useState<Section>("estado");
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(false);
  const [descargando, setDescargando] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    setError("");
    try { setDatos(await obtenerAdminAdicion(token)); }
    catch (exception) { setError(exception instanceof Error ? exception.message : "No fue posible cargar el panel."); }
  }, [token]);

  useEffect(() => { void cargar(); }, [cargar]);

  async function nuevaConvocatoria(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formulario = event.currentTarget;
    const valores = Object.fromEntries(new FormData(formulario).entries());
    const inicio = new Date(String(valores.inicio));
    const fin = new Date(String(valores.fin));
    if (fin <= inicio) return setError("La fecha final debe ser posterior a la inicial.");
    if (datos?.convocatoria && !window.confirm("La convocatoria actual pasará al historial. ¿Continuar?")) return;
    setCargando(true); setError(""); setMensaje("");
    try {
      await crearConvocatoriaAdicion(token, { nombre: String(valores.nombre), gestion: Number(valores.gestion), semestre: String(valores.semestre), inicio: inicio.toISOString(), fin: fin.toISOString() });
      formulario.reset(); setMensaje("Convocatoria de adición guardada correctamente."); await cargar();
    } catch (exception) { setError(exception instanceof Error ? exception.message : "No fue posible guardar."); }
    finally { setCargando(false); }
  }

  async function guardarCierre(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const fin = new Date(String(new FormData(event.currentTarget).get("fin")));
    setCargando(true); setError("");
    try { await actualizarFinAdicion(token, fin.toISOString()); setMensaje("Fecha de cierre actualizada."); await cargar(); }
    catch (exception) { setError(exception instanceof Error ? exception.message : "No fue posible actualizar."); }
    finally { setCargando(false); }
  }

  async function guardarPromedio(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const promedio = Number(new FormData(event.currentTarget).get("promedio_minimo"));
    setCargando(true); setError("");
    try { await actualizarPromedioAdicion(token, promedio); setMensaje(`Promedio mínimo actualizado a ${promedio}.`); await cargar(); }
    catch (exception) { setError(exception instanceof Error ? exception.message : "No fue posible actualizar."); }
    finally { setCargando(false); }
  }

  async function descargar(formato: "excel" | "word" | "pdf", convocatoriaId?: string) {
    const clave = `${convocatoriaId ?? "actual"}-${formato}`;
    setDescargando(clave); setError(""); setMensaje("");
    try {
      if (convocatoriaId) {
        if (formato === "excel") await descargarExcelConvocatoriaAdicion(token, convocatoriaId);
        else if (formato === "word") await descargarWordConvocatoriaAdicion(token, convocatoriaId);
        else await descargarPdfConvocatoriaAdicion(token, convocatoriaId);
      } else if (formato === "excel") await descargarExcelSolicitudesAdicion(token);
      else if (formato === "word") await descargarWordSolicitudesAdicion(token);
      else await descargarPdfSolicitudesAdicion(token);
      setMensaje(`${formato.toUpperCase()} descargado. Revisa la carpeta Descargas de tu navegador.`);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible descargar el archivo.");
    } finally { setDescargando(null); }
  }

  return <section className="admin-dashboard">
    <header className="dashboard-header"><div><span className="status">ADMINISTRACIÓN</span><h2>Adición de materia</h2><p>Gestiona convocatorias, requisitos y solicitudes.</p></div>
      <div className="admin-actions"><button disabled={descargando !== null} onClick={() => void descargar("excel")}>{descargando === "actual-excel" ? "Generando Excel..." : "Descargar Excel"}</button><button disabled={descargando !== null} onClick={() => void descargar("word")}>{descargando === "actual-word" ? "Generando Word..." : "Descargar Word"}</button><button disabled={descargando !== null} onClick={() => void descargar("pdf")}>{descargando === "actual-pdf" ? "Generando PDF..." : "Descargar PDF"}</button><button className="logout-button" onClick={onBack}>Salir</button></div>
    </header>
    {datos && <div className="dashboard-stats"><article><span>Estado</span><strong className={datos.convocatoria?.abierta ? "stat-open" : "stat-closed"}>{datos.convocatoria?.abierta ? "Abierta" : "Cerrada"}</strong><small>{datos.convocatoria?.nombre ?? "Sin convocatoria"}</small></article><article><span>Solicitudes actuales</span><strong>{datos.total}</strong><small>estudiantes</small></article><article><span>Promedio mínimo</span><strong>{datos.promedio_minimo}</strong><small>configurable</small></article></div>}
    <nav className="dashboard-tabs" aria-label="Secciones administrativas">
      {(["estado", "convocatoria", "solicitudes", "historial", "configuracion", "seguridad"] as Section[]).map((item) => <button key={item} className={section === item ? "active" : ""} onClick={() => { setSection(item); setMensaje(""); setError(""); }}>{item === "configuracion" ? "Requisitos" : item[0].toUpperCase() + item.slice(1)}</button>)}
    </nav>
    {error && <div className="alert error dashboard-error">{error}</div>}{mensaje && <div className="alert success">{mensaje}</div>}
    {!datos && !error && <div className="dashboard-loading">Cargando panel...</div>}
    {datos && <div className="dashboard-content">
      {section === "estado" && <div className="dashboard-section convocatoria-state"><span className="status">CONVOCATORIA DE ADICIÓN</span><h3>{datos.convocatoria?.nombre ?? "Sin convocatoria"}</h3>{datos.convocatoria ? <><p className="convocatoria-meta">Gestión {datos.convocatoria.gestion} · {datos.convocatoria.semestre}</p><div className={`convocatoria-status ${datos.convocatoria.abierta ? "open" : "closed"}`}><strong>{datos.convocatoria.abierta ? "Solicitudes abiertas" : "Solicitudes cerradas"}</strong><small>Desde {mostrarFecha(datos.convocatoria.inicio)} hasta {mostrarFecha(datos.convocatoria.fin)}</small></div><form className="student-form" onSubmit={guardarCierre}><label>Modificar cierre<input required name="fin" type="datetime-local" defaultValue={fechaParaInput(datos.convocatoria.fin)} /></label><button disabled={cargando}>Actualizar cierre</button></form></> : <p className="empty-state">Crea una convocatoria para habilitar solicitudes.</p>}</div>}
      {section === "convocatoria" && <div className="admin-convocatoria"><span className="status">NUEVO PERÍODO</span><h3>Crear convocatoria de adición</h3><form className="student-form" onSubmit={nuevaConvocatoria}><label>Nombre<input required name="nombre" placeholder="Ejemplo: Adición de materias 2026" /></label><div className="form-grid-2"><label>Gestión<input required type="number" name="gestion" min="2000" max="2100" defaultValue={new Date().getFullYear()} /></label><label>Semestre<select required name="semestre" defaultValue="Segundo semestre"><option>Primer semestre</option><option>Segundo semestre</option></select></label></div><div className="date-grid"><label>Desde<input required type="datetime-local" name="inicio" /></label><label>Hasta<input required type="datetime-local" name="fin" /></label></div><button disabled={cargando}>Guardar convocatoria</button></form></div>}
      {section === "solicitudes" && <div className="dashboard-section"><div className="section-heading"><div><span className="status">CONVOCATORIA ACTUAL</span><h3>Solicitudes registradas</h3></div><strong>{datos.total}</strong></div><RequestsTable solicitudes={datos.solicitudes} /></div>}
      {section === "historial" && <div className="dashboard-section"><h3>Convocatorias y estudiantes registrados</h3><p className="hint">Abre una convocatoria para ver sus solicitudes directamente.</p>
        {datos.convocatoria && <details className="closed-call current-call" open><summary><span><strong><span className="history-label">{datos.convocatoria.abierta ? "En marcha" : "Convocatoria actual"}</span>{datos.convocatoria.nombre}</strong><small>Gestión {datos.convocatoria.gestion} · {datos.convocatoria.semestre}</small><small>{mostrarFecha(datos.convocatoria.inicio)} — {mostrarFecha(datos.convocatoria.fin)}</small></span><span className="closed-call-actions"><b>{datos.total} solicitud{datos.total === 1 ? "" : "es"}</b>{(["excel", "word", "pdf"] as const).map((formato) => <button type="button" className="secondary" key={formato} disabled={descargando !== null} onClick={(event) => { event.preventDefault(); void descargar(formato); }}>{descargando === `actual-${formato}` ? "Generando..." : formato.toUpperCase()}</button>)}</span></summary><RequestsTable solicitudes={datos.solicitudes} /></details>}
        <h3 className="history-previous-title">Convocatorias anteriores</h3>{datos.convocatorias_cerradas.length === 0 ? <p className="empty-state">No existen convocatorias anteriores.</p> : datos.convocatorias_cerradas.map((item, index) => <details className="closed-call" key={item.id}><summary><span><strong><span className="history-label">{index === 0 ? "Última convocatoria" : "Convocatoria cerrada"}</span>{item.nombre}</strong><small>Gestión {item.gestion} · {item.semestre}</small><small>{mostrarFecha(item.inicio)} — {mostrarFecha(item.fin)}</small></span><span className="closed-call-actions"><b>{item.total} solicitud{item.total === 1 ? "" : "es"}</b>{(["excel", "word", "pdf"] as const).map((formato) => <button type="button" className="secondary" key={formato} disabled={descargando !== null} onClick={(event) => { event.preventDefault(); void descargar(formato, item.id); }}>{descargando === `${item.id}-${formato}` ? "Generando..." : formato.toUpperCase()}</button>)}</span></summary><RequestsTable solicitudes={item.solicitudes} /></details>)}</div>}
      {section === "configuracion" && <div className="dashboard-section"><span className="status">REQUISITOS</span><h3>Promedio mínimo permitido</h3><p className="hint">Las reglas de no tener materias reprobadas ni abandonadas permanecen activas. Puedes modificar el promedio requerido.</p><form className="student-form compact-form" onSubmit={guardarPromedio}><label>Promedio mínimo<input required type="number" name="promedio_minimo" min="0" max="100" step="0.01" defaultValue={datos.promedio_minimo} /></label><button disabled={cargando}>Guardar requisito</button></form></div>}
      {section === "seguridad" && <div className="dashboard-section security-section"><h3>Seguridad administrativa</h3><p>Estas credenciales son las mismas que utiliza el sistema de inglés.</p><AdminCredentialsForm token={token} /></div>}
    </div>}
  </section>;
}
