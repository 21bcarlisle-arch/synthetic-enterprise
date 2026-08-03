#!/usr/bin/env python3
"""Render the model-on-a-page EVIDENCE PAGES from primary state (atom
``SITE_evidence_pages_behind_nodes``).

One page per front-door diagram node, at ``site/evidence/<node_id>/index.html``, plus an
index at ``site/evidence/index.html``. Each page answers, for one node's present-tense claim:

  * which maturity-map atoms the claim rests on, and the LEVEL each is actually at
  * the derived stage word, and the rule that derived it
  * the level-move RECORD for those atoms (``gate_authorizations.jsonl``, R16)
  * measured fidelity-register rows, where any exist
  * the test modules that name the atom, with their test-function counts
  * the evidence documents the map declares -- and whether each one resolves
  * the last commit touching the atom's file_scope

THE SITE IS A RENDERING, NEVER AN AUTHOR. Every figure on these pages comes from
``tools/moap_evidence.py``'s derivation off primary state. Nothing is typed in. Where a
source is silent (no ledger row, no fidelity measurement) the page SAYS SO -- absence of
evidence is itself primary state, and hiding it would be the over-claim this atom exists
to kill.

Regenerate::

    python3 tools/generate_evidence_pages.py

``tools/moap_evidence_gate.py`` (wired to the publish gate through
``tests/tools/test_site_evidence_pages.py``) fails publication if any page's rendered
figures stop matching the derivation -- i.e. if the map moves and this is not re-run.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import subprocess
import sys
from pathlib import Path

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from moap_evidence import (  # noqa: E402
    REPO_ROOT,
    DerivationUnavailable,
    evidence_href_for,
    evidence_model,
)

SITE_ROOT = REPO_ROOT / "site"
EVIDENCE_ROOT = SITE_ROOT / "evidence"

_STAGE_CLASS = {"Live": "ev-live", "Building": "ev-building", "Planned": "ev-planned"}

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: system-ui, sans-serif;
  font-size: 14px; line-height: 1.5; }
.site-nav { background: var(--surface); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; padding: 0 20px; height: 48px; gap: 8px; flex-wrap: wrap; }
.nav-logo { font-weight: 700; color: var(--teal); text-decoration: none; margin-right: 16px; font-size: 15px; }
.nav-link { color: var(--muted); text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 13px; }
.nav-link:hover, .nav-link.active { color: var(--text); background: var(--surface2); }
.wrap { max-width: 1100px; margin: 0 auto; padding: 36px 20px 64px; }
.crumb { font-size: 12px; color: var(--muted); margin-bottom: 14px; }
.crumb a { color: var(--blue); text-decoration: none; }
.hero-h { font-size: 26px; font-weight: 800; letter-spacing: -0.4px; margin-bottom: 8px; }
.hero-p { font-size: 14px; line-height: 1.7; color: var(--muted); max-width: 760px; }
.sec { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--muted); margin: 36px 0 12px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 18px; margin-bottom: 14px; }
.muted { color: var(--muted); font-size: 12px; line-height: 1.6; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 16px 0; }
.kpi { background: var(--surface2); border-radius: 8px; padding: 10px 14px; }
.kpi-l { font-size: 10px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); margin-bottom: 4px; }
.kpi-v { font-size: 22px; font-weight: 700; letter-spacing: -0.4px; }
.stage-badge { display: inline-block; font-size: 12px; font-weight: 700; padding: 3px 10px;
  border-radius: 999px; border: 1px solid var(--border); background: var(--surface2); }
.ev-live { color: var(--green); }
.ev-building { color: var(--amber); }
.ev-planned { color: var(--muted); }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: .05em;
  color: var(--muted); padding: 8px 8px; border-bottom: 1px solid var(--border); white-space: nowrap; }
td { padding: 9px 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
tr:last-child td { border-bottom: none; }
code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; }
.ev-atom-id { color: var(--blue); }
.ok { color: var(--green); font-weight: 700; }
.no { color: var(--red); font-weight: 700; }
.gap { color: var(--amber); font-weight: 700; }
details { margin-top: 8px; }
summary { cursor: pointer; font-size: 12px; color: var(--muted); }
.prov { font-size: 11px; color: var(--muted); line-height: 1.6; margin-top: 6px;
  border-left: 2px solid var(--border); padding-left: 10px; }
.nodelist { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.nodecard { display: block; text-decoration: none; color: inherit; background: var(--surface);
  border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
.nodecard:hover { border-color: var(--blue); }
.nodecard h3 { font-size: 15px; margin-bottom: 6px; }
footer { margin-top: 48px; padding: 20px 0; border-top: 1px solid var(--border);
  text-align: center; font-size: 11px; color: var(--muted); }
"""


def _e(value) -> str:
    return html.escape(str(value), quote=True)


def _head(title: str, depth: int) -> str:
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_e(title)}</title>
<meta name="robots" content="noindex, nofollow">
<link rel="icon" type="image/svg+xml" href="{up}favicon.svg">
<link rel="stylesheet" href="{up}brand/brand.css">
<style>{_CSS}</style>
</head>
<body>
<nav class="site-nav">
  <a href="{up}" class="nav-logo wordmark">poesys.</a>
  <a href="{up}" class="nav-link">Home</a>
  <a href="{up}world/" class="nav-link">The World</a>
  <a href="{up}company/" class="nav-link">The Company</a>
  <a href="{up}proof/" class="nav-link">Proof</a>
</nav>
<div class="wrap">
"""


def _foot(generated_at: str, commit: str, sources: list[dict], depth: int) -> str:
    rows = "".join(
        f"<li><code>{_e(s['path'])}</code> &mdash; sha256 <code>{_e(s['sha256_16'] or 'unreadable')}</code></li>"
        for s in sources
    )
    return f"""
<div class="sec">Where these figures come from</div>
<div class="card">
  <p class="muted">Every figure on this page is DERIVED at build time from the files below and
  nothing else. No number here is typed in by hand; if a source moves and this page is not
  regenerated, the publish gate
  (<code>tools/moap_evidence_gate.py</code>) refuses to publish rather than let the page drift.</p>
  <ul class="muted" style="margin-top:10px;padding-left:18px;">{rows}</ul>
  <p class="muted" style="margin-top:10px;">Derived at <strong>{_e(generated_at)}</strong>
  from commit <code>{_e(commit)}</code>.</p>
</div>
<footer>&copy; 2026 Poesys Platforms. All rights reserved.</footer>
</div>
</body>
</html>
"""


def _bool_cell(flag: bool, yes: str = "yes", no: str = "no") -> str:
    cls = "ok" if flag else "gap"
    return f'<span class="{cls}">{yes if flag else no}</span>'


def _atom_row_html(atom: dict) -> str:
    docs = atom["evidence_docs"]
    if docs:
        doc_bits = "<br>".join(
            f'<code>{_e(d["path"])}</code> {_bool_cell(d["exists"], "resolves", "MISSING")}'
            for d in docs
        )
    else:
        doc_bits = '<span class="muted">none declared</span>'

    if atom["ledger_rows"]:
        ledger_cell = f'{len(atom["ledger_rows"])} recorded'
        prov = "".join(
            "<div class='prov'>"
            f"<strong>{_e(r['action'])}</strong> to level {_e(r['level'])}"
            f" &middot; {_e(_iso(r['ts']))} &middot; {_e(r['authorized_by'])}"
            f"<br>{_e(r['provenance'])}&hellip;</div>"
            for r in atom["ledger_rows"]
        )
        ledger_cell += f"<details><summary>record</summary>{prov}</details>"
    else:
        ledger_cell = '<span class="muted">no recorded move</span>'

    if atom["fidelity_rows"]:
        fid = "<br>".join(
            f'<code>{_e(r["layer"])}</code> {_e(r["cells"])} cells, measured {_e(str(r["measured_at"])[:10])}'
            for r in atom["fidelity_rows"]
        )
    else:
        fid = '<span class="muted">no measured row</span>'

    if atom["test_modules"]:
        mods = "".join(f"<div><code>{_e(m['path'])}</code> ({m['test_functions']})</div>"
                       for m in atom["test_modules"])
        tests_cell = (
            f'{atom["test_function_count"]} in {atom["test_module_count"]} module(s)'
            f"<details><summary>modules</summary><div class='prov'>{mods}</div></details>"
        )
    else:
        tests_cell = '<span class="gap">no module names this atom</span>'
    if atom["registry_modules"]:
        tests_cell += (
            f'<div class="muted">+{len(atom["registry_modules"])} map-wide registry module(s), '
            "not counted above</div>"
        )

    commit = atom["last_commit"]
    if commit:
        commit_cell = (
            f'<code>{_e(commit["sha"])}</code><br><span class="muted">{_e(commit["date"][:10])}</span>'
        )
    elif not atom["file_scope"]:
        commit_cell = '<span class="muted">no file scope declared</span>'
    else:
        commit_cell = '<span class="muted">no commit found in scope</span>'

    in_map = "" if atom["in_map"] else '<div class="no">ABSENT FROM THE MATURITY MAP</div>'
    return f"""<tr class="ev-atom" id="atom-{_e(atom['id'])}">
<td><code class="ev-atom-id">{_e(atom['id'])}</code>{in_map}
  <div class="muted">{_e(atom['name'])}</div>
  <div class="muted">lane {_e(atom['lane'])} &middot; loop stage {_e(atom['loop_stage'])}
  &middot; expert hour {_e(atom['expert_hour_status'])}</div></td>
<td class="ev-atom-level">{atom['level_current']} / {atom['level_target']}</td>
<td>{_bool_cell(atom['at_target'], 'at target', 'below target')}</td>
<td>{tests_cell}</td>
<td>{ledger_cell}</td>
<td>{fid}</td>
<td>{doc_bits}</td>
<td>{commit_cell}</td>
</tr>"""


def _iso(ts) -> str:
    try:
        return _dt.datetime.fromtimestamp(float(ts), _dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    except (TypeError, ValueError):
        return "unknown"


def node_page_html(node: dict, model: dict, generated_at: str, commit: str) -> str:
    stage = node["computed_stage"]
    badge = f'<span class="stage-badge {_STAGE_CLASS.get(stage, "")}">' \
            f'<span class="ev-stage-word">{stage}</span></span>'
    rows = "\n".join(_atom_row_html(a) for a in node["atoms"])
    below = [a for a in node["atoms"] if not a["at_target"]]
    if below:
        honest = (
            "<p class='muted'>This node is <strong>not</strong> Live because "
            + ", ".join(f"<code>{_e(a['id'])}</code> ({a['level_current']}/{a['level_target']})"
                        for a in below)
            + (" sits" if len(below) == 1 else " sit")
            + " below target. That is the whole reason the stage word reads "
            f"&ldquo;{_e(stage)}&rdquo; and not &ldquo;Live&rdquo;.</p>"
        )
    else:
        honest = (
            "<p class='muted'>Every atom behind this claim is at its target level, which is what "
            "makes the stage word &ldquo;Live&rdquo;. It is not a judgement; it is the rule below "
            "applied to the levels in the table.</p>"
        )

    declared = node["declared_stage"]
    declared_line = (
        f"<p class='muted'>The diagram declares <strong>{_e(declared)}</strong>; the derivation "
        f"computes <strong>{_e(stage)}</strong>. "
        + ("They agree." if declared == stage else "They DISAGREE &mdash; the publish gate fails on this.")
        + "</p>"
        if declared is not None
        else "<p class='muted'>The diagram declares no stage for this node; the derived stage is "
             "the one it renders.</p>"
    )

    look = node.get("look_href") or "../../"
    return (
        _head(f"Poesys -- Evidence: {node['name']}", 2)
        + f"""
<div class="crumb"><a href="../">Evidence</a> &rsaquo; {_e(node['name'])}</div>
<h1 class="hero-h">{_e(node['name'])} &mdash; the evidence behind the claim</h1>
<p class="hero-p">This is the primary state standing behind one node of the model-on-a-page
diagram. Node <code class="ev-node-id">{_e(node['id'])}</code>. Nothing below is restated
from a summary: every level, count and record is read from the files listed at the foot of
this page each time it is built.</p>

<div class="kpis">
  <div class="kpi"><div class="kpi-l">Derived stage</div><div class="kpi-v">{badge}</div></div>
  <div class="kpi"><div class="kpi-l">Atoms at target</div>
    <div class="kpi-v">{node['atoms_at_target']} / {node['atom_count']}</div></div>
  <div class="kpi"><div class="kpi-l">Test functions naming these atoms</div>
    <div class="kpi-v">{node['test_function_count']}</div></div>
  <div class="kpi"><div class="kpi-l">Recorded level moves</div>
    <div class="kpi-v">{node['ledger_row_count']}</div></div>
  <div class="kpi"><div class="kpi-l">Measured fidelity rows</div>
    <div class="kpi-v">{node['fidelity_row_count']}</div></div>
  <div class="kpi"><div class="kpi-l">Declared evidence docs resolving</div>
    <div class="kpi-v">{node['evidence_docs_resolving']} / {node['evidence_doc_count']}</div></div>
</div>

<div class="card">
  <div class="muted"><strong>How the stage word is derived.</strong> {_e(model['derivation_rule'])}</div>
  {honest}
  {declared_line}
  <p class="muted" style="margin-top:8px;">Walk to the figures themselves:
  <a href="{_e(look)}" style="color:var(--blue);">{_e(node['name'])} on the site</a>.</p>
</div>

<div class="sec">The atoms this claim rests on</div>
<div class="card" style="overflow-x:auto;">
<table>
<thead><tr>
  <th>Atom</th><th>Level now / target</th><th>State</th><th>Tests naming it</th>
  <th>Level-move record</th><th>Fidelity rows</th><th>Declared evidence</th><th>Last commit in scope</th>
</tr></thead>
<tbody>
{rows}
</tbody>
</table>
</div>
<p class="muted">&ldquo;Tests naming it&rdquo; counts test functions in modules under
<code>tests/</code> whose source names the atom id; map-wide registry modules (which name ten
or more atoms) are reported separately so one shared module cannot inflate every atom's count.
The counts are collected at build time from the test tree &mdash; the run that proves them
green is the publish gate itself (<code>pytest tests/</code>), which this page's own gate is
part of. &ldquo;Level-move record&rdquo; is the append-only gate-authorizations ledger (R16):
an atom with no row has had no recorded move, and the page says so rather than implying one.</p>
"""
        + _foot(generated_at, commit, model["sources"], 2)
    )


def index_page_html(model: dict, generated_at: str, commit: str) -> str:
    cards = []
    for node in model["nodes"]:
        stage = node["computed_stage"]
        cards.append(
            f"""<a class="nodecard" href="./{_e(node['id'])}/">
  <h3>{_e(node['name'])}</h3>
  <div><span class="stage-badge {_STAGE_CLASS.get(stage, '')}">
    <span class="ev-stage-word">{stage}</span></span></div>
  <p class="muted" style="margin-top:8px;">{node['atoms_at_target']} of {node['atom_count']}
  atoms at target &middot; {node['test_function_count']} test functions &middot;
  {node['ledger_row_count']} recorded level moves</p>
</a>"""
        )
    total_atoms = sum(n["atom_count"] for n in model["nodes"])
    at_target = sum(n["atoms_at_target"] for n in model["nodes"])
    return (
        _head("Poesys -- Evidence behind the model", 1)
        + f"""
<div class="crumb"><a href="../">Home</a> &rsaquo; Evidence</div>
<h1 class="hero-h">The evidence behind the model</h1>
<p class="hero-p">The front-door diagram makes six present-tense claims. Each one rests on a
named set of maturity-map atoms, and each atom is at a level that something moved it to. These
pages show that primary state directly &mdash; the levels, the recorded moves, the tests, the
measured fidelity rows, the documents &mdash; so a claim on the diagram can be checked rather
than taken on trust.</p>

<div class="kpis">
  <div class="kpi"><div class="kpi-l">Nodes</div><div class="kpi-v">{model['node_count']}</div></div>
  <div class="kpi"><div class="kpi-l">Atom claims behind them</div><div class="kpi-v">{total_atoms}</div></div>
  <div class="kpi"><div class="kpi-l">At target</div><div class="kpi-v">{at_target}</div></div>
  <div class="kpi"><div class="kpi-l">Atoms in the whole map</div>
    <div class="kpi-v">{model['map_atom_count']}</div></div>
</div>

<div class="sec">One page per node</div>
<div class="nodelist">
{''.join(cards)}
</div>

<div class="sec">What would make these pages fail</div>
<div class="card">
  <p class="muted">A node claiming a stage its atoms do not support, a node that walks to no
  page, a page rendering a level the maturity map no longer holds, or a page with no primary
  state on it at all &mdash; each of those blocks publication
  (<code>tools/moap_evidence_gate.py</code>, proven to fire on every one of those defects in
  <code>tests/tools/test_site_evidence_pages.py</code>). A control that cannot fail is worth
  nothing, so this one is tested by breaking it on purpose.</p>
</div>
"""
        + _foot(generated_at, commit, model["sources"], 1)
    )


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=str(REPO_ROOT),
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unavailable"


def generate(evidence_root: Path = EVIDENCE_ROOT, model: dict | None = None) -> list[Path]:
    """Write the index plus one page per node. Returns the paths written."""
    if model is None:
        model = evidence_model()
    generated_at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit = _git_commit()
    evidence_root.mkdir(parents=True, exist_ok=True)
    written = [evidence_root / "index.html"]
    written[0].write_text(index_page_html(model, generated_at, commit), encoding="utf-8")
    for node in model["nodes"]:
        out_dir = evidence_root / node["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "index.html"
        path.write_text(node_page_html(node, model, generated_at, commit), encoding="utf-8")
        written.append(path)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(EVIDENCE_ROOT), help="evidence page root")
    args = parser.parse_args(argv)
    try:
        written = generate(Path(args.out))
    except DerivationUnavailable as exc:
        print(f"FAILED: primary state unavailable -- {exc}", file=sys.stderr)
        return 2
    for path in written:
        print(f"wrote {path.relative_to(REPO_ROOT) if REPO_ROOT in path.parents else path}")
    print(f"\nevidence_href convention: {evidence_href_for('<node_id>')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
