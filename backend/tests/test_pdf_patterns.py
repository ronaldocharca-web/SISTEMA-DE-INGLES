import unittest

from app.services.pdf_extractor import (
    PATRON_CI,
    PATRON_RU,
    contiene_multiples_historiales,
)


class PdfPatternTests(unittest.TestCase):
    def test_detecta_ci_en_formatos_frecuentes(self):
        self.assertEqual(PATRON_CI.search("Cédula: 10921260").group(1), "10921260")
        self.assertEqual(
            PATRON_CI.search("C.I. de identidad: 10921260").group(1),
            "10921260",
        )

    def test_detecta_ru_sin_confundir_sigla_de_materia(self):
        self.assertEqual(PATRON_RU.search("RU: 1907963").group(1), "1907963")
        self.assertEqual(
            PATRON_RU.search("Reg. Univ.: 1907963").group(1), "1907963"
        )
        self.assertIsNone(PATRON_RU.search("TUR-401 Inglés Técnico Turístico I"))

    def test_detecta_dos_historiales_con_identidades_distintas(self):
        texto = """
        HISTORIAL ACADEMICO Nombre(s) Ana Pérez Fecha: 2026 CI: 1234567 RU: 111111
        HISTORIAL ACADEMICO Nombre(s) Luis Rojas Fecha: 2026 CI: 7654321 RU: 222222
        """

        self.assertTrue(contiene_multiples_historiales(texto))

    def test_permite_identidad_repetida_en_varias_paginas(self):
        texto = """
        Nombre(s) Ana Pérez Fecha: 2026 CI: 1234567 RU: 111111
        Nombre(s) Ana Pérez Fecha: 2026 CI: 1234567 RU: 111111
        """

        self.assertFalse(contiene_multiples_historiales(texto))

