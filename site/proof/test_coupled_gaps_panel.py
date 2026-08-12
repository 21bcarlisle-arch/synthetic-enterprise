"""Render-side tests for the Proof-door COUPLED-TRIAD gap panel (site/proof/index.html).

The DATA side (tools/generate_proof_data.py::_coupled_gaps) is tested separately in
tests/tools/test_generate_proof_coupled_gaps.py. THIS suite tests the RENDER: it executes
the page's actual inline JavaScript (via a Node/vm harness) against real generated data and
against synthetic mutation cases, then asserts on the produced HTML -- i.e. the rendered
pixel (R11), not the source string.

R15 (a control must be able to FAIL): the panel is a control surface -- it classifies each
measured gap by the reading convention (COUPLED_TRIAD_DESIGN.md 1.2) and must fail closed and
VISIBLE when the data side is absent/empty. Each mutation below feeds the panel its named
defect and asserts the panel fires: null gap -> untested/amber; gap 0 -> wall-leak/red;
gap>1 -> worse-than-blind/red; available:false or empty pairs -> a visible red failure block,
never a silently empty panel.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_render_harness.mjs"
PROJECT = HERE.parent.parent  # site/proof -> repo root

NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _render(data: dict) -> dict:
    """Run the page's inline renderCoupledGaps against `data`; return element contents."""
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps({"coupled_gaps": data}),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _live_coupled_gaps() -> dict:
    """The real data the generator would emit into proof.json.coupled_gaps."""
    sys.path.insert(0, str(PROJECT))
    from tools.generate_proof_data import _coupled_gaps, _load_atoms

    return _coupled_gaps(_load_atoms())


# --------------------------------------------------------------------------- #
# R11: the panel renders the LIVE generated data -- every coupled pair.
# 7 affordability-cluster pairs + the W2_11<->D5 payment triad (wired
# 2026-07-18) + the W1_5<->C13 weather-demand triad (wired 2026-07-21) + the
# W1_6<->C13 weather price-signal triad (ledger-surfaced, 2026-07-20) + the
# FABRIC triad's two rows (2026-08-03, H_GAP): W1_11<->C14 (what the EPC
# register believes) and W1_12<->C14 (what the company's own C14 posterior
# believes) + the RE-CONTRACTING triad (2026-08-08,
# WORLD_recontracting_relationship_start<->C_supply_start_semantic_separation --
# phantom tenure on a customer we won back) = 13. The fabric pair is two rows and
# not one because they are two distinct belief sources, and collapsing them would
# hide the only interesting number -- what the company's inference bought over the
# register it started from.
# Driven by the live coupling+ledger, not a frozen literal -- if a pair is
# added/removed the panel count follows.
# --------------------------------------------------------------------------- #
def test_live_data_renders_all_coupled_pairs():
    cg = _live_coupled_gaps()
    assert cg.get("available") is True
    expected = len(cg["pairs"])
    assert cg["pair_count"] == expected == 14, (
        "14 coupled pairs (7 affordability + payment + weather demand + "
        "weather price + 2 fabric + re-contracting + cohort). The cohort pair "
        "W2_2_population_draw<->C_cohort_discovery landed 2026-08-10 when RUNG 4b "
        "first drew a never_landed gap tool; tools/couple_cohort.py had carried "
        "--write-ledger and a green test since 2026-07-21 and had never put a "
        "number anywhere. It renders RED (1.0345 > 1) -- see docs/staging/"
        "WORKER_FINDING_A_WORST_CELL_HEADLINE_FLOORED_AT_THE_NO_SKILL_BASELINE_2026-08-10.md "
        "for why that headline cannot read below the no-skill baseline."
    )

    out = _render(cg)
    body = out["coupled-gaps"]["innerHTML"]

    # Every world<->company pair id must appear in the rendered rows.
    for pair in cg["pairs"]:
        assert pair["world_atom"] in body, f"{pair['world_atom']} not rendered"
        assert pair["company_atom"] in body, f"{pair['company_atom']} not rendered"

    # Exactly one gap row per coupled pair (no pair silently dropped, measured
    # or not) -- tracks the live pair count, not a frozen literal.
    assert body.count('class="gap-row"') == expected

    # The measured gap values are rendered to 3 dp (the pixel == the number, R11).
    for pair in cg["pairs"]:
        if pair["value"] is not None:
            assert f"{pair['value']:.3f}" in body, f"gap value for {pair['world_atom']} not rendered"

    # Summary / anti-decay counts are rendered in the KPI strip.
    kpis = out["gap-kpis"]["innerHTML"]
    assert str(cg["pair_count"]) in kpis
    assert str(cg["measured"]) in kpis


def test_live_data_faithfully_renders_the_alarms_the_data_reports():
    """The panel renders EXACTLY the alarms the (independent) ledger data reports --
    data-driven, not a frozen 'all green' snapshot, so it stays honest as pairs are
    added and as beliefs improve. A >=L2-unmeasured pair -> the 'depth nobody copes
    with yet' banner; a gap>1 or gap<=0 pair -> a red chip. Currently W1_5<->C13 is
    the one worse-than-blind pair (summer worst-cell gap 1.04: the company's
    temperature-only weather normalisation is genuinely worse than blind in summer,
    where there is no thermal signal -- an honest L1 finding, the CWV wind-chill term
    is the named L1->L2 refinement). When C13 improves past L1 this red disappears and
    the test still passes, because it asserts faithfulness, not a fixed colour."""
    cg = _live_coupled_gaps()
    out = _render(cg)
    if cg.get("unmeasured_ge_l2"):
        assert "depth nobody copes with yet" in out["gap-alarms"]["innerHTML"]
    body = out["coupled-gaps"]["innerHTML"]
    # The panel must render one red chip per data-reported leak / worse-than-blind pair.
    assert body.count('class="chip red"') == cg["wall_leak_count"] + cg["worse_than_blind_count"]


# --------------------------------------------------------------------------- #
# R15 mutation tests: feed the panel each named defect; assert the control fires.
# --------------------------------------------------------------------------- #
def _one_pair(value):
    return {
        "available": True,
        "source": "docs/observability/coupled_gap_ledger.json",
        "pair_count": 1,
        "measured": 0 if value is None else 1,
        "unmeasured": 1 if value is None else 0,
        "blocks_l3_count": 0,
        "wall_leak_count": 1 if (value is not None and value <= 0) else 0,
        "worse_than_blind_count": 1 if (value is not None and value > 1) else 0,
        "unmeasured_ge_l2": ["W2_X_test"] if value is None else [],
        "pairs": [{
            "world_atom": "W2_X_test", "company_atom": "CX_test",
            "world_name": "test world", "company_name": "test company",
            "world_level": 2, "company_level": 2,
            "metric": "belief", "value": value, "baseline_g0": 0.5,
            "raw_gap": None, "components": None, "note": "n",
            "measured_at": None, "run_git_commit": None,
            "trend": "single", "history": [], "chip": None, "severity": None,
            "blocks_l3": False, "blocks_l3_reason": None,
        }],
    }


def test_mutation_null_gap_renders_untested_amber():
    out = _render(_one_pair(None))
    body = out["coupled-gaps"]["innerHTML"]
    assert 'class="chip amber"' in body and "untested" in body
    # The >=L2-with-no-gap anti-decay alarm must fire (binding rule 1 made visible).
    assert "depth nobody copes with yet" in out["gap-alarms"]["innerHTML"]


def test_mutation_zero_gap_renders_wall_leak_red():
    out = _render(_one_pair(0.0))
    body = out["coupled-gaps"]["innerHTML"]
    assert '<span class="chip red">leak</span>' in body


def test_mutation_gap_above_one_renders_worse_than_blind_red():
    out = _render(_one_pair(1.4))
    body = out["coupled-gaps"]["innerHTML"]
    assert 'class="chip red"' in body and "worse than blind" in body


def test_mutation_normal_gap_renders_learning_blue():
    out = _render(_one_pair(0.42))
    body = out["coupled-gaps"]["innerHTML"]
    assert 'class="chip blue"' in body and "learning" in body
    assert "0.420" in body


def test_mutation_blocks_l3_flag_renders_badge():
    data = _one_pair(0.42)
    data["pairs"][0]["blocks_l3"] = True
    data["pairs"][0]["blocks_l3_reason"] = "twin below L2"
    data["blocks_l3_count"] = 1
    out = _render(data)
    assert "blocks L3" in out["coupled-gaps"]["innerHTML"]


def test_fail_closed_when_data_unavailable():
    """available:false must produce a VISIBLE failure, never a silently empty panel."""
    out = _render({"available": False, "note": "module not importable"})
    body = out["coupled-gaps"]["innerHTML"]
    assert "gap-fail" in body
    assert "not available" in body
    assert body.strip() != ""


def test_fail_closed_when_pairs_empty():
    """An empty pair list (ledger drained) must render a visible failure, not blank."""
    data = _one_pair(0.42)
    data["pairs"] = []
    data["pair_count"] = 0
    out = _render(data)
    body = out["coupled-gaps"]["innerHTML"]
    assert "gap-fail" in body
    assert body.strip() != ""


def test_missing_coupled_gaps_key_fails_visible():
    """proof.json with no coupled_gaps block at all -> visible failure."""
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps({}),  # no coupled_gaps key
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert "gap-fail" in out["coupled-gaps"]["innerHTML"]


# --------------------------------------------------------------------------- #
# atom D35 / H27 Expert Hour #18 (2026-08-11): THE DEPTH LIMIT MAY NOT SWALLOW
# A NUMBER.
#
# `fmtComponent` exists because this door was serving "[object Object]" for a
# nested component -- "a figure that cannot be read at all", found by driving
# the LIVE page. Its repair carried a depth limit, and the limit reintroduced
# the same failure ONE LEVEL DOWN. Measured on the rendered pixel: 53 published
# component numbers were served as "…" from their own row's components block
# (W1_11 22, W1_12 22, W2_11 9), and 43 of those -- every `two_level.cells.*`
# reading on both fabric rows -- were readable NOWHERE on their row, because
# their producer nests them one level below the limit.
#
# It was invisible on the row anybody was reading. The payment triad's six
# attributed measures are elided in this block too, and survive only because
# `format_remittance_attribution_summary` happens to repeat them in the note
# prose -- an accidental redundancy, not a control, and it does not exist on
# the fabric rows.
#
# NOTHING HERE ASSERTED IT. The R11 test above checks that each row's GAP
# renders at 3dp; no control had ever asked whether a published COMPONENT
# number reaches the reader at all. So the control is the population one: every
# finite number in a row's `components` must appear in THAT ROW's rendered
# components block. Per-row deliberately -- a panel-wide substring search
# passes on a number that is only legible two rows away, which is exactly the
# accident that hid this.
# --------------------------------------------------------------------------- #
def _leaf_numbers(obj, prefix=""):
    """Every finite numeric leaf in a components payload, path-qualified."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _leaf_numbers(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _leaf_numbers(v, f"{prefix}[{i}]")
    elif isinstance(obj, bool):
        return  # bool is a subclass of int; a flag is not a figure
    elif isinstance(obj, (int, float)):
        yield prefix, float(obj)


def _components_block(row_html: str) -> str:
    """The <details> block of ONE rendered row -- never the whole panel."""
    i = row_html.find("Components &amp; measurement basis")
    return row_html[i:] if i >= 0 else ""


def _unreadable_numbers(cg: dict, body: str):
    """(row, path, value) for every published component number NOT rendered in
    its own row's components block."""
    rows = body.split('<div class="gap-row">')[1:]
    assert len(rows) == len(cg["pairs"]), "row/pair split mismatch -- sweep is unsound"
    out = []
    for pair, row in zip(cg["pairs"], rows):
        block = _components_block(row)
        for path, value in _leaf_numbers(pair.get("components") or {}):
            if f"{value:.4f}" not in block:
                out.append((pair["world_atom"], path, value))
    return out


def _nested_past_the_limit(cg: dict) -> int:
    """How many published numbers sit BELOW `fmtComponent`'s structural limit --
    i.e. how many the control is actually exercised by. A sweep run on a payload
    that never reaches the limit passes without touching the defect."""
    n = 0
    for pair in cg["pairs"]:
        for path, _v in _leaf_numbers(pair.get("components") or {}):
            if path.count(".") + path.count("[") >= 3:
                n += 1
    return n


def test_every_published_component_number_reaches_the_reader():
    """R11 on the live payload: a number this door publishes must be legible on
    the row that publishes it (atom D35)."""
    cg = _live_coupled_gaps()
    body = _render(cg)["coupled-gaps"]["innerHTML"]

    total = sum(1 for pair in cg["pairs"] for _ in _leaf_numbers(pair.get("components") or {}))
    # VACUITY, both halves. A payload with no numbers, or one whose numbers all
    # sit above the structural limit, passes this control while proving nothing
    # -- an unexercised check is a failed check (R15 fail-silent).
    assert total > 100, f"only {total} component numbers swept -- control is vacuous"
    deep = _nested_past_the_limit(cg)
    assert deep > 0, (
        "no published number sits past `fmtComponent`'s structural limit on this "
        "payload, so this control never exercises the elision it exists to catch"
    )

    unreadable = _unreadable_numbers(cg, body)
    assert not unreadable, (
        f"{len(unreadable)} of {total} published component numbers are not "
        f"rendered in their own row: {unreadable[:8]}"
    )


def _render_with_mutated_page(mutation: str, replacement: str, data: dict) -> str:
    """Render `data` through a MUTATED copy of the page (R15: prove the control
    fires on its own named defect, not merely that it passes today)."""
    html = INDEX.read_text(encoding="utf-8")
    assert mutation in html, f"mutation anchor gone from index.html: {mutation!r}"
    mutated = html.replace(mutation, replacement, 1)
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "index.html"
        path.write_text(mutated, encoding="utf-8")
        proc = subprocess.run(
            [NODE, str(HARNESS), str(path)],
            input=json.dumps({"coupled_gaps": data}),
            capture_output=True, text=True, timeout=60,
        )
        assert proc.returncode == 0, f"mutated harness failed: {proc.stderr}"
        return json.loads(proc.stdout)["coupled-gaps"]["innerHTML"]


def test_R15_the_control_fires_on_the_pre_repair_depth_limit():
    """THE NAMED DEFECT: restore the bare `return "…"` the door shipped until
    2026-08-11 and this control must FAIL, naming the numbers lost. A control
    that passes both before and after its own repair is not a control."""
    cg = _live_coupled_gaps()
    body = _render_with_mutated_page(
        "    var flat = [], budget = { n: FLAT_NODE_BUDGET };\n"
        "    flattenNumbers(v, \"\", flat, budget);\n"
        "    return flat.length ? flat.join(\", \") : \"…\";",
        '    return "…";',
        cg,
    )
    unreadable = _unreadable_numbers(cg, body)
    assert unreadable, (
        "the pre-repair depth limit rendered every deeply-nested number as '…' "
        "and this control did not notice -- it cannot fail"
    )
    # And it fires WHERE the Hour measured it: both fabric rows, 43 numbers.
    lost = {row for row, _p, _v in unreadable}
    assert {"W1_11_fabric_physics_core", "W1_12_premise_trace_generator"} <= lost, lost
    assert len(unreadable) == 53, (
        f"the pre-repair door dropped 53 published numbers from their own row's "
        f"components block when this Hour measured it (W1_11 22, W1_12 22, "
        f"W2_11 9); this run says {len(unreadable)} -- the count is the finding, "
        "so a change here is a real movement to re-read, not a number to update"
    )


def test_R15_a_number_nested_deeper_than_the_repair_still_reaches_the_reader():
    """RAISING THE LIMIT WOULD HAVE BEEN AN INSTANCE FIX (R10). A figure nested
    one level deeper than anything shipped today must still be legible."""
    data = _one_pair(0.42)
    data["pairs"][0]["components"] = {
        "a": {"b": {"c": {"d": {"deep_figure": 0.123456}}}},
    }
    body = _render(data)["coupled-gaps"]["innerHTML"]
    assert "0.1235" in _components_block(body), body[-600:]


def test_R15_a_subtree_with_no_numbers_still_elides():
    """The repair is about FIGURES. A deep subtree carrying no number keeps the
    ellipsis rather than dumping prose into the components strip -- so this is a
    narrowing of the elision, not its removal."""
    data = _one_pair(0.42)
    data["pairs"][0]["components"] = {"a": {"b": {"c": ["only", "words"]}}}
    body = _render(data)["coupled-gaps"]["innerHTML"]
    assert "…" in _components_block(body)


def test_R15_the_node_budget_and_not_the_depth_bounds_a_cyclic_payload():
    """The depth limit was carrying the spin guard, and never could: a two-deep
    cycle spins INSIDE the limit. The budget is what bounds it -- proven by
    building a cycle in the harness rather than asserting the comment."""
    html = INDEX.read_text(encoding="utf-8")
    # `n` BEFORE the cycle: the budget bounds the walk, so a figure the walk
    # reaches is kept and everything after the cycle is dropped -- bounded, not
    # complete. Asserting completeness after a cycle would be asserting the
    # opposite of what a budget can promise.
    probe = (
        "const cyc = {}; cyc.self = cyc;\n"
        "const out = [];\n"
        "flattenNumbers({deep:{er:{n: 1.5, cyc: cyc}}}, '', out, {n: 2000});\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    code = html.split("<script>")[1].split("</script>")[0]
    with tempfile.TemporaryDirectory() as td:
        script = Path(td) / "probe.mjs"
        # Only the pure helper is needed; the page's DOM-touching tail is not run.
        helper = code[code.index("var FLAT_NODE_BUDGET"):code.index("function fmtComponent")]
        script.write_text(helper + probe, encoding="utf-8")
        proc = subprocess.run([NODE, str(script)], capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, f"the cyclic payload was not bounded: {proc.stderr[:400]}"
    assert "1.5000" in proc.stdout, proc.stdout
