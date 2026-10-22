"use client";

import { FormEvent, useState } from "react";
import { iniciarSesionAdmin } from "@/services/historialService";

type Props = { onSuccess: (token: string) => void; onBack: () => void };

export function AdminLoginScreen({ onSuccess, onBack }: Props) {
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCargando(true);
    setError("");
    const valores = Object.fromEntries(new FormData(event.currentTarget).entries());
    try {
      onSuccess(await iniciarSesionAdmin(String(valores.usuario), String(valores.password)));
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible iniciar sesión.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <section className="card admin-login">
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
        <span className="status">
          <span className="status-dot"></span>
          ACCESO ADMINISTRATIVO
        </span>
      </div>

      <h2>Iniciar sesión</h2>
      <p className="hint" style={{ marginTop: 0, marginBottom: "20px" }}>
        Ingresa con las credenciales de gestión de la carrera de Turismo.
      </p>

      <form onSubmit={enviar} className="student-form">
        <label>
          Usuario institucional
          <input required name="usuario" autoComplete="username" placeholder="Nombre de usuario" />
        </label>
        <label>
          Contraseña
          <input required type="password" name="password" autoComplete="current-password" placeholder="••••••••" />
        </label>
        
        <button disabled={cargando} type="submit" style={{ width: "100%", marginTop: "8px" }}>
          {cargando ? "Validando credenciales..." : "Ingresar al panel"}
        </button>

        {error && <div className="alert error">{error}</div>}
      </form>

      <button className="secondary" type="button" onClick={onBack} style={{ marginTop: "14px", width: "100%", marginLeft: 0 }}>
        ← Volver al verificador
      </button>
    </section>
  );
}
