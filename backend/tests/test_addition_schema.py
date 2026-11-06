import unittest

from pydantic import ValidationError

from app.schemas.adicion import SolicitudAdicionRequest


def solicitud(**cambios):
    datos = {
        "nombre": "Ana Pérez", "ci": "1234567", "ru": "20201234",
        "correo": "ana@umsa.bo", "celular": "71234567",
        "sigla_materia": "tur-305", "nombre_materia": "Gestión Turística",
        "semestre_materia": 5, "numero_materia_total": 7,
        "pdf_token": "00000000-0000-4000-8000-000000000001",
    }
    datos.update(cambios)
    return SolicitudAdicionRequest(**datos)


class SolicitudAdicionSchemaTests(unittest.TestCase):
    def test_acepta_semestre_y_carga_total_validos(self):
        datos = solicitud()
        self.assertEqual(datos.sigla_materia, "TUR 305")
        self.assertEqual(datos.semestre_materia, 5)
        self.assertEqual(datos.numero_materia_total, 7)

    def test_rechaza_semestre_fuera_de_rango(self):
        with self.assertRaises(ValidationError):
            solicitud(semestre_materia=11)

    def test_rechaza_sexta_materia(self):
        with self.assertRaises(ValidationError):
            solicitud(numero_materia_total=6)

    def test_acepta_octava_materia(self):
        self.assertEqual(solicitud(numero_materia_total=8).numero_materia_total, 8)
