"""Full-door render tests for the Proof door (site/proof/index.html).

The Proof door had only panel-specific tests (test_coupled_gaps_panel.py,
test_killlist_panel.py) -- no door-level render test like the other canonical
doors. This closes that parity gap, mirroring site/world/test_world_door.py and
site/project/test_project_door.py, and complements (does not replace) the two
existing panel tests.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness that drives the WHOLE render sequence) against
the REAL published site/data/proof.json, then assert the produced HTML contains
the actual source values, formatted the way the page's OWN num() helper formats
them (Number.toLocaleString "en-GB" grouping) -- the rendered pixel, not a brittle
Python int repr.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant).

R3 (the page is a rendering, never an author) and R1 (every claim links to its
evidence) are asserted structurally on the nav + evidence links.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
HARNESS = HERE / "_door_harness.mjs"
DATA = HERE.parent / "data" / "proof.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not available")


def _num(n) -> str:
    """Mirror the page's num(): Number.toLocaleString('en-GB') thousands grouping."""
    return f"{int(n):,}" if n is not None else "--"


def _live() -> dict:
    return json.loads(DATA.read_text())


def _render(data: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(data),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"harness failed: {proc.stderr}"
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# R11: the page renders the live source values (the pixel, not a source string)
# ---------------------------------------------------------------------------
def test_verification_kpis_render_live_values():
    d = _live()
    out = _render(d)
    kpis = out["verify-kpis"]["innerHTML"]
    v = d["verification"]
    # Rendered via num() -> toLocaleString grouping. Assert the grouped pixel.
    assert f'>{_num(v["expert_hour_passed"])}<' in kpis, kpis
    assert f'>{_num(v["findings_caught_total"])}<' in kpis, kpis
    assert f'>{_num(v["atom_count"])}<' in kpis, kpis


def test_build_note_renders_provenance_not_effort_metric():
    # RC5 (DIRECTOR_AXIS1 verdict 2026-07-23): effort metrics are NOT outcomes and
    # must not be surfaced. The build footer is provenance only.
    d = _live()
    out = _render(d)
    note = out["build-note"]["textContent"]
    # R2 freshness: the generated_at stamp is rendered on the surface.
    assert d["generated_at"] in note, note
    # ...and the effort metric (test_count) is NOT surfaced.
    assert "tests" not in note.lower(), f"effort metric leaked into build footer: {note!r}"
    assert str(d.get("test_count", "")) not in note, note


def test_timeline_intro_renders_live_rule_count():
    d = _live()
    out = _render(d)
    intro = out["timeline-intro"]["textContent"]
    # "N permanent rules (R1-RN)" both track d.rule_count.
    assert f'{d["rule_count"]} permanent rules' in intro, intro
    assert f'R1-R{d["rule_count"]}' in intro, intro


def test_banked_note_is_honest_and_evidence_linked():
    d = _live()
    out = _render(d)
    note = out["banked-note"]["innerHTML"]
    # Levels banked reflect the live levels_banked map (honest, not rounded up).
    lb = d["verification"]["levels_banked"]
    for lvl, cnt in lb.items():
        assert f"{cnt} at L{lvl}" in note, (lvl, cnt, note)
    # R1: the banked claim cites its evidence (the maturity map).
    assert "maturity_map.yaml" in note, note


# ---------------------------------------------------------------------------
# R15: independence -- a mutated source value must move the rendered pixel
# ---------------------------------------------------------------------------
def test_defects_caught_pixel_is_independent_of_render():
    d = _live()
    d["verification"]["findings_caught_total"] = 424242
    out = _render(d)
    assert ">424,242<" in out["verify-kpis"]["innerHTML"]


def test_freshness_pixel_is_independent_of_render():
    d = _live()
    d["generated_at"] = "2099-01-01T00:00:00Z"
    out = _render(d)
    assert "2099-01-01T00:00:00Z" in out["build-note"]["textContent"]


def test_rule_count_pixel_is_independent_of_render():
    d = _live()
    d["rule_count"] = 77
    out = _render(d)
    intro = out["timeline-intro"]["textContent"]
    assert "77 permanent rules" in intro
    assert "R1-R77" in intro


# ---------------------------------------------------------------------------
# R3 (nav is canonical) and R1 (claim -> evidence)
# ---------------------------------------------------------------------------
def _site_nav(text: str) -> str:
    m = re.search(r'<nav class="site-nav">(.*?)</nav>', text, re.S)
    assert m, "site-nav block not found"
    return m.group(1)


def test_canonical_nav_is_five_surface_ia():
    # SITE_V5 (ruling 2026-07-23): nav is cut to the five-surface IA. Method,
    # Journey and Simplified are KILLED doors -- they fold into Proof and must
    # NOT appear in the nav; their old URLs 301 (see site/_redirects).
    nav = _site_nav(INDEX.read_text())
    for label in ("Home", "The World", "The Company", "Proof"):
        assert f">{label}</a>" in nav, f"nav missing five-surface door {label!r}"
    assert 'href="../proof/" class="nav-link active">Proof</a>' in nav
    # killed doors are gone from the nav...
    for killed in ("../method/", "../simplified/", "../project/", "../tours/"):
        assert killed not in nav, f"killed door {killed!r} still linked in nav"
    for label in (">Method</a>", ">Journey</a>", ">Simplified</a>"):
        assert label not in nav, f"killed-door label {label!r} still in nav"
    # The Director door is auth-gated and must NOT appear in the public nav.
    assert "../director/" not in nav, "Director door must not be in the public nav"
    assert ">Director</a>" not in nav


# ---------------------------------------------------------------------------
# SITE_V5 surface 4 single job: "corrects itself in public" + Method/Simplified fold-in
# ---------------------------------------------------------------------------
def test_claim_status_legend_and_challenge_channel_present():
    text = INDEX.read_text()
    # Every figure carries a claim-status (SITE_CONSTITUTION rule 6): the reading key
    # is on the surface with the full vocabulary.
    for status in ("VERIFIED", "PROVISIONAL", "PLANNED", "RETRACTED"):
        assert status in text, f"claim-status vocabulary missing {status!r}"
    # The challenge channel -- the "corrects itself in public" loop, made usable.
    assert 'id="challenge-channel"' in text, "challenge channel section missing"
    assert "director_comments.py" in text, "challenge channel must name its server-side check"


def test_method_folds_in_rendered_from_live_data_r11():
    out = _render(_live())
    rules = out["method-rules"]["innerHTML"]
    roles = out["method-roles"]["innerHTML"]
    method = json.loads((DATA.parent / "method.json").read_text())
    # R11: real rules from method.json render as pixels (id + name).
    first = method["rules"][0]
    assert first["id"] in rules and first["name"] in rules, rules
    # the operating-model roles render too.
    assert method["operating_model"]["roles"][0]["name"] in roles, roles


def test_method_fold_in_is_independent_of_render_r15():
    # R15: inject a mutated method payload; the pixel must follow.
    sentinel_id, sentinel_name = "R999", "Sentinel Rule 9931"
    payload = {
        "proof": _live(),
        "method": {"rules": [{"id": sentinel_id, "name": sentinel_name,
                              "description": "d", "incident": "i"}],
                   "operating_model": {"roles": []},
                   "method_framing": "f"},
    }
    out = _render(payload)
    assert sentinel_id in out["method-rules"]["innerHTML"], "mutated rule id did not reach the pixel"
    assert sentinel_name in out["method-rules"]["innerHTML"], "mutated rule name did not reach the pixel"


def test_simplified_appendix_rendered_from_live_data_r11():
    out = _render(_live())
    kpis = out["simplified-kpis"]["innerHTML"]
    s = json.loads((DATA.parent / "simplified.json").read_text())
    # R11: the register totals render as pixels via num() grouping.
    assert f'>{_num(s["total_notes"])}<' in kpis, kpis
    assert f'>{_num(s["total_atoms_with_notes"])}<' in kpis, kpis


def test_simplified_appendix_is_independent_of_render_r15():
    # R15: mutate the note total; the rendered pixel must follow.
    d = _live()
    payload = {"proof": d, "simplified": {
        "total_notes": 987654, "total_atoms_with_notes": 321,
        "lanes": [{"lane": "x", "lane_name": "X Lane", "atoms": []}]}}
    out = _render(payload)
    assert ">987,654<" in out["simplified-kpis"]["innerHTML"], "mutated note total did not reach the pixel"


def test_corrections_rendered_in_place_from_live_data_r11():
    # The single job made mechanical: a real withdrawn claim renders IN PLACE --
    # the old value struck through (cor-was), the corrected value beside it, a
    # RETRACTED status, the artefact linked. Fed by proof.json.corrections.
    d = _live()
    out = _render(d)
    body = out["corrections"]["innerHTML"]
    cors = d.get("corrections", [])
    assert cors, "proof.json carries no corrections feed -- the single job has no data"
    first = cors[0]
    assert first["id"] in body, body
    assert first["was"] in body, "withdrawn value not rendered"
    assert first["now"] in body, "corrected value not rendered"
    assert "RETRACTED" in body, "RETRACTED status not rendered"
    assert "cor-was" in body, "struck-through class not present -- not 'in place'"
    # R1: the correction cites the artefact that forced it.
    assert first["source"] in body, "correction not evidence-linked"


def test_corrections_pixel_is_independent_of_render_r15():
    # R15: mutate a correction's corrected value; the rendered pixel must follow.
    d = _live()
    d["corrections"] = [{
        "id": "COR-TEST", "date": "2099-01-01", "status": "RETRACTED",
        "claim": "sentinel claim", "was": "the old sentinel value",
        "now": "SENTINEL-CORRECTED-7742", "correction": "c", "source": "docs/x.md"}]
    out = _render(d)
    assert "SENTINEL-CORRECTED-7742" in out["corrections"]["innerHTML"], "mutated correction did not reach the pixel"


def test_corrections_fail_closed_visible_when_absent():
    # R15 fail-silent guard: an empty corrections feed must say so, not render blank.
    d = _live()
    d["corrections"] = []
    out = _render(d)
    assert "No corrections on the record" in out["corrections"]["innerHTML"]


def test_no_effort_metric_on_the_surface_rc5():
    # RC5: no test-count / commit-count effort metric anywhere the page renders.
    out = _render(_live())
    surface = "".join((out[k]["innerHTML"] + out[k]["textContent"]) for k in out if out[k])
    for effort in ("18504", "18,504", "tests collected", "commits/day"):
        assert effort not in surface, f"effort metric {effort!r} leaked onto the proof surface"


def test_at_least_one_claim_evidence_link():
    d = _live()
    out = _render(d)
    # R1: the timeline rules link out to their retrospectives (the incident that
    # forged each rule), and the banked-levels claim cites the maturity map.
    combined = out["banked-note"]["innerHTML"]
    text = INDEX.read_text()
    assert 'class="evlink"' in text, "no evidence-link class present on the door"
    assert "maturity_map.yaml" in combined, "banked-levels claim not evidence-linked"
