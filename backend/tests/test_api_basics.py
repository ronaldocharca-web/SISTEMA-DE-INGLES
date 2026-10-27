import unittest

from fastapi.testclient import TestClient

from app.main import app


class ApiBasicsTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_responde_correctamente(self):
        respuesta = self.client.get("/health")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {"status": "ok"})

    def test_analisis_rechaza_archivo_no_pdf(self):
        respuesta = self.client.post(
            "/api/v1/historiales/analizar",
            files={"archivo": ("documento.txt", b"texto", "text/plain")},
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["detail"], "Solo se aceptan archivos PDF.")

    def test_modulos_admin_conservan_sus_rutas_publicas(self):
        rutas = set(app.openapi()["paths"])
        esperadas = {
            "/api/v1/admin/login",
            "/api/v1/admin/credenciales",
            "/api/v1/admin/estudiantes",
            "/api/v1/admin/convocatoria",
            "/api/v1/admin/convocatoria/fin",
            "/api/v1/admin/estudiantes/exportar",
            "/api/v1/admin/estudiantes/exportar-word",
            "/api/v1/admin/estudiantes/exportar-pdf",
        }

        self.assertTrue(esperadas.issubset(rutas))
