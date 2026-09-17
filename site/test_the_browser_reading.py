"""What a READER WITH A BROWSER meets on a published page -- the half the vm doors cannot see.

WHY THIS MODULE EXISTS. CLAUDE.md makes "done means the rendered value changed" load-bearing and
names `site/test_*_door.py` as its enforcement. Every one of those doors grades a string that the
page's own JavaScript wrote into an element inside node's `vm` -- `site/harness/_render_harness.mjs`
and the eight harnesses like it. That is strong evidence about the FEED and the WIRING. It is no
evidence at all about RENDERING, and on 2026-09-17 that was measured rather than argued: three
constructed breakages, each leaving a reader looking at nothing, all passed the live deployment
door with every one of its six legs green. `docs/design/WHAT_THE_VM_DOORS_GRADE.md` has the table
and the method; the worst of the three is worth stating here because it sets this module's bar --

    renaming `<div id="deployment">` to `<div id="deployment-panel">`, while the script still
    writes to `deployment`, passed all six legs. The vm's `document.getElementById` MINTS an
    element for any id asked of it, so the door read a complete, correct render out of an element
    that was not on the page. In chromium the same bytes killed four sections, published the
    sentence "The record behind this page could not be loaded, so no figures are shown" (false --
    it loaded fine), and raised no error anywhere, because the TypeError landed inside a `.then()`
    that a `.catch()` swallowed.

SO THE TWO HALVES ARE DIFFERENT QUESTIONS AND THIS PROJECT HAS BEEN ASKING ONE OF THEM. "The
rendered value" has two experiences behind it -- *the page computed it* and *a person can read it*
-- and CLAUDE.md names that exact shape ("Before measuring a thing, say what it is") as this
project's most expensive recurring failure. This module is the second experience, and ONLY that:
it does not re-grade the feed, which the vm doors already do better and faster.

WHY THE MECHANISM AND ITS PROOFS SHARE A FILE. Identical reasoning to
`site/test_the_published_bytes_reader.py`, which faced this first: `tools/capability_index.py`
classifies a module as evidence BY NAME (`test_*` or `conftest.py`), and the orphan ratchet walks
only the production graph. A `site/_browser_reading.py` whose only callers are door tests is
unreachable by construction -- it could never acquire a caller the ratchet can see, and the only
ways to clear that refusal are to invent a production caller or to `--freeze` it as "deliberately
dormant". It is not dormant; it runs on every `pytest site/`. Living beside its proofs under the
name the index already reserves for evidence is the classification being CORRECT, not a way round
a gate.

WHY IT SERVES PUBLISHED BYTES OVER HTTP rather than opening the working-tree file. Two reasons and
both were paid for. A probe pointed at `site/harness/index.html` on disk cannot tell "the reader
can see this" from "someone in this tree has fixed it and not landed it" -- the defect
`test_the_published_bytes_reader.py` was built for, and the reason it reads the INDEX copy. And a
`file://` page cannot `fetch()` its own `../data/*.json` under chromium's origin rules, so the one
thing being tested would never arrive. The index copy of `site/` is extracted to a temp directory
and served on an ephemeral port; the browser sees exactly the bytes a commit publishes.
"""
from __future__ import annotations

import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
PROBE = SITE / "_browser_probe.mjs"

sys.path.insert(0, str(SITE))

# `playwright_base` WAS WRITTEN HERE and now lives in `live_pixel_verify`, which needs it too for
# its own browser leg against the LIVE host. One definition, imported, rather than a copy in each:
# a resolver duplicated across two files is a resolver that will answer differently in one of them,
# and this one already went wrong once -- it reported "playwright is not installed" from every
# linked worktree, which is where every executor turn runs. The import direction is forced: that
# module is a TOOL and must not depend on pytest, so it cannot import from here.
from live_pixel_verify import playwright_base  # noqa: E402


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # a server logging every asset drowns the failure message
        pass


@contextmanager
def published_site(root: Path | None = None):
    """Extract and serve the PUBLISHED (index) copy of `site/`; yield `(base_url, docroot)`.

    THE DOCROOT IS YIELDED BECAUSE A READER-SIDE CONTROL USUALLY NEEDS BOTH HALVES OF ONE SUBJECT.
    `site/test_every_door_element_a_reader_meets.py` derives which element ids to ask the browser
    about by running the door's script under node's `vm` -- and if that vm run reads the WORKING
    TREE while the browser reads the published bytes, the two halves are describing different
    pages, and the control's whole claim ("the reader meets what the door rendered") is about a
    page that exists nowhere. One extract, both readings.

    `published_site_server` below is this function with the docroot dropped; it is what the
    per-door legs use, and it is kept because a caller that only wants a URL should not have to
    unpack a pair it will not use.

    FAIL-CLOSED, AND IN THOSE WORDS. git being unable to answer is not "assume the tree is fine".
    An unmerged index, a repo git cannot read, a timeout -- every one of them means the caller has
    NO SUBJECT, and the one fallback that would restore the whole defect is falling back to the
    working tree. So these fail the test with the git error in the message.

    IT READS THE INDEX WITHOUT LOCKING IT, and that is not a detail. The first version resolved the
    subject with `git write-tree`, which takes `.git/index.lock` -- and the very first run in the
    shared tree failed because another lane held it. Several sessions and daemons write this index
    continuously, so a door keyed to acquiring that lock is red on other lanes' TIMING rather than
    on its own subject, and would wedge every commit it ran under. `ls-files` + `cat-file --batch`
    answer the identical question (the index copy, exactly what `git show :<path>` returns) while
    only ever reading `.git/index`.
    """
    base = PROJECT if root is None else root
    try:
        listing = subprocess.run(
            ["git", "-C", str(base), "ls-files", "-s", "-z", "--", "site"],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover - environment
        pytest.fail(f"git could not be run to resolve the published site bytes: {exc}")
    if listing.returncode != 0:
        pytest.fail(
            "the published site bytes cannot be resolved, so no claim is made about what a reader "
            f"sees: git ls-files failed ({listing.stderr.strip()[:300]})"
        )

    entries = []
    for record in listing.stdout.split("\0"):
        if not record.strip():
            continue
        meta, _, rel = record.partition("\t")
        _mode, sha, stage = meta.split()
        if stage != "0":
            pytest.fail(
                "the index is unmerged at {!r} (stage {}), so there is no single published copy of "
                "the site to show a reader".format(rel, stage)
            )
        entries.append((sha, rel))
    if not entries:
        pytest.fail(f"no site/ paths are tracked in the index of {base}, so there is no page to serve")

    with tempfile.TemporaryDirectory(prefix="published-site-") as td:
        out = Path(td)
        batch = subprocess.Popen(
            ["git", "-C", str(base), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        )
        try:
            for sha, rel in entries:
                batch.stdin.write((sha + "\n").encode())
                batch.stdin.flush()
                header = batch.stdout.readline().decode().strip()
                parts = header.split()
                if len(parts) != 3 or parts[1] != "blob":
                    pytest.fail(f"git could not read the published bytes of {rel}: {header!r}")
                size = int(parts[2])
                blob = batch.stdout.read(size)
                batch.stdout.read(1)  # the trailing newline cat-file writes after every blob
                dest = out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(blob)
        finally:
            batch.stdin.close()
            batch.wait(timeout=60)

        docroot = out / "site"
        if not (docroot / "index.html").is_file():
            pytest.fail(f"the published site extract has no index.html at {docroot}")

        class _Server(socketserver.TCPServer):
            allow_reuse_address = True

            def finish_request(self, request, client_address):
                self.RequestHandlerClass(request, client_address, self, directory=str(docroot))

        with _Server(("127.0.0.1", 0), _QuietHandler) as httpd:
            port = httpd.socket.getsockname()[1]
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                yield f"http://127.0.0.1:{port}", docroot
            finally:
                httpd.shutdown()
                t.join(timeout=10)


@contextmanager
def published_site_server(root: Path | None = None):
    """`published_site` with the docroot dropped -- the published base URL, nothing else."""
    with published_site(root=root) as (base_url, _docroot):
        yield base_url


def browser_available() -> str | None:
    """None if a browser reading can be taken, else the REASON it cannot, in words for a message.

    THE SKIP AND THE FAILURE ARE DIFFERENT CASES and conflating them is how this control would go
    quiet. Playwright not installed is an environment this repo already tolerates (`node` absent
    skips the vm doors the same way). Playwright installed and the BROWSER refusing to launch is a
    broken door on a machine that is supposed to have one -- that is a failure, and it is raised
    by the probe rather than swallowed here.

    THE REASON MUST BE TRUE OF THE MACHINE, and for one day it was not. This returned "playwright
    is not installed" from every linked worktree while the main checkout had it installed the whole
    time, because the check resolved against `PROJECT` -- the worktree. A skip is a stated hole and
    a wrong statement of the hole is worse than the hole: the remedy it implies (`npx playwright
    install`) was not the remedy, and nothing would ever have corrected it, because a skip is the
    same colour as a pass in a run summary. Measured 2026-09-17; see
    `docs/design/WHAT_THE_VM_DOORS_GRADE.md`.
    """
    if shutil.which("node") is None:
        return "node is not available to run the browser probe"
    if not PROBE.is_file():
        return f"the browser probe is missing at {PROBE}"
    base = playwright_base()
    check = subprocess.run(
        ["node", "-e", "require.resolve('playwright')"],
        cwd=str(base), capture_output=True, text=True, timeout=120,
    )
    if check.returncode != 0:
        return (
            f"playwright is not installed under {base} (node_modules/ is gitignored, so it lives "
            "only in the main checkout; `npx playwright install` there), so no browser reading "
            "can be taken"
        )
    return None


def read_in_browser(url: str, *element_ids: str) -> dict:
    """Load `url` in chromium and report what the reader meets in each element.

    `node_modules/` is gitignored and exists only in the main checkout, and node's ESM resolution
    walks up from the IMPORTING FILE -- so a probe in a linked worktree reports "Cannot find
    package 'playwright'" and reads as a machine without a browser. That is the artefact shape this
    repo has been caught by three times now.

    `cwd` ALONE DOES NOT FIX IT and used to be the whole mitigation here. `cwd` is what CJS
    resolves against; ESM is not, so the `import` inside the probe failed identically with `cwd`
    set to the main checkout. Measured both ways 2026-09-17. The probe is therefore handed the base
    directory explicitly and resolves against it (see `loadPlaywright` in `_browser_probe.mjs`);
    `cwd` is still set for the benefit of anything CJS underneath it.
    """
    env = {**os.environ, "POESYS_PLAYWRIGHT_BASE": str(playwright_base())}
    proc = subprocess.run(
        ["node", str(PROBE), url, *element_ids],
        cwd=str(playwright_base()), capture_output=True, text=True, timeout=300, env=env,
    )
    if not proc.stdout.strip():
        pytest.fail(f"the browser probe returned nothing (rc={proc.returncode}): {proc.stderr[:400]}")
    payload = json.loads(proc.stdout)
    if not payload.get("ok"):
        pytest.fail(
            "the browser could not load the published page, so no claim is made about what a "
            f"reader sees: {payload.get('error')}"
        )
    return payload


def read_pages_in_browser(jobs: list[tuple[str, list[str]]]) -> dict[str, dict]:
    """Read MANY pages in ONE browser: `[(url, [ids...]), ...]` -> `{url: payload}`.

    Each payload has the same shape `read_in_browser` returns, so `assert_visible_reading` grades
    either without knowing which form produced it.

    WHY THIS IS NOT JUST A LOOP OVER `read_in_browser`. A chromium launch is ~1.5s and the page
    load it exists to serve is ~0.4s, so a control whose subject is EVERY published door spends
    four fifths of its time starting browsers. Measured over the 22 doors on 2026-09-17: 22 launches
    took 3m14s, one launch driving all 22 took 39s. The three-minute version is a control nobody
    leaves in the commit path, which is the only place it catches anything before it deploys.

    A PAGE THAT COULD NOT BE LOADED FAILS HERE, BY URL, rather than being returned as a reading
    with no elements -- which every caller would then report as "the reader meets nothing on this
    door", blaming the page for the probe's own failure to look at it.
    """
    payload_in = [{"url": url, "ids": list(ids)} for url, ids in jobs]
    env = {**os.environ, "POESYS_PLAYWRIGHT_BASE": str(playwright_base())}
    proc = subprocess.run(
        ["node", str(PROBE), "--jobs"],
        input=json.dumps(payload_in), cwd=str(playwright_base()),
        capture_output=True, text=True, timeout=1800, env=env,
    )
    if not proc.stdout.strip():
        pytest.fail(
            f"the browser probe returned nothing for {len(payload_in)} page(s) "
            f"(rc={proc.returncode}): {proc.stderr[:400]}"
        )
    out = json.loads(proc.stdout)
    pages = out.get("pages") or []
    unread = [f"{p.get('url')}: {p.get('error')}" for p in pages if not p.get("ok")]
    if unread:
        pytest.fail(
            "the browser could not load {} of {} published page(s), so no claim is made about what "
            "a reader sees on them: {}".format(len(unread), len(payload_in), "; ".join(unread))
        )
    if len(pages) != len(payload_in):
        pytest.fail(
            f"the probe was asked about {len(payload_in)} page(s) and reported on {len(pages)} -- "
            "a short reading read as a complete one is how a door drops out of a sweep unnoticed"
        )
    return {p["url"]: p for p in pages}


def assert_visible_reading(payload: dict, element_id: str, *, must_contain: str = "") -> dict:
    """The reading a door should assert: the element EXISTS, is VISIBLE, and carries the words.

    Each clause names a breakage measured on 2026-09-17 (WHAT_THE_VM_DOORS_GRADE.md): `exists`
    catches the renamed container, `visible` the stylesheet rule and the second `<script>`, and
    `must_contain` is the only clause the vm door could already make.
    """
    el = payload["elements"].get(element_id)
    assert el is not None, f"the probe was not asked about #{element_id}"
    assert el.get("exists"), (
        f"#{element_id} does not exist on the published page, so the reader meets nothing there -- "
        "the vm harness mints an element for any id and cannot see this"
    )
    assert el["visible"], (
        f"#{element_id} is on the page but not visible to a reader "
        f"(display={el['display']}, visibility={el['visibility']}, opacity={el['opacity']}, "
        f"box={el['width']}x{el['height']})"
    )
    if must_contain:
        assert must_contain in el["text"], (
            f"#{element_id} is visible but does not read {must_contain!r}; it reads "
            f"{el['text'][:200]!r}"
        )
    return el


# ---------------------------------------------------------------------------
# THE PROOFS. Every one runs against a SCRATCH page built here, never against a real door -- a
# mechanism proved only on this project's own tree passes whatever it happens to read.
# ---------------------------------------------------------------------------

_SCRATCH_PAGE = """<!doctype html><html><head><style>{css}</style></head><body>
<div id="present">hello reader</div>
<div id="wired"></div>
{extra_markup}
<script>
document.getElementById("wired").innerHTML = "the wired sentence";
</script>
{extra_script}
</body></html>"""


@contextmanager
def _serve(html: str):
    with tempfile.TemporaryDirectory(prefix="scratch-page-") as td:
        (Path(td) / "index.html").write_text(html)

        class _S(socketserver.TCPServer):
            allow_reuse_address = True

            def finish_request(self, request, client_address):
                self.RequestHandlerClass(request, client_address, self, directory=td)

        with _S(("127.0.0.1", 0), _QuietHandler) as httpd:
            port = httpd.socket.getsockname()[1]
            t = threading.Thread(target=httpd.serve_forever, daemon=True)
            t.start()
            try:
                yield f"http://127.0.0.1:{port}/index.html"
            finally:
                httpd.shutdown()
                t.join(timeout=10)


def _page(css: str = "", extra_markup: str = "", extra_script: str = "") -> str:
    return _SCRATCH_PAGE.format(css=css, extra_markup=extra_markup, extra_script=extra_script)


def test_the_reader_meets_a_plainly_rendered_element():
    """THE POSITIVE LEG, and it comes first on purpose. CLAUDE.md: when a branch exists to be taken
    rarely, assert it CAN be taken before asserting what it does -- a probe that reported
    `visible: false` for EVERYTHING would pass all three negative legs below."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with _serve(_page()) as url:
        payload = read_in_browser(url, "present", "wired")
        assert_visible_reading(payload, "present", must_contain="hello reader")
        assert_visible_reading(payload, "wired", must_contain="the wired sentence")


def test_a_stylesheet_rule_that_hides_the_element_is_caught():
    """BREAKAGE A, measured live on the deployment door: the render function is untouched and
    correct, and a CSS rule the vm harness never parses means nobody reads its output."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with _serve(_page(css="#wired { display: none; }")) as url:
        payload = read_in_browser(url, "wired")
        with pytest.raises(AssertionError, match="not visible to a reader"):
            assert_visible_reading(payload, "wired", must_contain="the wired sentence")
        # THE TEETH. The words ARE there -- `innerText` falls back to `textContent` for an element
        # that is not rendered -- so a control asserting only on text passes this page. That is
        # precisely the vm door's reading, and it is why `visible` is a separate clause.
        assert "the wired sentence" in payload["elements"]["wired"]["text"]


def test_a_second_inline_script_that_clears_the_element_is_caught():
    """BREAKAGE B: the vm harness's `match(/<script>([\\s\\S]*?)<\\/script>/)` is neither global nor
    greedy, so it extracts the FIRST inline script and is blind to every later one."""
    why = browser_available()
    if why:
        pytest.skip(why)
    later = '<script>document.getElementById("wired").innerHTML = "";</script>'
    with _serve(_page(extra_script=later)) as url:
        payload = read_in_browser(url, "wired")
        with pytest.raises(AssertionError, match="not visible to a reader"):
            assert_visible_reading(payload, "wired")


def test_an_element_the_page_does_not_have_is_caught():
    """BREAKAGE C, the worst of the three: the vm's `getElementById` mints an element for any id,
    so a door can read a complete render out of a container that is not in the markup."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with _serve(_page()) as url:
        payload = read_in_browser(url, "not-on-this-page")
        with pytest.raises(AssertionError, match="does not exist on the published page"):
            assert_visible_reading(payload, "not-on-this-page")


def test_a_machine_that_has_playwright_is_never_told_it_does_not():
    """THE ANTI-SKIP LEG, and the only one here that does NOT skip when there is no browser.

    Every other leg in this file guards itself with `browser_available()`, which is correct and is
    also the hole: if that function starts saying "not installed" on a machine that has it, all of
    them go quiet together and the run summary is the same colour as a pass. That is exactly what
    happened between `7f40070a6` and this commit -- 7 of 8 legs skipped in every linked worktree,
    which is where every executor turn runs, while the main checkout had playwright throughout.

    KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER (CLAUDE.md). It does not assert "this machine has
    a browser" -- that would red on a machine that legitimately has none, and this repo tolerates
    those. It asserts the REFUSAL IS TRUE: if playwright resolves anywhere this repo would look,
    then `browser_available()` must not claim it is absent. On a machine with no playwright at all
    both sides are "absent" and the leg passes, having asserted a real agreement.

    MUTATION-PROVED 2026-09-17: reverting `browser_available` to `cwd=PROJECT` reds this from a
    linked worktree and leaves it green in the main checkout -- which is the asymmetry that let
    the defect live.
    """
    if shutil.which("node") is None:
        pytest.skip("node is not available, so neither side of this comparison can be taken")
    base = playwright_base()
    resolvable = subprocess.run(
        ["node", "-e", "require.resolve('playwright')"],
        cwd=str(base), capture_output=True, text=True, timeout=120,
    ).returncode == 0
    why = browser_available()
    if resolvable:
        assert why is None, (
            f"playwright resolves from {base}, but the doors are being told {why!r}. Every browser "
            "leg in this tree is skipping on a machine that can render, and a skip is the same "
            "colour as a pass in a run summary"
        )
    elif why is not None:
        # The refusal is honest here; assert it POINTS somewhere, because "not installed" with no
        # location was the wording that hid the defect for a day.
        assert str(base) in why, (
            f"the refusal {why!r} does not name where it looked, so a reader cannot tell a machine "
            "without playwright from a checkout that was asked the wrong question"
        )


def test_many_pages_read_in_one_browser_give_each_page_its_own_reading():
    """THE BATCH POSITIVE LEG, and it is a NULL CONTROL as much as a positive one: it asserts the
    two pages read DIFFERENTLY. One browser reused across navigations is exactly the shape that
    silently returns the first page's DOM for every job, and every assertion in the sweep above it
    would then be graded against one page wearing twenty-two names."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with _serve(_page()) as first, _serve(
        _page(extra_markup='<div id="only-here">the second page</div>')
    ) as second:
        got = read_pages_in_browser([(first, ["present", "wired"]),
                                     (second, ["present", "only-here"])])
        assert set(got) == {first, second}, got.keys()
        assert_visible_reading(got[first], "wired", must_contain="the wired sentence")
        assert_visible_reading(got[second], "only-here", must_contain="the second page")
        # The teeth: the element that exists ONLY on the second page must be absent from the
        # first's reading. Without this the leg passes on a probe that read one page twice.
        assert got[first]["elements"]["present"]["exists"]
        alone = read_pages_in_browser([(first, ["only-here"])])
        assert not alone[first]["elements"]["only-here"]["exists"], (
            "the probe reports an element from a DIFFERENT page as present on this one"
        )


def test_a_page_the_batch_could_not_load_fails_and_is_named():
    """FAIL-CLOSED FOR THE BATCH. A job that did not load must not come back as a page whose
    elements are all absent -- that reads as a broken DOOR and would send the next session to fix a
    page that is fine. The port below is closed, so the navigation genuinely fails."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with _serve(_page()) as good:
        dead = "http://127.0.0.1:1/index.html"
        # `pytest.fail` raises `Failed`, which derives from BaseException and NOT from Exception --
        # `pytest.raises(Exception)` here would let the refusal through and red this leg on the
        # very behaviour it is asserting.
        with pytest.raises(pytest.fail.Exception, match="could not load"):
            read_pages_in_browser([(good, ["present"]), (dead, ["present"])])


def test_the_server_serves_the_index_copy_and_not_the_working_tree():
    """THE SUBJECT LEG. Proved against a scratch repo whose index and working tree deliberately
    disagree, because on this project's own tree they agree almost always and a control that only
    ran here would pass whatever it read."""
    with tempfile.TemporaryDirectory(prefix="scratch-repo-") as td:
        root = Path(td)
        (root / "site").mkdir()
        page = root / "site" / "index.html"
        def run(*a):
            return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True)

        run("init", "-q")
        run("config", "user.email", "t@t")
        run("config", "user.name", "t")
        page.write_text("<!doctype html><html><body><div id=x>INDEX COPY</div></body></html>")
        run("add", "-A")
        run("commit", "-qm", "base")
        # Now the working tree disagrees with the index, and ONLY the index copy may be served.
        page.write_text("<!doctype html><html><body><div id=x>WORKING TREE COPY</div></body></html>")
        with published_site(root=root) as (base_url, docroot):
            import urllib.request

            got = urllib.request.urlopen(f"{base_url}/index.html", timeout=30).read().decode()
            # THE DOCROOT IS THE SAME SUBJECT AS THE URL, and that is the whole reason it is
            # yielded: a sweep that drives the door's script over the docroot and reads the result
            # over the url is otherwise free to be describing two different pages.
            on_disk = (docroot / "index.html").read_text()
        assert "INDEX COPY" in on_disk and "WORKING TREE COPY" not in on_disk, (
            "the yielded docroot is not the published copy, so a caller reading the file and a "
            f"caller reading the url disagree about the page: {on_disk!r}"
        )
        assert "INDEX COPY" in got, "the server served something that is not the published copy"
        assert "WORKING TREE COPY" not in got, (
            "the browser reading is taken from the working tree, so it cannot tell 'the reader can "
            "see this' from 'someone in this tree has fixed it and not landed it'"
        )
