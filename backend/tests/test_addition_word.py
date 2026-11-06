from io import BytesIO
import unittest

from docx import Document

from app.services.word_service import generar_word_solicitudes_adicion


class AdditionWordTests(unittest.TestCase):
    def test_genera_word_con_datos_de_adicion(self):
        contenido = generar_word_solicitudes_adicion(
            [{
                "Nombre": "Ana Pérez",
                "CI": "123456",
                "RU": "2026001",
                "Sigla": "TUR 305",
                "Nombre de materia": "Gestión Turística",
                "Semestre de materia": "5",
                "Carga total": "6",
                "Promedio": "78.5",
                "Correo": "ana@example.com",
                "Celular": "70000000",
            }],
            {"nombre": "Prueba 2", "gestion": 2026, "semestre": "Segundo semestre"},
        )

        self.assertTrue(contenido.startswith(b"PK"))
        documento = Document(BytesIO(contenido))
        texto = " ".join(parrafo.text for parrafo in documento.paragraphs)
        celdas = " ".join(celda.text for tabla in documento.tables for fila in tabla.rows for celda in fila.cells)
        self.assertIn("SOLICITUDES DE ADICIÓN DE MATERIA", texto)
        self.assertIn("Prueba 2", texto)
        self.assertIn("Ana Pérez", celdas)
        self.assertIn("TUR 305", celdas)
        self.assertIn("Gestión Turística", celdas)


if __name__ == "__main__":
    unittest.main()
