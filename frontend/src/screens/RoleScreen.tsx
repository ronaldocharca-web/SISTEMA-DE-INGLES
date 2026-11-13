"use client";

import { useEffect, useState } from "react";

import { AdditionFlow } from "@/components/flows/AdditionFlow";
import { HistorialFlow } from "@/components/flows/HistorialFlow";
import { AdditionAdminDashboardScreen } from "@/screens/admin/AdditionAdminDashboardScreen";
import { AdminDashboardScreen } from "@/screens/admin/AdminDashboardScreen";
import { AdminLoginScreen } from "@/screens/admin/AdminLoginScreen";

type System = "ingles" | "adicion";
type View = "home" | "student" | "admin-login" | "admin";

export function RoleScreen() {
  const [view, setView] = useState<View>("home");
  const [system, setSystem] = useState<System>("ingles");
  const [token, setToken] = useState("");

  useEffect(() => {
    function sincronizarConNavegador() {
      const parametros = new URLSearchParams(window.location.search);
      const modulo = parametros.get("modulo");
      if (modulo !== "ingles" && modulo !== "adicion") {
        setView("home");
        return;
      }
      setSystem(modulo);
      setView(parametros.get("vista") === "admin" ? "admin-login" : "student");
    }

    sincronizarConNavegador();
    window.addEventListener("popstate", sincronizarConNavegador);
    return () => window.removeEventListener("popstate", sincronizarConNavegador);
  }, []);

  function navegar(nuevaVista: View, nuevoSistema?: System, reemplazar = false) {
    const sistemaActual = nuevoSistema ?? system;
    const parametros = new URLSearchParams();
    if (nuevaVista !== "home") parametros.set("modulo", sistemaActual);
    if (nuevaVista === "admin-login" || nuevaVista === "admin") parametros.set("vista", "admin");
    const url = parametros.size ? `?${parametros.toString()}` : window.location.pathname;
    window.history[reemplazar ? "replaceState" : "pushState"]({}, "", url);
    if (nuevoSistema) setSystem(nuevoSistema);
    setView(nuevaVista);
  }

  function abrirSistema(nuevo: System) {
    navegar("student", nuevo);
  }

  function volverInicio() {
    setToken("");
    navegar("home", undefined, true);
  }

  if (view === "home") {
    return <>
      <section className="hero module-hero">
        <div className="eyebrow">Carrera de Licenciatura en Turismo</div>
        <h1>Plataforma de Servicios Académicos</h1>
        <p className="subtitle">Selecciona el trámite que deseas realizar.</p>
      </section>
      <section className="module-selector" aria-label="Sistemas disponibles">
        <button className="module-option" onClick={() => abrirSistema("ingles")}>
          <span className="module-icon">EN</span><span><strong>Sistema de Inglés</strong><small>Verificación para el examen de clasificación</small></span><b>→</b>
        </button>
        <button className="module-option addition-option" onClick={() => abrirSistema("adicion")}>
          <span className="module-icon">+</span><span><strong>Adición de Materia</strong><small>Solicitud para adicionar una materia al semestre actual</small></span><b>→</b>
        </button>
      </section>
    </>;
  }

  if (view === "student") {
    return (
      <>
        <section className="hero system-hero">
          <button className="back-home" onClick={volverInicio}>← Volver al menú principal</button>
          <div className="eyebrow">Carrera de Licenciatura en Turismo</div>
          <h1>{system === "ingles" ? "Verificación Para Ingresar al Clasificacion de Examen de Inglés" : "Solicitud de Adición de Materia"}</h1>
          <p className="subtitle">{system === "ingles" ? "Sube tu historial académico para validar tu habilitación al examen." : "Verifica tus requisitos académicos para adicionar una materia al semestre actual."}</p>
        </section>
        <div className="student-entry">
        <button
          className="admin-icon"
          aria-label="Abrir acceso administrativo"
          title="Panel administrativo"
          onClick={() => navegar("admin-login")}
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <span>Admin</span>
        </button>
        {system === "ingles" ? <HistorialFlow /> : <AdditionFlow />}
      </div>
      </>
    );
  }

  if (view === "admin-login") {
    return (
      <AdminLoginScreen
        onSuccess={(newToken) => {
          setToken(newToken);
          setView("admin");
        }}
        onBack={volverInicio}
      />
    );
  }

  return system === "ingles" ? (
    <AdminDashboardScreen
      token={token}
      onBack={volverInicio}
    />
  ) : (
    <AdditionAdminDashboardScreen token={token} onBack={volverInicio} />
  );
}
