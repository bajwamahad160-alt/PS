#!/usr/bin/env python3
"""Build the web reading page for the book from the chapter files.

Run this after every chapter change, next to build_pdf.py:

    python3 book/build_web.py

It writes book/web/the-forgotten-seven.html, a single self-contained page
(cover, contents and every chapter) that is published as the book's
reading page, and book/The-Forgotten-Seven.md, the whole book as one text
file that opens in the session's file viewer.
"""

import base64
import datetime
import glob
import io
import os

from PIL import Image

from build_pdf import (
    ART_DIR,
    AUTHOR,
    BOOK_DIR,
    CHAPTER_DIR,
    TITLE,
    inline_markup,
    parse_chapter,
)

OUTPUT = os.path.join(BOOK_DIR, "web", "the-forgotten-seven.html")
TEXT_OUTPUT = os.path.join(BOOK_DIR, "The-Forgotten-Seven.md")
PDF_URL = ("https://github.com/bajwamahad160-alt/PS/blob/"
           "claude/awesome-hawking-r3k95u/book/The-Forgotten-Seven.pdf")


def emblem_data_uri():
    path = os.path.join(ART_DIR, "reqrium-emblem-gold.png")
    image = Image.open(path)
    image.thumbnail((360, 360))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


PAGE = """<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap">
<style>
:root {{
  --paper: #eceef2;
  --page: #fbfbfa;
  --ink: #1b2130;
  --muted: #5c6477;
  --gold: #9a7624;
  --rule: #d5d8df;
  --cover: #141b2d;
  --cover-gold: #c9a54a;
  --cover-text: #e9e4d6;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --paper: #0c111b;
    --page: #121826;
    --ink: #dcdfe6;
    --muted: #9098aa;
    --gold: #d2b060;
    --rule: #262e40;
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --paper: #0c111b;
  --page: #121826;
  --ink: #dcdfe6;
  --muted: #9098aa;
  --gold: #d2b060;
  --rule: #262e40;
}}
html {{ scroll-behavior: smooth; }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
body {{
  background: var(--paper);
  color: var(--ink);
  font-family: "Crimson Text", Georgia, "Times New Roman", serif;
  font-size: 19px;
  line-height: 1.62;
  padding-inline: 16px;
  padding-block: 0 64px;
}}
.progress {{
  position: fixed; top: 0; left: 0; right: 0; height: 3px;
  padding-top: env(safe-area-inset-top, 0px);
  background: transparent; z-index: 10; pointer-events: none;
}}
.progress span {{
  display: block; height: 3px; width: 0; background: var(--cover-gold);
}}
.book {{ max-width: 44rem; margin: 0 auto; display: grid; gap: 28px; padding-top: 28px; }}
.cover {{
  background: var(--cover);
  color: var(--cover-text);
  border-radius: 4px;
  padding: 48px 24px 40px;
  display: grid; justify-items: center; gap: 22px; text-align: center;
  outline: 1px solid var(--cover-gold); outline-offset: -12px;
}}
.cover h1 {{
  font-family: "Cinzel", "Trajan Pro", Georgia, serif;
  font-weight: 400; color: var(--cover-gold);
  font-size: clamp(2rem, 7vw, 3.1rem); line-height: 1.15;
  letter-spacing: 0.04em; margin: 0; text-wrap: balance;
}}
.cover img {{ width: min(190px, 48vw); height: auto; }}
.cover .author {{
  font-family: "Cinzel", Georgia, serif; color: var(--cover-gold);
  letter-spacing: 0.14em; font-size: 0.95rem; margin: 0;
}}
.meta {{
  display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 20px;
  font-size: 0.95rem; color: var(--muted);
}}
.meta a {{ color: var(--gold); }}
.panel {{
  background: var(--page); border: 1px solid var(--rule); border-radius: 4px;
  padding: 36px clamp(20px, 6vw, 64px);
}}
.contents h2 {{
  font-family: "Cinzel", Georgia, serif; font-weight: 400; text-align: center;
  font-size: 1.35rem; letter-spacing: 0.06em; margin: 0 0 18px;
}}
.contents ol {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 6px; }}
.contents a {{
  display: flex; gap: 12px; align-items: baseline; color: var(--ink); text-decoration: none;
}}
.contents a:hover .name, .contents a:focus-visible .name {{ text-decoration: underline; }}
.contents .label {{
  font-family: "Cinzel", Georgia, serif; color: var(--gold); font-size: 0.8rem;
  letter-spacing: 0.1em; white-space: nowrap;
}}
.contents .words {{ margin-left: auto; color: var(--muted); font-size: 0.9rem;
  font-variant-numeric: tabular-nums; white-space: nowrap; }}
.chapter header {{ text-align: center; margin: 12px 0 36px; }}
.chapter .label {{
  font-family: "Cinzel", Georgia, serif; color: var(--gold);
  letter-spacing: 0.16em; font-size: 0.85rem; margin: 0;
}}
.chapter h2 {{
  font-family: "Cinzel", Georgia, serif; font-weight: 400;
  font-size: clamp(1.7rem, 5vw, 2.3rem); margin: 6px 0 0; text-wrap: balance;
}}
.chapter p {{ margin: 0; text-indent: 1.4em; hyphens: auto; }}
.chapter p.first {{ text-indent: 0; }}
.chapter p.first::first-letter {{
  font-family: "Cinzel", Georgia, serif; color: var(--gold);
  float: left; font-size: 3.2em; line-height: 0.9; padding: 0.06em 0.08em 0 0;
}}
.chapter .break {{
  text-align: center; color: var(--muted); letter-spacing: 0.8em;
  margin: 22px 0; text-indent: 0;
}}
.chapter .end {{
  text-align: center; font-family: "Cinzel", Georgia, serif; color: var(--muted);
  letter-spacing: 0.2em; font-size: 0.8rem; margin-top: 36px;
}}
a:focus-visible {{ outline: 2px solid var(--gold); outline-offset: 3px; border-radius: 2px; }}
@media (max-width: 480px) {{ body {{ font-size: 18px; }} }}
</style>

<div class="progress" aria-hidden="true"><span id="progress-bar"></span></div>
<main class="book">
  <section class="cover" aria-label="Cover">
    <h1>{title_upper}</h1>
    <img src="{emblem}" alt="The Reqrium emblem: three crescents joined by a ring">
    <p class="author">{author_upper}</p>
  </section>
  <p class="meta">
    <span>Draft edition · {chapter_count} · about {word_total} words · updated {updated}</span>
    <a href="{pdf_url}" target="_blank" rel="noopener">Open the PDF</a>
  </p>
  <nav class="panel contents" aria-label="Contents">
    <h2>Contents</h2>
    <ol>
{toc}
    </ol>
  </nav>
{chapters}
</main>
<script>
(function () {{
  var bar = document.getElementById("progress-bar");
  function update() {{
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var pct = max > 0 ? Math.min(100, Math.max(0, window.scrollY / max * 100)) : 0;
    bar.style.width = pct + "%";
  }}
  window.addEventListener("scroll", update, {{ passive: true }});
  window.addEventListener("resize", update);
  update();
}})();
</script>
"""


def write_text_edition(chapter_files):
    """Write the whole book as one Markdown file that opens in the file viewer."""
    parts = [f"# {TITLE}", "", f"*by {AUTHOR}*", "", "## Contents", ""]
    for number, path in enumerate(chapter_files, start=1):
        label, name, _ = parse_chapter(path, number)
        parts.append(f"{number}. {label}: {name}")
    for path in chapter_files:
        with open(path, encoding="utf-8") as f:
            text = f.read().strip()
        parts += ["", "---", "", text.replace("# Chapter", "## Chapter", 1)]
    with open(TEXT_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    print(f"Wrote {os.path.relpath(TEXT_OUTPUT)}.")


def build():
    chapter_files = sorted(glob.glob(os.path.join(CHAPTER_DIR, "chapter-*.md")))
    toc_items, chapter_html, word_total = [], [], 0

    for number, path in enumerate(chapter_files, start=1):
        label, name, blocks = parse_chapter(path, number)
        words = sum(len(b.split()) for b in blocks if b)
        word_total += words
        anchor = f"chapter-{number}"
        toc_items.append(
            f'      <li><a href="#{anchor}"><span class="label">{inline_markup(label).upper()}</span>'
            f'<span class="name">{inline_markup(name)}</span>'
            f'<span class="words">{words:,} words</span></a></li>'
        )

        body, first = [], True
        for block in blocks:
            if block is None:
                body.append('    <p class="break" aria-hidden="true">* * *</p>')
                first = True
                continue
            cls = ' class="first"' if first else ""
            body.append(f"    <p{cls}>{inline_markup(block)}</p>")
            first = False
        chapter_html.append(
            f'  <article class="panel chapter" id="{anchor}">\n'
            f'    <header><p class="label">{inline_markup(label).upper()}</p>'
            f"<h2>{inline_markup(name)}</h2></header>\n"
            + "\n".join(body)
            + '\n    <p class="end">End of ' + inline_markup(label) + "</p>\n"
            "  </article>"
        )

    count = len(chapter_files)
    page = PAGE.format(
        title=TITLE,
        title_upper=TITLE.upper(),
        author_upper=AUTHOR.upper(),
        emblem=emblem_data_uri(),
        chapter_count=f"{count} chapter" + ("" if count == 1 else "s"),
        word_total=f"{round(word_total, -2):,}",
        updated=datetime.date.today().strftime("%B %-d, %Y"),
        pdf_url=PDF_URL,
        toc="\n".join(toc_items),
        chapters="\n".join(chapter_html),
    )
    write_text_edition(chapter_files)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Wrote {os.path.relpath(OUTPUT)} with {count} chapter(s), "
          f"{word_total:,} words.")


if __name__ == "__main__":
    build()
