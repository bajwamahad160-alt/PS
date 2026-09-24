#!/usr/bin/env python3
"""Build the full book PDF from the chapter files.

Run this after every chapter is added or changed:

    python3 book/build_pdf.py

It collects every book/chapters/chapter-*.md in order and writes
book/The-Forgotten-Seven.pdf with a cover, title page, contents page and
all chapters. If book/art/cover.png or book/art/cover.jpg exists, that
image becomes the cover; otherwise a simple typographic cover is drawn.
"""

import datetime
import glob
import os
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)
from reportlab.platypus.tableofcontents import TableOfContents

BOOK_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BOOK_DIR, "fonts")
CHAPTER_DIR = os.path.join(BOOK_DIR, "chapters")
ART_DIR = os.path.join(BOOK_DIR, "art")
OUTPUT = os.path.join(BOOK_DIR, "The-Forgotten-Seven.pdf")

TITLE = "The Forgotten Seven"
AUTHOR = "Mahad A. Bajwa"

PAGE_W, PAGE_H = 6 * inch, 9 * inch
MARGIN_IN, MARGIN_OUT = 0.75 * inch, 0.6 * inch
MARGIN_TOP, MARGIN_BOTTOM = 0.8 * inch, 0.8 * inch

NAVY = HexColor("#141b2d")
GOLD = HexColor("#c9a54a")
INK = HexColor("#1c1c1c")
GREY = HexColor("#6b6b6b")


def register_fonts():
    fonts = {
        "Crimson": "CrimsonText-Regular.ttf",
        "Crimson-Italic": "CrimsonText-Italic.ttf",
        "Crimson-Bold": "CrimsonText-Bold.ttf",
        "Crimson-BoldItalic": "CrimsonText-BoldItalic.ttf",
        "Cinzel": "Cinzel.ttf",
    }
    for name, filename in fonts.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, filename)))
    pdfmetrics.registerFontFamily(
        "Crimson",
        normal="Crimson",
        italic="Crimson-Italic",
        bold="Crimson-Bold",
        boldItalic="Crimson-BoldItalic",
    )


STYLES = {
    "body": ParagraphStyle(
        "body", fontName="Crimson", fontSize=11, leading=15.2,
        alignment=TA_JUSTIFY, firstLineIndent=14, textColor=INK,
    ),
    "body_first": ParagraphStyle(
        "body_first", fontName="Crimson", fontSize=11, leading=15.2,
        alignment=TA_JUSTIFY, firstLineIndent=0, textColor=INK,
    ),
    "chapter_label": ParagraphStyle(
        "chapter_label", fontName="Cinzel", fontSize=11, leading=14,
        alignment=TA_CENTER, textColor=GOLD, spaceBefore=1.1 * inch,
    ),
    "chapter_title": ParagraphStyle(
        "chapter_title", fontName="Cinzel", fontSize=22, leading=28,
        alignment=TA_CENTER, textColor=INK, spaceBefore=6, spaceAfter=34,
    ),
    "scene_break": ParagraphStyle(
        "scene_break", fontName="Crimson", fontSize=11, leading=15,
        alignment=TA_CENTER, textColor=GREY, spaceBefore=8, spaceAfter=8,
    ),
    "title_page": ParagraphStyle(
        "title_page", fontName="Cinzel", fontSize=26, leading=34,
        alignment=TA_CENTER, textColor=INK, spaceBefore=2 * inch,
    ),
    "title_author": ParagraphStyle(
        "title_author", fontName="Crimson-Italic", fontSize=14, leading=18,
        alignment=TA_CENTER, textColor=GREY, spaceBefore=24,
    ),
    "small_center": ParagraphStyle(
        "small_center", fontName="Crimson", fontSize=9, leading=13,
        alignment=TA_CENTER, textColor=GREY,
    ),
    "contents_heading": ParagraphStyle(
        "contents_heading", fontName="Cinzel", fontSize=16, leading=20,
        alignment=TA_CENTER, textColor=INK, spaceBefore=0.8 * inch,
        spaceAfter=24,
    ),
    "toc_entry": ParagraphStyle(
        "toc_entry", fontName="Crimson", fontSize=12, leading=18,
        textColor=INK,
    ),
}


def smart_quotes(text):
    """Turn straight quotes into curly ones, the way a printed book has them."""
    # A quote opens at the start of a line or after a space, bracket or dash,
    # even with italic/bold asterisks in between (*"Hey!"* or *'Cable Street'*).
    text = re.sub(r'(^|[\s(\[{—])(\**)"', "\\1\\2\u201c", text)
    text = text.replace('"', "\u201d")
    text = re.sub(r"(^|[\s(\[{—])(\**)'", "\\1\\2\u2018", text)
    text = text.replace("'", "\u2019")
    return text


def inline_markup(text):
    """Convert the small amount of Markdown the chapters use into ReportLab markup."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = smart_quotes(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",
    7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven",
    12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
    16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen",
    20: "Twenty",
}


def parse_chapter(path, number):
    """Split a chapter file into its title and a list of paragraphs/breaks."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    title = f"Chapter {NUMBER_WORDS.get(number, number)}"
    name = ""
    if lines and lines[0].startswith("# "):
        heading = lines.pop(0)[2:].strip()
        if ":" in heading:
            title, name = [part.strip() for part in heading.split(":", 1)]
        else:
            name = heading

    blocks, current = [], []
    for line in lines + [""]:
        stripped = line.strip()
        if stripped == "---":
            if current:
                blocks.append(" ".join(current))
                current = []
            blocks.append(None)  # scene break
        elif stripped == "":
            if current:
                blocks.append(" ".join(current))
                current = []
        else:
            current.append(stripped)
    return title, name, blocks


class BookTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, pagesize=(PAGE_W, PAGE_H), **kwargs)
        full = Frame(0, 0, PAGE_W, PAGE_H, id="full", leftPadding=0,
                     rightPadding=0, topPadding=0, bottomPadding=0)
        body = Frame(MARGIN_IN, MARGIN_BOTTOM, PAGE_W - MARGIN_IN - MARGIN_OUT,
                     PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="body")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[full], onPage=draw_cover),
            PageTemplate(id="front", frames=[body]),
            PageTemplate(id="chapter_open", frames=[body], onPage=draw_footer),
            PageTemplate(id="chapter", frames=[body], onPage=draw_header_footer),
        ])

    def afterFlowable(self, flowable):
        if getattr(flowable, "toc_entry", None):
            self.notify("TOCEntry", (0, flowable.toc_entry, self.page))


def find_cover_image():
    for ext in ("png", "jpg", "jpeg"):
        path = os.path.join(ART_DIR, f"cover.{ext}")
        if os.path.exists(path):
            return path
    return None


def draw_cover(canvas, doc):
    canvas.saveState()
    image = find_cover_image()
    if image:
        canvas.drawImage(image, 0, 0, PAGE_W, PAGE_H,
                         preserveAspectRatio=False, mask="auto")
    else:
        canvas.setFillColor(NAVY)
        canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        canvas.setStrokeColor(GOLD)
        canvas.setLineWidth(0.8)
        canvas.rect(0.3 * inch, 0.3 * inch, PAGE_W - 0.6 * inch,
                    PAGE_H - 0.6 * inch, stroke=1, fill=0)
        canvas.setFillColor(GOLD)
        canvas.setFont("Cinzel", 30)
        canvas.drawCentredString(PAGE_W / 2, PAGE_H - 2.0 * inch, "THE")
        canvas.drawCentredString(PAGE_W / 2, PAGE_H - 2.55 * inch, "FORGOTTEN")
        canvas.drawCentredString(PAGE_W / 2, PAGE_H - 3.1 * inch, "SEVEN")
        emblem = os.path.join(ART_DIR, "reqrium-emblem-gold.png")
        if os.path.exists(emblem):
            size = 2.2 * inch
            canvas.drawImage(emblem, (PAGE_W - size) / 2, PAGE_H / 2 - 1.9 * inch,
                             size, size, mask="auto", preserveAspectRatio=True)
        canvas.setFont("Cinzel", 14)
        canvas.drawCentredString(PAGE_W / 2, 1.0 * inch, AUTHOR.upper())
    canvas.restoreState()


def draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Crimson", 9)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(PAGE_W / 2, 0.45 * inch, str(doc.page))
    canvas.restoreState()


def draw_header_footer(canvas, doc):
    draw_footer(canvas, doc)
    canvas.saveState()
    canvas.setFont("Cinzel", 7.5)
    canvas.setFillColor(GREY)
    label = AUTHOR.upper() if doc.page % 2 == 0 else TITLE.upper()
    canvas.drawCentredString(PAGE_W / 2, PAGE_H - 0.5 * inch, label)
    canvas.restoreState()


def build():
    register_fonts()
    chapter_files = sorted(glob.glob(os.path.join(CHAPTER_DIR, "chapter-*.md")))
    story = []

    # Cover
    story += [NextPageTemplate("front"), Spacer(1, 1), PageBreak()]

    # Title page
    story += [
        Paragraph(TITLE.upper(), STYLES["title_page"]),
        Paragraph(AUTHOR, STYLES["title_author"]),
        PageBreak(),
    ]

    # Copyright-style page
    today = datetime.date.today().strftime("%B %d, %Y")
    story += [
        Spacer(1, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM - 1.2 * inch),
        Paragraph(f"{TITLE}", STYLES["small_center"]),
        Paragraph(f"Copyright \u00a9 {datetime.date.today().year} {AUTHOR}. "
                  "All rights reserved.", STYLES["small_center"]),
        Paragraph(f"Draft edition, built {today}.", STYLES["small_center"]),
        PageBreak(),
    ]

    # Contents
    toc = TableOfContents()
    toc.levelStyles = [STYLES["toc_entry"]]
    toc.dotsMinLevel = 0
    story += [Paragraph("Contents", STYLES["contents_heading"]), toc]

    # Chapters
    for number, path in enumerate(chapter_files, start=1):
        label, name, blocks = parse_chapter(path, number)
        story += [NextPageTemplate("chapter_open"), PageBreak(),
                  NextPageTemplate("chapter")]
        label_para = Paragraph(inline_markup(label).upper(), STYLES["chapter_label"])
        title_para = Paragraph(inline_markup(name), STYLES["chapter_title"])
        title_para.toc_entry = f"{label}: {name}" if name else label
        story += [label_para, title_para]

        first = True
        for block in blocks:
            if block is None:
                story.append(Paragraph("*\u2003*\u2003*", STYLES["scene_break"]))
                first = True
                continue
            style = STYLES["body_first"] if first else STYLES["body"]
            story.append(Paragraph(inline_markup(block), style))
            first = False

    doc = BookTemplate(OUTPUT, title=TITLE, author=AUTHOR)
    doc.multiBuild(story)
    print(f"Wrote {os.path.relpath(OUTPUT)} with {len(chapter_files)} chapter(s), "
          f"{doc.page} pages.")


if __name__ == "__main__":
    build()
