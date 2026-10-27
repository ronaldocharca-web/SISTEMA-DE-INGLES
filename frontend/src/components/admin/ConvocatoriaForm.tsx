"use client";

import { FormEvent, useState } from "react";

import { Convocatoria } from "@/models/admin";
import { crearConvocatoriaAdmin } from "@/services/adminService";

type Props = {
  token: string;
  actual: Convocatoria | null;
  onSaved: () => Promise<void>;
};

export function ConvocatoriaForm({ token, actual, onSaved }: Props) {
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  async function guardar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formulario = event.currentTarget;
    const valores = Object.fromEntries(new FormData(formulario).entries());
    const inicio = new Date(String(valores.inicio));
    const fin = new Date(String(valores.fin));

    if (fin <= inicio) {
      setError("La fecha final debe ser posterior a la fecha inicial.");
      return;
    }
    if (actual && !window.confirm("Se cerrará la convocatoria actual y la tabla comenzará vacía para el nuevo período. Los datos anteriores se conservarán. ¿Continuar?")) {
      return;
    }

    setCargando(true);
    setMensaje("");
    setError("");
    try {
      await crearConvocatoriaAdmin(
        token,
        String(valores.nombre),
        Number(valores.gestion),
        String(valores.semestre) as "Primer semestre" | "Segundo semestre",
        inicio.toISOString(),
        fin.toISOString(),
      );
      formulario.reset();
      setMensaje("Convocatoria guardada. Los estudiantes solo podrán registrarse dentro del intervalo indicado.");
      await onSaved();
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "No fue posible guardar la convocatoria.");
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="admin-convocatoria">
      <span className="status">NUEVO PERÍODO</span>
      <h3>Crear convocatoria</h3>
      <p className="hint">Define el período para un nuevo examen. La convocatoria actual pasará al historial y conservará sus estudiantes.</p>
      <form onSubmit={guardar} className="student-form convocatoria-form">
        <label>Nombre de la convocatoria<input required name="nombre" placeholder="Ejemplo: Examen de clasificación de inglés" /></label>
        <div className="form-grid-2">
          <label>Gestión<input required type="number" name="gestion" min="2000" max="2100" defaultValue={new Date().getFullYear()} /></label>
          <label>Semestre<select required name="semestre" defaultValue="Segundo semestre"><option value="Primer semestre">Primer semestre</option><option value="Segundo semestre">Segundo semestre</option></select></label>
        </div>
        <div className="date-grid">
          <label>Desde<input required type="datetime-local" name="inicio" /></label>
          <label>Hasta<input required type="datetime-local" name="fin" /></label>
        </div>
        <button disabled={cargando} type="submit">{cargando ? "Guardando..." : actual ? "Iniciar nueva convocatoria" : "Habilitar inscripciones"}</button>
      </form>
      {mensaje && <div className="alert success">{mensaje}</div>}
      {error && <div className="alert error">{error}</div>}
    </div>
  );
}
