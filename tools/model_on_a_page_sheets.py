#!/usr/bin/env python3
"""The L2 sheets behind the front-door diagram: one per band, one tap down from it.

Director, 9 Oct: the diagram stays simple, and going deeper means "L2 drill-down sheets, one per
band, in the same visual grammar"; any claim of state on one derives from the maturity map.
Director, 24 Oct: ship them, the weather cascade first, each linking on to the live evidence.

Same two inputs as the picture (tools/model_on_a_page_picture.py) and no third: the words are the
`sheets:` entry of the ```yaml block under "## The picture" in THE_MODEL_ON_A_PAGE.md, and each
box's state is the map's, through moap_stage.compute_stage. A sheet is a grid of columns read top
to bottom (a chain from cause to what follows, or a plain list where `arrows: false`), an optional full-width box, and the wall bar naming what
crosses. No figure goes on a sheet either: depth here is more of the model, not more numbers.

Writes site/assets/model-<band>.svg and site/model/<band>/index.html for every band the spec
carries. Run:  python3 tools/model_on_a_page_sheets.py
"""
from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.model_on_a_page_picture import (  # noqa: E402
    BODY,
    INK,
    LINE,
    MUTED,
    SANS,
    PictureSpecError,
    _fit,
    load_spec,
    map_atom_levels,
    stage_of,
    text,
)

SITE = ROOT / "site"
sys.path.insert(0, str(SITE))
from ia_register import render_nav  # noqa: E402
from moap_stage import BUILDING, LIVE, PLANNED  # noqa: E402

# The front door's own chips (site/index.html .stage-*; site/brand/tokens.css), so a newcomer reads
# one vocabulary on both: the word is the state, the fill only reinforces it. Copy pack A3, 25 Oct:
# the glyph legend ". done, _ in build, ~ not started" was unreadable one tap down.
CHIP = {LIVE: ("#D6F2E0", INK), BUILDING: ("#FFF0C9", INK), PLANNED: ("#F4F4F4", "#666666")}

COL_W, GAP, X0 = 256, 16, 40


def _state(atoms, levels):
    stage = stage_of(atoms, levels)
    return stage if stage in CHIP else PLANNED


def _box(x, y, w, cell, levels, out):
    lines = _fit(cell["lines"], 4, cell["title"])
    h = 58 + 16 * len(lines)
    out.append('<rect x="{}" y="{}" width="{}" height="{}" rx="8" fill="#FFFFFF" stroke="{}"/>'.format(x, y, w, h, LINE))
    out.append(text(x + 14, y + 24, cell["title"], 14, font_weight=700))
    out += [text(x + 14, y + 42 + 16 * j, s, 12, BODY) for j, s in enumerate(lines)]
    word = _state(cell["atoms"], levels)
    fill, ink = CHIP[word]
    out.append('<rect x="{}" y="{}" width="{}" height="18" fill="{}"/>'.format(
        x + 14, y + h - 26, round(len(word) * 7.4 + 16), fill))
    out.append('<text x="{}" y="{}" font-size="10" font-weight="700" letter-spacing="0.6" fill="{}">{}</text>'.format(
        x + 22, y + h - 13, ink, word.upper()))
    return h


def render_svg(sheet: dict, levels: dict) -> str:
    cols = _fit(sheet["columns"], 3, "a sheet's columns")
    n = len(cols)
    w = (800 - GAP * (n - 1)) // n if n else COL_W
    xs = [X0 + (w + GAP) * i for i in range(n)]
    o = [text(xs[i] + 2, 28, c, 12, MUTED, font_weight=700, letter_spacing=1.5) for i, c in enumerate(cols)]
    y = 44
    for r, row in enumerate(sheet["rows"]):
        if len(row) != n:
            raise PictureSpecError("row {} of '{}' has {} cells for {} columns".format(r + 1, sheet["title"], len(row), n))
        heights = [_box(xs[i], y, w, cell, levels, o) if cell else 0 for i, cell in enumerate(row)]
        bottom = y + max(heights)
        if r + 1 < len(sheet["rows"]):
            for i, cell in enumerate(row):
                if cell and sheet["rows"][r + 1][i] and sheet.get("arrows", True):
                    cx = xs[i] + w // 2
                    o.append('<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" stroke="{3}" stroke-width="2" '
                             'marker-end="url(#arr)"/>'.format(cx, y + heights[i], bottom + 30, INK))
        y = bottom + 36
    if sheet.get("across"):
        y += _box(X0, y, 800, sheet["across"], levels, o) + 20
    wall = sheet["wall"]
    o.append('<rect x="{}" y="{}" width="800" height="92" fill="{}"/>'.format(X0, y, INK))
    o.append(text(X0 + 24, y + 28, wall["heading"], 13, "#FAFAF8", font_weight=700, letter_spacing=2))
    x = X0 + 24
    for s in wall["items"]:
        wd = max(64, round(len(s) * 6.2 + 26))  # wider than the picture's: sheets carry longer labels
        o.append('<rect x="{}" y="{}" width="{}" height="26" rx="13" fill="none" stroke="#FAFAF8"/>'.format(x, y + 40, wd))
        o.append(text(x + wd // 2, y + 57, s, 11.5, "#FAFAF8", text_anchor="middle"))
        x += wd + 8
    if x > X0 + 800:
        raise PictureSpecError("the wall bar of '{}' runs past the sheet".format(sheet["title"]))
    o.append(text(X0 + 24, y + 84, wall["note"], 12, "#B9BCC2", font_style="italic"))
    height = y + 92 + 24
    head = ['<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{0}" viewBox="0 0 880 {0}" '
            'font-family="{1}">'.format(height, SANS),
            '<!-- GENERATED by tools/model_on_a_page_sheets.py from docs/design/THE_MODEL_ON_A_PAGE.md '
            '(## The picture, sheets) and docs/design/maturity_map.yaml. Do not edit by hand. -->',
            '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{}"/></marker></defs>'.format(INK),
            '<rect width="880" height="{}" fill="#FAFAF8"/>'.format(height)]
    return "\n".join(head + o + ["</svg>"]) + "\n"


def _alt(sheet, levels) -> str:
    parts = []
    for i, c in enumerate(sheet["columns"]):
        chain = [cell["title"] + " (" + _state(cell["atoms"], levels) + ")"
                 for row in sheet["rows"] if (cell := row[i])]
        parts.append(c.capitalize() + ": " + (" → " if sheet.get("arrows", True) else "; ").join(chain) + ".")
    if sheet.get("across"):
        a = sheet["across"]
        parts.append(a["title"] + " (" + _state(a["atoms"], levels) + ").")
    parts.append(sheet["wall"]["heading"].capitalize() + ": " + ", ".join(sheet["wall"]["items"]) + ".")
    return " ".join(parts)


def render_page(band: str, sheet: dict, levels: dict) -> str:
    links = "\n".join('    <li><a href="../../{}">{}</a> — {}</li>'.format(
        escape(lk["href"]), escape(lk["label"]), escape(lk["why"])) for lk in sheet["links"])
    lead = " ".join(escape(s) for s in sheet["lead"])
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Poesys &mdash; {title}, one tap down from the model</title>
<link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="stylesheet" href="../../brand/brand.css">
<style>
/* Generated by tools/model_on_a_page_sheets.py -- do not hand-edit. Brand tokens only. */
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; font-size: 14px; line-height: 1.6; }}
main {{ max-width: 920px; margin: 0 auto; padding: 28px 20px 60px; }}
.back {{ font-size: 13px; color: var(--muted); }}
h1 {{ font-size: 27px; font-weight: 800; letter-spacing: -0.4px; margin: 10px 0 8px; }}
.lead {{ font-size: 15px; max-width: 70ch; color: var(--text); }}
.how {{ font-size: 13px; color: var(--muted); margin-top: 8px; max-width: 70ch; }}
figure {{ margin-top: 22px; border: 1px solid var(--border); background: var(--surface); }}
figure img {{ display: block; width: 100%; height: auto; }}
h2 {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.09em; color: var(--muted); margin: 30px 0 10px; }}
ul.next {{ list-style: none; }}
.stage {{ font-size: 10px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; padding: 2px 8px; color: var(--text); }}
.stage-live {{ background: var(--green-soft); }}
.stage-building {{ background: var(--amber-soft); }}
.stage-planned {{ background: var(--surface2); color: var(--muted); }}
ul.next li {{ padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 14px; }}
@media (max-width: 640px) {{ body {{ font-size: 15px; }} main {{ padding-left: 14px; padding-right: 14px; }} h1 {{ font-size: 24px; }} }}
</style>
</head>
<body>
<nav class="site-nav">
  <a href="../../" class="nav-logo wordmark">poesys.</a>
  {nav}
</nav>
<main>
  <a class="back" href="../../#model">&larr; The model on a page</a>
  <h1>{title}</h1>
  <p class="lead">{lead}</p>
  <p class="how">{how} Each box carries its state, read from the maturity map at publish: <span class="stage stage-live">Live</span> built and at target, <span class="stage stage-building">Building</span> under way, <span class="stage stage-planned">Planned</span> not started.</p>
  <figure>
    <img src="../../assets/model-{band}.svg" alt="{alt}">
  </figure>
  <h2>Where to see it working</h2>
  <ul class="next">
{links}
  </ul>
</main>
</body>
</html>
""".format(title=escape(sheet["title"]), lead=lead, nav=render_nav("/model/", depth=1), band=band,
           alt=escape(_alt(sheet, levels)), links=links,
           how=escape(sheet.get("how", "Read each column top to bottom, from cause to what follows.")))


def build(spec=None, levels=None) -> dict[Path, str]:
    spec = spec if spec is not None else load_spec()
    levels = levels if levels is not None else map_atom_levels()
    out = {}
    for band, sheet in (spec.get("sheets") or {}).items():
        out[SITE / "assets" / "model-{}.svg".format(band)] = render_svg(sheet, levels)
        out[SITE / "model" / band / "index.html"] = render_page(band, sheet, levels)
    return out


def write() -> bool:
    """Publish step; fails closed, leaving the previous sheets served."""
    try:
        files = build()
    except (PictureSpecError, OSError, KeyError, yaml.YAMLError) as exc:
        print("MODEL SHEETS NOT WRITTEN: {}".format(exc), file=sys.stderr)
        return False
    for path, body in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != body:
            path.write_text(body, encoding="utf-8")
    return True


if __name__ == "__main__":
    sys.exit(0 if write() else 1)
