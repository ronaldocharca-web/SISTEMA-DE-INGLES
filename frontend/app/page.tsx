import { RoleScreen } from "@/screens/RoleScreen";

export default function Home() {
  return (
    <main className="container">
      <section className="hero">
        <div className="eyebrow">Carrera de Licenciatura en Turismo</div>
        <h1>Verificación Para Ingresar al Examen de Inglés</h1>
        <p className="subtitle">
          Sube tu historial académico oficial en formato PDF para verificar automáticamente tus asignaturas y validar tu habilitación al examen.
        </p>
      </section>
      <RoleScreen />
    </main>
  );
}
