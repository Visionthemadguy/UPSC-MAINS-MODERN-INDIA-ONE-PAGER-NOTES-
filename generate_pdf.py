import re
from markdown import markdown
from bs4 import BeautifulSoup

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


# Create PDF
doc = SimpleDocTemplate(
    "UPSC_OnePager_Notes.pdf",
    pagesize=A4,
    leftMargin=0.4 * inch,
    rightMargin=0.4 * inch,
    topMargin=0.4 * inch,
    bottomMargin=0.4 * inch
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontSize=14,
    alignment=TA_CENTER,
    spaceAfter=10
)

heading_style = ParagraphStyle(
    "Heading",
    parent=styles["Heading2"],
    fontSize=10,
    spaceAfter=6
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=8,
    leading=10,
    spaceAfter=3
)

story = []

# Read markdown
with open("notes.md", "r", encoding="utf-8") as f:
    md = f.read()

# Split by microtheme
microthemes = re.split(r'(?=# MICROTHEME)', md)

for mt in microthemes:

    if not mt.strip():
        continue

    lines = mt.splitlines()

    title = lines[0].replace("#", "").strip()

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 5))

    # Convert markdown → HTML
    html = markdown(
        "\n".join(lines[1:]),
        extensions=["tables"]
    )

    soup = BeautifulSoup(html, "html.parser")

    for item in soup.find_all(
            ["h2", "h3", "h4", "p", "li", "table"]):

        # TABLES
        if item.name == "table":

            data = []

            for row in item.find_all("tr"):

                cols = row.find_all(["th", "td"])

                data.append([
                    col.get_text(" ", strip=True)
                    for col in cols
                ])

            if data:

                table = Table(data)

                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0),
                     colors.lightgrey),

                    ('TEXTCOLOR', (0, 0), (-1, 0),
                     colors.black),

                    ('GRID', (0, 0), (-1, -1),
                     0.5, colors.black),

                    ('FONTNAME', (0, 0), (-1, 0),
                     'Helvetica-Bold'),

                    ('FONTSIZE', (0, 0), (-1, -1), 7),

                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),

                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),

                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4)
                ]))

                story.append(table)
                story.append(Spacer(1, 8))

        # HEADINGS
        elif item.name in ["h2", "h3", "h4"]:

            story.append(
                Paragraph(
                    item.get_text(" ", strip=True),
                    heading_style
                )
            )

        # NORMAL TEXT
        else:

            text = item.get_text(" ", strip=True)

            if text:
                story.append(
                    Paragraph(text, body_style)
                )

    # New microtheme starts on fresh page
    story.append(PageBreak())

doc.build(story)

print("PDF created successfully!")
