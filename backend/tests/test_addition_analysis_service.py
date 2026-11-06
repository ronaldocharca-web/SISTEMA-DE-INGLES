import unittest

from app.services.addition_analysis_service import AdditionAnalysisService


class ExtractorFalso:
    def __init__(self, registros, promedio_general):
        self.registros = registros
        self.promedio_general = promedio_general

    def extraer(self, _contenido):
        return self.registros, "1234567", "Ana Pérez", "20201234", [], [], self.promedio_general


class RepositorioFalso:
    def __init__(self, minimo=75, registrado=False):
        self.minimo = minimo
        self.registrado = registrado

    def obtener_promedio_minimo(self):
        return self.minimo

    def esta_registrado(self, _ci, _ru):
        return self.registrado

    def registrar_incidencia(self, *_datos):
        pass


def materia(nota, observacion="APROBADO", sigla="TUR 100"):
    return {
        "ci": "1234567", "gestion": "2026", "periodo": "PRIMERO", "numero": 1,
        "sigla": sigla, "materia": "Materia de prueba", "paralelo": "A", "nota": nota,
        "folio": "", "libro": "", "observacion": observacion, "docente": "",
    }


def servicio(registros, minimo=75, promedio_general=80):
    instancia = AdditionAnalysisService()
    instancia.extractor = ExtractorFalso(registros, promedio_general)
    instancia.repository = RepositorioFalso(minimo)
    return instancia


class AdditionAnalysisServiceTests(unittest.TestCase):
    def test_habilita_si_no_hay_reprobados_ni_abandonos_y_alcanza_promedio(self):
        resultado = servicio([materia(20), materia(30)], promedio_general=85).analizar(b"pdf", "historial.pdf")
        self.assertEqual(resultado["estado"], "PUEDE_SOLICITAR")
        self.assertEqual(resultado["promedio"], 85)

    def test_muestra_todas_las_razones_de_rechazo(self):
        resultado = servicio([
            materia(50, "REPROBADO", "TUR 101"),
            materia(0, "ABANDONADO", "TUR 102"),
        ], promedio_general=40).analizar(b"pdf", "historial.pdf")
        self.assertEqual(resultado["estado"], "NO_PUEDE_SOLICITAR")
        self.assertEqual(len(resultado["motivos"]), 3)
        self.assertEqual(len(resultado["materias_observadas"]), 2)

    def test_respeta_promedio_configurado_por_administrador(self):
        resultado = servicio([materia(100)], minimo=85, promedio_general=80).analizar(b"pdf", "historial.pdf")
        self.assertEqual(resultado["estado"], "NO_PUEDE_SOLICITAR")
        self.assertIn("85.00", resultado["motivos"][0])

    def test_rechaza_historial_sin_promedio_general(self):
        resultado = servicio([materia(90)], promedio_general=None).analizar(b"pdf", "historial.pdf")
        self.assertEqual(resultado["estado"], "PDF_NO_VALIDO")
        self.assertIn("PROM.GRAL.", resultado["advertencias"][0])
