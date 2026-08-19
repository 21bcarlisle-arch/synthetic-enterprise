"""R15 proof that site/live_pixel_verify.py can FAIL -- on each defect it names.

SITE1_expert_doors residual (b) is "R11 live-pixel verify". The verifier itself is a
control, so R15 binds: no control counts as evidence unless a mutation test proves it
fires on its own named defect. The three killer patterns are tested explicitly.

  TAUTOLOGY   -- the verifier must judge the RENDERED output, not the source markup.
                 test_source_string_does_not_satisfy_the_check.
  FAIL-OPEN   -- it must not pass on missing / empty / malformed input.
                 test_* for empty payload, 404 feed, redirected door, blank body,
                 empty sitemap.
  FAIL-SILENT -- an unavailable check is a FAILED check, never a skip.
                 test_network_unavailable_is_a_failure_not_a_skip.

Every test here is OFFLINE. The verifier takes an injectable `fetcher`, which is the
seam that makes it testable at all -- and the same seam lets these tests serve a
synthetic door whose defect is known by construction, rather than waiting for the live
site to break.

ANTI-PIN: nothing asserts a figure, a count, a stamp or a door list from the real site.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))

import live_pixel_verify as V  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node required")


# --------------------------------------------------------------------------
# A synthetic door. It boots exactly the way the real doors do: fetch a JSON
# feed, then write rendered content into elements by id.
# --------------------------------------------------------------------------
DOOR_HTML = """<!doctype html><html><body>
<div id="headline">Loading...</div>
<div id="detail">Loading...</div>
<script>
fetch("../data/thing.json?t="+Date.now()).then(function(r){return r.json();}).then(function(d){
  document.getElementById("headline").innerHTML = "Net: " + d.net;
  document.getElementById("detail").innerHTML = "coeffs: " + String(d.coeffs);
}).catch(function(e){
  document.getElementById("headline").innerHTML = "Could not load thing.json";
});
</script></body></html>"""

GOOD_FEED = {"net": 1234, "coeffs": "b_hdd=0.4"}


def make_fetcher(pages):
    """pages: {url -> (status, bytes)}. Anything not listed 404s, as it would live."""
    def fetch(url):
        return pages.get(url, (404, b""))
    return fetch


def door_pages(html=DOOR_HTML, feed=GOOD_FEED, door_status=200, feed_status=200):
    return {
        "https://poesys.net/x/": (door_status, html.encode()),
        "https://poesys.net/data/thing.json": (feed_status, json.dumps(feed).encode()),
    }


# --------------------------------------------------------------------------
# BASELINE: a healthy door passes. Without this the failure tests below prove
# nothing -- a verifier that fails on everything is not a control either.
# --------------------------------------------------------------------------
def test_healthy_door_passes():
    r = V.verify_door("/x/", make_fetcher(door_pages()))
    assert r.ok, r.failures
    assert r.rendered_elements > 0
    assert "Net: 1234" in r.sample.get("headline", "")


# --------------------------------------------------------------------------
# TAUTOLOGY killer
# --------------------------------------------------------------------------
def test_source_string_does_not_satisfy_the_check():
    """The door's markup CONTAINS the right words, but its script never renders them.

    A source-string test passes here. The verifier must not: nothing was rendered.
    This is the exact difference between R11 and a grep.
    """
    html = """<!doctype html><html><body>
    <div id="headline">Net: 1234</div>
    <script>var unused = 1;</script></body></html>"""
    r = V.verify_door("/x/", make_fetcher(door_pages(html=html)))
    assert not r.ok
    assert any("rendered NOTHING" in f for f in r.failures), r.failures


# --------------------------------------------------------------------------
# FAIL-OPEN killers
# --------------------------------------------------------------------------
def test_empty_feed_payload_fails():
    """An empty feed makes every structural assertion pass vacuously. Must fail."""
    r = V.verify_door("/x/", make_fetcher(door_pages(feed={})))
    assert not r.ok
    assert any("empty payload" in f for f in r.failures), r.failures


def test_feed_404_fails_and_the_door_error_path_is_caught():
    r = V.verify_door("/x/", make_fetcher(door_pages(feed_status=404)))
    assert not r.ok
    assert any("returned 404" in f for f in r.failures), r.failures
    # The door's own catch branch rendered its error text; that is caught too.
    assert any("could not load" in f.lower() for f in r.failures), r.failures


def test_malformed_feed_json_fails():
    pages = door_pages()
    pages["https://poesys.net/data/thing.json"] = (200, b"{not json")
    r = V.verify_door("/x/", make_fetcher(pages))
    assert not r.ok
    assert any("not valid JSON" in f for f in r.failures), r.failures


def test_redirected_door_fails_g1():
    """A canonical door that only resolves via a redirect is advertising a URL that is
    not the real one. Following redirects here would turn that into a silent pass."""
    r = V.verify_door("/x/", make_fetcher(door_pages(door_status=301)))
    assert not r.ok
    assert any("does not serve 200" in f for f in r.failures), r.failures


def test_empty_body_fails():
    r = V.verify_door("/x/", make_fetcher(door_pages(html="")))
    assert not r.ok
    assert any("empty body" in f for f in r.failures), r.failures


def test_empty_sitemap_does_not_yield_an_empty_pass(tmp_path):
    """Zero doors verified must never report success -- the classic fail-open shape."""
    empty = tmp_path / "sitemap.xml"
    empty.write_text('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"/>')
    with pytest.raises(V.LiveCheckUnavailable):
        V.canonical_doors(empty)


def test_missing_sitemap_is_unavailable_not_empty(tmp_path):
    with pytest.raises(V.LiveCheckUnavailable):
        V.canonical_doors(tmp_path / "nope.xml")


# --------------------------------------------------------------------------
# COVERAGE fail-open: a deployed door the default run never looks at
# --------------------------------------------------------------------------
def test_default_coverage_includes_the_internal_doors():
    """canonical_doors() reads the SITEMAP, and the sitemap deliberately excludes the
    off-nav surfaces -- so deriving coverage from it alone silently skipped every
    internal door while still reporting "N/N doors verified". Found 2026-08-03."""
    covered = V.all_doors()
    for internal in V.INTERNAL_DOORS:
        assert internal in covered, f"{internal} deployed but outside default coverage"
    # additive, never a replacement: the advertised set must survive intact
    for advertised in V.canonical_doors():
        assert advertised in covered


def test_every_deployed_door_directory_is_covered_by_a_default_run():
    """Independent oracle: the door set is derived from the REPO (directories that
    ship an index.html and are not 301'd away), not from the sitemap the verifier
    already reads -- otherwise the control would be checking a list against itself,
    which is the TAUTOLOGY pattern. A new door cannot ship unverified."""
    redirected = set()
    for line in (V.SITE / "_redirects").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("/"):
            redirected.add("/" + parts[0].strip("/").rstrip("*").strip("/") + "/")
    on_disk = {"/" + p.parent.name + "/" for p in V.SITE.glob("*/index.html")}
    deployed = {d for d in on_disk if d not in redirected}
    assert deployed, "no deployed doors discovered -- control would be vacuous"
    # An UNDER_CONSTRUCTION door is deployed and deliberately absent from the sitemap, so it
    # would read as uncovered here. It is not exempt -- it is verified as its own kind: the
    # register already asserts each one carries the reader-facing "being built" marker
    # (`register_violations`), which is a stronger check than a pixel run and the one that
    # matters for a hole. Listing them here as exempt-from-THIS-run keeps the honest property:
    # a door nobody verifies at all still fails.
    import sys
    sys.path.insert(0, str(V.SITE))
    import ia_register as _reg
    early = set(_reg.UNDER_CONSTRUCTION_DOORS)
    uncovered = sorted(deployed - set(V.all_doors()) - early)
    assert uncovered == [], (
        f"door(s) deployed but never live-verified by a default run: {uncovered}. "
        "Add to site/sitemap.xml (public), INTERNAL_DOORS (off-nav), or "
        "UNDER_CONSTRUCTION_DOORS (an early door whose page says it is being built)."
    )


def test_the_coverage_control_fires_when_an_internal_door_is_dropped(monkeypatch):
    """R15: the coverage check must be able to FAIL."""
    monkeypatch.setattr(V, "INTERNAL_DOORS", ())
    covered = set(V.all_doors())
    assert "/director/" not in covered, "mutation did not take effect"


# --------------------------------------------------------------------------
# FAIL-SILENT killer -- the property this module exists for
# --------------------------------------------------------------------------
def test_network_unavailable_is_a_failure_not_a_skip():
    def dead(url):
        raise V.LiveCheckUnavailable(f"{url}: network is down")

    with pytest.raises(V.LiveCheckUnavailable):
        V.verify_door("/x/", dead)


def test_main_reports_unavailable_as_nonzero_exit(monkeypatch):
    """The CLI must exit non-zero when it could not check. If an offline run exited 0,
    every scheduled invocation would report green while verifying nothing."""
    monkeypatch.setattr(V, "verify_all",
                        lambda *a, **k: (_ for _ in ()).throw(V.LiveCheckUnavailable("offline")))
    assert V.main(["--json"]) == 1


# --------------------------------------------------------------------------
# The defect this verifier actually found on the LIVE proof door
# --------------------------------------------------------------------------
def test_object_object_is_caught_as_a_rendered_defect():
    """[object Object] is what a nested map renders as when concatenated into a string.

    This is not hypothetical: on 2026-08-03 the live /proof/ coupled-gap panel served
    'belief_coeffs: [object Object]', found by this verifier and fixed in
    site/proof/index.html (fmtComponent). The control that found it must stay able to.
    """
    r = V.verify_door("/x/", make_fetcher(door_pages(feed={"net": 1, "coeffs": {"b_hdd": 0.4}})))
    assert not r.ok
    assert any("[object object]" in f.lower() for f in r.failures), r.failures


def test_prose_discussing_nan_is_not_flagged():
    """The anti-false-positive half, and it has teeth.

    This site publishes its own defects, so its honest-hold notes discuss NaN fail-opens
    in plain English. An earlier draft of this control substring-matched 'nan' and
    flagged 11 such notes on the live proof door -- it would have failed the door on its
    most honest content, and 'gover(nan)ce' too. A control that fires on the description
    of a defect rather than the defect is a false positive, and a false positive on a
    publish path is how this project has stalled before.
    """
    assert V.rendered_defects("a single NaN mark walks through the live path") == []
    assert V.rendered_defects("company/governance/decision_rights.py") == []
    # ...but a NaN in a VALUE position is still caught.
    assert V.rendered_defects('<div class="kpi-v">NaN</div>')
    assert V.rendered_defects("NaN")
