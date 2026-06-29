```python
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

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

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

with open("notes.md", "r", encoding="utf-8") as f:
    md = f.read()

microthemes = re.split(r'(?=# MICROTHEME)', md)

for mt in microthemes:

    if not mt.strip():
        continue

    lines = mt.splitlines()

    title = lines[0].replace("#", "").strip()

    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 5))

    # -------- Detect and convert broken pipe tables --------
    processed_lines = []
    table_buffer = []

    for line in lines[1:]:

        # Line looks like a table row
        if line.count("|") >= 2:

            cleaned = line.strip()

            if cleaned.startswith("|"):
                cleaned = cleaned[1:]

            if cleaned.endswith("|"):
                cleaned = cleaned[:-1]

            cols = [c.strip() for c in cleaned.split("|")]

            # Ignore markdown separator rows
            if all(set(c) <= {"-"} for c in cols):
                continue

            table_buffer.append(cols)

        else:

            # Flush buffered table
            if table_buffer:

                table = Table(table_buffer)

                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0),
                     colors.lightgrey),

                    ('GRID', (0, 0), (-1, -1),
                     0.5, colors.black),

                    ('FONTNAME', (0, 0), (-1, 0),
                     'Helvetica-Bold'),

                    ('FONTSIZE', (0, 0), (-1, -1), 7),

                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))

                story.append(table)
                story.append(Spacer(1, 8))
                table_buffer = []

            processed_lines.append(line)

    # Flush last table if file ended with one
    if table_buffer:

        table = Table(table_buffer)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0),
             colors.lightgrey),

            ('GRID', (0, 0), (-1, -1),
             0.5, colors.black),

            ('FONTNAME', (0, 0), (-1, 0),
             'Helvetica-Bold'),

            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ]))

        story.append(table)
        story.append(Spacer(1, 8))

    # -------- Normal markdown processing --------

    html = markdown2.markdown(
        "\n".join(processed_lines)
    )

    soup = BeautifulSoup(html, "html.parser")

    for item in soup.find_all(
            ["h2", "h3", "h4", "p", "li"]):

        if item.name in ["h2", "h3", "h4"]:

            story.append(
                Paragraph(
                    item.get_text(" ", strip=True),
                    heading_style
                )
            )

        else:

            text = item.get_text(" ", strip=True)

            if text:
                story.append(
                    Paragraph(text, body_style)
                )

    story.append(PageBreak())

doc.build(story)

print("PDF created successfully!")
```
