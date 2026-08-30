"""The departure reason mix must reach the rendered page AS A RANGE, never as a point.

THE DEFECT IT SERVES. C2 gave every departure in this world a cause, and the split of the price
family between "my own bill rose" and "someone else is cheaper" is identified by nothing: no
domestic instrument separates them, and Ofgem's Consumer Impacts survey codes both as one answer
(`docs/staging/WORKER_FINDING_THE_P0_CALIBRATION_IS_EITHER_INFEASIBLE_OR_IT_CHOOSES_THE_ANSWER_2026-08-30.md`).
The world still has to roll a die, so it runs at one declared point of that family. **The failure
this guards is that point reaching a reader with no bound on it** -- a single share per cause, which
a reader cannot tell from a measurement, and which would be this project publishing its own free
parameter back as a finding.

WHY THE SUBJECT IS THE RENDERED DOM AND NOT THE JSON. This project's own
`test_published_caveat_reaches_the_reader.py` records the class: a corrected sentence sat in the
code and in the working tree and NOT in what a browser put on screen, and nothing was red, because
every assertion took an in-process object as its subject. So this drives the REAL harness door
through its own boot path with `site/_live_harness.mjs` and asserts on what the page rendered.

AND WHY THE FEED IS BUILT FROM THE LIVE GENERATOR RATHER THAN READ FROM `site/data/proof.json`.
The first draft read the published file, and it went red inside the commit gate for a reason that
had nothing to do with this change: the publish lane regenerates that file every few minutes, and
it did so between this control being written and the gate reading it, from a generator that did not
yet carry the row. A gate slower than the tree's landing cadence never converges -- this repository
has that written down -- and a control that reds on another lane's timing is a flapping control, not
a stricter one. The claim this file owns is *the generator's row reaches the reader*, and the
generator is the subject. Whether the PUBLISHED file is current is a different claim with its own
owner: the G13 store-agreement audit rendered on this same door, which says in as many words when
the figures differ from the committed record.

R15 -- the mutations, each cheap to state because the page is the subject:
  * publish the declared point without the range (drop `interval` from the note) ->
    `test_the_mix_reaches_the_reader_as_a_range` red.
  * delete the row from `_not_proven()` ->
    `test_the_mix_reaches_the_reader_as_a_range` red (the claim is not on the page at all).
  * render a row whose note came back from the fail-closed branch ->
    `test_an_unreadable_measurement_still_reaches_the_reader_as_a_row` proves the row survives,
    so a missing artefact cannot make the caveat quietly disappear.
  * widen the interval to 0-100% ->
    `test_the_range_is_narrower_than_the_thing_it_is_meant_to_bound` red: a bound that admits
    everything is not a bound, it is a decoration.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
HARNESS = SITE / "_live_harness.mjs"
DOOR = SITE / "harness" / "index.html"
PROOF = SITE / "data" / "proof.json"   # for the shape of the feed, never for its `not_proven`
DELIVERY = SITE / "data" / "delivery.json"
DIRECTOR_DELTA = SITE / "data" / "director_delta.json"
DIRECTOR_RESERVED = SITE / "data" / "director_reserved.json"
MIX = PROJECT / "docs" / "reports" / "c2_reason_mix_interval.json"

#: The claim text the generator writes. Matched on a distinctive fragment rather than in full, so
#: an editorial rewording does not red this, but the row disappearing does.
CLAIM_FRAGMENT = "Why households leave"


def _feed(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _live_proof_feed() -> dict:
    """The published feed's shape, carrying the `not_proven` list the CURRENT generator builds.

    Everything else on this door (the stamp, the gaps, the corrections) comes from the published
    file, because the door has to boot; only the list under test is taken from the live code.
    """
    import tools.generate_proof_data as gen

    return {**_feed(PROOF), "not_proven": gen._not_proven()}


def _render(proof: dict) -> dict:
    """Drive the real harness door with the given proof feed and return its rendered elements.

    FAIL-CLOSED: an unresolved feed, a script error or a missing element raises here rather than
    degrading to an empty string that a `not in` assertion would happily pass on.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- the render check is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    payload = {
        "../data/proof.json": proof,
        "../data/delivery.json": _feed(DELIVERY),
        "../data/director_delta.json": _feed(DIRECTOR_DELTA),
        "../data/director_reserved.json": _feed(DIRECTOR_RESERVED),
    }
    proc = subprocess.run(
        ["node", str(HARNESS), str(DOOR)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, "the render harness failed: {}".format(proc.stderr[-2000:])
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), (
        "the door asked for a feed this test did not supply ({}), so whatever it rendered is not "
        "what a browser would".format(meta.get("unresolved"))
    )
    assert not meta.get("scriptError"), "the door's own script threw: {}".format(
        meta.get("scriptError"))
    return out


def _reader_text(element: dict) -> str:
    """What a reader actually sees: tags stripped and entities UNESCAPED.

    The harness is a DOM shim, so `textContent` only carries what the page ASSIGNED to
    `textContent`, and this door builds its cards with `innerHTML`. Reading the raw markup instead
    would be reading a string no reader ever meets -- the note escapes its typographic quotes and
    its em dash, so a checker looking for a range in `&#8211;`-separated markup finds one thing and
    a reader finds another. Unescape, then assert.
    """
    return html.unescape(re.sub(r"<[^>]+>", " ", element["innerHTML"]))


def _rendered_row(proof: dict) -> str:
    """The rendered text of the departure-reason row, as a reader meets it."""
    text = _reader_text(_render(proof)["not-proven"])
    assert CLAIM_FRAGMENT in text, (
        "the departure reason mix is not on the rendered page at all. The feed can carry it and "
        "the reader can still never meet it -- that is the class this file exists for. Rendered "
        "text began: {!r}".format(text[:400])
    )
    start = text.index(CLAIM_FRAGMENT)
    return text[start:start + 1400]


def _percentages(fragment: str) -> list[float]:
    return [float(m) for m in re.findall(r"(\d+(?:\.\d+)?)%", fragment)]


def test_the_mix_reaches_the_reader_as_a_range():
    """MUTATION: publish the declared point alone and this fires.

    A RANGE, and the test for one is that the two endpoints DIFFER. A single share per cause is
    what a reader would take for a measurement, and it is precisely what the evidence does not
    support.
    """
    fragment = _rendered_row(_live_proof_feed())
    ranges = re.findall(r"(\d+(?:\.\d+)?)%[–—-](\d+(?:\.\d+)?)%", fragment)
    assert len(ranges) >= 3, (
        "the rendered reason mix carries {} ranges, not one per cause. A cause published as a "
        "point is this project reporting its own free parameter back as a measurement. "
        "Rendered: {!r}".format(len(ranges), fragment)
    )
    for lo, hi in ranges[:3]:
        assert float(hi) > float(lo), (
            "a published range {}%-{}% has equal endpoints, which is a point wearing a range's "
            "punctuation".format(lo, hi)
        )


def test_the_rendered_range_is_the_measured_one():
    """MUTATION: hand-write the interval in the generator instead of reading the artefact.

    The endpoints on the page must be the ones `tools/fit_departure_hazards.py` measured. A
    transcribed interval is a number that goes stale the next time the family is re-swept, and
    nothing says so.
    """
    measured = json.loads(MIX.read_text())["interval"]
    fragment = _rendered_row(_live_proof_feed())
    shown = _percentages(fragment)
    for cause, (lo, hi) in measured.items():
        for value in (round(100 * lo), round(100 * hi)):
            assert value in [round(s) for s in shown], (
                "the page does not show the measured {} endpoint {}% -- the interval on the page "
                "is not the interval that was measured. Rendered: {!r}".format(
                    cause, value, fragment)
            )


def test_the_range_is_narrower_than_the_thing_it_is_meant_to_bound():
    """MUTATION: widen any endpoint pair to 0-100% and this fires.

    THE NULL CONTROL. A bound that admits every possible answer passes every check and tells a
    reader nothing -- the fail-open a range check degrades into. At least one cause must be bounded
    to a range narrower than half the scale, or the "interval" is a decoration.
    """
    measured = json.loads(MIX.read_text())["interval"]
    widths = {c: hi - lo for c, (lo, hi) in measured.items()}
    assert min(widths.values()) < 0.5, (
        "every cause's published range spans more than half the scale ({}), which cannot "
        "discriminate any reason mix from any other".format(
            {c: round(w, 3) for c, w in widths.items()})
    )


def test_an_unreadable_measurement_still_reaches_the_reader_as_a_row():
    """MUTATION: make the generator's except branch return nothing and this fires.

    FAIL CLOSED ON THE SURFACE. If the artefact cannot be read, the honest outcome is a row that
    says the mix could not be read -- not a silently shorter list. A caveat that disappears when
    its evidence does is the worst of both: the reader sees fewer open questions precisely when
    there is more that is not known.
    """
    import tools.generate_proof_data as gen

    original = gen.REASON_MIX_PATH
    try:
        gen.REASON_MIX_PATH = PROJECT / "docs" / "reports" / "no_such_mix_artefact.json"
        row = gen._why_households_leave()
    finally:
        gen.REASON_MIX_PATH = original
    assert CLAIM_FRAGMENT in row["claim"], "the row vanished when its artefact did"
    assert "could not be read" in row["note"], (
        "an unreadable measurement produced a note that does not say so: {!r}".format(row["note"])
    )
    assert "%" not in row["note"], (
        "the fail-closed branch still shows a share, which would be a stale number presented as "
        "a live one: {!r}".format(row["note"])
    )

    rendered = _rendered_row({**_feed(PROOF), "not_proven": [row]})
    assert "could not be read" in rendered
