"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { AdminCredentialsForm } from "@/components/admin/AdminCredentialsForm";
import { AdminDashboardHeader } from "@/components/admin/AdminDashboardHeader";
import { AdminDashboardStats } from "@/components/admin/AdminDashboardStats";
import { ConvocatoriaForm } from "@/components/admin/ConvocatoriaForm";
import { ConvocatoriasCerradas } from "@/components/admin/ConvocatoriasCerradas";
import { EstudiantesSection } from "@/components/admin/EstudiantesSection";
import { EstadoConvocatoria } from "@/components/admin/EstadoConvocatoria";
import { AdminStudentsResponse } from "@/models/admin";
import { obtenerEstudiantesAdmin } from "@/services/adminService";

type Props = { token: string; onBack: () => void };
type Section = "estado" | "convocatoria" | "estudiantes" | "historial" | "seguridad";

export function AdminDashboardScreen({ token, onBack }: Props) {
  const [datos, setDatos] = useState<AdminStudentsResponse | null>(null);
  const [section, setSection] = useState<Section>("estado");
  const [error, setError] = useState("");
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

  return (
    <section className="admin-dashboard">
      <AdminDashboardHeader token={token} onBack={onBack} onError={setError} />

      {datos && <AdminDashboardStats datos={datos} />}

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

        {section === "estudiantes" && <EstudiantesSection datos={datos} />}

        {section === "historial" && <div className="dashboard-section"><ConvocatoriasCerradas token={token} convocatorias={datos.convocatorias_cerradas} /></div>}
        {section === "seguridad" && <div className="dashboard-section security-section"><h3>Seguridad administrativa</h3><p>Cambia el usuario y la contraseña de acceso.</p><AdminCredentialsForm token={token} /></div>}
      </div>}
    </section>
  );
}
