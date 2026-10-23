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
import re
from pathlib import Path

from test_the_published_bytes_reader import (
    published_blob,
    published_json,
    refuse_working_tree_reads,
)

HERE = Path(__file__).resolve().parent

# THE SUBJECTS, AS PATHS IN GIT RATHER THAN FILES ON DISK (2026-09-10). These are strings and not
# `Path`s because a door test whose subject is `HERE / "index.html"` cannot tell "the reader can
# see this" from "someone in this tree has edited it and not landed it" -- and those are the only
# two states it exists to separate. The front door is the one every other door's nav points at, so
# a ruling re-broken in the tree reading here as a ruling still held is the worst version of that.
# `site/test_the_published_bytes_reader.py` holds the reader and argues why the published copy is the INDEX copy
# and not `HEAD`.
INDEX_REL = "site/index.html"
DASHBOARD_REL = "site/data/dashboard.json"
CAPABILITIES_REL = "site/capabilities/index.html"

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
    text = published_blob(INDEX_REL)
    assert 'id="pulse-strip"' not in text, "cohort-financial pulse strip is back on the front door (RC7)"
    assert "renderPulseStrip" not in text, "renderPulseStrip re-added to the front door (RC7)"
    for cohort_fin in ("net_margin_gbp", "treasury_end_gbp", "enterprise_value_gbp", "bills_total"):
        assert cohort_fin not in text, f"cohort financial {cohort_fin!r} leads the front door (RC7)"
    # Teeth: the source data DOES carry these fields (so the guard is meaningful,
    # not vacuously passing on an empty schema) -- they are simply not on this door.
    p = published_json(DASHBOARD_REL)["portfolio"]
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
    """The mission is on the front door, and the account of what it does not yet deliver is one
    click away on Capabilities (director steer of 22 Oct 2026: "the claims are really weak they
    mostly point to failings in the model"; the gaps moved there, none deleted). The front door
    names money, time and carbon, so this reds if the page that says which of them is unmeasured
    stops carrying that account, or the front door stops linking to it."""
    text = published_blob(INDEX_REL)
    # SCAN WHAT A READER SEES, NOT THE SOURCE: a comment recording which sentence was superseded
    # necessarily quotes it.
    rendered = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    body = rendered.split("</head>", 1)[-1].replace("\n    ", " ").replace("\n  ", " ")
    rendered = rendered.replace("\n    ", " ")
    assert "<meta name=\"description\"" in text and "money, time and carbon" not in body.split("<body")[0], (
        "the head/body split this control depends on has moved"
    )
    assert "carbon abatement through personalisation" not in rendered, (
        "the front door still publishes the mission sentence the director superseded on 2026-08-28"
    )
    assert "find individual customers we can create value for" in body, (
        "the front door does not carry the mission's finding-and-creating clause"
    )
    assert "money, time and carbon" in body, (
        "the front door names fewer than the mission's three currencies"
    )
    assert "cheapest tonne" not in rendered, "the front door leads with the withdrawn carbon headline"
    assert 'href="./capabilities/#not-built"' in body, (
        "the front door names three currencies and no longer links to what is not built"
    )

    caps = published_blob(CAPABILITIES_REL)
    gaps = caps[caps.index('<section id="not-built">'):]
    gaps = gaps[: gaps.index("</section>")].replace("\n    ", " ")
    assert "273/tCO&#8322;e (2025)" in gaps, "the £273/tCO2e (2025) yardstick has no home"
    assert "per tonne of CO&#8322;e saved" in gaps
    assert "Time is defined but not yet measured" in gaps, (
        "the site claims to save time without saying nothing measures it yet"
    )
    assert "only <strong>tariffs</strong> reaches one today" in gaps, (
        "the site names three channels without saying only one reaches a household"
    )
    assert "NOT YET MEASURED" in gaps, "carbon saved's honest tag has gone"
    assert "Abatement is not emissions" in gaps, (
        "the site no longer distinguishes abatement from emissions"
    )
    assert "No customers. No licence." in gaps, "the licence disclosure has no home"
    # The per-domain lines moved up on 23 Oct into their own table (steer "the other pages match
    # the front door", item 3.2); the not-built section points to it.
    assert 'href="#against"' in gaps, "what is not built no longer points to the per-domain lines"
    against = caps[caps.index('<section id="against">'):]
    against = against[: against.index("</section>")]
    assert against.count("<b>Not yet:</b>") >= 6, "the per-domain 'Not yet' lines did not all move"


def test_cost_arbitrage_leg_no_longer_leads_the_front_door():
    """The cost-to-serve arbitrage hypothesis recast the company as
    cheap-therefore-green (the wrong thesis, director 2026-07-24). It must be OFF
    the front door -- no numerator framing, no live opex_ledger render, no chart."""
    text = published_blob(INDEX_REL)
    assert "numerator of &pound;/tCO" not in text, "the cost-to-serve numerator leg still leads the front door"
    assert 'id="thesis-chart"' not in text, "the cost-to-serve chart is still on the front door"
    assert "renderThesisChart" not in text, "the cost-to-serve render is still on the front door"
    assert "opex_ledger" not in text, "the front door still renders the cohort opex_ledger figure"
    # It is preserved on /proof -- the front points there rather than deleting it.
    assert 'href="./harness/"' in text, "the front does not point to the relocated economics leg"


# ---------------------------------------------------------------------------
# R3 (nav is canonical) and R1 (claim -> evidence)
# ---------------------------------------------------------------------------
def _site_nav(text: str) -> str:
    # SITE_V5 surface 1 iteration 2 (2026-07-23): the nav is the architectural
    # header block (BRAND_CONSTITUTION exemplar) -- type-only wordmark + the door
    # links. The canonical door list + Home-active + director-absent invariants are
    # unchanged; only the markup grammar moved (tests move with the doors).
    # ONE GRAMMAR (2026-08-19). Home used `<header class="site-nav">` while every other page
    # used `<nav class="site-nav">`, which is why a layout rule that fixed the others could not
    # fix Home -- the structural half of "it renders differently between those pages". Home now
    # uses the same element as everywhere else, so this matches the shared shape.
    m = re.search(r'<nav class="site-nav">(.*?)</nav>', text, re.S)
    assert m, "site-nav block not found"
    return m.group(1)


def test_canonical_nav_present_and_director_absent():
    nav = _site_nav(published_blob(INDEX_REL))
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
    assert 'href="./" class="nav-link active">Home</a>' in nav
    # The Director door is auth-gated and must NOT appear in the public nav.
    assert "./director/" not in nav, "Director door must not be in the public nav"
    assert ">Director</a>" not in nav


def test_at_least_one_claim_evidence_link():
    text = published_blob(INDEX_REL)
    # R1: the front door leads with the idea + diagram (no live figure of its own),
    # so its claims link OUT to the evidence surfaces -- the mission's economics leg
    # to /proof, and the door/node cards to the World/Company/Proof surfaces.
    assert 'href="./harness/"' in text, "mission block does not link to its economics evidence"
    assert 'href="./capabilities/' in text or 'href="./harness/' in text, \
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
    text = published_blob(INDEX_REL)
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


def test_the_front_door_carries_its_figures_without_javascript():
    """Director steer of 22 Oct 2026, item 8: "Loading the latest run..." showed a search engine,
    a link preview or a script-blocked reader nothing. The proof strip is now written into the
    HTML at publish (`tools/generate_dashboard_data.py::write_front_door_proof_strip`), so the
    published bytes themselves must hold every figure and its clock. Reds if the strip goes back
    to being filled by a script, or is published empty."""
    html = published_blob(INDEX_REL)
    start = html.find("<!-- PROOF-STRIP:START")
    end = html.find("<!-- PROOF-STRIP:END -->")
    assert 0 <= start < end, "the front door has lost the proof strip's markers"
    cells = re.findall(r'<div class="lf"><div class="v">([^<]+)</div><div class="l">([^<]+)</div>'
                       r'<div class="c">([^<]+)</div></div>', html[start:end])
    assert len(cells) >= 3, f"the published strip holds {len(cells)} figures, not three or more"
    assert all(value.strip() and clock.strip() for value, _label, clock in cells), cells
    assert "Loading the latest run" not in html
    assert 'getElementById("lf-row")' not in html, "a script fills the strip again"


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    """THE RELAPSE GUARD: this file's own AST, rather than my having been careful.

    Every assertion above is a class guard over a director ruling -- no cohort figure leads the
    front door, the nav is complete, each claim links to its evidence. All of them would go on
    passing on a front door that had been repaired in this tree and never published. The scanner's
    own teeth are proved in `site/test_the_published_bytes_reader.py`.
    """
    refuse_working_tree_reads(__file__, (INDEX_REL, DASHBOARD_REL, CAPABILITIES_REL))
