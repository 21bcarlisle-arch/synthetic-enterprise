"""R15 contract for the retirement of the sanctioned interim bypass shape (atom OPS5).

WHAT WAS RETIRED. The 2026-08-09 ruling retroactively sanctioned one hook-bypass shape --
four conditions required together (disclosed in-message, both parents independently gated,
docs-only, filed) -- and said in the same breath that the class closes by MECHANISM, not by
exception. `OPS4_surgical_landing_tool` is that mechanism. This atom executes the expiry the
ruling attached to the exception.

WHY A TEST AND NOT A PARAGRAPH. An expiry nobody executes is an orphan transition (R11), and
a retro-sanctioned exception with no expiry becomes the rule. Every rule that decayed in this
project was an exhortation; every rule that held was a mechanism (MAKE_IT_STICK). So the
retirement is asserted here, on disk, rather than announced.

THE THREE WAYS THIS RETIREMENT COULD BE FALSE, one test each:

1. THE CANON NEVER LEARNS THE WALL. The design doc records the retirement, but CLAUDE.md --
   the file a seat actually reads at 21:00 on a wedged tree -- says nothing about hook-bypass
   and nothing about the legal move. The seat then hand-rolls a `commit-tree` for the same
   reason as last time. Guarded by `test_the_operating_canon_states_the_wall_and_names_the_
   legal_move`.

2. THE EXCEPTION IS STILL WRITTEN AS LIVE. A live-canon document restates the four-condition
   shape as an available option. Whoever finds it uses it; the retirement never happened where
   it counts. Guarded by `test_no_live_canon_document_offers_the_interim_shape_as_available`,
   which scans the canon set rather than one hand-named file, so a NEW doc restating the
   carve-out is caught too (R10: close the class, not the instance).

3. THE REPLACEMENT IS DEAD. This is the dangerous one, and the reason the retirement is bound
   to a live check rather than to the mere existence of `tools/surgical_land.py`. Withdrawing
   the exception while the legal move does not run leaves NO legal move on a dirty shared
   tree, and SURGICAL_LANDING.md's own argument is that a rule with no legal move does not get
   obeyed, it gets forgotten. The check runs the CLI in a SUBPROCESS because this repo has
   already been bitten by a tool whose in-process tests were green while its `python3 -m`
   entry point was broken by a sys.path defect -- an import in this test file would reproduce
   that blindness exactly. Guarded by `test_the_replacement_runs_from_a_cold_command_line`.

THE MARKER. The retirement is recorded in `docs/design/SURGICAL_LANDING.md` as one
machine-readable line rather than as prose, so that tests 1-3 key on a declaration someone had
to write deliberately and cannot satisfy by accident:

    <!-- INTERIM_BYPASS_SHAPE: RETIRED 2026-08-10 -- replaced by tools/surgical_land.py (OPS5) -->

MUTATIONS KILLED (seven, each run against this file on 2026-08-10 and each observed red on its
own defect before the atom was certified; the file restores green afterwards):
  * marker deleted -> marker test
  * the replacement path named in the marker points at a file that does not exist -> marker test
  * CLAUDE.md loses the tool name -> test 1
  * CLAUDE.md loses the wall -> test 1
  * the carve-out restated with "RETIRED" removed -> test 2 (+ marker test)
  * the account of what was retired deleted from the design doc -> test 2's VACUITY guard, which
    is the mutation that matters most here: without it, erasing the section would make the class
    guard pass by having nothing to check
  * `tools/surgical_land.py` made unrunnable from the CLI -> test 3 (+ marker test)
The forward-tense guard needed no mutation: it was red on HEAD, on the doc's own live sentence
("expires with this tool"), until this atom rewrote it.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

DESIGN_DOC = ROOT / "docs" / "design" / "SURGICAL_LANDING.md"
OPERATING_CANON = ROOT / "CLAUDE.md"

# The marker the retirement is recorded as. Anchored to a REPLACEMENT PATH, not just a date,
# because "retired" without a named successor is the orphan-transition shape R11 forbids.
MARKER_RE = re.compile(
    r"INTERIM_BYPASS_SHAPE:\s*RETIRED\s+(?P<date>\d{4}-\d{2}-\d{2})\s*--\s*"
    r"replaced by (?P<replacement>\S+)"
)

# The live canon: documents that tell a seat what it may do TODAY. Deliberately EXCLUDES
# `docs/staging/**` -- the rulings and worker findings there are the historical RECORD of what
# was said on the day, and rewriting the record to make a test pass would be the falsification
# this project's whole evidence discipline exists to prevent. The record keeps saying the
# exception was granted; the canon must stop offering it.
def _live_canon_files() -> list[Path]:
    files = [OPERATING_CANON]
    files += sorted((ROOT / "docs" / "design").rglob("*.md"))
    return [f for f in files if f.is_file()]


# Phrases that DESCRIBE the carve-out. A file only trips the scan if it also talks about
# bypassing the hook, so an unrelated "four conditions" elsewhere in the design corpus cannot
# false-fire (a control that reds on innocent text gets routed around -- see the write-time
# gate's own note on that failure mode).
_CARVE_OUT_PHRASES = ("four conditions", "interim exception", "interim shape", "interim bypass")
_BYPASS_PHRASES = ("--no-verify", "commit-tree", "bypass")


# The two phrase sets must land in the SAME PARAGRAPH, not merely the same file.
#
# 2026-08-10: whole-file co-occurrence was too loose and it wedged publishing for a full gate
# cycle. `docs/design/KNIFE_HOTSPOT_PASSES.md` says "Four conditions, measured per file" about
# the epistemic WALKER's lift test (zero walled importers, nothing the codebase uses, an entry
# point, only observables) and, 150 lines away, calls a seam crossing a "comment-shaped bypass".
# Neither sentence is about hook-bypass; together they read as the carve-out. That is precisely
# the "reds on innocent text" failure this predicate's own comment set out to avoid -- and the
# cost was not theoretical, since a red here blocks every publish.
#
# Proximity is the discriminator that survives both ways: a document actually RESTATING the
# carve-out has to say what is being bypassed next to the conditions for bypassing it, because
# that is the only way the sentence means anything. Splitting on blank lines keeps the window
# tied to the author's own unit of argument rather than to an arbitrary character count.
def _paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def _mentions_the_carve_out(text: str) -> bool:
    return any(
        any(p in low for p in _CARVE_OUT_PHRASES) and any(p in low for p in _BYPASS_PHRASES)
        for low in (para.lower() for para in _paragraphs(text))
    )


def test_the_retirement_is_recorded_as_a_marker_naming_a_replacement_that_exists():
    """The declaration itself: a date, and a successor that is really on disk.

    Fails if the marker is absent, if it is left forward-looking, or if it names a replacement
    path that does not exist -- the three ways a retirement note can be written and still mean
    nothing.
    """
    text = DESIGN_DOC.read_text(encoding="utf-8")
    m = MARKER_RE.search(text)
    assert m is not None, (
        f"{DESIGN_DOC.relative_to(ROOT)} carries no INTERIM_BYPASS_SHAPE retirement marker. "
        "The interim four-condition bypass was sanctioned WITH an expiry; the expiry is only "
        "executed when it is recorded here in the form the guards read."
    )
    replacement = ROOT / m.group("replacement")
    assert replacement.is_file(), (
        f"The retirement marker names {m.group('replacement')} as the replacement, but that "
        "file does not exist. A retirement whose successor is missing withdraws the only "
        "sanctioned shape and leaves nothing in its place (R11: no orphan transitions)."
    )


def test_the_operating_canon_states_the_wall_and_names_the_legal_move():
    """CLAUDE.md is what a seat reads under pressure; the wall has to be IN it, with the way out.

    Both halves are load-bearing. The wall alone is the 2026-08-09 situation exactly -- a rule
    with two sins and no third option -- which is how the bypass happened in the first place.
    """
    text = OPERATING_CANON.read_text(encoding="utf-8")
    low = text.lower()
    assert "hook-bypass is a wall" in low, (
        "CLAUDE.md does not state that hook-bypass is a WALL. The design doc recording it is "
        "not enough: the operating canon is the file consulted when the tree is wedged."
    )
    assert "surgical_land" in text, (
        "CLAUDE.md states the wall but never names `tools/surgical_land` -- a wall with no "
        "legal move beside it is an exhortation with extra steps (SURGICAL_LANDING.md's own "
        "argument for why the rule alone would not have held)."
    )


def test_no_live_canon_document_offers_the_interim_shape_as_available():
    """Class guard, not an instance guard: ANY live-canon doc describing the carve-out must
    mark it retired.

    Scans the whole canon set so a future document that restates the four conditions is caught
    without anyone remembering to extend a list of filenames (R10).
    """
    mentioning = [f for f in _live_canon_files() if _mentions_the_carve_out(f.read_text(encoding="utf-8"))]

    # Vacuity guard. If nothing in the canon describes the carve-out at all, this test would
    # pass while asserting nothing -- and it would keep passing after someone deleted the
    # retirement section wholesale. The design doc is required to keep describing what was
    # retired, precisely so the population under test is never empty.
    assert DESIGN_DOC in mentioning, (
        f"{DESIGN_DOC.relative_to(ROOT)} no longer describes the interim bypass shape at all. "
        "The retirement must remain legible -- deleting the account of what was retired empties "
        "this control's population and makes it pass vacuously."
    )

    offenders = []
    for f in mentioning:
        text = f.read_text(encoding="utf-8")
        if "RETIRED" not in text:
            offenders.append(str(f.relative_to(ROOT)))
    assert not offenders, (
        "These live-canon documents describe the sanctioned interim bypass shape without "
        f"marking it RETIRED, so they read as a live permission: {offenders}. The 2026-08-09 "
        "exception expired when `tools/surgical_land.py` landed."
    )


def test_the_replacement_runs_from_a_cold_command_line():
    """The legal move must actually run -- checked through `python3 -m`, not an import.

    An import here would pass on a tool whose CLI entry point is broken, which is a defect
    class this repo has already paid for. `--help` is enough: it exercises module resolution,
    import of every top-level dependency, and argument-parser construction, without touching
    the repo's git state.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "tools.surgical_land", "--help"],
        cwd=str(ROOT), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, (
        "`python3 -m tools.surgical_land --help` failed with rc="
        f"{proc.returncode}. The interim bypass shape is retired, so this IS the legal move on "
        f"a dirty shared tree; while it does not run there is no legal move at all.\n"
        f"stdout: {proc.stdout[-800:]}\nstderr: {proc.stderr[-800:]}"
    )
    assert "-m" in proc.stdout and "paths" in proc.stdout, (
        "The CLI runs but no longer offers the message/paths interface the canon tells a seat "
        f"to use. stdout:\n{proc.stdout[-800:]}"
    )


@pytest.mark.parametrize("phrase", ["expires with this tool", "will retire", "retires under"])
def test_the_design_doc_does_not_leave_the_retirement_in_the_future_tense(phrase: str):
    """The failure this atom exists to prevent, in its most likely form: the doc still says the
    exception is *going to* expire. That sentence was true while OPS5 was unbuilt and is a
    live-permission statement now."""
    section = DESIGN_DOC.read_text(encoding="utf-8")
    assert phrase not in section.lower(), (
        f"{DESIGN_DOC.relative_to(ROOT)} still defers the retirement to future work "
        f"({phrase!r}). OPS5 has executed it; the doc must record it in the past tense or the "
        "expiry reads as pending."
    )
