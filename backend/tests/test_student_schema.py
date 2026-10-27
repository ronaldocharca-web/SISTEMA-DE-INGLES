import unittest

from pydantic import ValidationError

from app.schemas.student import RegistroEstudianteRequest


class RegistroEstudianteSchemaTests(unittest.TestCase):
    def test_acepta_datos_validos_y_limpia_espacios(self):
        estudiante = RegistroEstudianteRequest(
            nombre="  Ana Pérez  ",
            ci=" 1234567 ",
            ru=" 20201234 ",
            correo=" ana@umsa.bo ",
            celular=" 71234567 ",
            pdf_token="00000000-0000-4000-8000-000000000001",
        )

        self.assertEqual(estudiante.nombre, "Ana Pérez")
        self.assertEqual(estudiante.ci, "1234567")
        self.assertEqual(estudiante.celular, "71234567")

    def test_rechaza_celular_demasiado_corto(self):
        with self.assertRaises(ValidationError):
            RegistroEstudianteRequest(
                nombre="Ana Pérez",
                ci="1234567",
                ru="20201234",
                correo="ana@umsa.bo",
                celular="123",
                pdf_token="00000000-0000-4000-8000-000000000001",
            )

