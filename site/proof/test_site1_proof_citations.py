"""Proof-door half of the 2026-07-29 cold-eyes Expert Hour on SITE1_expert_doors.

Findings closed here (verbatim ids from
docs/design/maturity_map.yaml :: SITE1_expert_doors.expert_hour.findings):

  MAJOR-7  "evidence citations that are inert by construction ... the /proof/ rule/
           correction timeline renders sources as <a class=evlink href=# onclick=return
           false> -- 10 such anchors in the served HTML, using the SAME class as
           genuinely live evidence links. The cited paths are not published:
           /docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md -> 404,
           and that is the source for COR-1, the flagship retraction."
  MINOR-9  (proof-door half ONLY) "all evidentiary content is JS-only with no <noscript>
           fallback ... a non-JS crawler indexes 'Loading...' as the content of the
           evidence pages."  The sitemap.xml / robots.txt / glossary legs of MINOR-9 are
           OUTSIDE this fork's file scope and remain OPEN.
  MINOR-10 "the claim-status vocabulary cannot say 'we chose this number': /proof/
           renders VERIFIED / PROVISIONAL / PLANNED / RETRACTED -- missing
           chosen-not-derived and external-benchmark, both of which SITE_CONSTITUTION
           rule 6 names."

MAJOR-3 (the predictions ledger that could not record a miss) is NOT covered here --
it was closed independently on main by a7f71b3b0 and is tested by the sibling file
test_predictions_ledger_can_fail.py.

R11: the citation tests execute the page's ACTUAL inline JavaScript through the existing
Node/vm door harness and assert on the RENDERED string, never the source alone. The
<noscript> and claim-legend tests assert on the served HTML because that content IS
static markup -- no JS runs to produce it, so the file byte IS the rendered pixel.

R15: every control below is proven to fire on its own named defect AND to clear on good
input. Absence-style assertions ("no dead anchor") are the classic FAIL-OPEN shape -- an
empty or truncated file would satisfy them trivially -- so each one is paired with a
non-emptiness floor asserted first.

Anti-pin discipline: nothing here pins a generated value (a count of links, a date, a
specific rule id). Every assertion is a RELATIONSHIP -- "a published path renders as a
link, a repo-internal one does not" -- so regenerating the data can never wedge it.
"""
from __future__ import annotations

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

# The exact defect signature MAJOR-7 named: an anchor that is dead by construction.
# Deliberately BROADER than the finding's literal string (any bare-fragment href, with or
# without the click suppressor) so a cosmetic rewrite of the same lie is still caught.
_DEAD_ANCHOR = re.compile(r'<a\b[^>]*\bhref="#"[^>]*>')
_SUPPRESSED_CLICK = re.compile(r'onclick="return false"')

# A citation the reviewer verified 404s live, and the source for COR-1, the flagship
# retraction. Named as a path fragment, not pinned to a line/count.
COR1_SOURCE_FRAGMENT = "HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md"


def _index_text() -> str:
    """Read the served HTML, with the FAIL-OPEN floor asserted up front: a missing,
    empty or truncated index.html must never let an absence-test pass vacuously."""
    assert INDEX.is_file(), f"{INDEX} does not exist -- absence checks would pass vacuously"
    text = INDEX.read_text()
    assert len(text) > 10_000, f"index.html implausibly small ({len(text)} B)"
    assert 'class="evlink"' in text, "no evlink citations at all -- the checker has nothing to check"
    assert "function srcCite(" in text, "srcCite (the MAJOR-7 shared citation renderer) is gone"
    return text


def _live() -> dict:
    assert DATA.is_file(), f"{DATA} missing"
    return json.loads(DATA.read_text())


def _render(payload: dict) -> dict:
    proc = subprocess.run(
        [NODE, str(HARNESS), str(INDEX)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=60,
    )
    # FAIL-SILENT guard: a harness that cannot run is a FAILED check, never a skipped one.
    assert proc.returncode == 0, f"door harness failed (rc={proc.returncode}): {proc.stderr}"
    out = json.loads(proc.stdout)
    assert out, "harness produced an empty render"
    return out


def _dead_anchor_count(html_text: str) -> int:
    return len(_DEAD_ANCHOR.findall(html_text))


# ===========================================================================
# MAJOR-7 -- source-level: the defect signature is gone from the served HTML
# ===========================================================================
def test_no_dead_anchor_in_the_served_html():
    text = _index_text()
    assert _dead_anchor_count(text) == 0, (
        "a fake evidence anchor (bare-fragment href) is present in the served HTML")
    assert not _SUPPRESSED_CLICK.search(text), (
        "a click-suppressed anchor is present in the served HTML")


def test_dead_anchor_checker_fires_on_the_reintroduced_defect_and_clears_again():
    """R15 both ways, on a SCRATCH string -- never the real file."""
    clean = _index_text()
    assert _dead_anchor_count(clean) == 0

    # Fires: the exact historical defect.
    reintroduced = clean.replace(
        "</body>",
        '<a class="evlink" href="#" onclick="return false" title="docs/x.md">docs/x.md</a></body>')
    assert _dead_anchor_count(reintroduced) == 1, "checker did NOT fire on the reintroduced defect"
    assert _SUPPRESSED_CLICK.search(reintroduced)

    # Still fires on the cosmetic variant (click suppressor dropped) -- the lie is the
    # bare-fragment href, not the onclick.
    cosmetic = clean.replace("</body>", '<a class="evlink" href="#">docs/x.md</a></body>')
    assert _dead_anchor_count(cosmetic) == 1, "checker missed the cosmetic variant of the same defect"

    # Clears: a genuinely resolvable link must NOT trip the checker (no false positive).
    good = clean.replace(
        "</body>", '<a class="evlink" href="https://example.com/x.md">x</a></body>')
    assert _dead_anchor_count(good) == 0, "checker false-positives on a real link"


# ===========================================================================
# MAJOR-7 -- rendered pixels (R11)
# ===========================================================================
def test_whole_rendered_door_contains_no_dead_anchor():
    out = _render(_live())
    rendered = "".join((v or {}).get("innerHTML", "") for v in out.values())
    # FAIL-OPEN floor: prove the door actually rendered before asserting an absence.
    assert len(rendered) > 5_000, f"render implausibly small ({len(rendered)} B)"
    assert 'class="evlink"' in rendered, "no real evidence links rendered at all"
    assert _dead_anchor_count(rendered) == 0, "a dead anchor is present in the RENDERED door"


def test_repo_internal_path_renders_as_an_inert_tagged_span_not_a_link():
    out = _render(_live())
    note = out["banked-note"]["innerHTML"]
    assert "maturity_map.yaml" in note, note
    assert 'class="evsrc"' in note, f"repo-internal citation is not rendered inert: {note}"
    assert "unpublished" in note, note
    assert "<a " not in note, f"repo-internal citation still rendered as an anchor: {note}"


def test_the_cor1_404_citation_specifically_renders_inert():
    """The finding's own flagship example: COR-1's source 404s live."""
    out = _render(_live())
    cors = out["corrections"]["innerHTML"]
    assert COR1_SOURCE_FRAGMENT in cors, (
        "COR-1's source citation is not on the page at all -- provenance must still be SHOWN, "
        "just not dressed as a link")
    idx = cors.index(COR1_SOURCE_FRAGMENT)
    window = cors[max(0, idx - 300):idx + 300]
    assert 'class="evsrc"' in window, f"COR-1's 404 source is not rendered inert: {window}"
    assert 'class="evlink"' not in window, f"COR-1's 404 source still styled as a live link: {window}"


def test_a_genuine_https_source_still_renders_as_a_real_link():
    """R15 the other way: the fix must not turn EVERY citation inert."""
    d = _live()
    d["principles"] = [{"title": "Sentinel", "number": "N=1", "claim": "c", "why": "w",
                        "basis": "b", "source": "https://example.com/real-source"}]
    body = _render({"proof": d})["principles"]["innerHTML"]
    assert '<a class="evlink" href="https://example.com/real-source"' in body, body
    assert 'target="_blank"' in body and 'rel="noopener"' in body, body
    assert 'class="evsrc"' not in body, f"a genuinely resolvable source was wrongly made inert: {body}"


def test_a_published_retrospective_path_renders_as_a_real_link():
    """docs/retrospectives/*.md IS published (mirrored to GitHub Pages), so it stays a link.
    Asserts the RELATIONSHIP -- path maps onto the same base the page already uses for its
    timeline retro links -- not a pinned URL from generated data."""
    d = _live()
    d["principles"] = [{"title": "S2", "number": "N=1", "claim": "c", "why": "w", "basis": "b",
                        "source": "docs/retrospectives/2026-07-04-verification-week.md"}]
    body = _render({"proof": d})["principles"]["innerHTML"]
    m = re.search(r'<a class="evlink" href="(https://[^"]+/retrospectives/[^"]+\.md)"', body)
    assert m, f"a published retrospective path was not rendered as a real link: {body}"
    assert m.group(1).endswith("2026-07-04-verification-week.md"), m.group(1)


def test_a_bare_retrospectives_directory_is_not_faked_into_a_file_link():
    """The bare directory is not itself a served page -- it must render inert rather than
    become a link to a URL that does not resolve. (COR-3 carries exactly this source.)"""
    d = _live()
    d["principles"] = [{"title": "S3", "number": "N=1", "claim": "c", "why": "w", "basis": "b",
                        "source": "docs/retrospectives/"}]
    body = _render({"proof": d})["principles"]["innerHTML"]
    assert 'class="evsrc"' in body, f"bare docs/retrospectives/ was turned into a link: {body}"
    assert '<a ' not in body, body


def test_timeline_shows_both_the_retro_links_and_the_source_citation():
    """The dead-code half of MAJOR-7: `src` was computed and never used -- the source only
    appeared when retro links were ABSENT, so a rule with both showed its source nowhere."""
    d = _live()
    d["timeline"] = [{
        "date": "2026-01-01", "id": "R-TEST", "name": "n", "rule": "r", "incident": "i",
        "source": "docs/staging/SENTINEL_SOURCE.md",
        "retro_links": [{"filename": "sentinel-retro.md",
                         "link": "https://example.com/retrospectives/sentinel-retro.md"}],
    }]
    d["rule_count"] = 1
    tl = _render({"proof": d})["timeline"]["innerHTML"]
    assert "sentinel-retro.md" in tl, f"retro link lost: {tl}"
    assert "SENTINEL_SOURCE.md" in tl, f"source citation still dropped when a retro link exists: {tl}"
    assert 'class="evsrc"' in tl, f"the staging-doc source is not inert: {tl}"


def test_timeline_says_so_when_a_rule_has_no_source_at_all():
    """FAIL-OPEN guard on the timeline citation: a rule with neither source nor retro link
    must render an explicit statement, not a silently empty cell."""
    d = _live()
    d["timeline"] = [{"date": "2026-01-01", "id": "R-NOSRC", "name": "n", "rule": "r",
                      "incident": "i", "source": "", "retro_links": []}]
    d["rule_count"] = 1
    tl = _render({"proof": d})["timeline"]["innerHTML"]
    assert "No source recorded." in tl, tl


# ===========================================================================
# MAJOR-7 -- the half the styling fix does not reach: a citation the door SHOWS
# must point at an artefact that EXISTS. Rendering a dead path as an inert tag
# stops it lying about being clickable; it does not stop it lying about being
# there. Audited 2026-08-03: 6 of 15 published repo paths pointed at nothing
# (archived by the staging protocol after the citation was authored).
# The generator-side resolver + its own gate live in
# tests/tools/test_site1_proof_citations_resolve.py; these are the R11
# rendered-pixel assertions of the same fix.
# ===========================================================================
_EVSRC_PATH = re.compile(
    r'<span class="evsrc" title="repo-internal path, not published on the web: ([^"]+)"')
_SECTION_LABEL = re.compile(r"\s*\(§[^)]*\)\s*$")
REPO = HERE.parents[1]


def _rendered_html(out: dict) -> str:
    return "".join((v or {}).get("innerHTML", "") for v in out.values())


def test_every_repo_path_the_door_renders_actually_exists():
    out = _render(_live())
    html = _rendered_html(out)
    paths = _EVSRC_PATH.findall(html)
    # FAIL-OPEN floor: prove citations were rendered before asserting none are broken.
    assert len(paths) >= 5, f"only {len(paths)} inert citations rendered -- checking nothing"
    missing = [p for p in sorted(set(paths))
               if not (REPO / _SECTION_LABEL.sub("", p)).exists()]
    assert missing == [], (
        "the door renders citation(s) pointing at nothing: %s -- a reader told to walk "
        "the figure to its evidence finds an empty path" % missing)


def test_the_rendered_path_existence_check_fires_on_a_phantom_citation():
    """R15: prove the control above can FAIL, by rendering a real phantom."""
    d = _live()
    d["principles"] = [{"title": "S", "number": "N=1", "claim": "c", "why": "w", "basis": "b",
                        "source": "docs/staging/NO_SUCH_ARTEFACT_ANYWHERE.md"}]
    html = _rendered_html(_render({"proof": d}))
    paths = _EVSRC_PATH.findall(html)
    missing = [p for p in set(paths) if not (REPO / _SECTION_LABEL.sub("", p)).exists()]
    assert missing == ["docs/staging/NO_SUCH_ARTEFACT_ANYWHERE.md"], (
        f"the rendered-citation existence control did not fire: {missing}")


def test_a_section_annotated_citation_is_not_read_as_a_filename():
    """"docs/design/X.md (§12)" cites a SECTION of a real file. The label must
    render, and must not make the checker think the file is missing."""
    d = _live()
    d["principles"] = [{"title": "S", "number": "N=1", "claim": "c", "why": "w", "basis": "b",
                        "source": "docs/design/PURPOSE_PITCH_V4.md (§12)"}]
    html = _rendered_html(_render({"proof": d}))
    assert "PURPOSE_PITCH_V4.md (§12)" in html, html
    paths = _EVSRC_PATH.findall(html)
    missing = [p for p in set(paths) if not (REPO / _SECTION_LABEL.sub("", p)).exists()]
    assert missing == [], missing


def test_every_retro_link_the_door_renders_points_at_a_real_retrospective():
    """The other side: a citation rendered as a LIVE link must resolve too. The
    published retro mirror is a 1:1 mirror of docs/retrospectives/, so the repo
    file is the honest local oracle for it."""
    html = _rendered_html(_render(_live()))
    urls = re.findall(r'<a class="evlink" href="(https://[^"]*/retrospectives/[^"]+)"', html)
    assert len(urls) >= 3, f"only {len(urls)} retro links rendered -- checking nothing"
    missing = [u for u in sorted(set(urls))
               if not (REPO / "docs" / "retrospectives" / u.rsplit("/", 1)[-1]).is_file()]
    assert missing == [], f"the door links to retrospective(s) that do not exist: {missing}"


def test_the_retro_link_check_fires_on_a_link_to_a_missing_retrospective():
    """R15 for the control above."""
    d = _live()
    d["timeline"] = [{
        "date": "2026-01-01", "id": "R-X", "name": "n", "rule": "r", "incident": "i",
        "source": "docs/retrospectives/2999-01-01-never-written.md", "retro_links": []}]
    d["rule_count"] = 1
    html = _rendered_html(_render({"proof": d}))
    urls = re.findall(r'<a class="evlink" href="(https://[^"]*/retrospectives/[^"]+)"', html)
    missing = [u for u in set(urls)
               if not (REPO / "docs" / "retrospectives" / u.rsplit("/", 1)[-1]).is_file()]
    assert any("2999-01-01-never-written.md" in u for u in missing), (
        f"the retro-link existence control did not fire: urls={urls} missing={missing}")


# ===========================================================================
# MINOR-9 (proof-door half) -- <noscript> fallback
# ===========================================================================
def test_noscript_fallback_names_the_real_json_endpoints():
    text = _index_text()
    m = re.search(r"<noscript>(.*?)</noscript>", text, re.S)
    assert m, "no <noscript> fallback on /proof/ -- a non-JS crawler indexes 'Loading...'"
    block = m.group(1)
    assert "JavaScript" in block, block
    assert "../data/proof.json" in block, block
    # Every endpoint the fallback advertises must actually exist on disk -- a fallback
    # pointing at a 404 would be the same class of defect as MAJOR-7 itself.
    hrefs = re.findall(r'href="\.\./data/([^"]+)"', block)
    assert hrefs, block
    for name in hrefs:
        assert (DATA.parent / name).is_file(), f"<noscript> advertises ../data/{name}, which does not exist"


# ===========================================================================
# MINOR-10 -- the claim-status vocabulary can say "we chose this number"
# ===========================================================================
def test_claim_legend_carries_chosen_and_benchmark():
    text = _index_text()
    m = re.search(r'<div class="claim-legend".*?</div>\s*</div>', text, re.S)
    assert m, "claim-status legend not found"
    legend = m.group(0)
    for status in ("VERIFIED", "PROVISIONAL", "PLANNED", "RETRACTED", "CHOSEN", "BENCHMARK"):
        assert f">{status}</span>" in legend, f"claim-status {status} missing from the legend: {legend}"


def test_claim_legend_maps_onto_the_constitution_vocabulary():
    text = _index_text()
    for name in ("observed-with-evidence", "external-benchmark", "chosen-not-derived",
                 "not-yet-instrumented", "hypothesis-with-a-designed-test"):
        assert name in text, f"SITE_CONSTITUTION rule 6 status {name!r} is not mapped on the page"
