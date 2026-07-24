"""R15 mechanism self-test for the R11 internal link-walk (link_walk.classify)
PLUS the live-site cleanliness gate.

Two roles in one file:
  1. MECHANISM self-tests (R15) -- prove the walker can distinguish canonical /
     dead / redirected links using synthetic fixture trees, and that the control
     can FAIL on each of its named defects (not vacuously green).
  2. LIVE GATE -- assert the real site has zero dead / redirected internal links.

WHY THE LIVE GATE IS ON NOW (2026-07-24, DIRECTOR_RULING_CANONICAL_DOOR_A):
Decision A (COMMIT THE FOLD) resolved the door set -- /method, /simplified,
/project, /tours fold into /proof; the temporary /method live-door is retired.
With the canonical door set decided, the live assertion flips on and becomes the
publish gate the ruling names ("the R11 link-walk must pass green post-fold ...
use it as the gate"). Prior to the ruling this was deliberately a mechanism-only
test because the IA was mid-cutover (asserting clean then would have re-wedged
the publish gate); that condition is gone.

R15 (a control must be able to FAIL): the two positive fixture tests below mutate
in a dead link and a redirect-source link respectively and assert classify()
reports each -- proving the control fires on both its named defects. The negative
fixture test proves a wholly-canonical tree yields zero findings (independence --
classify() is not always-positive). The live gate rests on that proven mechanism.
"""
from pathlib import Path

from link_walk import classify

# The live site root is this test file's own directory (site/).
_SITE_ROOT = Path(__file__).resolve().parent


def test_live_site_has_no_noncanonical_links():
    """LIVE GATE (R11, DIRECTOR_RULING_CANONICAL_DOOR_A 2026-07-24): the deployed
    site must have zero dead and zero redirected internal links. Every internal
    link points at a canonical door, never at a legacy /redirects source. This is
    the publish gate for the SITE_V5 fold -- if it reds, an internal link points
    at a killed door (fix the link, do not revive the door)."""
    findings = classify(_SITE_ROOT)
    assert findings["DEAD"] == [], (
        "dead internal links (target missing on disk): "
        + "; ".join(f"{src} -> {url}" for src, _, url in findings["DEAD"])
    )
    assert findings["REDIRECTED"] == [], (
        "internal links pointing at a legacy /redirects source (fix the link to "
        "the canonical door, per DIRECTOR_RULING_CANONICAL_DOOR_A): "
        + "; ".join(f"{src} -> {url}" for src, _, url in findings["REDIRECTED"])
    )


def _write(root: Path, rel: str, html: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")


def _base_tree(tmp: Path) -> Path:
    """A minimal canonical site: a home + two real doors, no bad links."""
    site = tmp / "site"
    _write(site, "index.html", '<a href="./proof/">Proof</a><a href="./world/">World</a>')
    _write(site, "proof/index.html", '<a href="../">Home</a>')
    _write(site, "world/index.html", '<a href="../">Home</a>')
    _write(site, "_redirects", "/method /proof/ 301\n/method/* /proof/ 301\n")
    return site


def test_clean_tree_has_no_findings():
    """Independence: a wholly-canonical tree produces zero findings (the control
    is not always-positive)."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        site = _base_tree(Path(d))
        findings = classify(site)
        assert findings["DEAD"] == [], findings["DEAD"]
        assert findings["REDIRECTED"] == [], findings["REDIRECTED"]


def test_dead_link_is_flagged():
    """R15 direction 1: a link to a non-existent page is reported DEAD."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        site = _base_tree(Path(d))
        _write(site, "proof/index.html", '<a href="../ghost/">Ghost</a>')
        findings = classify(site)
        dead_urls = [u for _, _, u in findings["DEAD"]]
        assert "/ghost" in dead_urls or "/ghost/" in dead_urls, findings


def test_redirect_source_link_is_flagged():
    """R15 direction 2: a link pointing at a _redirects SOURCE (a legacy URL) is
    reported REDIRECTED -- the exact 'backward link' class the director hit."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        site = _base_tree(Path(d))
        # /method is a redirect source in the fixture _redirects; make the page
        # exist on disk (so it is NOT dead) but linked-to (so it IS backward).
        _write(site, "method/index.html", "<p>legacy</p>")
        _write(site, "world/index.html", '<a href="../method/">Method</a>')
        findings = classify(site)
        redir_urls = [u for _, _, u in findings["REDIRECTED"]]
        assert any(u.rstrip("/") == "/method" for u in redir_urls), findings
        assert findings["DEAD"] == [], "existing legacy page must not read as DEAD"
