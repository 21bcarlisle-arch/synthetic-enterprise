"""Render-side tests for the Home door (site/index.html).

The Home door is the front door in every door's nav, yet -- like the Journey door
before its test landed -- it had no full render test (only the cross-door audit's
static scan). This closes that parity gap, mirroring site/world/test_world_door.py
and site/project/test_project_door.py.

R11 (verify to the rendered value): these execute the page's ACTUAL inline
JavaScript (via a Node/vm harness) against the REAL published site/data/*.json the
page consumes, then assert the produced HTML contains the actual source values,
formatted the way the page's OWN gbp() helper formats them (Number.toLocaleString
"en-GB" grouping, round-half-up to whole pounds) -- the rendered pixel, not a
brittle Python float repr of the source.

R15 (a control must be able to FAIL): a mutation of a source value must change the
rendered pixel (independence -- the render is not a hard-coded constant).

R3 (the page is a rendering, never an author) and R1 (every claim links to its
evidence) are asserted structurally on the nav + evidence links.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = HERE / "index.html"
DATA = HERE / "data"

# DIRECTOR_RULING_FRONT_MISSION_BLOCK (2026-07-24): the front door no longer renders
# any live figure -- it leads with the idea (the personalisation-abatement mission),
# the score/yardstick, the honest "not yet instrumented" state, and the diagram. The
# cost-to-serve leg (the only dynamic render this door had) moved to /proof, and its
# R11/R15 render tests moved with it (site/proof/test_proof_door.py). These remaining
# tests are static-scan structural guards, so no Node render harness is needed.


# ---------------------------------------------------------------------------
# RC7: no cohort-derived £ figure leads the front door
# ---------------------------------------------------------------------------
def test_no_cohort_financials_lead_the_front_door():
    """RC7 (DIRECTOR_RULING_IDEA_FIRST_EXTERNAL_REGISTER 2026-07-24): no £ figure
    derived from the curriculum cohort may lead a public surface. The pulse strip
    (net margin / treasury / enterprise value / bills) is removed from the front
    door -- those diagnostics live only inside /proof, framed as teaching-cohort
    output. This is an R10 class guard: it reds if ANY cohort aggregate financial
    is re-rendered on the front door (re-adding renderPulseStrip -> fail), not just
    the one instance the ruling caught.
    """
    text = INDEX.read_text()
    assert 'id="pulse-strip"' not in text, "cohort-financial pulse strip is back on the front door (RC7)"
    assert "renderPulseStrip" not in text, "renderPulseStrip re-added to the front door (RC7)"
    for cohort_fin in ("net_margin_gbp", "treasury_end_gbp", "enterprise_value_gbp", "bills_total"):
        assert cohort_fin not in text, f"cohort financial {cohort_fin!r} leads the front door (RC7)"
    # Teeth: the source data DOES carry these fields (so the guard is meaningful,
    # not vacuously passing on an empty schema) -- they are simply not on this door.
    p = json.loads((DATA / "dashboard.json").read_text())["portfolio"]
    assert "net_margin_gbp" in p and "treasury_end_gbp" in p


# ---------------------------------------------------------------------------
# DIRECTOR_RULING_FRONT_MISSION_BLOCK (2026-07-24): the falsifiable claim on the
# front door is the personalisation-abatement MISSION -- its score (£/tCO2e) and
# yardstick (£273/tCO2e, 2025) named, its number honestly ABSENT until instrumented.
# The cost-to-serve arbitrage leg (the wrong thesis: "cheap-therefore-green") is
# GONE from the front and lives on /proof#economics-anchor. These are static-scan
# guards on the rendered markup (the block carries no live figure to render).
# ---------------------------------------------------------------------------
def test_mission_block_leads_with_score_and_yardstick():
    text = INDEX.read_text()
    # The score and the external yardstick lead the front door, in the v4 register.
    assert "carbon abatement through personalisation" in text
    assert "273/tCO&#8322;e (2025)" in text, "the £273/tCO2e (2025) government yardstick is not on the front door"
    assert "per tonne of CO&#8322;e saved" in text
    # The honest state is stated plainly: designed, not instrumented, no number shown.
    assert "designed, not\n    yet instrumented" in text or "designed, not yet instrumented" in text.replace("\n    ", " ")


def test_cost_arbitrage_leg_no_longer_leads_the_front_door():
    """The cost-to-serve arbitrage hypothesis recast the company as
    cheap-therefore-green (the wrong thesis, director 2026-07-24). It must be OFF
    the front door -- no numerator framing, no live opex_ledger render, no chart."""
    text = INDEX.read_text()
    assert "numerator of &pound;/tCO" not in text, "the cost-to-serve numerator leg still leads the front door"
    assert 'id="thesis-chart"' not in text, "the cost-to-serve chart is still on the front door"
    assert "renderThesisChart" not in text, "the cost-to-serve render is still on the front door"
    assert "opex_ledger" not in text, "the front door still renders the cohort opex_ledger figure"
    # It is preserved on /proof -- the front points there rather than deleting it.
    assert 'href="./proof/#economics-anchor"' in text, "the front does not point to the relocated economics leg"


# ---------------------------------------------------------------------------
# R3 (nav is canonical) and R1 (claim -> evidence)
# ---------------------------------------------------------------------------
def _site_nav(text: str) -> str:
    # SITE_V5 surface 1 iteration 2 (2026-07-23): the nav is the architectural
    # header block (BRAND_CONSTITUTION exemplar) -- type-only wordmark + the door
    # links. The canonical door list + Home-active + director-absent invariants are
    # unchanged; only the markup grammar moved (tests move with the doors).
    m = re.search(r'<header class="site-nav">(.*?)</header>', text, re.S)
    assert m, "site-nav header block not found"
    return m.group(1)


def test_canonical_nav_present_and_director_absent():
    nav = _site_nav(INDEX.read_text())
    # SITE_V5 surface 1: the five-surface IA -- Home / The World / The Company /
    # Proof (Director window is off-nav, auth-gated). Method/Journey/Simplified
    # folded into Proof/World at their own surfaces; updated in lockstep with the
    # nav rebuild (SITE_V5_STRUCTURE_CONFIRMATION.md §1: tests move with the doors).
    # DERIVED FROM THE REGISTER, not listed here (2026-08-19). This assertion used to name the
    # labels literally, which is why it went red the moment the director folded the nav from
    # eight tabs to five -- and why eight separate copies of the tab list existed to drift apart
    # in the first place. That drift IS the defect Step 0 was written to abolish: the director
    # read six items on Home and nine on Knowledge. A test that re-states the nav is a second
    # definition of it. There is one definition, and this reads it.
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
    from ia_register import CANONICAL_NAV as _NAV
    for label in tuple(i.label for i in _NAV):
        assert f">{label}</a>" in nav, f"nav missing canonical door {label!r}"
    # Home is the current door -> marked active.
    assert 'href="./" class="active">Home</a>' in nav
    # The Director door is auth-gated and must NOT appear in the public nav.
    assert "./director/" not in nav, "Director door must not be in the public nav"
    assert ">Director</a>" not in nav


def test_at_least_one_claim_evidence_link():
    text = INDEX.read_text()
    # R1: the front door leads with the idea + diagram (no live figure of its own),
    # so its claims link OUT to the evidence surfaces -- the mission's economics leg
    # to /proof, and the door/node cards to the World/Company/Proof surfaces.
    assert 'href="./proof/#economics-anchor"' in text, "mission block does not link to its economics evidence"
    assert 'href="./company/"' in text or 'href="./world/"' in text, \
        "no claim->evidence link to an evidence door found"


# ---------------------------------------------------------------------------
# F-MOAP-1: the director-approved model-on-a-page diagram is hosted on the front
# door, exactly once, as a resolvable asset with real alt text.
# R11 (verify to the rendered value): the <img src> the page ships MUST resolve to
# a file that exists in the published tree -- a broken image is a dead pixel.
# R15 (a control that can FAIL): the guard fails if the asset is missing (rename
# the file -> red) or the alt text is stripped (accessibility regression -> red).
# ---------------------------------------------------------------------------
def test_model_on_a_page_diagram_hosted_and_resolves():
    text = INDEX.read_text()
    m = re.search(r'<img\s+src="(\./assets/model-on-a-page\.svg)"\s+alt="([^"]+)"', text)
    assert m, "model-on-a-page diagram <img> (with src+alt) not found on the front door"
    src, alt = m.group(1), m.group(2)
    # Hosted exactly once -- ONE host, no duplicate embeds (§B: one host).
    assert text.count("assets/model-on-a-page.svg") == 1, "diagram must be hosted exactly once"
    # R11: the referenced asset exists in the published tree.
    asset = (HERE / "assets" / "model-on-a-page.svg")
    assert asset.exists(), f"diagram asset missing on disk: {asset}"
    # Alt text is real, not a placeholder -- names the model's four movements.
    assert len(alt) > 200, "alt text too thin for a complex diagram (accessibility)"
    for movement in ("wall", "company", "score", "governance"):
        assert movement.lower() in alt.lower(), f"alt text omits the {movement!r} movement"
