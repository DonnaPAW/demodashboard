import os
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND = colors.HexColor("#ec058c")
BRAND_DARK = colors.HexColor("#c00475")
LIGHT = colors.HexColor("#fdeef3")
DARK = colors.HexColor("#000000")
BORDER = colors.HexColor("#d6d6d6")

styles = getSampleStyleSheet()
h1 = ParagraphStyle(
    "H1", parent=styles["Title"], textColor=DARK, fontName="Helvetica-Bold",
    fontSize=22, spaceAfter=2, alignment=0,
)
h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], textColor=DARK, fontName="Helvetica-Bold",
    fontSize=13, spaceBefore=14, spaceAfter=6,
)
small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#6b7280"))


def _doc(title):
    fd, path = tempfile.mkstemp(prefix=title, suffix=".pdf")
    os.close(fd)
    doc = SimpleDocTemplate(
        path, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm, title=title,
    )
    return doc, path


def _table(data, widths):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BRAND),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _kpi_box(label, value):
    t = Table([[Paragraph(f"<b>{value}</b>", styles["Normal"])], [Paragraph(label, small)]], colWidths=[4.2 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.8, BRAND_DARK),
                ("LINEBELOW", (0, 0), (-1, 0), 2, BRAND),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
            ]
        )
    )
    return t


def _kpi_row(items):
    t = Table([[_kpi_box(l, v) for l, v in items]], hAlign="LEFT")
    t.setStyle(TableStyle([("LEFTPADDING", (1, 0), (-1, -1), 8)]))
    return t


def company_pdf(report):
    company = report["company"]
    doc, path = _doc(f"Bericht_{company['name']}")

    story = [
        Paragraph("Auswertung Unternehmensbericht", h1),
        Paragraph("Demo-Dashboard · fiktive Daten", small),
        Spacer(0, 12),
        Paragraph(f"{company['name']}", h2),
        Paragraph(f"Branche: {company['industry']} · Ansprechpartner: {company['contact']}", styles["Normal"]),
        Spacer(0, 10),
    ]

    kpis = [
        ("Punkte verbraucht", str(report["points_used"])),
        ("Punkte übrig", str(report["points_left"])),
        ("Workshops insgesamt", str(report["workshop_count"])),
        ("Events insgesamt", str(report["event_count"])),
    ]
    story.append(_kpi_row(kpis))

    story.append(Paragraph("Gebuchte Events (inkl. teilnehmender Unternehmen)", h2))
    rows = [["Datum", "Event", "Typ", "Punkte", "Teilnehmende andere Unternehmen"]]
    for e in report["events"]:
        rows.append(
            [e["date"], e["title"], e["type"], str(e["point_cost"]),
             ", ".join(e["guests"]) or "—"]
        )
    story.append(_table(rows, [2.0 * cm, 5.6 * cm, 2.6 * cm, 1.5 * cm, 5.5 * cm]))

    story.append(Paragraph("Teilnahme an Events anderer Unternehmen", h2))
    if report["other_events"]:
        rows2 = [["Datum", "Event", "Gastgeber", "Typ", "Punkte"]]
        for e in report["other_events"]:
            rows2.append([e["date"], e["title"], e["host_name"], e["type"], str(e["point_cost"])])
        story.append(_table(rows2, [2.0 * cm, 6.2 * cm, 4.2 * cm, 2.8 * cm, 1.6 * cm]))
    else:
        story.append(Paragraph("Keine Teilnahmen an Events anderer Unternehmen.", styles["Normal"]))

    doc.build(story)
    return path


def overview_pdf():
    doc, path = _doc("Auswertung_Gesamt")

    story = [
        Paragraph("Gesamtauswertung", h1),
        Paragraph("Demo-Dashboard · fiktive Daten", small),
        Spacer(0, 12),
        Paragraph("Punktekontingente je Unternehmen", h2),
    ]

    data = _overview_data()
    rows = [["Unternehmen", "Branche", "Kontingent", "Verbraucht", "Übrig", "Events", "Workshops"]]
    for r in data:
        rows.append(
            [r["name"], r["industry"], str(r["points_contingent"]),
             str(r["points_used"]), str(r["points_left"]),
             str(r["bookings"]), str(r["workshops"])]
        )
    story.append(_table(rows, [4.6 * cm, 3.0 * cm, 2.2 * cm, 2.0 * cm, 1.6 * cm, 1.6 * cm, 2.0 * cm]))
    doc.build(story)
    return path


def _overview_data():
    from db import overview

    rows = overview()["companies"]
    return [
        {
            "name": r["name"],
            "industry": r["industry"],
            "points_contingent": r["points_contingent"],
            "points_used": r["points_used"],
            "points_left": r["points_contingent"] - r["points_used"],
            "bookings": r["bookings"],
            "workshops": r["workshops"] or 0,
        }
        for r in rows
    ]
