import re
import markdown2
from bs4 import BeautifulSoup

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

# ---------------- PDF SETUP ----------------

doc = SimpleDocTemplate(
    "UPSC_OnePager_Notes.pdf",
    pagesize=A4,
    leftMargin=0.45 * inch,
    rightMargin=0.45 * inch,
    topMargin=0.45 * inch,
    bottomMargin=0.45 * inch
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    alignment=TA_CENTER,
    fontSize=14,
    spaceAfter=10
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=10,
    spaceBefore=8,
    spaceAfter=5
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=8,
    leading=10,
    spaceAfter=3
)

story = []

# ---------------- READ FILE ----------------

with open("notes.md", "r", encoding="utf-8") as f:
    md = f.read()

microthemes = re.split(r'(?=# MICROTHEME)', md)

for mt in microthemes:

    if not mt.strip():
        continue

    lines = mt.splitlines()

    title = lines[0].replace("#", "").strip()

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 6))

    i = 1

    while i < len(lines):

        line = lines[i].strip()

        # ---------- TABLE DETECTION ----------
        if line.startswith("|"):

            table_lines = []

            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1

            data = []

            for row in table_lines:

                cells = [
                    c.strip()
                    for c in row.strip("|").split("|")
                ]

                # skip separator rows
                if all(
                    set(cell) <= set("-:")
                    for cell in cells
                ):
                    continue

                data.append(cells)

            if data:

                max_cols = max(len(r) for r in data)

                for r in data:
                    while len(r) < max_cols:
                        r.append("")

                usable_width = A4[0] - (0.9 * inch)

                tbl = Table(
                    data,
                    colWidths=[usable_width / max_cols] * max_cols,
                    repeatRows=1
                )

                tbl.setStyle(TableStyle([
                    ('BACKGROUND',
                     (0, 0), (-1, 0),
                     colors.lightgrey),

                    ('FONTNAME',
                     (0, 0), (-1, 0),
                     'Helvetica-Bold'),

                    ('GRID',
                     (0, 0), (-1, -1),
                     0.5, colors.black),

                    ('VALIGN',
                     (0, 0), (-1, -1),
                     'TOP'),

                    ('FONTSIZE',
                     (0, 0), (-1, -1),
                     7),

                    ('LEFTPADDING',
                     (0, 0), (-1, -1),
                     4),

                    ('RIGHTPADDING',
                     (0, 0), (-1, -1),
                     4),

                    ('TOPPADDING',
                     (0, 0), (-1, -1),
                     4),

                    ('BOTTOMPADDING',
                     (0, 0), (-1, -1),
                     4),
                ]))

                story.append(tbl)
                story.append(Spacer(1, 8))

        # ---------- NORMAL CONTENT ----------
        else:

            html = markdown2.markdown(line)

            soup = BeautifulSoup(html, "html.parser")

            for item in soup.find_all(
                    ["h1", "h2", "h3", "h4", "p", "li"]):

                text = item.get_text(" ", strip=True)

                if not text:
                    continue

                if item.name in ["h1", "h2", "h3", "h4"]:

                    story.append(
                        Paragraph(text, heading_style)
                    )

                else:

                    story.append(
                        Paragraph(text, body_style)
                    )

            i += 1

    story.append(PageBreak())

# ---------------- BUILD PDF ----------------

doc.build(story)

print("PDF created successfully!")
