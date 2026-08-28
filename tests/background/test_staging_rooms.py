#!/usr/bin/env python3
"""R15 proof for the staging room taxonomy (director, 2026-08-28, having read all 49):

    "The draw takes files in alphabetical filename order, and that is the least of it ... Four
     different kinds of thing share one folder and only one is work. And not one file carries a
     lane, an epoch or an atom id, so the queue is disconnected from the map entirely."

The mutation that matters here is NOT "does it sort" -- a sort that reads correctly and drops
one kind of file would be a queue that never serves that kind, and this project's own standing
lesson is that a control keyed to a structure that moved goes QUIET rather than loud. So every
test below drives one of the two directions that lose work:

  1. A real ask classified as noise, or dropped from the queue entirely.
  2. A room emptying underneath a reader, with nothing said.

The filenames are the real ones from `docs/staging/` on the morning of 2026-08-28.
"""
from __future__ import annotations

import pytest

from background import staging_rooms as sr

# Verbatim from the folder the director read.
REFERENCE = "CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md"
CONSOLE = "DIRECTOR_CONSOLE_2026-08-27.md"
GUIDANCE = "DIRECTOR_GUIDANCE_THE_WORLD_MUST_PRESS_2026-08-28.md"
ALARM = "WORKER_FINDING_REPEATING_ALARM_RUN_BOTH_INSTRUMENTS_AT_FULL_WINDOW_WAS_CLAIMED_AND_2026-08-27.md"
FINDING = "WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25.md"
DOORBELL = "run_complete_20260828T054500Z.md"
FROM_RICH = "from_rich_20260828T064500Z.md"


# ---------------------------------------------------------------------------
# KIND
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,kind", [
    (REFERENCE, sr.KIND_REFERENCE),
    (CONSOLE, sr.KIND_CONSOLE),
    (GUIDANCE, sr.KIND_DIRECTIVE),
    (ALARM, sr.KIND_ALARM),
    (FINDING, sr.KIND_FINDING),
    (DOORBELL, sr.KIND_DOORBELL),
    (FROM_RICH, sr.KIND_FROM_RICH),
])
def test_the_real_filenames_classify(name, kind):
    assert sr.kind_of(name) == kind


def test_MUTATION_a_console_transcript_is_not_a_directive():
    """The order of the prefix tests is the whole of this. `DIRECTOR_CONSOLE_` and
    `DIRECTOR_RULING_` share eight letters, and a taxonomy that tested the shorter prefix
    first would file 76KB of archived transcript at rank 2 of the work queue -- which is
    exactly the state the director found."""
    assert sr.kind_of(CONSOLE) != sr.KIND_DIRECTIVE
    assert sr.kind_of("DIRECTOR_RULING_SOMETHING_2026-08-01.md") == sr.KIND_DIRECTIVE


def test_MUTATION_an_unrecognised_file_is_WORK_and_outranks_the_alarms():
    """The fail-safe direction. The costly misclassification for an ORDERING module is a
    person's ask filed as noise; for a MOVING module it is the reverse, which is why
    `staging_archive_policy` fails the other way and says so."""
    assert sr.kind_of("SOMETHING_NOBODY_ANTICIPATED.md") == sr.KIND_UNKNOWN
    assert sr.ORDER[sr.KIND_UNKNOWN] < sr.ORDER[sr.KIND_ALARM]


# ---------------------------------------------------------------------------
# ORDER — D1
# ---------------------------------------------------------------------------

def _write(root, name, text="**Severity:** LATENT · **Lane:** H_harness\n\n# x\n"):
    p = root / name
    p.write_text(text, encoding="utf-8")
    return p


def test_MUTATION_the_directors_guidance_is_not_behind_six_reference_documents(tmp_path):
    """THE CASE. Alphabetically `CLASS_` < `DIRECTOR_` < `WORKER_`, so the six documents that
    can never drain sorted ahead of the guidance the director wrote that morning."""
    for name in (REFERENCE, CONSOLE, GUIDANCE, ALARM, FINDING):
        _write(tmp_path, name)
    queue = [i.name for i in sr.work_queue(tmp_path)]
    assert queue[0] == GUIDANCE, f"the guidance is at position {queue.index(GUIDANCE) + 1}"
    assert REFERENCE not in queue and CONSOLE not in queue


def test_MUTATION_an_alarm_never_outranks_a_persons_ask(tmp_path):
    """On 2026-08-25 eighteen copies of one alarm took the head of the draw and pushed three
    self-drawable mints to positions 43-46 of 48, where no bounded session ever reached them."""
    for i in range(18):
        _write(tmp_path, f"WORKER_FINDING_REPEATING_ALARM_A{i:02d}_2026-08-25.md")
    _write(tmp_path, GUIDANCE)
    assert sr.work_queue(tmp_path)[0].name == GUIDANCE


def test_within_a_rank_the_OLDEST_is_served_first(tmp_path):
    """A queue serves by age. The filename only ever breaks a tie between two files of the
    same kind written in the same second."""
    import os

    a = _write(tmp_path, "DIRECTOR_RULING_ZEBRA_2026-08-01.md")
    b = _write(tmp_path, "DIRECTOR_RULING_ALPHA_2026-08-27.md")
    os.utime(a, (1_000_000, 1_000_000))
    os.utime(b, (2_000_000, 2_000_000))
    assert [i.name for i in sr.work_queue(tmp_path)] == [a.name, b.name]


def test_MUTATION_a_doorbell_is_not_work(tmp_path):
    """R3_WORK_GRANTING_REDESIGN, 2026-07-12: a run_complete marker in the work list
    short-circuited find_work() before it ever reached the map draw, every ~2 minutes, while
    ~35 open atoms sat idle. That exclusion must survive this rewrite."""
    _write(tmp_path, DOORBELL)
    assert sr.work_queue(tmp_path) == []


def test_a_subdirectory_is_never_read_as_a_queue_item(tmp_path):
    (tmp_path / sr.ARCHIVE_DIRNAME).mkdir()
    _write(tmp_path / sr.ARCHIVE_DIRNAME, FINDING)
    assert sr.work_queue(tmp_path) == []


# ---------------------------------------------------------------------------
# THE CHAIN — D4 / the director's P8
# ---------------------------------------------------------------------------

def test_the_chain_parses_off_the_header_finding_severity_already_owns(tmp_path):
    p = _write(tmp_path, FINDING,
               "**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** 3 · "
               "**Atom:** `EP1_clv_three_horizon`\n\n# x\n")
    chain = sr.chain_of(p)
    assert chain.lane == "B_commercial"
    assert chain.epoch == 3
    assert chain.atom == "EP1_clv_three_horizon"
    assert chain.is_chained


def test_MUTATION_a_lane_that_is_not_a_lane_is_not_a_lane(tmp_path):
    """Fail-closed. A header naming `H_harnes` must read as MISSING a lane, not as carrying
    one -- a chain whose link points nowhere is worse than a visibly absent one."""
    p = _write(tmp_path, FINDING,
               "**Severity:** LATENT · **Lane:** H_harnes · **Epoch:** 3 · **Atom:** `x`\n\n# x\n")
    assert sr.chain_of(p).lane is None
    assert not sr.chain_of(p).is_chained


def test_UNMINTED_is_a_chain_and_a_MISSING_atom_is_not(tmp_path):
    """The distinction is the whole reason the field exists. An explicit `unminted` means
    somebody connected this item to the map and the answer was 'not yet'; an ABSENT atom means
    nobody looked. Only the second is P8. A control that could not tell them apart would
    either nag for ever or go quiet."""
    yes = _write(tmp_path, "WORKER_FINDING_A_2026-08-28.md",
                 f"**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · "
                 f"**Atom:** `{sr.UNMINTED}`\n\n# x\n")
    no = _write(tmp_path, "WORKER_FINDING_B_2026-08-28.md",
                "**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3\n\n# x\n")
    assert sr.chain_of(yes).is_chained
    assert not sr.chain_of(no).is_chained
    assert sr.chain_of(no).missing == ("atom",)
    assert [c.path.name for c in sr.unchained(tmp_path)] == [no.name]


@pytest.mark.skipif(__import__("os").geteuid() == 0, reason="root can read a 000 file")
def test_MUTATION_an_UNREADABLE_document_is_not_reported_as_unchained(tmp_path):
    """A control refusing on input it could not READ was found three times in one day, and its
    blast radius is every commit. Unreadable is EXCLUDED, never reported as a gap: claiming a
    file is missing its lane without having opened it is a claim about contents nobody read.

    THE FILE IS REALLY MADE UNREADABLE rather than `Path.read_text` monkeypatched, because
    patching it globally also blinds `conftest`'s own ghost-pusher check, which reads git
    state through the same call and correctly failed the run when it could not. A mutation
    test that disables the harness's controls to reach its subject is not evidence about the
    subject."""
    p = _write(tmp_path, FINDING, "**Severity:** LATENT · **Lane:** H_harness\n\n# x\n")
    p.chmod(0o000)
    try:
        assert sr.unchained(tmp_path) == []
        assert not sr.chain_of(p).is_chained, "an unreadable file read as chained"
    finally:
        p.chmod(0o644)


def test_stamping_EXTENDS_an_existing_header_and_never_overwrites_it(tmp_path):
    """The severity a human set and the lane a class guard already trusts must survive."""
    out = sr.stamp_chain("**Severity:** BLOCKING · **Lane:** B_commercial\n\n# x\n",
                         lane="H_harness", epoch=3, atom="A1")
    assert "BLOCKING" in out and "B_commercial" in out and "H_harness" not in out
    assert "**Epoch:** 3" in out and "**Atom:** `A1`" in out


def test_stamping_is_IDEMPOTENT(tmp_path):
    once = sr.stamp_chain("# x\n", lane="H_harness", epoch=3, atom="A1")
    twice = sr.stamp_chain(once, lane="H_harness", epoch=9, atom="ZZ")
    assert twice.count("**Epoch:**") == 1
    assert "**Epoch:** 3" in twice, "a re-stamp overwrote a chain somebody had already set"


# ---------------------------------------------------------------------------
# THE ROOMS, AND THE FLOOR UNDER THEM
# ---------------------------------------------------------------------------

def test_MUTATION_a_class_register_is_found_in_EITHER_room(tmp_path):
    """The reason there is a fallback at all. Moving a file is how a control goes quiet: it
    keeps reading the old location, finds nothing, and reports nothing wrong."""
    _write(tmp_path, REFERENCE)
    assert sr.class_document_path(REFERENCE, tmp_path).name == REFERENCE
    assert sr.class_document_path(REFERENCE, tmp_path).parent == tmp_path

    (tmp_path / sr.REFERENCE_DIRNAME).mkdir()
    _write(tmp_path / sr.REFERENCE_DIRNAME, REFERENCE)
    assert sr.class_document_path(REFERENCE, tmp_path).parent.name == sr.REFERENCE_DIRNAME


def test_a_half_finished_move_reads_as_ONE_document_not_two(tmp_path):
    _write(tmp_path, REFERENCE)
    (tmp_path / sr.REFERENCE_DIRNAME).mkdir()
    _write(tmp_path / sr.REFERENCE_DIRNAME, REFERENCE)
    assert len(sr.reference_documents(tmp_path)) == 1


def test_MUTATION_a_room_that_EMPTIES_is_LOUD(tmp_path):
    """The population floor. Five emptied subjects were found in one day by floors of this
    shape: without one, a scanner reports 'nothing found' identically whether its subject is
    clean or gone."""
    (tmp_path / sr.REFERENCE_DIRNAME).mkdir()
    (tmp_path / sr.CONSOLE_DIRNAME).mkdir()
    violations = sr.population_floor_violations(tmp_path)
    assert len(violations) == 2
    assert all("POPULATION FLOOR" in v for v in violations)


def test_MUTATION_a_room_that_VANISHES_is_LOUD_too(tmp_path):
    """The failure a floor most easily misses: not a room that emptied, but one that was
    renamed. `iterdir()` on a missing directory raises or returns nothing depending on how it
    is written, and 'returns nothing' is silence."""
    out = sr.population_floor_violations(tmp_path)
    assert len(out) == 2 and all("ROOM MISSING" in v for v in out)


def test_a_full_room_passes(tmp_path):
    for room, n in sr.POPULATION_FLOORS.items():
        (tmp_path / room).mkdir()
        for i in range(n):
            _write(tmp_path / room, f"CLASS_X{i}_2026-08-12.md")
    assert sr.population_floor_violations(tmp_path) == []


# ---------------------------------------------------------------------------
# THE LIVE TREE
# ---------------------------------------------------------------------------

def test_no_LIVE_reference_or_console_document_exists_ONLY_in_the_root():
    """The migration is done when no not-work document is stranded in the queue.

    THE ASSERTION IS "NOT ONLY IN THE ROOT", NOT "ABSENT FROM THE ROOT", and the difference is
    a real property of this repo rather than a softening. `tools/pre_commit_test_gate.py`
    re-materialises tracked-but-deleted paths from HEAD into the working tree while it runs, so
    during the very commit that lands a room move, every moved file is briefly present in BOTH
    rooms — which is what `background/staging_two_rooms_repair.py` observed and could not
    attribute ("consistent with something restoring a tracked-but-deleted path from HEAD... it
    stopped reappearing once its deletion was COMMITTED"). A test asserting absence from the
    root can therefore NEVER pass inside the commit that makes it true: the first version of
    this test failed for exactly that reason, twice.

    What actually matters is that a reference or console document is never STRANDED — present
    in the queue with no copy in its room, which is the state where a reader sees it as work.
    The two-rooms DUPLICATE is a different condition with a different owner:
    `finding_classes --check` refuses the commit on it, and `staging_two_rooms_repair` resolves
    it. Two controls, two conditions, no overlap.
    """
    root = sr.DEFAULT_STAGING_ROOT
    stranded = []
    for p in sorted(root.glob("*.md")):
        room = sr.room_for(sr.kind_of(p.name))
        if room is None:
            continue
        if not (root / room / p.name).exists():
            stranded.append(p.name)
    assert stranded == [], (
        f"not-work documents sitting in the queue with no copy in their room: {stranded}"
    )


def test_the_LIVE_rooms_are_populated():
    assert sr.population_floor_violations() == []


def test_the_LIVE_queue_carries_no_reference_or_console_WORK():
    """The other half, and the one the draw actually reads: whatever is on disk, `work_queue()`
    must never offer a CLASS register or a console transcript as work. This holds during the
    gate's re-materialisation too, because the classification is by NAME and does not depend on
    which room the file is sitting in."""
    kinds = {i.kind for i in sr.work_queue()}
    assert sr.KIND_REFERENCE not in kinds and sr.KIND_CONSOLE not in kinds
