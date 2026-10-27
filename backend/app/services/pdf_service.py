from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generar_pdf_estudiantes(estudiantes: list[dict[str, str]], convocatoria: dict | None) -> bytes:
    """Genera el listado PDF del examen, con una fila por estudiante."""
    datos = convocatoria or {}
    gestion = datos.get("gestion", "")
    semestre = str(datos.get("semestre", "")).upper()
    periodo = f"GESTIÓN {gestion}, {semestre}" if gestion and semestre else ""
    titulo = "EXAMEN DE CLASIFICACIÓN DE INGLÉS"
    if periodo:
        titulo = f"{titulo} - {periodo}"

    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=letter,
        rightMargin=0.42 * inch,
        leftMargin=0.42 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch,
    )
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "TituloExamen",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=4,
    )
    estilo_subtitulo = ParagraphStyle(
        "SubtituloExamen",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=10,
    )
    estilo_celda = ParagraphStyle(
        "CeldaExamen",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        textColor=colors.black,
    )
    estilo_celda_centrada = ParagraphStyle(
        "CeldaCentradaExamen",
        parent=estilo_celda,
        alignment=TA_CENTER,
    )

    filas = [["N°", "NOMBRE", "CÉDULA", "NOTA", "NIVEL", "OBS"]]
    for numero, estudiante in enumerate(estudiantes, start=1):
        filas.append([
            Paragraph(str(numero), estilo_celda_centrada),
            Paragraph(str(estudiante.get("Nombre", "")), estilo_celda),
            Paragraph(str(estudiante.get("CI", "")), estilo_celda_centrada),
            Paragraph("", estilo_celda_centrada),
            Paragraph("", estilo_celda_centrada),
            Paragraph("", estilo_celda),
        ])
    if not estudiantes:
        filas.append([Paragraph("No hay estudiantes registrados.", estilo_celda_centrada), "", "", "", "", ""])

    tabla = Table(filas, colWidths=[0.35 * inch, 3.02 * inch, 1.05 * inch, 0.62 * inch, 0.72 * inch, 1.05 * inch], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9E9E9E")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elementos = [Paragraph(titulo, estilo_titulo), Paragraph(str(datos.get("nombre", "")), estilo_subtitulo), tabla]
    documento.build(elementos)
    salida.seek(0)
    return salida.getvalue()
