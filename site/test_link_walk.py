"""R15 mechanism self-test for the R11 internal link-walk (link_walk.classify).

This is a MECHANISM test, NOT a site-cleanliness gate. It proves the walker can
distinguish canonical / dead / redirected links using synthetic fixture trees --
so it passes green regardless of the live site's current 22 non-canonical links.

WHY NOT ASSERT THE LIVE SITE IS CLEAN (yet): the SITE_V5 IA is mid-cutover
(/method et al. are both live nav doors AND redirect sources). Asserting zero
findings against the real site would re-wedge the just-cleared publish gate. The
live assertion flips on only once the WORDS->DIAGRAM->EVIDENCE canonical door set
is decided (director-pixel-gated). See link_walk.py module docstring + the parked
campaign doc for the sequencing.

R15 (a control must be able to FAIL): the two positive tests below mutate in a
dead link and a redirect-source link respectively and assert classify() reports
each -- proving the control fires on both its named defects, not vacuously. The
negative test proves a wholly-canonical tree yields zero findings (independence
-- classify() is not always-positive).
"""
from pathlib import Path

from link_walk import classify


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
