import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from pathlib import Path

from app.repositories.pdf_usage_repository import (
    EN_USO,
    REGISTRADO,
    RESERVADO,
    PdfUsageRepository,
)


class PdfUsageRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.repository = PdfUsageRepository()
        self.repository._usar_fallback_local = True
        self.repository.path = Path(self.temporal.name) / "pdf_usos.json"
        self.convocatoria_id = "00000000-0000-0000-0000-000000000010"

    def tearDown(self):
        self.temporal.cleanup()

    def test_bloquea_el_mismo_pdf_mientras_esta_en_uso(self):
        barrera = Barrier(2)

        def reservar():
            barrera.wait()
            return self.repository.reservar(b"mismo-pdf", self.convocatoria_id)

        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(lambda _: reservar(), range(2)))

        estados = [estado for estado, _token in resultados]
        self.assertEqual(estados.count(RESERVADO), 1)
        self.assertEqual(estados.count(EN_USO), 1)

    def test_pdf_registrado_no_puede_volver_a_reservarse(self):
        estado, token = self.repository.reservar(b"pdf-registrado", self.convocatoria_id)
        self.assertEqual(estado, RESERVADO)
        self.repository.asociar_identidad(token, self.convocatoria_id, "1234567", "111111")
        self.repository.marcar_registrado(token)

        nuevo_estado, nuevo_token = self.repository.reservar(
            b"pdf-registrado",
            self.convocatoria_id,
        )

        self.assertEqual(nuevo_estado, REGISTRADO)
        self.assertIsNone(nuevo_token)
