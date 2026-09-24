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

from background import alarm_repetition as sr_alarm
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


def _alarm(root, name, *, mtime, reasked=None):
    """An alarm document with its write time and its attention record set independently.

    The two are what the defect confused, so the fixture has to be able to set them apart.
    """
    import os

    body = "# alarm\n\n## Still live\n\n- **2026-09-01** — still live. Observed again.\n"
    if reasked:
        body += f"\n{sr_alarm.REASK_HEADING}\n\n- **{reasked}** — re-asked: **still_holds**. Asked.\n"
    p = root / name
    p.write_text(body, encoding="utf-8")
    os.utime(p, (mtime, mtime))
    return p


def test_MUTATION_the_loudest_alarm_is_not_served_last(tmp_path):
    """THE CASE, measured in 15e61d604 and again on the live band 2026-09-24.

    An alarm document is rewritten by its own machinery on every firing, so the within-band
    term `mtime` measured how recently the alarm WROTE. Ascending, that served the loudest
    condition LAST: `DEADMAN_WORKTREE_UNDECLARED` -- 298 repeats over 8 days, 10 members --
    sat 7th of 10 BECAUSE it fires most, and every still-live line it earned pushed it further
    down. Anti-correlated, so inverted rather than merely arbitrary.

    LOUD is the one filed FIRST and written LAST: longest neglected, most recently annotated.
    Under the old term it came second; under an attention term it comes first.
    """
    loud = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_LOUD_2026-09-01.md",
                  mtime=2_000_000_000)
    quiet = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_QUIET_2026-09-20.md",
                   mtime=1_000_000_000)
    queue = [i.name for i in sr.work_queue(tmp_path)]
    assert queue == [loud.name, quiet.name], (
        "the alarm nobody has looked at for longest must draw first, however recently its own "
        "machinery annotated it")


def test_MUTATION_a_reask_is_attention_and_moves_an_alarm_down_the_band(tmp_path):
    """The channel that makes the term about ATTENTION rather than about filing dates.

    Both documents are equally old and equally quiet on disk. The only difference is that
    somebody re-asked one of them yesterday. A term reading only the filing date -- which is
    what `unattended_since`'s fallback gives when the re-ask section is absent, and which is
    the whole live population today -- would leave `OLDER` first and pass this test for the
    wrong reason. It must not: a document somebody looked at is not the one owed attention.
    """
    older = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_AAA_OLDER_2026-09-01.md",
                   mtime=1_000_000_000, reasked="2026-09-23")
    newer = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_ZZZ_NEWER_2026-09-10.md",
                   mtime=1_000_000_000)
    queue = [i.name for i in sr.work_queue(tmp_path)]
    assert queue == [newer.name, older.name], (
        "a re-asked alarm has been looked at; the one nobody asked about is the stale one")


def test_an_alarm_the_term_cannot_price_goes_to_the_TOP_of_its_band(tmp_path):
    """FAIL-OPEN, and in the direction that gets the document read.

    A name carrying no filing date and a body carrying no re-ask says nothing about when it was
    last looked at. Burying it is how a document stops being read at all, so it goes first --
    and NOT to mtime, which would restore the inversion for exactly the documents nothing else
    could describe.
    """
    undated = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_NO_DATE_IN_THIS_NAME.md",
                     mtime=2_000_000_000)
    dated = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_AAA_DATED_2026-09-01.md",
                   mtime=1_000_000_000)
    queue = [i.name for i in sr.work_queue(tmp_path)]
    assert queue == [undated.name, dated.name]


def test_MUTATION_when_the_attention_term_cannot_be_REACHED_the_band_does_not_fall_back_to_mtime(
        tmp_path, monkeypatch):
    """The fail-open branch, driven rather than assumed.

    Written because mutating that branch to fall through to mtime went GREEN: no test reached
    it, so the fail-open DIRECTION was uncontrolled while three tests watched the happy path.
    A missing test, established, not an equivalence.

    Both alarms here are unreadable to the term, so both price at the top of the band and the
    NAME orders them -- which is the only job the name ever had. The mtimes are arranged to
    disagree with the names, so a fallback to mtime returns the other order and this reds.
    """
    def _refuse(*a, **k):
        raise RuntimeError("the term is unavailable")

    monkeypatch.setattr(sr_alarm, "unattended_since", _refuse)
    zzz = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_ZZZ_2026-09-01.md",
                 mtime=1_000_000_000)
    aaa = _alarm(tmp_path, "WORKER_FINDING_REPEATING_ALARM_AAA_2026-09-20.md",
                 mtime=2_000_000_000)
    assert [i.name for i in sr.work_queue(tmp_path)] == [aaa.name, zzz.name], (
        "an alarm the term cannot price goes to the top of its band on its name, never to the "
        "mtime order this replaced")


def test_MUTATION_the_attention_term_is_scoped_to_the_alarms(tmp_path):
    """The other half of the partition, and it can fail.

    `_within_band_key` is one function over every kind, so a change written for the alarms can
    silently re-order the bands that were never wrong. Every other kind still serves by age,
    including a FINDING whose filename date disagrees with its mtime -- which is the shape that
    would break if the attention term leaked out of its band.
    """
    import os

    old_write = tmp_path / "SEAT_FINDING_NAMED_LATE_2026-09-20.md"
    new_write = tmp_path / "SEAT_FINDING_NAMED_EARLY_2026-09-01.md"
    for p, when in ((old_write, 1_000_000_000), (new_write, 2_000_000_000)):
        p.write_text("# finding\n", encoding="utf-8")
        os.utime(p, (when, when))
    assert [i.name for i in sr.work_queue(tmp_path)] == [old_write.name, new_write.name]


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
    # KEYED TO THE FLOORS AND NOT TO TWO. This asserted `== 2` and went red on 2026-09-03 when
    # `records/` became the third floored room -- i.e. it failed because the control got WIDER,
    # which is the pinned-to-today's-answer shape this file's own subject exists to catch. Every
    # floored room must be loud, however many there are.
    for room in sr.POPULATION_FLOORS:
        (tmp_path / room).mkdir()
    violations = sr.population_floor_violations(tmp_path)
    assert len(violations) == len(sr.POPULATION_FLOORS)
    assert all("POPULATION FLOOR" in v for v in violations)


def test_MUTATION_a_room_that_VANISHES_is_LOUD_too(tmp_path):
    """The failure a floor most easily misses: not a room that emptied, but one that was
    renamed. `iterdir()` on a missing directory raises or returns nothing depending on how it
    is written, and 'returns nothing' is silence."""
    out = sr.population_floor_violations(tmp_path)
    assert len(out) == len(sr.POPULATION_FLOORS) and all("ROOM MISSING" in v for v in out)


def test_a_full_room_passes(tmp_path):
    for room, n in sr.POPULATION_FLOORS.items():
        (tmp_path / room).mkdir()
        for i in range(n):
            _write(tmp_path / room, f"CLASS_X{i}_2026-08-12.md")
    assert sr.population_floor_violations(tmp_path) == []


def test_MUTATION_a_room_ABOVE_its_literal_floor_that_LOST_a_document_is_LOUD(tmp_path):
    """The defect the literal floor cannot see, and the reason `room_shrinkage_violations` exists.

    `records/` was floored at 38 on 2026-09-03 and held 377 by 2026-09-23, so it had to lose 340
    documents before `population_floor_violations` said a word. Three went missing that day -- two
    of them pre-registrations, the artefact class whose whole value is that it cannot be revised
    after the answer is known -- and `--check` printed `Population floors: 0 violation(s)`.

    BOTH LEGS ON ONE TREE STATE, because a control that flagged EVERY room would pass a
    one-leg version of this: the full room must be silent in the same call that the robbed room is
    loud. That is this file's own standing shape (`assert plan["restart"] and plan["defer"]`).

    MUTATION (must fire): key the new leg to `POPULATION_FLOORS[dirname]` instead of to HEAD --
    i.e. make it a second copy of the literal floor. The robbed room is still 40 documents clear of
    38, so it goes silent and this test reds on the `gone` assertion.
    """
    head_names = {}
    for room in sr.POPULATION_FLOORS:
        (tmp_path / room).mkdir()
        # Deliberately WELL ABOVE every literal floor, which is the whole point: the loss below
        # is invisible to a bound written as a number on the day it was true.
        names = {f"CLASS_X{i}_2026-08-12.md" for i in range(max(sr.POPULATION_FLOORS.values()) + 3)}
        head_names[room] = names
        for name in names:
            _write(tmp_path / room, name)

    assert sr.population_floor_violations(tmp_path) == []
    assert sr.room_shrinkage_violations(tmp_path, head_names=head_names) == []

    robbed = sr.RECORDS_DIRNAME
    stolen = sorted(head_names[robbed])[0]
    (tmp_path / robbed / stolen).unlink()

    # The literal floor is still silent -- the room is far above 38. That is the defect, asserted.
    assert sr.population_floor_violations(tmp_path) == []

    out = sr.room_shrinkage_violations(tmp_path, head_names=head_names)
    assert len(out) == 1, f"exactly the robbed room must speak, not every room: {out}"
    assert robbed in out[0] and "ROOM SHRINKING" in out[0]
    assert stolen in out[0], f"the message must NAME what went missing, not just count it: {out[0]}"


def test_MUTATION_an_EMPTY_read_of_a_floored_room_is_a_VIOLATION_and_not_a_pass(tmp_path):
    """The fail-open leg. If the path filter matches nothing, every room reads zero and every
    room is therefore 'not shrinking' -- a control whose own filter emptied its evidence, which
    is a shape this repo has paid for repeatedly.

    MUTATION (must fire): `if not at_head: continue` instead of appending. Both asserts below go
    red, because an unreadable room and a healthy one become indistinguishable.
    """
    for room in sr.POPULATION_FLOORS:
        (tmp_path / room).mkdir()
    out = sr.room_shrinkage_violations(tmp_path, head_names={r: set() for r in sr.POPULATION_FLOORS})
    assert len(out) == len(sr.POPULATION_FLOORS)
    assert all("SHRINKAGE UNREADABLE" in v for v in out)


def test_MUTATION_an_UNREADABLE_git_is_a_VIOLATION_and_not_a_pass(tmp_path, monkeypatch):
    """`head_room_documents` failing must not read as 'no room shrank'. The sibling
    `sediment_violations` has this exact leg; without it a machine with no git is fully green.

    MUTATION (must fire): `return []` on the unreadable branch.
    """
    import subprocess

    def _boom(*a, **k):
        raise OSError("no git here")

    monkeypatch.setattr(subprocess, "run", _boom)
    assert sr.head_room_documents(tmp_path)["readable"] is False
    out = sr.room_shrinkage_violations(tmp_path)
    assert len(out) == 1 and "SHRINKAGE UNREADABLE" in out[0]


def test_the_check_EXITS_NONZERO_on_room_shrinkage_too():
    """A measurement printed and not gated is a receipt.

    MUTATION (must fire): drop `room_shrinkage_violations(args.root)` from `main`.
    """
    import inspect

    assert "room_shrinkage_violations(args.root)" in " ".join(inspect.getsource(sr.main).split())


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

    TODAY'S CONSOLE TRANSCRIPT IS NOT STRANDED, IT IS OPEN (carve-out added 2026-09-01). The
    transcript writer APPENDS to `DIRECTOR_CONSOLE_<today>.md` in the root all day. Migrating it
    while it is still being written does not archive a record, it freezes a snapshot — and that
    is not hypothetical: the room's copy of `DIRECTOR_CONSOLE_2026-08-30.md` was found this
    morning holding **1 turn of a conversation that has 8**, with the fuller copy sitting in the
    root, so the migration had run mid-conversation and the room held the truncated half. The
    director's ruling on reservation was in the part that never reached the room.

    Without the carve-out this control reds every single day, for a state that is correct, until
    the day rolls over — and a control that is red on correct code every morning is one that gets
    deleted rather than fixed. It is keyed to the DATE IN THE NAME and to today's date, so it
    exempts exactly one file and only while that file can still grow.
    """
    import datetime as dt

    root = sr.DEFAULT_STAGING_ROOT
    open_today = f"DIRECTOR_CONSOLE_{dt.date.today().isoformat()}.md"
    stranded = []
    for p in sorted(root.glob("*.md")):
        room = sr.room_for(sr.kind_of(p.name))
        if room is None or p.name == open_today:
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


def test_an_archive_twin_NEVER_holds_turns_its_record_room_copy_lacks():
    """DEFECT: the thinner copy of a console transcript wins, and the director's words go with it.

    THE RECORD ROOM IS `console/`. That is not a preference, it is a decision already taken and
    already written down: on 2026-09-07 a backfill recovered eight turns of 30 August that no room
    held, hit the gate's two-rooms condition, and resolved it -- *"Consolidated into `console/`,
    and the root copy's deletion staged so the move completes rather than sitting half-staged"*
    (`docs/staging/console/SEAT_REPLY_2026-09-07.md`). `done/` is where a transcript rests after
    that; it is never the copy that arbitrates what was said.

    WHY THIS IS A TEST AND NOT A THIRD PARAGRAPH OF PROSE. The decision has now been re-asked
    three times, because the state it produces -- a document present in `console/` whose name also
    sits in `done/` -- reads from outside as a half-finished move whose deletion completes it:

        2026-09-07  the gate flagged the two-rooms condition; consolidated into `console/`.
        2026-09-22  an archival pass was handed the same file and HELD THE DELETION BACK, having
                    found 243 of 279 lines absent from the `done/` copy (32,798B -> 2,505B),
                    among them the director's verbatim ruling on suspending I&C.
        2026-09-23  a delivery item named it again as *"source side of a move whose done/ copy is
                    ALREADY at HEAD, so these are half-landed and the deletion completes them"*.

    Each of the first two decisions was correct, recorded in `docs/staging/`, and bought exactly
    nothing, because a finding cannot refuse a commit. Landing that deletion would have left the
    2,505-byte one-turn capture as the only surviving copy of a nine-turn day.

    KEYED TO THE PROPERTY AND NOT TO TODAY'S ANSWER. The subject is the SUPERSET RELATION between
    the two rooms' copies, not the byte counts either of them happens to have today: the twin may
    grow, the record copy may grow, and this stays green while `console/` holds every turn `done/`
    does. It reds the moment that inverts -- which is what both a deletion and a re-thinning of
    the record copy look like from here.

    THE NON-EMPTY GUARD IS THE OTHER HALF, and it is this module's own documented fail-open: a
    comparison whose filter matches no pair passes identically whether the rooms agree or the
    record copy is gone. If the last pair is ever legitimately retired, this reds and names why,
    so retiring it is a decision someone takes rather than one that happens quietly.
    """
    import re

    root = sr.DEFAULT_STAGING_ROOT
    console, archive = root / sr.CONSOLE_DIRNAME, root / sr.ARCHIVE_DIRNAME
    def turns(p):
        return set(re.findall(r"^### (\S+)$", p.read_text(), flags=re.M))

    pairs = [(p, archive / p.name) for p in sorted(console.glob("DIRECTOR_CONSOLE_*.md"))
             if (archive / p.name).is_file()]
    assert pairs, (
        "no console transcript is held in BOTH rooms, so the superset comparison below ran over "
        "nothing and passed for that reason alone. This is the fail-open this file names "
        "elsewhere ('an empty read is not a pass'). If the last twin was retired deliberately, "
        "re-key this control to the decision that retired it; if it was not, a record-room copy "
        "has gone missing and that is the loss this test exists to refuse.")

    thinner = [f"{c.name}: {len(missing)} turn(s) held ONLY by the done/ twin ({sorted(missing)})"
               for c, a in pairs if (missing := turns(a) - turns(c))]
    assert thinner == [], (
        "the archive twin holds turns the record room's copy does not, so the thinner copy is the "
        "one a reader arbitrating this day would find authoritative: " + "; ".join(thinner))


def test_a_finding_about_a_preregistration_is_a_finding():
    """DEFECT: a live finding is filed into the room that means "this was never work".

    `kind_of` tested `"PREREG" in name.upper()` — a substring, anywhere in the name — ahead of
    the finding rule, and the ordering is right for the reason its own comment gives:
    `SEAT_PREREGISTRATION_…` begins with a prefix that classifies as work. But the SUBSTRING
    reached further than the ordering needed. A finding WHOSE SUBJECT IS a pre-registration
    carries the token deep in its name and classified as one, so it routed to `records/` —
    whose entire claim is THIS IS NOT WORK AND NEVER WAS, and which has no exit: nothing
    archives out of it, so nothing ever revisits what is filed there.

    Two such documents existed in the tree on 2026-09-03, out of 7,414. Both are real defects
    somebody has to act on:
      * `SEAT_FINDING_A_PREREGISTRATION_FIXED_AN_OBSERVATION_OF_MUTABLE_STATE…`
      * `WORKER_FINDING_A_PREREGISTERED_WITHDRAWAL_TRIGGER_KEYED_TO_TWO_NULL_VERDICTS…`

    R15 — the mutations, each run and reverted:
      * restore the bare `in name.upper()` substring test -> the first two cases red.
      * widen the kind position from the first two underscore-segments to the first three ->
        `SEAT_FINDING_A_PREREGISTRATION_…` reds, because `A` then `PREREGISTRATION` puts the
        token back in scope.
      * narrow it to the first segment only -> every real `SEAT_PREREGISTRATION_…` reds, which
        is the other direction and is the failure the original ordering existed to prevent.
    """
    # The kind position — the document declaring its own kind — stays a pre-registration.
    for name in (
        "SEAT_PREREGISTRATION_WHETHER_THE_YEAR_ANCHOR_RE_EXPRESSES_THE_MECHANISM_2026-09-03.md",
        "WORKER_PREREGISTRATION_WHAT_THE_BALANCED_GAS_LEVEL_CEILING_MUST_SHOW_2026-09-03.md",
        "DIRECTOR_PREREGISTRATION_ANYTHING_2026-09-03.md",
    ):
        assert sr.kind_of(name) == sr.KIND_PREREGISTRATION, (
            "{} is a pre-registration and no longer classifies as one -- the ordering that keeps "
            "records out of the work channel has been narrowed too far".format(name))

    # The token describing the SUBJECT does not.
    for name in (
        "SEAT_FINDING_A_PREREGISTRATION_FIXED_AN_OBSERVATION_OF_MUTABLE_STATE_AND_IT_WAS_FALSE"
        "_BEFORE_THE_TURN_READ_IT_2026-09-03.md",
        "WORKER_FINDING_A_PREREGISTERED_WITHDRAWAL_TRIGGER_KEYED_TO_TWO_NULL_VERDICTS_FIRED"
        "_2026-08-29.md",
    ):
        assert sr.kind_of(name) == sr.KIND_FINDING, (
            "{} is a FINDING about a pre-registration and classifies as a pre-registration, so "
            "it files into records/ -- out of the queue, undrawable, and recorded as something "
            "that was never work".format(name))
        assert sr.room_for(sr.kind_of(name)) is None, (
            "a finding is work and belongs in the staging ROOT, not in a room")


# --- The record agreeing with the disk (2026-09-19) ---------------------------------------------
#
# 98 archive moves existed on disk and in no commit. `root_flow()` reads from git ON PURPOSE so a
# disk-only archival cannot read as drained -- and that same correct choice means it counts a
# disposition that HAPPENED as one that did not, then recommends a change to filing. The defect
# each test below drives is that misattribution, in both directions.


def _plant(root, *, in_root=(), archived=(), vanished=()):
    """A staging root on disk. Returns the HEAD name set the record would hold.

    HEAD is injected rather than committed: the branch where a document is absent from disk is the
    RARE one, and a test that had to build a git repository to reach it would reach it once.
    """
    (root / "done").mkdir(parents=True, exist_ok=True)
    for name in in_root:
        (root / name).write_text("still in the queue\n", encoding="utf-8")
    for name in archived:
        (root / "done" / name).write_text("dispositioned\n", encoding="utf-8")
    return set(in_root) | set(archived) | set(vanished)


def test_an_archival_that_reached_no_commit_is_named_as_a_landing_and_not_as_a_filing_problem(tmp_path):
    """The defect: an uncommitted archival reported as undispositioned work.

    Mutations that must red this:
      * drop the `elsewhere` lookup and put every absent document in one bucket -> the archived
        count goes to 0 and the vanished count to 2, so the remedy named is loss and not a landing.
      * read the root from disk instead of HEAD (`root.glob("*.md")`) -> nothing is ever absent,
        `archived` is always empty, and this control can never fire at all.
    """
    head = _plant(tmp_path, in_root=["A_2026-09-01.md"],
                  archived=["B_2026-09-01.md", "C_2026-09-01.md"])
    got = sr.stranded_dispositions(tmp_path, head_names=head)

    assert got["readable"], "a readable root reported unreadable"
    assert got["archived"] == ["B_2026-09-01.md", "C_2026-09-01.md"], (
        "an archive move present in a sub-room on disk and still in the root at HEAD is the "
        "uncommitted-archival case and must be named as one")
    assert got["vanished"] == [], (
        "a document with a copy in done/ is archived, not lost -- calling it loss sends the "
        "reader looking for bytes that are right there")

    violations = sr.stranded_disposition_violations(tmp_path, head_names=head)
    assert len(violations) == 1 and violations[0].startswith("STRANDED ARCHIVAL:"), violations
    assert "a landing" in violations[0], (
        "the violation must name the remedy that works -- committing both sides of the move -- "
        "because the sediment alarm's standing advice is about filing and would be wrong here")


def test_a_document_gone_from_the_root_with_no_copy_anywhere_is_not_reported_as_an_archival(tmp_path):
    """The defect: possible LOSS reported as progress.

    The two buckets have opposite remedies, so collapsing them is the failure either way round.
    Mutation: return a single list -> the assertion that `archived` is empty here reds.
    """
    head = _plant(tmp_path, in_root=["A_2026-09-01.md"], vanished=["GONE_2026-09-01.md"])
    got = sr.stranded_dispositions(tmp_path, head_names=head)

    assert got["vanished"] == ["GONE_2026-09-01.md"], (
        "a root document at HEAD with no copy under docs/staging/ left no trace on disk, and "
        "reporting it as archived would file possible loss as a discharge")
    assert got["archived"] == [], "there is no copy, so nothing here was archived"

    violations = sr.stranded_disposition_violations(tmp_path, head_names=head)
    assert len(violations) == 1 and violations[0].startswith("VANISHED FROM THE ROOT:"), violations


def test_both_stranded_buckets_are_reachable_and_the_clean_case_is_silent(tmp_path):
    """ONE control over the WHOLE partition, because a guard that reports NOTHING passes every
    per-branch test. This is the assertion that a mutation making the function return `{}` — or
    making the absence test `if not (root / name).exists(): continue` — cannot survive.
    """
    head = _plant(tmp_path, in_root=["KEPT_2026-09-01.md"],
                  archived=["MOVED_2026-09-01.md"], vanished=["GONE_2026-09-01.md"])
    got = sr.stranded_dispositions(tmp_path, head_names=head)

    assert got["archived"] and got["vanished"], (
        "both stranded branches must be reachable in one root -- a control that reports neither "
        "passes every test written per branch while seeing nothing")
    assert "KEPT_2026-09-01.md" not in got["archived"] + got["vanished"], (
        "a document in the root at HEAD and on disk is not stranded, and flagging it would make "
        "this control fire on every healthy queue and therefore be turned off")

    clean = _plant(tmp_path / "clean", in_root=["ONLY_2026-09-01.md"])
    assert sr.stranded_disposition_violations(tmp_path / "clean", head_names=clean) == [], (
        "a root whose record matches its disk must be SILENT, or the violation carries no "
        "information")


def test_the_unreadable_record_is_a_violation_and_never_a_pass(tmp_path, monkeypatch):
    """"I could not tell" must not wear a pass's colour.

    The git read is monkeypatched rather than injected, so this drives the REAL unreadable branch
    of `stranded_dispositions` and not a hand-built dict. Mutation: return `[]` when the record
    cannot be read -> reds here. That fail-open has shipped in this repository more than once.
    """
    monkeypatch.setattr(sr, "head_root_documents",
                        lambda root=None: {"readable": False, "why": "git could not be asked"})
    got = sr.stranded_dispositions(tmp_path)
    assert got["readable"] is False and got["why"] == "git could not be asked"

    out = sr.stranded_disposition_violations(tmp_path)
    assert out and out[0].startswith("STRANDED DISPOSITIONS UNREADABLE:"), out
    assert "not evidence that it does" in out[0], (
        "an unreadable probe must say that silence is not agreement")
