"""EVERY published door, EVERY element its own script asked for, READ BY A BROWSER.

WHAT THIS OWNS. CLAUDE.md makes "done means the rendered value changed" load-bearing and names the
door suites as its enforcement. Those suites -- roughly twenty-four of them, hanging off five
harnesses (`site/_live_harness.mjs`, `site/harness/_render_harness.mjs`,
`site/explore/_bill_render_harness.mjs`, `site/assets/_freshness_harness.mjs`,
`site/knowledge/electricity-wholesale/_render_harness.mjs`) -- grade a string the page's own
JavaScript wrote into an element inside node's `vm`. That is strong evidence about the FEED and the
WIRING and none at all about RENDERING. On 2026-09-17 three constructed breakages, each leaving a
reader looking at nothing, passed every leg of the deployment door
(`docs/design/WHAT_THE_VM_DOORS_GRADE.md`):

  A  a `display: none` rule in the page's own `<style>`   -- the vm parses no CSS
  B  a SECOND inline `<script>` clearing the section      -- `_render_harness` reads only the FIRST
  C  the container renamed in the markup                  -- the vm MINTS an element for any id

"The rendered value" has two experiences behind it -- *the page computed it* and *a person can read
it* -- and this project has been measuring one of them across all twenty-four doors and publishing
the other one's name. That is the definitional split CLAUDE.md calls this project's most expensive
recurring shape. This file is the second experience and only that: it re-grades no feed, asserts no
sentence, and would pass a door whose every figure was wrong but readable. The suites beside it
already do the other half, better and faster.

WHY ONE FILE AND NOT TWENTY-FOUR LEGS. The per-suite shape exists -- `site/harness/
test_the_deployment_reading_is_visible_to_a_browser.py` is it, and it is worth having, because it
names that door's own sections and their own words. But twenty-three more of those would be
twenty-three hand-kept lists of element ids, and a hand-kept list is how a control comes to grade a
population that has drifted out from under it. Here **nothing is written down**: the doors are
globbed out of the published extract, and the ids come from the vm harness's OWN OUTPUT -- every
element the door's script ASKED FOR on this run. A door that gains a section gains coverage the
same day, and a door renamed or deleted takes its coverage with it.

WHAT THIS DOES NOT COVER, stated here rather than discovered later. An element the door's script
never mentions is not in the subject, so a section deleted from BOTH the markup and the script is
invisible to this file. That is the vm suites' question -- they assert the words -- and it is the
reason this file is an addition to them and not a replacement.

WHY THE SUBJECT IS THE PUBLISHED (INDEX) BYTES. A probe pointed at the working tree cannot tell
"the reader can see this" from "someone in this tree has fixed it and not landed it" -- the defect
`site/test_the_published_bytes_reader.py` was built for. Both halves read the SAME extract, which
is why `published_site` yields the docroot as well as the URL: a vm run over the working tree and a
browser reading over the published bytes would be describing a page that exists nowhere.

HOW THIS DIFFERS FROM G4, which lands in the same week and takes a browser reading of every door.
G4 (`site/live_pixel_verify.py`) reads the LIVE HOST -- it is the only control that can tell you the
deployed page is readable, and it is the one that must exist. But it needs the internet and a
deployed door, so it is a door-CLOSE tool and is in no gate. It therefore catches breakage A, B or C
only AFTER it has shipped. This one runs in the commit path against bytes that have not deployed
yet, which is the whole of its reason to exist alongside.

MEASURED, NOT ASSUMED (2026-09-17, first run, prediction filed before it in
`docs/staging/records/SEAT_PREREG_A_BROWSER_LEG_DERIVED_FROM_THE_VM_DOORS_OWN_ELEMENT_LIST_OVER_PUBLISHED_BYTES_2026-09-17.md`):
22 doors, 417 element readings, 0 failures, 30s in one browser -- so this control goes green on a
correct tree, which is the thing a fail-closed sweep most needs proving about itself and the reason
`test_the_sweep_can_fail` below is not optional. The first draft of the prediction said the
population was 2 static doors; it is 1. The Front Door renders client-side and is graded like any
other door, which is the better answer and not the one that was predicted.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from test_the_browser_reading import (  # noqa: E402  (must follow the sys.path insertion)
    assert_visible_reading,
    browser_available,
    published_site,
    read_pages_in_browser,
)

#: The generic harness: it knows no function names, supplies `fetch`, and lets the door's own boot
#: sequence drive itself. Every per-door harness is a narrower version of this one, so driving the
#: page through this one covers doors whose suites use any of the five.
_LIVE_HARNESS = _HERE / "_live_harness.mjs"

#: The whole-page reading, for a door with no client render to write into an element. Its value is
#: `live_pixel_verify.WHOLE_PAGE` and it is spelled here rather than imported because importing a
#: tool into a test to borrow one string is a dependency the orphan ratchet then has to reason
#: about; the two are held together by `test_the_whole_page_id_matches_the_live_verifier` below.
_WHOLE_PAGE = ":body"

#: A door is re-driven while each round discovers feeds the last one did not ask for. Bounded, so a
#: page that asks for one new url per round cannot hang the sweep; 5 is well clear of the deepest
#: door in the tree, which settles in 2.
_MAX_FEED_ROUNDS = 5


def _resolve_feed(door: Path, url: str, docroot: Path) -> Path | None:
    """The file in the PUBLISHED extract a door's `fetch(url)` names, or None if it names none.

    None is not an error here. A door may fetch an absolute origin, or a feed that is deliberately
    not published; `_live_harness.mjs` then reports it `unresolved` and the page takes its own
    `.catch()` branch -- which is the live behaviour and a thing the reader-side leg should see, not
    a thing this helper should paper over.
    """
    if "://" in url:
        return None
    clean = url.split("?", 1)[0].split("#", 1)[0]
    target = (docroot / clean.lstrip("/")) if clean.startswith("/") else (door.parent / clean)
    try:
        target = target.resolve()
        target.relative_to(docroot.resolve())
    except (OSError, ValueError):
        return None  # outside the extract: not a published feed, whatever the page thinks
    return target if target.is_file() else None


def _drive(door: Path, docroot: Path) -> dict:
    """Run the door's own script under `vm` over the published bytes; return the element map.

    The feed map is discovered by RUNNING the door, not by grepping it: `_live_harness.mjs` reports
    what the page asked for in `_meta.requested`, and a door whose second-round render fetches
    something the first round did not would otherwise be driven half-booted. Bounded rounds, so a
    page that asks for one new url per round cannot hang the sweep.
    """
    feeds: dict[str, object] = {}
    out: dict = {}
    for _ in range(_MAX_FEED_ROUNDS):
        proc = subprocess.run(
            ["node", str(_LIVE_HARNESS), str(door)],
            input=json.dumps(feeds), capture_output=True, text=True, timeout=300,
        )
        assert proc.returncode == 0, (
            f"the published copy of {door.name} could not be driven at all: {proc.stderr[:400]}"
        )
        out = json.loads(proc.stdout)
        wanted = [u for u in (out.get("_meta", {}) or {}).get("requested", []) if u not in feeds]
        grew = False
        for url in wanted:
            resolved = _resolve_feed(door, url, docroot)
            if resolved is None:
                continue
            try:
                feeds[url] = json.loads(resolved.read_text())
            except (OSError, json.JSONDecodeError):
                continue  # the door's own .catch() is the right reader-side behaviour to read
            grew = True
        if not grew:
            break
    return out


def _door_path(door: Path, docroot: Path) -> str:
    rel = door.relative_to(docroot).parent.as_posix()
    return "/index.html" if rel == "." else f"/{rel}/index.html"


@pytest.fixture(scope="module")
def sweep():
    """One extract, one browser, every published door. Yields `{door_path: (payload, ids)}`.

    Module-scoped because the launch is the cost (measured 2026-09-17: 22 separate launches 3m14s,
    one launch 39s) and every leg below asks about the same set of page loads.
    """
    if shutil.which("node") is None:
        pytest.skip("node is not available to drive the doors")
    why = browser_available()
    if why:
        pytest.skip(why)
    with published_site() as (base, docroot):
        doors = sorted(docroot.glob("**/index.html"))
        # FAIL-CLOSED ON AN EMPTY POPULATION. A glob that stops matching -- a layout change, an
        # extract that landed empty -- would otherwise make every leg below pass vacuously, which
        # is this repo's recorded shape for a control that quietly stops being one.
        assert doors, f"no published door was found under {docroot}, so this sweep has no subject"
        jobs, ids_by_path, written_by_path, statics = [], {}, {}, []
        for door in doors:
            rendered = _drive(door, docroot)
            meta = rendered.pop("_meta", {}) or {}
            path = _door_path(door, docroot)
            if meta.get("static"):
                statics.append(path)
            # THE SUBJECT IS EVERY ELEMENT THE DOOR'S SCRIPT ASKED FOR, not every element it left
            # content in, and the difference is a hole this control fell into on its first day.
            # Filtering to "wrote content" is the control's OWN filter emptying its OWN evidence:
            # a later `<script>` that CLEARS a section removes that section from the id list, so
            # the sweep never asks the browser about the one element the reader just lost, and
            # goes green. Mutation-proved 2026-09-17 -- a deferred clear on `#deployment` passed
            # the content-filtered version and reds the version below.
            #
            # Measured before it was adopted rather than argued: over the 22 published doors the
            # wider subject is 417 ids against 414, and all three extras read visible. The filter
            # was buying nothing and costing the element that matters most.
            ids_by_path[path] = [_WHOLE_PAGE, *sorted(rendered)]
            written_by_path[path] = sorted(
                eid for eid, c in rendered.items()
                if f"{c.get('innerHTML', '')} {c.get('textContent', '')}".strip()
            )
            jobs.append((base + path, ids_by_path[path]))
        started = time.monotonic()
        readings = read_pages_in_browser(jobs)
        elapsed = time.monotonic() - started
    yield {
        path: (readings[base + path], ids, written_by_path[path])
        for path, ids in ids_by_path.items()
    }, statics, elapsed


def test_every_element_the_door_rendered_exists_on_the_page_a_reader_gets(sweep):
    """CATCHES BREAKAGE C ACROSS EVERY DOOR. The vm's `getElementById` mints an element for any id
    asked of it, so a door test can read a complete, correct render out of a container that is not
    in the markup -- and did: renaming `<div id="deployment">` passed all six legs of its own door
    while chromium showed a reader four dead sections and a false load-failure sentence.

    Nothing here is keyed to today's ids. The subject is exactly the set the door's script wrote
    into on this run, so this leg cannot go stale and cannot be satisfied by editing a list.
    """
    readings, _statics, _elapsed = sweep
    missing = []
    for path, (payload, ids, _written) in sorted(readings.items()):
        for eid in ids:
            el = payload["elements"].get(eid) or {}
            if not el.get("exists"):
                missing.append(f"{path} #{eid}")
    assert not missing, (
        "the door's own script wrote content into {} element(s) that are NOT on the page a reader "
        "gets. The vm harness mints an element for any id and reports a perfect render into it, so "
        "every suite grading these doors is green: {}".format(len(missing), ", ".join(missing[:20]))
    )


def test_every_element_the_door_rendered_is_visible_to_a_reader(sweep):
    """CATCHES BREAKAGES A AND B ACROSS EVERY DOOR -- a stylesheet rule the vm never parses, and a
    later inline `<script>` the per-door harnesses' non-global regex cannot see.

    `visible` is a separate clause from the words on purpose. `innerText` falls back to
    `textContent` for an element that is not rendered, so a door hidden by CSS returns its full
    sentence to a text assertion -- which is precisely the vm door's reading.
    """
    readings, _statics, _elapsed = sweep
    hidden = []
    for path, (payload, ids, _written) in sorted(readings.items()):
        for eid in ids:
            el = payload["elements"].get(eid) or {}
            if el.get("exists") and not el.get("visible"):
                hidden.append(
                    f"{path} #{eid} (display={el.get('display')}, "
                    f"visibility={el.get('visibility')}, opacity={el.get('opacity')}, "
                    f"box={el.get('width')}x{el.get('height')})"
                )
    assert not hidden, (
        "{} element(s) carry a render nobody can read. Each was written by the door's own script "
        "and each is invisible in a browser: {}".format(len(hidden), "; ".join(hidden[:20]))
    )


def test_a_door_that_rendered_nothing_at_all_is_caught(sweep):
    """THE FLOOR, and without it the two legs above are satisfied by a door that renders NOTHING --
    an empty id list makes every "for each id" assertion pass, which is the fail-open this repo has
    recorded as a class ("a classifier's empty list is a hole every group-by drops").

    A STATIC door (`/privacy/`, deliberately server-rendered with no inline script) legitimately
    writes into no element and is judged on its whole-page reading instead. It is not excepted:
    `_live_harness.mjs` decides which doors those are, by whether the page HAS an inline script,
    and the whole-page reading is a real reading -- a shell served by a broken build has a body and
    no words in it.
    """
    readings, statics, _elapsed = sweep
    silent = [path for path, (_p, _ids, written) in readings.items()
              if not written and path not in statics]
    assert not silent, (
        "these doors carry an inline script that rendered into NO element at all, so every "
        "reader-side assertion about them passes on an empty set: {}".format(", ".join(silent))
    )
    for path in statics:
        payload, _ids, _written = readings[path]
        body = assert_visible_reading(payload, _WHOLE_PAGE)
        assert len(body["text"].split()) >= 50, (
            f"{path} is a static door serving only {len(body['text'].split())} words a reader can "
            "see -- that is a shell, not a page"
        )


def test_the_sweep_covers_every_door_the_live_verifier_names(sweep):
    """THE POPULATION CONTROL. The two legs above conclude about "every door"; this is the only
    thing that makes that word mean anything. `live_pixel_verify.all_doors()` is the independently
    maintained list of what is DEPLOYED, so a door that exists in the repo and is swept here but
    served to nobody -- or, the direction that matters, a deployed door this glob does not reach --
    shows up as a disagreement between two lists neither of which is this file's own.
    """
    readings, _statics, _elapsed = sweep
    import live_pixel_verify as verifier

    swept = {p.rsplit("index.html", 1)[0] for p in readings}
    uncovered = [d for d in verifier.all_doors() if d not in swept]
    assert not uncovered, (
        "the live verifier deploys door(s) this reader-side sweep never looked at, so 'every door' "
        "is not what this file measures: {}".format(", ".join(uncovered))
    )


def test_the_whole_page_id_matches_the_live_verifier():
    """The one string this file spells rather than imports. If the verifier's whole-page id ever
    changes, a static door here would be asked about an id no probe understands and would report
    `exists: false` -- a red naming the page rather than the disagreement. Cheap to hold, and it
    does not need the browser, so it runs on machines that skip everything else in this file."""
    import live_pixel_verify as verifier

    assert _WHOLE_PAGE == verifier.WHOLE_PAGE, (
        f"this sweep asks for {_WHOLE_PAGE!r} and the probe understands "
        f"{verifier.WHOLE_PAGE!r} as the whole-page reading"
    )


def test_the_sweep_can_fail(sweep):
    """THE CONTROL OVER THE CONTROL, and it is the leg that earns the rest their meaning.

    Every assertion above is of the form "no element is broken", and a sweep that looked at NOTHING
    satisfies all of them -- an empty extract, a probe returning empty element maps, a glob that
    matched no door. CLAUDE.md: when a branch exists to be taken rarely, assert it CAN be taken
    before asserting what it does. So this asserts the sweep ACTUALLY READ something, and it asserts
    it over the whole partition rather than one leg at a time: real doors, real ids, and at least
    one id per door that a browser reported as genuinely visible with a box.

    It also prints the cost, because a control that quietly grows to three minutes is one a future
    session removes from the commit path without anyone deciding to.
    """
    readings, statics, elapsed = sweep
    assert len(readings) >= 2, f"only {len(readings)} door(s) were read at all"
    read_ids = sum(len(ids) for _p, ids, _w in readings.values())
    assert read_ids > len(readings), (
        f"{read_ids} element reading(s) across {len(readings)} door(s) -- the sweep asked about "
        "little more than the whole-page fallback, so it is not grading rendered elements"
    )
    visible_somewhere = [
        path for path, (payload, ids, _w) in readings.items()
        if any((payload["elements"].get(i) or {}).get("visible") for i in ids)
    ]
    assert len(visible_somewhere) == len(readings), (
        "these doors produced no visible element AT ALL, which is a probe that cannot see rather "
        "than {} broken doors: {}".format(
            len(readings) - len(visible_somewhere),
            ", ".join(sorted(set(readings) - set(visible_somewhere))))
    )
    print(f"\nreader-side sweep: {len(readings)} doors ({len(statics)} static), "
          f"{read_ids} element readings, {elapsed:.0f}s in one browser")
