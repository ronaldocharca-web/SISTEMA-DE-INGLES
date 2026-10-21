"use client";

import { FormEvent, useState } from "react";
import { iniciarSesionAdmin } from "@/services/historialService";

type Props = { onSuccess: (token: string) => void; onBack: () => void };

export function AdminLoginScreen({ onSuccess, onBack }: Props) {
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  async function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setCargando(true); setError("");
    const valores = Object.fromEntries(new FormData(event.currentTarget).entries());
    try { onSuccess(await iniciarSesionAdmin(String(valores.usuario), String(valores.password))); }
    catch (exception) { setError(exception instanceof Error ? exception.message : "No fue posible iniciar sesión."); }
    finally { setCargando(false); }
  }
  return <section className="card admin-login"><span className="status">NIVEL ADMINISTRATIVO</span><h2>Iniciar sesión</h2><form onSubmit={enviar} className="student-form"><label>Usuario<input required name="usuario" autoComplete="username" /></label><label>Contraseña<input required type="password" name="password" autoComplete="current-password" /></label><button disabled={cargando} type="submit">{cargando ? "Ingresando..." : "Ingresar"}</button>{error && <div className="alert error">{error}</div>}</form><button className="secondary" onClick={onBack}>Volver</button></section>;
}
