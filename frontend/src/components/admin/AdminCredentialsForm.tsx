"use client";

import { FormEvent, useState } from "react";
import { actualizarCredencialesAdmin } from "@/services/historialService";

type Props = { token: string };

export function AdminCredentialsForm({ token }: Props) {
  const [visible, setVisible] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);
  async function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setCargando(true); setMensaje(""); setError("");
    const formulario = event.currentTarget;
    const valores = Object.fromEntries(new FormData(formulario).entries());
    try { setMensaje(await actualizarCredencialesAdmin(token, String(valores.usuario), String(valores.password))); formulario.reset(); }
    catch (exception) { setError(exception instanceof Error ? exception.message : "No fue posible actualizar las credenciales."); }
    finally { setCargando(false); }
  }
  if (!visible) return <button className="secondary" type="button" onClick={() => setVisible(true)}>Cambiar credenciales</button>;
  return <div className="admin-credentials"><h3>Cambiar usuario y contraseña</h3><form onSubmit={enviar} className="student-form"><label>Nuevo usuario<input required minLength={3} name="usuario" /></label><label>Nueva contraseña<input required minLength={8} type="password" name="password" /></label><button disabled={cargando} type="submit">{cargando ? "Guardando..." : "Guardar cambios"}</button></form>{mensaje && <div className="alert success">{mensaje}</div>}{error && <div className="alert error">{error}</div>}<button className="secondary" type="button" onClick={() => setVisible(false)}>Cancelar</button></div>;
}
