# Book project (`book/`)

This repo holds the author's novel *The Forgotten Seven* by Mahad A. Bajwa,
alongside the SAM Online site.

## Rules for book work

- **Rebuild the PDF after every chapter change.** Whenever a file in
  `book/chapters/` is added or edited, run `python3 book/build_pdf.py`
  and commit the updated `book/The-Forgotten-Seven.pdf` in the same commit.
  The build needs `reportlab` (`pip install reportlab`).
- **Chapter files** are `book/chapters/chapter-NN.md`, starting with a
  `# Chapter One: Title` heading. `---` on its own line is a scene break.
  Only `*italic*` and `**bold**` markup is supported.
- **Chapter sizes** set by the author: small ~4,000 words, medium ~7,000,
  large ~10,000. If the author doesn't pick one, use judgment and say
  which size you chose.
- **Cover:** if `book/art/cover.png` (or `.jpg`) exists, the PDF uses it as
  the cover. Otherwise it draws the typographic cover with the gold
  Reqrium emblem.
- The magic books are called **griamores**. That's the author's spelling.
- Keep `book/world-bible.md` and `book/characters.md` in sync with the
  chapters. Mark the author's calls as *(author's decision)* and your own
  suggestions as *(proposed)*.
