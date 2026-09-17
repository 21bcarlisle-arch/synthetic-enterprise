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
import urllib.parse
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
    """pages: {url -> (status, bytes)}. Anything not listed 404s, as it would live.

    The double ASSERTS the cache-buster rather than merely tolerating it. Every fetch on
    the real path must carry a `cb` nonce (see `live_pixel_verify.cache_bust`), so any
    future fetch that loses it fails every test in this file at once, not just the one
    someone thought to write. Keying on the exact URL and quietly ignoring the query
    would have let the nonce be removed without a single test noticing -- and reading a
    stale edge copy is precisely the failure this module exists to prevent.
    """
    def fetch(url):
        parsed = urllib.parse.urlsplit(url)
        query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        assert query.pop("cb", None), f"fetch reached the edge with no cache-buster: {url}"
        bare = urllib.parse.urlunsplit(
            parsed._replace(query=urllib.parse.urlencode(sorted(query.items())))
        )
        return pages.get(bare, (404, b""))
    return fetch


def test_two_fetches_of_one_url_never_share_a_cache_key():
    """R15: the nonce has to be per-REQUEST. A constant, or a whole-second timestamp,
    would let a second check inside the same second read the first one's cache entry --
    which is the bug, not a milder version of it."""
    seen = {V.cache_bust("https://poesys.net/proof/") for _ in range(50)}
    assert len(seen) == 50, "cache_bust repeated a URL; the nonce is not per-request"


def test_cache_bust_keeps_the_existing_query_intact():
    busted = V.cache_bust("https://poesys.net/x/?a=1&a=2&b=")
    q = urllib.parse.parse_qsl(urllib.parse.urlsplit(busted).query, keep_blank_values=True)
    assert [kv for kv in q if kv[0] != "cb"] == [("a", "1"), ("a", "2"), ("b", "")]


def door_pages(html=DOOR_HTML, feed=GOOD_FEED, door_status=200, feed_status=200):
    return {
        "https://poesys.net/x/": (door_status, html.encode()),
        "https://poesys.net/data/thing.json": (feed_status, json.dumps(feed).encode()),
    }


# --------------------------------------------------------------------------
# The G4 seam. `reader` is to the browser half what `fetcher` is to G1-G3: without it
# every test in this file would launch chromium against the real poesys.net.
# --------------------------------------------------------------------------
HEALTHY_READING = {
    "exists": True, "visible": True, "display": "block", "visibility": "visible",
    "opacity": "1", "width": 900, "height": 40, "innerLength": 20, "text": "a readable sentence",
}


def make_reader(overrides=None, *, status=200, ok=True, error=None):
    """A double for the chromium probe: healthy for every id asked, except where overridden.

    IT MIRRORS THE REAL PAYLOAD KEY FOR KEY, and `test_the_real_probe_answers_in_the_shape_this_
    double_claims` binds it to the subject. A double more permissive than the mechanism it stands
    in for turns a fail-open into a green suite -- this repo's catalogued R15 mode -- and the
    shape of the reading is exactly where that would happen silently.
    """
    def read(url, ids):
        if not ok:
            return {"ok": False, "url": url, "error": error, "pageErrors": []}
        elements = {}
        for i in ids:
            el = dict(HEALTHY_READING)
            el.update((overrides or {}).get(i, {}))
            elements[i] = el
        return {"ok": True, "url": url, "status": status, "elements": elements, "pageErrors": []}
    return read


# --------------------------------------------------------------------------
# BASELINE: a healthy door passes. Without this the failure tests below prove
# nothing -- a verifier that fails on everything is not a control either.
# --------------------------------------------------------------------------
def test_healthy_door_passes():
    r = V.verify_door("/x/", make_fetcher(door_pages()), make_reader())
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
    r = V.verify_door("/x/", make_fetcher(door_pages(html=html)), make_reader())
    assert not r.ok
    assert any("rendered NOTHING" in f for f in r.failures), r.failures


# --------------------------------------------------------------------------
# FAIL-OPEN killers
# --------------------------------------------------------------------------
def test_empty_feed_payload_fails():
    """An empty feed makes every structural assertion pass vacuously. Must fail."""
    r = V.verify_door("/x/", make_fetcher(door_pages(feed={})), make_reader())
    assert not r.ok
    assert any("empty payload" in f for f in r.failures), r.failures


def test_feed_404_fails_and_the_door_error_path_is_caught():
    r = V.verify_door("/x/", make_fetcher(door_pages(feed_status=404)), make_reader())
    assert not r.ok
    assert any("returned 404" in f for f in r.failures), r.failures
    # The door's own catch branch rendered its error text; that is caught too.
    assert any("could not load" in f.lower() for f in r.failures), r.failures


def test_malformed_feed_json_fails():
    pages = door_pages()
    pages["https://poesys.net/data/thing.json"] = (200, b"{not json")
    r = V.verify_door("/x/", make_fetcher(pages), make_reader())
    assert not r.ok
    assert any("not valid JSON" in f for f in r.failures), r.failures


def test_redirected_door_fails_g1():
    """A canonical door that only resolves via a redirect is advertising a URL that is
    not the real one. Following redirects here would turn that into a silent pass."""
    r = V.verify_door("/x/", make_fetcher(door_pages(door_status=301)), make_reader())
    assert not r.ok
    assert any("does not serve 200" in f for f in r.failures), r.failures


def test_empty_body_fails():
    r = V.verify_door("/x/", make_fetcher(door_pages(html="")), make_reader())
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
        V.verify_door("/x/", dead, make_reader())


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
    r = V.verify_door("/x/", make_fetcher(door_pages(feed={"net": 1, "coeffs": {"b_hdd": 0.4}})),
                      make_reader())
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


# --------------------------------------------------------------------------
# FAIL-OPEN: a region built by DOM construction rather than by innerHTML
# --------------------------------------------------------------------------
def test_a_region_built_by_appendChild_is_not_reported_empty():
    """The harness must see content a door BUILDS, not only content it assigns.

    THE FAIL-OPEN THIS CLOSES (found 2026-09-08 while building the producer-branch pointer
    sweep). `_live_harness.mjs` pushed `appendChild` children onto an array nothing read, and
    `createElement` nodes never entered the output map at all. So a door that rendered by
    `createElement`/`appendChild` -- the ordinary way to build a list -- reported an EMPTY
    region, and every control reading this output passed on the silence: `verify_door` would
    call a blank panel healthy, and both here-relative pointer sweeps derive a sentence's homes
    from these strings, so every payload string on such a door reported ZERO homes and was
    judged nowhere.

    Measured before fixing: no deployed door uses either call, so this changed no live result.
    That is exactly why it needed a control -- a fail-open with no current instance is one
    nothing will notice arriving.

    Fires on: the descent being removed; `createElement` nodes losing their content; a nested
    child (built into a child, then appended) being dropped.
    """
    html = """<div id="panel"></div><script>
      const root = document.getElementById("panel");
      const row = document.createElement("div");
      row.textContent = "BUILT_BY_APPEND";
      const deep = document.createElement("span");
      deep.innerHTML = "<b>NESTED_TWO_DEEP</b>";
      row.appendChild(deep);
      root.appendChild(row);
    </script>"""
    rendered = V.run_harness(html, {})
    panel = rendered.get("panel") or {}
    blob = "{} {}".format(panel.get("innerHTML") or "", panel.get("textContent") or "")
    assert "BUILT_BY_APPEND" in blob, (
        "a region whose content was appended as a child element reports empty, so every "
        "control reading this output judges it as a blank panel: {!r}".format(blob))
    assert "NESTED_TWO_DEEP" in blob, (
        "the descent stops at the first child, so content built two levels deep is invisible "
        "and a door that nests its rows reports a fraction of what it renders: {!r}".format(blob))


def test_an_element_appended_to_itself_does_not_hang_the_harness():
    """The cycle guard, which is the cost of descending at all.

    A door that appends an element into its own subtree is a bug, but an infinite recursion in
    the VERIFIER turns that bug into a hang, and `run_harness` treats a timeout as unavailable
    -- which is a FAILED check for every door in the same run, not just the broken one.
    """
    html = """<div id="panel"></div><script>
      const root = document.getElementById("panel");
      const row = document.createElement("div");
      row.textContent = "CYCLIC_ROW";
      row.appendChild(row);
      root.appendChild(row);
      root.appendChild(root);
    </script>"""
    rendered = V.run_harness(html, {})
    panel = rendered.get("panel") or {}
    assert "CYCLIC_ROW" in "{}".format(panel.get("textContent") or ""), (
        "the cycle guard dropped the honest content along with the cycle")


# ==========================================================================
# G4 -- the READER-SIDE reading of the LIVE host (wired 2026-09-17).
#
# G2 answers "the page computed it"; these answer "a person can read it". Every leg below names
# one of the three breakages measured on 2026-09-17 against a live vm door, each of which left a
# reader looking at nothing and passed all six of that door's legs
# (docs/design/WHAT_THE_VM_DOORS_GRADE.md). They run OFFLINE through the `reader` seam, for the
# same reason the rest of this file runs offline through `fetcher`: a control proved only against
# the real site is a control that passes whatever the real site happens to be doing today.
# ==========================================================================
def test_a_healthy_door_is_actually_READ_by_the_browser():
    """THE POSITIVE LEG, first on purpose (CLAUDE.md: assert the branch CAN be taken).

    Without it, every negative leg below is satisfied by a G4 that reports nothing readable on
    any page -- and `read_elements` would sit at 0 while the door still passed, because "no
    failures" and "something was read" are different statements.
    """
    r = V.verify_door("/x/", make_fetcher(door_pages()), make_reader())
    assert r.ok, r.failures
    assert r.read_elements > 0, "G4 raised no failure and also read nothing -- it has no subject"


def test_the_browser_is_asked_about_exactly_what_the_door_WROTE_INTO():
    """THE DERIVATION, which is the whole design and the thing most likely to rot.

    The subject list is G2's own output plus the whole-page reading -- never a hand-typed list.
    If it ever becomes one, a section added to a door stops being graded on the day it ships and
    nothing says so. This asserts the coupling directly rather than trusting the comment.
    """
    asked = []

    def spy(url, ids):
        asked.append((url, sorted(ids)))
        return make_reader()(url, ids)

    r = V.verify_door("/x/", make_fetcher(door_pages()), spy)
    assert r.ok, r.failures
    assert len(asked) == 1, asked
    url, ids = asked[0]
    assert url.startswith("https://poesys.net/x/"), url
    assert "cb=" in url, f"G4 loaded the live page through a copy the edge may have cached: {url}"
    # `headline` and `detail` are what DOOR_HTML's script writes into; `:body` is the floor.
    assert ids == [V.WHOLE_PAGE, "detail", "headline"], ids


def test_a_renamed_container_passes_the_vm_and_is_caught_HERE():
    """BREAKAGE C, the worst of the three and the one that sets this control's bar.

    The vm's `document.getElementById` MINTS an element for any id asked of it, so G2 reads a
    complete, correct render out of a div that is not on the live page at all. In chromium the
    same bytes raise a TypeError inside a `.then()`, a `.catch()` swallows it, four later
    sections never render, and the page publishes "The record behind this page could not be
    loaded" -- which is false. Nothing in this repository could see that before G4.
    """
    r = V.verify_door("/x/", make_fetcher(door_pages()),
                      make_reader({"headline": {"exists": False}}))
    assert not r.ok
    assert any("#headline is not in the live DOM" in f for f in r.failures), r.failures
    # ...and G2 is still perfectly happy, which is the point being proved.
    assert not any(f.startswith("G2") for f in r.failures), r.failures


def test_a_stylesheet_rule_that_hides_the_rendered_element_is_caught():
    """BREAKAGE A: the render function is untouched and correct, and a CSS rule the vm harness
    never parses means nobody reads its output. Note the reading still carries the WORDS --
    `innerText` falls back to `textContent` for an unrendered element -- so a control asserting
    only on text passes this. `visible` is why it is a separate clause."""
    r = V.verify_door("/x/", make_fetcher(door_pages()),
                      make_reader({"detail": {"visible": False, "display": "none",
                                              "width": 0, "height": 0}}))
    assert not r.ok
    assert any("#detail is on the live page but not visible" in f for f in r.failures), r.failures
    assert any("display=none" in f for f in r.failures), r.failures


def test_an_element_that_is_visible_but_WORDLESS_is_caught():
    """BREAKAGE B: a later inline `<script>` clears the section after it renders. The vm's
    `match(/<script>...)` is neither global nor greedy, so it is blind to every script after the
    first -- and the emptied container can keep its box (padding, a border, a min-height), so
    `visible` alone passes it. This is why emptiness is judged separately from visibility rather
    than assumed to follow from a collapsed box."""
    r = V.verify_door("/x/", make_fetcher(door_pages()),
                      make_reader({"detail": {"text": "   ", "innerLength": 0}}))
    assert not r.ok
    assert any("#detail is visible but the reader meets no words" in f for f in r.failures), \
        r.failures


def test_a_static_door_is_still_read_as_a_WHOLE_PAGE():
    """THE FAIL-OPEN THIS CLOSES. A static door (/privacy/, the Front Door) has no client render,
    so it writes into no element -- and a G4 whose subject is "the written elements" would have
    an EMPTY subject there and pass silently. Those are exactly the doors where a broken build
    ships a nav-and-footer shell. `:body` is always in the list, so the subject is never empty.
    """
    static_html = "<!doctype html><html><body><p>a page with no script at all</p></body></html>"
    asked = []

    def spy(url, ids):
        asked.append(sorted(ids))
        return make_reader({V.WHOLE_PAGE: {"visible": False, "display": "none"}})(url, ids)

    r = V.verify_door("/x/", make_fetcher(door_pages(html=static_html)), spy)
    assert asked == [[V.WHOLE_PAGE]], f"a static door gave G4 no subject at all: {asked}"
    assert not r.ok
    assert any("the page is on the live page but not visible" in f for f in r.failures), r.failures


def test_a_browser_that_could_not_LOOK_is_a_failure_never_a_pass():
    """FAIL-SILENT, the killer this module exists for, on the new half.

    A reading that could not be taken must raise `LiveCheckUnavailable` -- which `main` reports
    as a non-zero exit -- and must never return an empty reading. An empty reading has no
    element to complain about, so it would pass G4 on every door in the run at once, and the
    report would say the live doors were verified by a browser that never opened.
    """
    with pytest.raises(V.LiveCheckUnavailable, match="no claim is made about what a reader sees"):
        V.verify_door("/x/", make_fetcher(door_pages()),
                      make_reader(ok=False, error="net::ERR_CONNECTION_REFUSED"))


def test_a_reading_that_answers_about_OTHER_elements_is_refused():
    """A probe that silently drops an id it was asked about would make that section ungraded and
    report nothing -- the same colour as a pass. The answer must cover the question exactly."""
    def short(url, ids):
        payload = make_reader()(url, ids)
        payload["elements"].pop("detail", None)
        return payload

    with pytest.raises(V.LiveCheckUnavailable, match="does not answer about what it was asked"):
        V.verify_door("/x/", make_fetcher(door_pages()), short)


def test_a_reading_MISSING_THE_KEYS_IT_IS_JUDGED_ON_is_refused():
    """The guard on the double itself. A reader returning `{"exists": true}` and nothing else
    would be judged only on existence, quietly dropping the visibility and emptiness clauses --
    a fake more permissive than its subject, which is this repository's catalogued way of
    turning a fail-open into a green suite. It is refused rather than partially believed."""
    def thin(url, ids):
        return {"ok": True, "url": url, "status": 200, "pageErrors": [],
                "elements": {i: {"exists": True} for i in ids}}

    with pytest.raises(V.LiveCheckUnavailable, match="is missing"):
        V.verify_door("/x/", make_fetcher(door_pages()), thin)


def test_the_browser_being_served_a_non_200_is_caught_even_though_G1_passed():
    """G1 and G4 fetch the live host by different clients, and they can disagree: a UA-gated
    rule, a bot challenge, or an edge that answers a browser's `Accept` header differently gives
    the reader a page G1 never saw. Whichever one is right, a disagreement is a finding."""
    r = V.verify_door("/x/", make_fetcher(door_pages()), make_reader(status=403))
    assert not r.ok
    assert any("G4 the browser was served 403" in f for f in r.failures), r.failures


def test_the_real_probe_answers_in_the_SHAPE_these_doubles_claim():
    """THE CONTRACT LEG, binding every double above to the mechanism it stands in for.

    Every G4 test here is offline, so all of them together are evidence about `_judge_reading`
    and none about whether the real chromium probe reports what it is being judged on. A double
    that drifts from its subject makes this whole section decorative -- so this runs the REAL
    probe against a REAL page and asserts the keys, and that a `display:none` element genuinely
    comes back with `visible: false` rather than merely being assumed to.
    """
    reading = pytest.importorskip("test_the_browser_reading")
    why = reading.browser_available()
    if why:
        pytest.skip(why)
    page = ("<!doctype html><html><head><style>#gone{display:none}</style></head><body>"
            "<div id='shown'>readable words</div><div id='gone'>hidden words</div></body></html>")
    with reading._serve(page) as url:
        payload = reading.read_in_browser(url, "shown", "gone")
    assert set(payload["elements"]) == {"shown", "gone"}
    for eid, el in payload["elements"].items():
        missing = [k for k in V._READING_KEYS if k not in el]
        assert not missing, f"the real probe omits {missing} for #{eid}, which G4 judges on"
    assert payload["elements"]["shown"]["visible"] is True
    assert payload["elements"]["gone"]["visible"] is False, (
        "the real probe reports a display:none element as visible, so every G4 visibility leg "
        "above is proving something the mechanism does not do"
    )
    assert set(HEALTHY_READING) <= set(payload["elements"]["shown"]), (
        "the double claims keys the real probe does not send, so it is not a stand-in for it"
    )


def test_the_WHOLE_PAGE_reading_is_a_real_reading_and_not_a_carve_out():
    """`:body` is what carries a STATIC door, and it needed an exemption to work at all --
    `offsetParent` is specified to return null for `document.body`, the same answer it gives for
    `display:none`, so without a carve-out the whole-page reading would call every healthy page
    invisible. An exemption written to stop a control firing on everything is one keystroke from
    an exemption that stops it firing at all, and this repository has catalogued that exact
    move. So: the carve-out is proved to be NARROW, in a real browser, on a real page -- a
    healthy body reads visible WITH ITS WORDS, and a hidden body still reads invisible.
    """
    reading = pytest.importorskip("test_the_browser_reading")
    why = reading.browser_available()
    if why:
        pytest.skip(why)
    healthy = "<!doctype html><html><body><p>words a reader meets</p></body></html>"
    with reading._serve(healthy) as url:
        el = reading.read_in_browser(url, V.WHOLE_PAGE)["elements"][V.WHOLE_PAGE]
    assert el["exists"] and el["visible"], f"a healthy page reads as unreadable: {el}"
    assert "words a reader meets" in el["text"], el["text"]

    hidden = ("<!doctype html><html><head><style>body{display:none}</style></head>"
              "<body><p>nobody meets this</p></body></html>")
    with reading._serve(hidden) as url:
        el = reading.read_in_browser(url, V.WHOLE_PAGE)["elements"][V.WHOLE_PAGE]
    assert not el["visible"], (
        "a page whose whole body is display:none reads as visible, so the `:body` carve-out is "
        f"a blanket exemption and every static door is ungraded: {el}"
    )
