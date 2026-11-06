from __future__ import annotations

from html import escape
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import landscape, letter
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


def generar_pdf_solicitudes_adicion(
    solicitudes: list[dict[str, str]],
    convocatoria: dict | None,
) -> bytes:
    """Genera un PDF apaisado con las solicitudes de una convocatoria de adición."""
    datos = convocatoria or {}
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=landscape(letter),
        rightMargin=0.28 * inch,
        leftMargin=0.28 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch,
    )
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "TituloAdicion",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.black,
        spaceAfter=4,
    )
    subtitulo = ParagraphStyle(
        "SubtituloAdicion",
        parent=estilos["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"),
        spaceAfter=9,
    )
    celda = ParagraphStyle(
        "CeldaAdicion",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=6.2,
        leading=7.5,
        textColor=colors.black,
    )
    centrada = ParagraphStyle("CeldaAdicionCentrada", parent=celda, alignment=TA_CENTER)

    encabezados = ["N°", "NOMBRE", "CI", "RU", "SIGLA", "MATERIA", "SEM.", "CARGA", "PROM.", "CORREO", "CELULAR"]
    filas: list[list] = [encabezados]
    for numero, solicitud in enumerate(solicitudes, start=1):
        semestre = solicitud.get("Semestre de materia", "")
        carga = solicitud.get("Carga total", "")
        valores = [
            str(numero), solicitud.get("Nombre", ""), solicitud.get("CI", ""),
            solicitud.get("RU", ""), solicitud.get("Sigla", ""),
            solicitud.get("Nombre de materia", ""), f"{semestre}.º" if semestre else "—",
            f"{carga}.ª" if carga else "—", solicitud.get("Promedio", ""),
            solicitud.get("Correo", ""), solicitud.get("Celular", ""),
        ]
        filas.append([
            Paragraph(escape(str(valor)), celda if indice in (1, 5, 9) else centrada)
            for indice, valor in enumerate(valores)
        ])
    if not solicitudes:
        filas.append([Paragraph("No hay solicitudes registradas.", centrada)] + [""] * 10)

    tabla = Table(
        filas,
        colWidths=[ancho * inch for ancho in [0.28, 1.35, 0.65, 0.65, 0.58, 1.35, 0.42, 0.48, 0.48, 1.35, 0.72]],
        repeatRows=1,
    )
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#9E9E9E")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7E6E6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 6.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("SPAN", (0, 1), (-1, 1)) if not solicitudes else ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    descripcion = " · ".join(filter(None, [
        str(datos.get("nombre") or "Convocatoria"),
        f"Gestión {datos['gestion']}" if datos.get("gestion") else "",
        str(datos.get("semestre") or ""),
    ]))
    documento.build([
        Paragraph("SOLICITUDES DE ADICIÓN DE MATERIA", titulo),
        Paragraph(escape(descripcion), subtitulo),
        tabla,
    ])
    salida.seek(0)
    return salida.getvalue()
