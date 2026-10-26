"""No published page scrolls sideways on a 390 px phone.

THE DEFECT, measured 2026-10-26 in headless chromium at 390x844 over the 77 published pages: 25
scrolled sideways. The director's steer of that day named three (Capabilities,
knowledge/payments-and-direct-debit/, knowledge/switching-mechanics/); the sweep found 22 more.
Two causes, neither a table: the Knowledge pages' two-column `.wrap` is a grid, and a grid child
defaults to `min-width: auto`, so one long word in a heading widened the column past the screen;
and an unbroken file path in a Capabilities provenance line pushed its line out. Both are fixed
once, in site/brand/brand.css.

WHY THE SOURCE-LEVEL CHECK DID NOT CATCH IT. `site/test_expert_doors_mobile.py` requires every
`<table>` to open inside an overflow-x wrapper, and every page passed it. Sideways scroll is a
property of the LAID-OUT page, not of its markup, so this reads the laid-out page: the published
(index) bytes, served, in a browser at 390 px, every page found on disk, one browser launch.

THE SUBJECT IS EVERY PUBLISHED .html, not every index.html: the Knowledge census page
(knowledge/how-these-pages-are-checked.html) is a flat file and a reader reaches it all the same.

It runs after every publish as well as in the commit path: `background/post_publish_readers.py`
names it in `PAGE_READERS`, because a publish rewrites pages and feeds whose rendered width no
artefact path in a test's text can predict.
"""
from __future__ import annotations

import shutil
import socketserver
import sys
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from test_the_browser_reading import (  # noqa: E402  (must follow the sys.path insertion)
    _QuietHandler,
    browser_available,
    published_site,
    read_pages_in_browser,
)

PHONE = {"width": 390, "height": 844}

#: Directories under site/ that hold feeds, assets and machine state, not pages a reader opens.
#: The same set `test_every_served_page_takes_the_canonical_nav.py` skips.
_NOT_PAGES = {"__pycache__", "assets", "brand", "data", "state", "snapshots", "shadow",
              "node_modules", "harness_out"}


def published_pages(docroot: Path) -> list[Path]:
    return sorted(p for p in docroot.rglob("*.html")
                  if not (set(p.relative_to(docroot).parts[:-1]) & _NOT_PAGES))


def sideways(readings: dict[str, dict]) -> dict[str, str]:
    """{url: why} for every reading that overflows its viewport's width, or carries no reading."""
    out = {}
    for url, payload in readings.items():
        h = payload.get("hscroll")
        if not isinstance(h, dict) or "overflowing" not in h:
            out[url] = "no sideways-scroll reading came back, so nothing is claimed for this page"
        elif h["overflowing"]:
            out[url] = "{} px wide in a {} px viewport; sticking out: {}".format(
                h.get("scrollWidth"), h.get("clientWidth"), ", ".join(h.get("culprits") or []))
    return out


def _skip_without_a_browser():
    if shutil.which("node") is None:
        pytest.skip("node is not available to run the browser probe")
    why = browser_available()
    if why:
        pytest.skip(why)


@pytest.fixture(scope="module")
def phone_readings():
    _skip_without_a_browser()
    with published_site() as (base, docroot):
        pages = published_pages(docroot)
        assert len(pages) >= 20, (
            f"only {len(pages)} published page(s) found under {docroot}: treated as a broken scan, "
            "since a short population makes the sweep below pass vacuously")
        jobs = [(f"{base}/{p.relative_to(docroot).as_posix()}", [":body"]) for p in pages]
        yield read_pages_in_browser(jobs, viewport=PHONE)


def test_no_published_page_scrolls_sideways_at_390px(phone_readings):
    bad = sideways(phone_readings)
    assert not bad, "{} of {} published page(s) scroll sideways on a 390 px phone:\n{}".format(
        len(bad), len(phone_readings), "\n".join(f"  {u}: {w}" for u, w in sorted(bad.items())))


@contextmanager
def _scratch(pages: dict[str, str]):
    with tempfile.TemporaryDirectory(prefix="hscroll-scratch-") as td:
        for name, html in pages.items():
            (Path(td) / name).write_text(html)

        class _S(socketserver.TCPServer):
            allow_reuse_address = True

            def finish_request(self, request, client_address):
                self.RequestHandlerClass(request, client_address, self, directory=td)

        with _S(("127.0.0.1", 0), _QuietHandler) as httpd:
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                yield f"http://127.0.0.1:{httpd.socket.getsockname()[1]}"
            finally:
                httpd.shutdown()
                t.join(timeout=10)


_HEAD = ('<!doctype html><html><head><meta name="viewport" content="width=device-width, '
         'initial-scale=1"><link rel="stylesheet" href="brand.css"></head><body>{}</body></html>')
_GRID = '<div class="wrap" style="display:grid;grid-template-columns:1fr"><main>{}</main></div>'
_LONG = "docs/observability/" + "a_very_long_unbroken_file_name_" * 6 + ".json"


def test_MUTATION_the_sweep_can_fail_and_the_sheet_is_what_passes_it():
    """Both legs of one partition, on the shapes that were live on 26 Oct: a page WITHOUT the
    brand sheet's rule overflows and is named, and the same page WITH it does not. A sweep that
    could not see the first, or a sheet that did not fix the second, fails here."""
    _skip_without_a_browser()
    sheet = (_HERE / "brand" / "brand.css").read_text(encoding="utf-8")
    body = _GRID.format(f"<h1>{_LONG}</h1><p>text</p>")
    with _scratch({"brand.css": sheet, "with.html": _HEAD.format(body),
                   "without.html": _HEAD.replace("brand.css", "none.css").format(body)}) as base:
        got = read_pages_in_browser([(f"{base}/with.html", [":body"]),
                                     (f"{base}/without.html", [":body"])], viewport=PHONE)
    bad = sideways(got)
    assert f"{base}/without.html" in bad and "sticking out" in bad[f"{base}/without.html"], got
    assert f"{base}/with.html" not in bad, bad


def test_MUTATION_a_reading_with_no_hscroll_is_not_a_pass():
    assert sideways({"u": {"ok": True, "elements": {}}}) == {
        "u": "no sideways-scroll reading came back, so nothing is claimed for this page"}
