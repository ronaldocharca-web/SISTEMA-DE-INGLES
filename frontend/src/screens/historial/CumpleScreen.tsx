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

  return (
    <section className="card">
      <div className="result puede_tomar" style={{ marginTop: 0 }}>
        <span className="status">
          <span className="status-dot"></span>
          CUMPLE LOS REQUISITOS
        </span>
        <h2>Habilitado para continuar con el registro</h2>
        <p className="result-message">{resultado.mensaje}</p>
      </div>

      {estado === "success" || estado === "duplicate" ? (
        <div className={`alert ${estado === "duplicate" ? "error" : "success"}`}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span className="status-dot"></span>
            <strong style={{ fontSize: "16px" }}>
              {estado === "duplicate" ? "Inscripción previamente registrada" : "¡Registro completado exitosamente!"}
            </strong>
          </div>
          <p style={{ margin: 0 }}>{mensaje}</p>
        </div>
      ) : (
        <form onSubmit={enviar} className="student-form">
          <h2 style={{ fontSize: "20px", marginTop: "12px" }}>Confirmar datos del estudiante</h2>
          
          <label>
            Nombre completo
            <input required name="nombre" defaultValue={resultado.nombre} placeholder="Nombres y Apellidos" />
          </label>

          <div className="form-grid-2">
            <label>
              Cédula de identidad (CI)
              <input required name="ci" defaultValue={resultado.ci} placeholder="Ej: 8392102" />
            </label>
            <label>
              Registro Universitario (RU)
              <input required name="ru" defaultValue={resultado.ru} placeholder="Ej: 1729381" />
            </label>
          </div>

          <div className="form-grid-2">
            <label>
              Correo electrónico
              <input required type="email" name="correo" placeholder="estudiante@umsa.bo" />
            </label>
            <label>
              Número de WhatsApp / Celular
              <input required type="tel" name="celular" placeholder="Ej: 71234567" />
            </label>
          </div>

          <button disabled={estado === "loading"} type="submit" style={{ marginTop: "12px" }}>
            {estado === "loading" ? "Registrando estudiante..." : "Completar inscripción oficial"}
          </button>
          
          {estado === "error" && <div className="alert error">{mensaje}</div>}
        </form>
      )}

      <button className="secondary" type="button" onClick={onBack} style={{ marginTop: "16px" }}>
        ← Analizar otro historial
      </button>
    </section>
  );
}
