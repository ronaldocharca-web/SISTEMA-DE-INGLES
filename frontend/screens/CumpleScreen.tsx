"use client";

import { FormEvent, useState } from "react";
import { ResultadoAnalisis } from "../models/historial";

type Props = { resultado: ResultadoAnalisis; onBack: () => void };

export function CumpleScreen({ resultado, onBack }: Props) {
  const [enviado, setEnviado] = useState(false);
  function enviar(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setEnviado(true); }
  return <section className="card"><div className="result puede_tomar"><span className="status">CUMPLE LOS REQUISITOS</span><h2>Puede continuar con el registro</h2><p>{resultado.mensaje}</p></div>{enviado ? <div className="alert success">Datos registrados correctamente para continuar con el trámite.</div> : <form onSubmit={enviar} className="student-form"><h2>Datos del estudiante</h2><label>Nombre completo<input required name="nombre" defaultValue={resultado.nombre} /></label><label>Cédula de identidad<input required name="ci" defaultValue={resultado.ci} /></label><label>RU<input required name="ru" defaultValue={resultado.ru} /></label><label>Correo electrónico<input required type="email" name="correo" /></label><label>Número de celular<input required name="celular" /></label><button type="submit">Continuar</button></form>}<button className="secondary" type="button" onClick={onBack}>Analizar otro historial</button></section>;
}
