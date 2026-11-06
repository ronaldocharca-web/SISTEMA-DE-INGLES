from io import BytesIO
import unittest

from openpyxl import load_workbook

from app.repositories.student_repository import StudentRepository


class SupabaseStudentRepository(StudentRepository):
    @property
    def usa_supabase(self) -> bool:
        return True

    def listar(self, convocatoria_id=None):
        return [{
            "Fecha": "2026-11-05",
            "Nombre": "Ana Pérez",
            "CI": "123",
            "RU": "456",
            "Correo": "ana@example.com",
            "Celular": "70000000",
        }]

    def listar_incidencias(self, convocatoria_id=None):
        return []


class StudentExcelTests(unittest.TestCase):
    def test_exportacion_contiene_solo_las_tres_hojas_utiles(self):
        contenido = SupabaseStudentRepository().generar_excel(
            "convocatoria-1",
            {"nombre": "Prueba 2", "gestion": 2026, "semestre": "Segundo semestre"},
        )

        libro = load_workbook(BytesIO(contenido), read_only=True)
        self.assertEqual(libro.sheetnames, ["Convocatoria", "Estudiantes", "Incidencias"])
        self.assertEqual(libro["Convocatoria"]["B2"].value, "Prueba 2")
        self.assertEqual(libro["Estudiantes"]["B2"].value, "Ana Pérez")
        self.assertNotIn("Sheet", libro.sheetnames)


if __name__ == "__main__":
    unittest.main()
