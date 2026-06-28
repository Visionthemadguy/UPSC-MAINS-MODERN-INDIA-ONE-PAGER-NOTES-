import re
from markdown import markdown
from bs4 import BeautifulSoup

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER


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
    'title',
    parent=styles['Heading1'],
    fontSize=14,
    alignment=TA_CENTER,
    spaceAfter=10
)

body_style = ParagraphStyle(
    'body',
    parent=styles['BodyText'],
    fontSize=8,
    leading=9.5,
    spaceAfter=3
)

story = []

with open("notes.md", encoding="utf-8") as f:
    md = f.read()

microthemes = re.split(r'(?=# MICROTHEME)', md)

for mt in microthemes:

    if not mt.strip():
        continue

    lines = mt.splitlines()

    title = lines[0].replace("#", "").strip()

    story.append(Paragraph(title, title_style))

    html = markdown("\n".join(lines[1:]))

    soup = BeautifulSoup(html, "html.parser")

    for item in soup.find_all(["h2", "h3", "h4", "p", "li"]):

        txt = item.get_text(" ", strip=True)

        if txt:
            story.append(
                Paragraph(txt, body_style)
            )

    story.append(PageBreak())

doc.build(story)

print("PDF created successfully!")
