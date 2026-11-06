"use client";

import { FormEvent, useState } from "react";

import { ResultadoAdicion } from "@/models/addition";
import { liberarReservaAdicion, registrarSolicitudAdicion } from "@/services/additionService";

export function AdditionApprovedScreen({ resultado, onBack }: { resultado: ResultadoAdicion; onBack: () => void }) {
  const [estado, setEstado] = useState<"idle" | "loading" | "success" | "duplicate" | "error">("idle");
  const [mensaje, setMensaje] = useState("");

  async function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const valores = Object.fromEntries(new FormData(event.currentTarget).entries());
    setEstado("loading");
    try {
      const respuesta = await registrarSolicitudAdicion({
        nombre: String(valores.nombre), ci: String(valores.ci), ru: String(valores.ru),
        correo: String(valores.correo), celular: String(valores.celular),
        sigla_materia: String(valores.sigla_materia), nombre_materia: String(valores.nombre_materia),
        semestre_materia: Number(valores.semestre_materia), numero_materia_total: Number(valores.numero_materia_total),
        pdf_token: resultado.pdf_token ?? "",
      });
      setMensaje(respuesta.mensaje);
      setEstado(respuesta.duplicado ? "duplicate" : "success");
    } catch (exception) {
      setMensaje(exception instanceof Error ? exception.message : "No fue posible registrar la solicitud.");
      setEstado("error");
    }
  }

  function volver() {
    window.sessionStorage.removeItem("sistema-adicion-reserva-pdf");
    void liberarReservaAdicion(resultado.pdf_token).finally(onBack);
  }

  return (
    <section className="card">
      <div className="result puede_tomar" style={{ marginTop: 0 }}>
        <span className="status"><span className="status-dot" />CUMPLE LOS REQUISITOS</span>
        <h2>Habilitado para solicitar adición</h2>
        <p className="result-message">Promedio detectado: <strong>{resultado.promedio.toFixed(2)}</strong> (mínimo {resultado.promedio_minimo.toFixed(2)}).</p>
      </div>
      {estado === "success" || estado === "duplicate" ? (
        <div className={`alert ${estado === "duplicate" ? "error" : "success"}`}><strong>{mensaje}</strong></div>
      ) : (
        <form className="student-form" onSubmit={enviar}>
          <h2>Datos de la solicitud</h2>
          <label>Nombre completo <span className="required-mark">*</span><input required minLength={2} name="nombre" defaultValue={resultado.nombre} /></label>
          <div className="form-grid-2">
            <label>Cédula de identidad <span className="required-mark">*</span><input required minLength={3} name="ci" defaultValue={resultado.ci} /></label>
            <label>Registro Universitario <span className="required-mark">*</span><input required minLength={3} name="ru" defaultValue={resultado.ru} /></label>
          </div>
          <div className="form-grid-2">
            <label>Correo electrónico <span className="required-mark">*</span><input required type="email" name="correo" placeholder="estudiante@umsa.bo" /></label>
            <label>WhatsApp / Celular <span className="required-mark">*</span><input required type="tel" name="celular" minLength={7} maxLength={15} pattern="[0-9 +()-]{7,15}" /></label>
          </div>
          <div className="form-grid-2 subject-fields">
            <label>Sigla de la materia <span className="required-mark">*</span>
              <input required minLength={2} maxLength={30} name="sigla_materia" placeholder="Ejemplo: TUR 305" />
            </label>
            <label>Nombre de la materia <span className="required-mark">*</span>
              <input required minLength={2} maxLength={150} name="nombre_materia" placeholder="Ejemplo: Gestión Turística" />
            </label>
          </div>
          <div className="form-grid-2 subject-fields">
            <label>Semestre de la materia <span className="required-mark">*</span>
              <input required type="number" inputMode="numeric" name="semestre_materia" min="1" max="10" step="1" placeholder="Escribe un número del 1 al 10" />
            </label>
            <label>Con esta adición será tu <span className="required-mark">*</span>
              <input required type="number" inputMode="numeric" name="numero_materia_total" min="7" max="8" step="1" placeholder="Escribe 7 u 8" />
            </label>
          </div>
          <button disabled={estado === "loading"} type="submit">{estado === "loading" ? "Registrando solicitud..." : "Enviar solicitud de adición"}</button>
          {estado === "error" && <div className="alert error">{mensaje}</div>}
        </form>
      )}
      <button className="secondary" type="button" onClick={volver}>← Analizar otro historial</button>
    </section>
  );
}
