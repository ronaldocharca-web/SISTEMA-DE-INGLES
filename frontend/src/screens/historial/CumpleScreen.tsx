"use client";

import { FormEvent, useState } from "react";
import { ResultadoAnalisis } from "@/models/historial";
import { registrarEstudiante } from "@/services/historialService";

type Props = { resultado: ResultadoAnalisis; onBack: () => void };

export function CumpleScreen({ resultado, onBack }: Props) {
  const [estado, setEstado] = useState<"idle" | "loading" | "success" | "duplicate" | "error">("idle");
  const [mensaje, setMensaje] = useState("");

  async function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const valores = Object.fromEntries(new FormData(event.currentTarget).entries());
    setEstado("loading");
    try {
      const respuesta = await registrarEstudiante({
        nombre: String(valores.nombre),
        ci: String(valores.ci),
        ru: String(valores.ru),
        correo: String(valores.correo),
        celular: String(valores.celular),
      });
      setMensaje(respuesta.mensaje);
      setEstado(respuesta.duplicado ? "duplicate" : "success");
    } catch (error) {
      setMensaje(error instanceof Error ? error.message : "No fue posible registrar los datos.");
      setEstado("error");
    }
  }

  return <section className="card"><div className="result puede_tomar"><span className="status">CUMPLE LOS REQUISITOS</span><h2>Puede continuar con el registro</h2><p>{resultado.mensaje}</p></div>{estado === "success" || estado === "duplicate" ? <div className={`alert ${estado === "duplicate" ? "error" : "success"}`}><strong>{estado === "duplicate" ? "Tú ya te inscribiste antes" : "Registro realizado"}</strong><p>{mensaje}</p></div> : <form onSubmit={enviar} className="student-form"><h2>Datos del estudiante</h2><label>Nombre completo<input required name="nombre" defaultValue={resultado.nombre} /></label><label>Cédula de identidad<input required name="ci" defaultValue={resultado.ci} /></label><label>RU<input required name="ru" defaultValue={resultado.ru} /></label><label>Correo electrónico<input required type="email" name="correo" /></label><label>Número de celular<input required name="celular" /></label><button disabled={estado === "loading"} type="submit">{estado === "loading" ? "Guardando..." : "Guardar datos"}</button>{estado === "error" && <div className="alert error">{mensaje}</div>}</form>}<button className="secondary" type="button" onClick={onBack}>Analizar otro historial</button></section>;
}
