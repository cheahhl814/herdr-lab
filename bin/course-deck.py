#!/usr/bin/env python3
"""course-deck.py — wrap a lesson's slides in the html-template-pack slide template (SKILL.md §10).

    course-deck.py <lesson-dir> < slides.html

Reads the <section class="slide" ...> fragment from stdin, swaps it in for the
template's <main class="deck"> contents (so every Template Reference slide is
gone), sets <title> from the lesson frontmatter, namespaces annotation storage
per course+lesson, adds the details.hint style, writes <lesson-dir>/deck.html
and adds `deck: deck.html` to the README frontmatter if it is missing.
Then run course-vet.py on the course.

The slides must form a lecture for a student with no prior knowledge
(SKILL.md §10 Deck authoring): why → (concept → worked example → practice)× →
recap → closing. This script only assembles; it can't judge teaching quality.

Template lookup: $HTML_TEMPLATE_PACK, else the usual skills dirs.
"""
from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

SKILL_DIRS = ["~/.agents/skills", "~/.claude/skills", "~/.pi/agent/skills"]
TEMPLATE = "templates/slide/slide-template.html"

HINT_CSS = """<style>
/* herdr-lab §10: hint ladder rungs on practice slides */
details.hint { margin: 8px 0; border: 1px solid var(--border, #334155); border-radius: 10px; padding: 6px 14px; }
details.hint > summary { cursor: pointer; font-weight: 600; color: var(--accent, #14b8a6); }
details.hint[open] > summary { margin-bottom: 6px; }
details.hint pre { margin: 6px 0 4px; }
</style>
"""


def find_template() -> Path:
    roots = [os.environ["HTML_TEMPLATE_PACK"]] if os.environ.get("HTML_TEMPLATE_PACK") else []
    roots += [f"{d}/html-template-pack" for d in SKILL_DIRS]
    for r in roots:
        p = Path(r).expanduser() / TEMPLATE
        if p.is_file():
            return p
    sys.exit("course-deck: html-template-pack not found — git clone "
             "https://github.com/cheahhl814/html-template-pack ~/.agents/skills/html-template-pack")


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    lesson = Path(sys.argv[1]).resolve()
    readme = lesson / "README.md"
    text = readme.read_text(encoding="utf-8")
    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not fm:
        sys.exit(f"course-deck: {readme} has no frontmatter")
    m = re.search(r'^title:\s*"?(.*?)"?\s*$', fm.group(1), re.M)
    title = m.group(1) if m else lesson.name
    course = lesson.parent.parent.name
    slides = sys.stdin.read().strip()
    tags = re.findall(r'<section class="slide[^"]*"', slides)
    if not tags:
        sys.exit("course-deck: stdin has no <section class=\"slide\"> blocks")
    if "active" not in tags[0]:
        sys.exit("course-deck: the first slide must carry class \"active\"")

    tpl = find_template().read_text(encoding="utf-8")
    key = f"{course}-{lesson.name}"
    out, n = re.subn(r'(<main class="deck">).*?(</main>)', lambda m: f"{m.group(1)}\n\n{slides}\n\n{m.group(2)}", tpl, flags=re.S)
    if n != 1:
        sys.exit("course-deck: template has no single <main class=\"deck\"> — html-template-pack layout changed")
    # [^<]* — the template's header comment mentions "<title>" in prose; don't match from there
    out, n = re.subn(r"<title>[^<]*</title>", f"<title>{html.escape(title)}</title>", out, count=1)
    if n != 1:
        sys.exit("course-deck: template has no <title> element — html-template-pack layout changed")
    out = out.replace('data-annot-storage="slide-template"', f'data-annot-storage="{key}"', 1)
    out = out.replace('data-annot-export="slide-template-annotations.json"', f'data-annot-export="{key}-notes.json"', 1)
    out = out.replace("</head>", HINT_CSS + "</head>", 1)
    (lesson / "deck.html").write_text(out, encoding="utf-8")

    if not re.search(r"^deck:", fm.group(1), re.M):
        readme.write_text(text.replace(fm.group(0), f"---\n{fm.group(1)}\ndeck: deck.html\n---\n", 1), encoding="utf-8")
    print(f"course-deck: wrote {lesson / 'deck.html'} ({len(tags)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
