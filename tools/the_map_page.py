#!/usr/bin/env python3
"""The map's page: the generated map, in the shape of the mock-up the director approved.

Director steer of 24 Oct, item 2 (`docs/staging/advisor/DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN_2026-10-24.md`):
"Show the page as the mock-up does, with the topic interconnections under the selected concept,
each tappable to jump across spines." The mock-up (`docs/design/the_map_mockup_2026-10-24/Main.dc.html`)
matched its links by hand. This page carries none of its own: every row is `tools.the_map.build()`
over the register, so a concept, a home, a gap or a link exists here only because the map found it.

Two inputs and no third: the map, and the measures `tools/world_claims.py` already computes. A
world-claims row whose note attaches to a mapped concept's page is shown on that concept as a
measure definition with its `computed_by`; a row whose note reaches no mapped page is a finding,
not a silent omission.

Selection is the URL fragment and CSS `:target`, so the page needs no script: tapping a link opens
that concept's panel wherever it sits. Writes `site/model/map/index.html`. Run:
python3 tools/the_map_page.py
"""
from __future__ import annotations

import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SITE = ROOT / "site"
OUT = SITE / "model" / "map" / "index.html"

#: The two pilot slices the steer names. Every other step is shown, and says it is not mapped yet.
PILOT = ("supplier/Collect", "build/Testing and controls")
STATUS_WORD = {"wired": "called", "entrypoint": "a command", "orphan": "nothing calls it",
               "gone": "not in the tree", "wrong side": "on the wrong side of the wall"}
LAYER_HEAD = {"page": "Knowledge", "world": "World rule", "wall": "Crosses the wall",
              "supplier": "Supplier feature"}


def claim_measures(the_map: dict, root: Path = ROOT) -> tuple[dict[str, list[dict]], list[dict]]:
    """({page id: the world-claims rows whose note attaches to it}, the rows that reach no mapped page).

    The note-to-page join is the map's own (`notes_by_page`), so a claim is placed by the same rule
    as the note that states it."""
    from tools import world_claims
    on_page: dict[str, list[dict]] = {}
    unplaced = []
    mapped = {c["page"]["id"]: set(c["page"]["notes"]) for c in the_map["concepts"] if c.get("page")}
    for row in world_claims.claims(root):
        note = Path(row["page"]).stem
        fn = world_claims.MEASURES.get(row.get("measure"))
        measure = {"id": row["id"], "band": row.get("band"), "source": row.get("source", ""),
                   "note": note,
                   "computed_by": f"tools.world_claims.{fn.__name__}" if fn else None}
        pages = [p for p, notes in mapped.items() if note in notes]
        for p in pages:
            on_page.setdefault(p, []).append(measure)
        if not pages:
            unplaced.append(measure)
    return on_page, unplaced


def _tag(status: str) -> str:
    cls = "ok" if status in ("wired", "entrypoint") else "bad"
    return f'<span class="tag {cls}">{escape(STATUS_WORD.get(status, status))}</span>'


def _modules(mods: list[dict]) -> str:
    return "<br>".join(f"<code>{escape(m['module'])}</code> {_tag(m['status'])}" for m in mods)


def _gap(c: dict, need: str) -> str:
    why = (c.get("gap") or {}).get(need)
    return (f'<span class="gap">Gap: {escape(why)}</span>' if why
            else '<span class="gap bad">Gap, and no reason recorded</span>')


def _cell(c: dict, layer: str) -> str:
    if layer == "page":
        p = c.get("page")
        if not p:
            return _gap(c, "page")
        name = (f'<a href="../../knowledge/{escape(p["id"])}/">{escape(p["id"])}</a>' if p["published"]
                else f'{escape(p["id"])} <span class="tag bad">not published</span>')
        return f'{name}<br><span class="sub">{len(p["notes"])} research notes</span>'
    if c.get(layer):
        return _modules(c[layer])
    return _gap(c, layer)


def _band(band) -> str:
    return f"{band[0]:.1%} to {band[1]:.1%}" if isinstance(band, list) and len(band) == 2 else "no band"


def _measure_rows(c: dict, claims: list[dict]) -> str:
    rows = []
    m = c.get("measure")
    if m:
        code = (f"<code>{escape(m['computed_by'])}</code>" if m.get("computed_by")
                else _gap(c, "computed_by"))
        rows.append(f"<li><b>{escape(c['prefLabel'])}</b>: counts {escape(m['counts'])}, over "
                    f"{escape(m['over'])}. Computed by {code}.</li>")
    for k in claims:
        code = (f"<code>{escape(k['computed_by'])}</code>" if k["computed_by"]
                else '<span class="gap bad">no function computes it</span>')
        rows.append(f"<li><b><code>{escape(k['id'])}</code></b>, stated on <code>{escape(k['note'])}</code>: "
                    f"published range {_band(k['band'])}, checked against the drawn world by {code}. "
                    f'<span class="sub">{escape(k["source"])}</span></li>')
    return "\n".join(rows)


def _spine_of(cid: str, by_id: dict) -> str:
    placed = (by_id.get(cid) or {}).get("placed") or ["?"]
    return placed[0].split("/", 1)[0]


def _panel(c: dict, by_id: dict, spines: dict, claims: list[dict]) -> str:
    bits = [f'<section class="panel" id="c-{escape(c["id"])}">',
            f'<h3>{escape(c["prefLabel"])} <span class="sub">{escape(c["id"])}</span></h3>',
            f'<p>{escape(c["definition"])}</p>']
    if c.get("match"):
        bits.append(f'<p class="sub">Taken from: {escape("; ".join(c["match"]))}</p>')
    if c.get("altLabel"):
        bits.append(f'<p class="sub">Also called: {escape(", ".join(c["altLabel"]))}</p>')
    flags = [f"{escape(LAYER_HEAD.get(n, n.replace('_', ' ')))}: "
             f"{escape((c.get('gap') or {}).get(n) or 'missing, with no reason recorded')}"
             for n in c.get("missing", [])]
    if c.get("also_named"):
        flags.append(f"{len(c['also_named'])} modules carry this concept's name and are not its declared home: "
                     + ", ".join(f"<code>{escape(m['module'])}</code> ({escape(STATUS_WORD.get(m['status'], m['status']))})"
                                 for m in c["also_named"]))
    measures = _measure_rows(c, claims)
    if measures:
        bits.append(f'<h4>Measures, one definition each</h4><ul class="list">{measures}</ul>')
    if c.get("atoms"):
        bits.append(f'<p class="sub">Map atoms building it: {escape(", ".join(c["atoms"]))}</p>')
    if c.get("controls"):
        bits.append(f'<p class="sub">Canon rules whose mechanisms touch it: {escape(", ".join(c["controls"]))}</p>')
    bits.append("<h4>What the map flags</h4>")
    bits.append(f'<ul class="list">{"".join(f"<li>{f}</li>" for f in flags)}</ul>' if flags
                else "<p>Nothing: every layer it needs is filled and no second home was found.</p>")
    bits.append("<h4>How it connects, across all four spines</h4>")
    if c["links"]:
        groups: dict[str, list[str]] = {}
        for link in c["links"]:
            spine = _spine_of(link["to"], by_id)
            name = by_id[link["to"]]["prefLabel"] if link["to"] in by_id else link["to"]
            groups.setdefault(spine, []).append(
                f'<li>{escape(link["rel"].replace("_", " "))} '
                f'<a href="#c-{escape(link["to"])}">{escape(name)}</a></li>')
        for spine, items in groups.items():
            label = (spines.get(spine) or {}).get("prefLabel", spine)
            bits.append(f'<p class="sub">{escape(label)}</p><ul class="list">{"".join(items)}</ul>')
    else:
        bits.append("<p>No link from here.</p>")
    bits.append("</section>")
    return "\n".join(bits)


def _supplier_slice(concepts: list[dict], on_page: dict) -> str:
    plain = [c for c in concepts if c.get("kind") is None]
    head = "".join(f"<th>{LAYER_HEAD[k]}</th>" for k in ("page", "world", "wall", "supplier"))
    rows = "\n".join(
        f'<tr><th><a href="#c-{escape(c["id"])}">{escape(c["prefLabel"])}</a></th>'
        + "".join(f"<td>{_cell(c, k)}</td>" for k in ("page", "world", "wall", "supplier")) + "</tr>"
        for c in plain)
    beliefs = "\n".join(
        f'<div class="belief"><h4><a href="#c-{escape(c["id"])}">{escape(c["prefLabel"])}</a></h4>'
        f'<p><b>Built from</b> {escape(c.get("built_from", ""))}</p>'
        f'<p><b>The belief, in code</b> {_modules(c.get("supplier", [])) or _gap(c, "supplier")}</p>'
        f'<p><b>Decides</b> {escape(c.get("decides", ""))}</p>'
        f'<p><b>Graded against the truth</b> {_gap(c, "graded_by") if "graded_by" in c.get("missing", []) else "graded"}</p>'
        "</div>" for c in concepts if c.get("kind") == "belief")
    measures = [c for c in concepts if c.get("kind") == "measure"]
    pages = sorted({c["page"]["id"] for c in concepts if c.get("page")})
    claim_rows = [k for p in pages for k in on_page.get(p, [])]
    measure_list = "".join(_measure_rows(c, []) for c in measures) + _measure_rows({"id": "", "prefLabel": ""}, claim_rows)
    return f"""
  <div class="table-scroll"><table class="grid"><thead><tr><th>Concept</th>{head}</tr></thead>
  <tbody>
{rows}
  </tbody></table></div>
  <h3 class="band">Beliefs and decisions</h3>
  <p class="sub">The data the supplier decides on: each belief is built only from what crosses the wall,
  feeds named decisions, and is graded against the simulation's hidden truth.</p>
  <div class="beliefs">{beliefs}</div>
  <h3 class="band">Measures, one definition each</h3>
  <p class="sub">A measure carries what it counts, over whom, and the one function that computes it. The
  ranges a knowledge page states about the drawn world are measures too, and come from
  <code>tools/world_claims.py</code>.</p>
  <ul class="list">{measure_list}</ul>"""


def _build_slice(concepts: list[dict]) -> str:
    rows = []
    for c in concepts:
        rule = c.get("rule")
        rule_cell = (f"<code>{escape(rule)}</code>" + (f'<br><span class="sub">its mechanisms: {escape(", ".join(c["rule_mechanisms"]))}</span>'
                                                       if c.get("rule_mechanisms") else "")
                     if rule else _gap(c, "rule"))
        enforced = "<br>".join(f"<code>{escape(p['path'])}</code>" + ("" if p["exists"] else ' <span class="tag bad">gone</span>')
                               for p in c.get("enforced_by", [])) or _gap(c, "enforced_by")
        rows.append(f'<tr><th><a href="#c-{escape(c["id"])}">{escape(c["prefLabel"])}</a></th>'
                    f'<td>{escape("; ".join(c.get("match", [])))}</td><td>{rule_cell}</td><td>{enforced}</td>'
                    f'<td>{escape(c.get("evidence") or "none computed")}</td></tr>')
    return f"""
  <div class="table-scroll"><table class="grid"><thead><tr><th>Concept</th><th>Established practice</th>
  <th>Our rule</th><th>What enforces it</th><th>What the record shows, computed at publish</th></tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody></table></div>"""


def render(the_map: dict, on_page: dict, unplaced: list[dict]) -> str:
    if str(SITE) not in sys.path:
        sys.path.insert(0, str(SITE))
    from ia_register import render_footer, render_nav
    concepts = the_map["concepts"]
    by_id = {c["id"]: c for c in concepts}
    spines = the_map["spines"]
    counts: dict[str, int] = {}
    for f in the_map["findings"]:
        counts[f["kind"]] = counts.get(f["kind"], 0) + 1
    for _ in unplaced:
        counts["measure on no mapped page"] = counts.get("measure on no mapped page", 0) + 1

    spine_list = []
    for key, sp in spines.items():
        steps = []
        for step in sp["steps"]:
            here = [c for c in concepts if f"{key}/{step}" in c.get("placed", [])]
            pilot = f"{key}/{step}" in PILOT
            steps.append(f'<a class="step{" on" if pilot else ""}" href="#s-{escape(key)}-{escape(step.replace(" ", "-"))}">'
                         f'{escape(step)}</a>' if pilot else
                         f'<span class="step" title="{len(here)} concepts placed here">{escape(step)}'
                         f'{f" ({len(here)})" if here else ""}</span>')
        spine_list.append(f'<li><b>{escape(sp["prefLabel"])}</b><div class="steps">{"".join(steps)}</div></li>')

    slices = []
    for placed in PILOT:
        key, step = placed.split("/", 1)
        here = [c for c in concepts if placed in c.get("placed", [])]
        body = _build_slice(here) if key == "build" else _supplier_slice(here, on_page)
        slices.append(f'<section class="slice" id="s-{escape(key)}-{escape(step.replace(" ", "-"))}">'
                      f'<h2>{escape(spines[key]["prefLabel"])} &rsaquo; {escape(step)}</h2>{body}</section>')

    panels = []
    for c in concepts:
        claims = [k for k in on_page.get((c.get("page") or {}).get("id"), [])] if c.get("kind") == "measure" else []
        panels.append(_panel(c, by_id, spines, claims))

    finding_list = "".join(f"<li>{escape(k)}: {v}</li>" for k, v in sorted(counts.items()))
    unplaced_list = "".join(f"<li><code>{escape(k['id'])}</code>, stated on <code>{escape(k['note'])}</code>, "
                            f"computed by <code>{escape(k['computed_by'] or 'nothing')}</code></li>" for k in unplaced)
    n = the_map["notes"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Poesys &mdash; The map</title>
<link rel="icon" type="image/svg+xml" href="../../favicon.svg">
<link rel="stylesheet" href="../../brand/brand.css">
<style>
/* Generated by tools/the_map_page.py from tools/the_map.build() -- do not hand-edit. Brand tokens only. */
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; font-size: 14px; line-height: 1.6; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 28px 20px 60px; }}
.back, .sub {{ font-size: 13px; color: var(--muted); }}
h1 {{ font-size: 27px; font-weight: 800; letter-spacing: -0.4px; margin: 10px 0 8px; }}
.lead {{ font-size: 15px; max-width: 72ch; }}
h2 {{ font-size: 18px; font-weight: 750; margin: 34px 0 10px; }}
h3 {{ font-size: 16px; margin: 0 0 6px; }}
h3.band {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.09em; color: var(--muted); margin: 24px 0 6px; }}
h4 {{ font-size: 13px; margin: 12px 0 4px; }}
ul.spines {{ list-style: none; margin-top: 18px; }}
ul.spines li {{ padding: 8px 0; border-bottom: 1px solid var(--border); }}
.steps {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }}
.step {{ font-size: 12px; padding: 2px 8px; border: 1px dashed var(--border); color: var(--muted); }}
.step.on {{ border-style: solid; color: var(--text); font-weight: 650; }}
.table-scroll {{ overflow-x: auto; }}
table.grid {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
table.grid th, table.grid td {{ border: 1px solid var(--border); padding: 6px 8px; vertical-align: top; text-align: left; }}
.tag {{ font-size: 11px; padding: 0 5px; border: 1px solid var(--border); white-space: nowrap; }}
.tag.bad, .gap.bad {{ font-weight: 700; }}
.gap {{ font-size: 12px; color: var(--muted); font-style: italic; }}
.beliefs {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; }}
.belief {{ border: 1px solid var(--border); background: var(--surface); padding: 10px; font-size: 13px; }}
ul.list {{ margin: 4px 0 0 18px; font-size: 13px; }}
.panel {{ display: none; border: 1px solid var(--border); background: var(--surface); padding: 14px; margin-top: 12px; }}
.panel:target {{ display: block; }}
code {{ font-size: 12px; overflow-wrap: anywhere; }}
@media (max-width: 640px) {{ body {{ font-size: 15px; }} main {{ padding-left: 14px; padding-right: 14px; }} h1 {{ font-size: 24px; }} }}
</style>
</head>
<body>
<nav class="site-nav">
  <a href="../../" class="nav-logo wordmark">poesys.</a>
  {render_nav("/model/", depth=1)}
</nav>
<main>
  <a class="back" href="../../harness/">&larr; How it&rsquo;s built</a>
  <h1>The map</h1>
  <p class="lead">Everything the project knows and does, hung on one register of concepts. Four spines:
  the simulated world, the supplier&rsquo;s value chain, the running of the company, and how the whole
  thing is built. The register is small and kept by hand; every link and every gap below is generated
  from it at publish, from what the code and documents already say.</p>
  <p class="sub">This is the pilot: two slices are mapped, supplier &lsquo;Collect&rsquo; and How it&rsquo;s
  built &lsquo;Testing and controls&rsquo;. A step in a dashed box is not on the register yet. Tap a concept
  to open it; its links jump across spines.</p>
  <ul class="spines">{"".join(spine_list)}</ul>
  {"".join(slices)}
  <h2>The selected concept</h2>
  <p class="sub">Tap a concept above. Nothing is selected until you do.</p>
  {"".join(panels)}
  <h2>What the map finds</h2>
  <p>{len(concepts)} concepts registered. Findings, by kind:</p>
  <ul class="list">{finding_list}</ul>
  <p class="sub">{n['on_a_page']} of {n['notes']} research notes attach to a published knowledge page;
  {len(n['on_no_page'])} attach to none.</p>
  <h4>Measures a page states about the world that reach no mapped concept</h4>
  <ul class="list">{unplaced_list or "<li>none</li>"}</ul>
  <p class="sub">The register is <code>docs/design/the_map/concepts.yaml</code>; the map is
  <code>tools/the_map.py</code>; this page is <code>tools/the_map_page.py</code>.</p>
</main>
{render_footer("../../privacy/")}
</body>
</html>
"""


def build(root: Path = ROOT) -> str:
    from tools import the_map
    the_map_now = the_map.build(root)
    on_page, unplaced = claim_measures(the_map_now, root)
    return render(the_map_now, on_page, unplaced)


def write(out: Path = OUT) -> bool:
    """Publish step; fails closed, leaving the previous page served."""
    try:
        body = build()
    except Exception as exc:  # noqa: BLE001 -- any failure leaves the last page, said aloud
        print(f"THE MAP PAGE NOT WRITTEN: {type(exc).__name__}: {exc}", file=sys.stderr)
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.read_text(encoding="utf-8") != body:
        out.write_text(body, encoding="utf-8")
    return True


if __name__ == "__main__":
    sys.exit(0 if write() else 1)
