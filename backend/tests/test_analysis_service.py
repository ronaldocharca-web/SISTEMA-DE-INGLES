import unittest

from app.services.analysis_service import AnalisisService
from app.services.pdf_extractor import MULTIPLES_HISTORIALES


class ExtractorFalso:
    def __init__(self, respuesta):
        self.respuesta = respuesta

    def extraer(self, _contenido):
        return self.respuesta


class EstudiantesFalsos:
    def __init__(self, inscrito=False):
        self.inscrito = inscrito
        self.incidencias = []

    def esta_registrado(self, _ci, _ru):
        return self.inscrito

    def registrar_incidencia(self, *datos):
        self.incidencias.append(datos)


def crear_servicio(respuesta_extractor, inscrito=False):
    servicio = AnalisisService()
    servicio.extractor = ExtractorFalso(respuesta_extractor)
    servicio.students = EstudiantesFalsos(inscrito)
    return servicio


class AnalisisServiceTests(unittest.TestCase):
    def test_pdf_invalido_registra_incidencia(self):
        servicio = crear_servicio(([], "", "", "", [], ["título HISTORIAL ACADEMICO"]))

        resultado = servicio.analizar(b"contenido", "archivo.pdf")

        self.assertEqual(resultado["estado"], "PDF_NO_VALIDO")
        self.assertEqual(len(servicio.students.incidencias), 1)

    def test_estudiante_ya_inscrito_no_llega_al_formulario(self):
        filas = [{"sigla": "TUR 100", "materia": "Turismo", "numero": 1}]
        servicio = crear_servicio((filas, "10921260", "Ana", "1907963", [], []), inscrito=True)

        resultado = servicio.analizar(b"contenido", "historial.pdf")

        self.assertEqual(resultado["estado"], "YA_INSCRITO")

    def test_materia_de_ingles_impide_registro(self):
        filas = [{
            "sigla": "TUR 401", "materia": "Inglés Técnico", "numero": 1,
            "nota": 80, "ci": "10921260", "gestion": "2026", "periodo": "PRIMERO",
            "paralelo": "A", "folio": "", "libro": "", "observacion": "APROBADO", "docente": "",
        }]
        servicio = crear_servicio((filas, "10921260", "Ana", "1907963", [], []))

        resultado = servicio.analizar(b"contenido", "historial.pdf")

        self.assertEqual(resultado["estado"], "NO_PUEDE_TOMAR")
        self.assertEqual(resultado["materias_requisito"][0]["sigla"], "TUR 401")

    def test_historial_sin_ingles_habilita_registro(self):
        filas = [{"sigla": "TUR 100", "materia": "Turismo", "numero": 1}]
        servicio = crear_servicio((filas, "10921260", "Ana", "1907963", [], []))

        resultado = servicio.analizar(b"contenido", "historial.pdf")

        self.assertEqual(resultado["estado"], "PUEDE_TOMAR")

    def test_pdf_con_varios_historiales_muestra_mensaje_especifico(self):
        servicio = crear_servicio(([], "1234567", "Ana", "111111", [], [MULTIPLES_HISTORIALES]))

        resultado = servicio.analizar(b"contenido", "varios.pdf")

        self.assertEqual(resultado["estado"], "PDF_NO_VALIDO")
        self.assertEqual(resultado["mensaje"], "Este PDF no está permitido.")

