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

# ------------------------------------------------
# PDF SETUP
# ------------------------------------------------

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

# ------------------------------------------------
# READ MARKDOWN
# ------------------------------------------------

with open("notes.md", "r", encoding="utf-8") as f:
    md = f.read()

# Split into microthemes
microthemes = re.split(r'(?=# MICROTHEME)', md)

for mt in microthemes:

    if not mt.strip():
        continue

    lines = mt.splitlines()

    title = lines[0].replace("#", "").strip()

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 6))

    content = "\n".join(lines[1:])

    # ------------------------------------------------
    # FIX TABLES AUTOMATICALLY
    # Adds blank line before any table row
    # ------------------------------------------------

    content = re.sub(
        r'(\*\*.*?\*\*)\n(\|)',
        r'\1\n\n\2',
        content
    )

    # Convert markdown to HTML with table support
    html = markdown2.markdown(
        content,
        extras=[
            "tables",
            "fenced-code-blocks",
            "strike",
            "task_list"
        ]
    )

    soup = BeautifulSoup(html, "html.parser")
    print(html)
    for item in soup.find_all(
            ["h1", "h2", "h3", "h4",
             "p", "li", "table"]):

        # ----------------------------------------
        # TABLES
        # ----------------------------------------
        if item.name == "table":

            data = []

            for row in item.find_all("tr"):

                cols = row.find_all(["th", "td"])

                data.append([
                    c.get_text(" ", strip=True)
                    for c in cols
                ])

            if data:

                col_width = (
                    (A4[0] - 0.9 * inch)
                    / len(data[0])
                )

                tbl = Table(
                    data,
                    colWidths=[col_width] * len(data[0]),
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

        # ----------------------------------------
        # HEADINGS
        # ----------------------------------------
        elif item.name in ["h1", "h2", "h3", "h4"]:

            story.append(
                Paragraph(
                    item.get_text(" ", strip=True),
                    heading_style
                )
            )

        # ----------------------------------------
        # PARAGRAPHS / LISTS
        # ----------------------------------------
        else:

            text = item.get_text(" ", strip=True)

            if text:
                story.append(
                    Paragraph(text, body_style)
                )

    # Each microtheme starts on fresh page
    story.append(PageBreak())

# ------------------------------------------------
# BUILD PDF
# ------------------------------------------------

doc.build(story)

print("PDF created successfully!")
