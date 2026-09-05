"""A mutation-harness marker must never reach production source.

THE DEFECT THIS EXISTS FOR (2026-09-05, found while merging the shared tree's eight stranded
commits onto origin/main --
SEAT_FINDING_THE_FILE_THAT_HELD_THE_ADVANCE_FOR_NINE_ATTEMPTS_CARRIED_WORK_ORIGIN_HAD_ALREADY_REIMPLEMENTED_2026-09-05.md).
`background/sanity_daemon.py:364`, committed on `main` at `78a36a2b5`, read:

    except OSError as e:
        last_sent = None  # MUTANT

That is the once-per-day digest stamp's unreadable branch, and `None` there is precisely the
fail-open the surrounding docstring argues against at length: an unreadable stamp is UNWRITABLE
too, so the stamp never advances, and the director gets a repeated digest every 30-minute cycle
until somebody intervenes -- the alarm-that-repeats-unactionably the function exists to prevent.

A mutation-harness edit was committed, pushed to a branch, and survived nine days of gates. It was
removed only incidentally, because the merge happened to prefer origin's copy of that file for an
unrelated reason. **Nothing in this repository could see it**, and the harness that writes these
markers is run routinely -- so the next one is a matter of when, not whether.

WHY THIS IS ONE LEG AND NOT A REGISTER (director's standing instruction: "build the smallest
mechanism that can fail, and prefer doing the work to building the thing that watches the work").
There is no marker vocabulary to maintain, no per-module allowlist and no YAML. One scan, one
shape, and the shape is the one the harness actually emits.

THE DISCRIMINATOR, because a blanket ban on the word is WRONG and would fire on honest prose.
`background/gap_metric.py:1525` legitimately says, in a standalone comment block explaining a
measure:

    # a named mutant, `_MUTANT_displacement_over_whole_population`, and it must fail

and `_MUTANT_*` helper functions inside `tests/` are this project's established way of pinning a
defect shape so a control can be proven able to fail. Both are load-bearing and neither is
residue. What separates them from residue is not the word but the POSITION: harness residue is a
TRAILING comment annotating a line of code it has just rewritten. Prose about a mutant is a
comment on its own line, and a named mutant is an identifier, not a comment at all.

So the leg is: **a trailing comment, on a line that has code before it, whose body opens with
`MUTANT`.** Tokenised rather than grepped, so a `"# MUTANT"` inside a string literal -- which is
what this very test file needs in order to prove the detector can fire -- is not a hit.

WHAT THIS DOES NOT CLAIM. It does not detect a mutation whose author deleted the marker, and it
cannot: an unmarked mutation is indistinguishable from ordinary code, which is the whole reason
the harness marks them. This catches the residue, which is the observed defect.
"""

from __future__ import annotations

import io
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# The same production roots the write-time reuse gate uses (`tools/write_time_gate.CODE_ROOTS`),
# named here rather than imported so this control does not go green by the other one's edit.
CODE_ROOTS = ("background", "company", "interface", "saas", "sim", "simulation", "tools")


def residue_markers(source: str) -> list[tuple[int, str]]:
    """`(line_number, comment)` for every trailing MUTANT marker in `source`. Pure.

    Tokenised, not grepped, for two reasons that are the same reason: a string literal containing
    the marker is not a marker (this module holds one on purpose, and so would any future test of
    the harness itself), and the "is there code before it" question is answered exactly by the
    token's own start column rather than by guessing where a `#` inside a string ends.

    A file that will not tokenise returns `[]` rather than raising. That is deliberately NOT
    fail-closed and it is the one place this control declines to be: an unparseable production
    module is already a red in `tests/architecture/test_a_test_module_imports_a_name_that_exists`
    and everywhere else, and a second, worse-worded failure from here would tell the reader
    nothing the first one did not.
    """
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, SyntaxError, IndentationError, UnicodeDecodeError):
        return []
    lines = source.splitlines()
    hits = []
    for tok in tokens:
        if tok.type != tokenize.COMMENT:
            continue
        row, col = tok.start
        if row - 1 >= len(lines):
            continue
        # TRAILING is the whole discriminator: something other than whitespace precedes the `#`
        # on its own line. A comment on its own line is prose and is left alone.
        if not lines[row - 1][:col].strip():
            continue
        body = tok.string.lstrip("#").strip()
        if body == "MUTANT" or body.startswith("MUTANT ") or body.startswith("MUTANT:"):
            hits.append((row, tok.string.strip()))
    return hits


def _production_modules() -> list[Path]:
    out = []
    for root in CODE_ROOTS:
        base = ROOT / root
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith("tests/") or "/tests/" in rel or path.name.startswith("test_"):
                continue
            out.append(path)
    return sorted(out)


# ── the detector can fire ───────────────────────────────────────────────────────────────────
# ASSERTED BEFORE ANYTHING IS ASSERTED ABOUT THE TREE. A detector that matches nothing passes the
# tree scan below on every possible input, and would read exactly like the mechanism working --
# this project's most expensive recurring control failure. The sample is the defect verbatim.

_THE_DEFECT_VERBATIM = '''
def _maybe_send_daily_digest(any_new_this_cycle):
    try:
        last_sent = LAST_DIGEST_DATE_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        last_sent = None  # never stamped -- ABSENT is not UNREADABLE
    except OSError as e:
        last_sent = None  # MUTANT
    return last_sent
'''


def test_the_detector_fires_on_the_marker_that_actually_shipped():
    """background/sanity_daemon.py:364 as it stood at 78a36a2b5, unedited."""
    hits = residue_markers(_THE_DEFECT_VERBATIM)
    assert len(hits) == 1, (
        "the detector must find exactly the one trailing MUTANT marker in the sample; "
        "got {}".format(hits))
    assert hits[0][1] == "# MUTANT"
    assert "MUTANT" not in _THE_DEFECT_VERBATIM.splitlines()[hits[0][0] - 2], (
        "sanity: the hit must be the OSError line, not the FileNotFoundError line above it")


# ── and it declines on both honest shapes ───────────────────────────────────────────────────

_HONEST_PROSE = '''
# displacement over the WHOLE population -- re-imports the D6 defect. That shape is pinned as
# a named mutant, `_MUTANT_displacement_over_whole_population`, and it must fail
# the prevalence test.
# MUTANT markers are written by the harness at the END of the line it rewrote. This comment is
# prose ABOUT that convention, on its own line, and is not itself residue.
BALANCED = 1


def _MUTANT_ordinal_over_no_skill(truth, belief):
    """A named mutant is an identifier, not a comment."""
    return truth


NOTE = "the harness writes '# MUTANT' at the end of the line it rewrote"
'''


def test_the_detector_declines_on_prose_a_named_mutant_and_a_string():
    """The four shapes that carry the word legitimately, all in one sample.

    THE NEGATIVE LEG EXISTS BECAUSE THE CHEAP VERSION OF THIS CONTROL IS A GREP, and a grep is
    red on `background/gap_metric.py` today -- so the cheap version would have been deleted or
    allowlisted within a day of shipping, and an allowlist is the register this deliberately is
    not. `NOTE` additionally proves the tokenised read: a grep sees a marker inside that string.

    THE FOURTH SHAPE IS HERE BECAUSE ITS ABSENCE MADE THIS TEST A TAUTOLOGY, and the mutation
    harness said so before the file was committed. With only the first three, deleting the
    trailing-position check from `residue_markers` left every test in this module GREEN: none of
    those comments BEGINS with `MUTANT`, so the body-prefix test alone excluded them and the
    discriminator this module's docstring calls "the whole discriminator" was carrying no load
    and could not be proven to. The standalone `# MUTANT markers are written by...` line is a
    comment that would be a hit under a prefix-only reading and must not be one -- so position is
    now the only thing separating it from the defect, which is what was claimed all along.
    """
    assert residue_markers(_HONEST_PROSE) == []


def test_position_and_not_vocabulary_is_what_discriminates():
    """The control over the whole partition: both samples open a comment with the token; one hits.

    Keyed to the PROPERTY rather than to today's answer, and the property is specifically that
    POSITION decides. A future edit that made the detector key on the word or the prefix alone
    reds this even if both samples were rewritten.
    """
    assert "MUTANT" in _THE_DEFECT_VERBATIM and "MUTANT" in _HONEST_PROSE
    # Both samples contain a comment whose body OPENS with the marker word. Without this, the
    # assertion below would hold for a detector that never looks at position at all.
    assert any(ln.strip().startswith("# MUTANT") for ln in _HONEST_PROSE.splitlines())
    assert any(ln.strip().endswith("# MUTANT") for ln in _THE_DEFECT_VERBATIM.splitlines())
    assert residue_markers(_THE_DEFECT_VERBATIM) and not residue_markers(_HONEST_PROSE)


# ── the tree itself ─────────────────────────────────────────────────────────────────────────

def test_no_production_module_carries_a_mutation_marker():
    offenders = []
    for path in _production_modules():
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for row, comment in residue_markers(source):
            offenders.append("{}:{}  {}".format(path.relative_to(ROOT).as_posix(), row, comment))
    assert not offenders, (
        "A mutation-harness marker is committed in production source. This is residue from a "
        "mutation run, not code anybody meant to ship, and the branch it annotates has been "
        "REWRITTEN -- read the original before deleting the comment:\n  " +
        "\n  ".join(offenders))


def test_the_tree_scan_has_a_subject():
    """The scan above passes trivially if it walks nothing, and a path typo would do that."""
    modules = _production_modules()
    assert len(modules) > 100, "expected the production roots to hold modules; got {}".format(
        len(modules))
    assert any(p.as_posix().endswith("background/sanity_daemon.py") for p in modules), (
        "the module the defect shipped in must be inside this control's subject")
