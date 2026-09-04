"""Three kinds of NOT-WORK were in the work channel, and the folder had no alarm on itself.

THE STATE, 2026-09-03. Director: *"Staging is at 168 in the root and 120 in progress — up from 15
on 28 August, eleven-fold in six days. 153 of the 168 are your own documents: 85 findings, 51
pre-registrations, 17 seat findings. The prioritising works. The clearing doesn't, and the reason
is that filing is free and dispositioning isn't. Fix the class, not the pile."*

Measured before touching anything, and the pile turned out to be four different problems:

  1. **89 of the 168 were not in the root at all.** They had been deleted from `docs/staging/` and
     the deletion was never committed, with the dispositioned copy untracked in `done/`. Landed
     separately at `04ba0e387`; it is a LANDING failure, not a clearing one, and the same shape
     armed a red on `test_switching_rate_commons` that morning.
  2. **55 pre-registrations were work items.** A prediction filed before its measurement has no
     exit: it cannot be actioned (that would be running the measurement), it cannot be revised (a
     prediction edited after the answer is not a prediction), and all it can do is be graded
     beside a result in another document. It is `D2` — reference and archive in the work channel —
     one kind further on.
  3. **16 findings classified as `KIND_UNKNOWN` and drew at the wrong rank.** `_FINDING_PREFIXES`
     was `("WORKER_FINDING_", "WORKER_ALARM_")`, written when the worker turn was the only channel
     filing findings. The delivery seat then began writing `SEAT_FINDING_` and every one of them
     fell through to UNKNOWN. Nothing was lost — UNKNOWN fails safe toward work — but the ORDER
     was wrong, silently, for as long as the seat has been filing.
  4. **11 of the 36 findings were graded RECORDED** — landed, nothing owed. `finding_classes`
     already excludes RECORDED from consolidation for exactly that reason; the work channel was
     the last place in the pipeline still offering them.

And nothing read the FOLDER. Every control here reads the documents, so the root could go from 15
to 168 without a single thing in the tree having an opinion about it.
"""
from __future__ import annotations

import pytest

from background import finding_classes as fc
from background import staging_rooms as sr

# --------------------------------------------------------------------------- #
# A pre-registration is a record                                               #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", [
    "SEAT_PREREGISTRATION_WHETHER_THE_ANCHOR_HOLDS_2026-09-03.md",
    "WORKER_PREREGISTRATION_WHAT_A_RECAPTURE_MUST_SHOW_2026-09-01.md",
    "PREREG_THE_PUBLISH_REFUSAL_NAMES_GREEN_TESTS_2026-09-03.md",
    "SOME_NEW_CHANNEL_PREREGISTRATION_OF_SOMETHING_2026-12-01.md",
])
def test_a_PREREGISTRATION_is_not_work_whatever_channel_wrote_it(name):
    """FOUR name shapes were in the root and a prefix tuple would have caught whichever ones the
    author had in front of them. The kind is what the document IS, and every one of them says so
    in its own name.

    MUTATION (must fire): make `_PREREGISTRATION_TOKEN` a prefix test.
    """
    assert sr.kind_of(name) == sr.KIND_PREREGISTRATION
    assert sr.kind_of(name) in sr.NOT_WORK
    assert sr.room_for(sr.kind_of(name)) == sr.RECORDS_DIRNAME


def test_a_preregistration_goes_to_RECORDS_and_never_to_DONE():
    """`done/` means dispositioned and out of the way, and `staging_archive_policy` may fold an
    archived document once it is old and unreferenced. A pre-registration must stay readable for
    as long as the claim it graded is published — it is the only evidence the experiment was
    designed before its answer was known.

    MUTATION (must fire): route pre-registrations to `done/`.
    """
    assert sr.RECORDS_DIRNAME != sr.ARCHIVE_DIRNAME
    assert sr.room_for(sr.KIND_PREREGISTRATION) == sr.RECORDS_DIRNAME
    assert sr.RECORDS_DIRNAME in sr.POPULATION_FLOORS, (
        "the records room needs a floor: it is the one room whose documents are never deleted, so "
        "a drop means the machine's own falsifiability record is being tidied away"
    )


def test_a_preregistration_never_reaches_the_draw(tmp_path):
    """The queue, not just the classifier. A kind that is `NOT_WORK` and still enumerated would be
    a classification that changed nothing.

    MUTATION (must fire): drop `KIND_PREREGISTRATION` from `NOT_WORK`.
    """
    (tmp_path / "SEAT_PREREGISTRATION_WHETHER_IT_HOLDS_2026-09-03.md").write_text("x")
    (tmp_path / "WORKER_FINDING_A_REAL_ONE_2026-09-03.md").write_text("x")

    names = [i.name for i in sr.work_queue(tmp_path)]

    assert names == ["WORKER_FINDING_A_REAL_ONE_2026-09-03.md"]


# --------------------------------------------------------------------------- #
# A finding is a finding whoever filed it                                      #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", [
    "SEAT_FINDING_THE_SELF_AUDIT_CARRIED_NOTHING_2026-09-03.md",
    "WORKER_FINDING_SOMETHING_2026-09-01.md",
    "FINDING_THE_BILL_SHOCK_SPLIT_IS_IN_THE_WRONG_LAYER_2026-09-02.md",
    "A_FUTURE_CHANNELS_FINDING_ABOUT_SOMETHING_2027-01-01.md",
])
def test_a_FINDING_is_a_finding_whoever_filed_it(name):
    """Sixteen of the seat's own findings drew at `KIND_UNKNOWN`'s rank because a tuple named the
    worker turn and nothing else. A new channel adopting an existing document kind must not have
    to remember to edit a tuple.

    MUTATION (must fire): revert `_FINDING_TOKEN` to the prefix tuple.
    """
    assert sr.kind_of(name) == sr.KIND_FINDING


def test_a_REPEATING_ALARM_is_still_an_alarm_and_not_a_finding():
    """THE NULL CONTROL for the leg above. `WORKER_FINDING_REPEATING_ALARM_` carries the finding
    token in its name and is not a finding — it is the machine complaining about the machine, and
    it ranks below a person's ask for a reason paid for on 2026-08-25, when eighteen copies of one
    alarm took the head of the draw.

    MUTATION (must fire): test the finding token before the alarm prefix.
    """
    name = "WORKER_FINDING_REPEATING_ALARM_TREE_DIVERGENCE_2026-09-01.md"

    assert sr.kind_of(name) == sr.KIND_ALARM
    assert sr.ORDER[sr.KIND_ALARM] > sr.ORDER[sr.KIND_FINDING]


def test_a_DIRECTOR_CONSOLE_transcript_is_still_not_a_directive():
    """The original ordering hazard this file's subject already carries, re-asserted because two
    new name tests were inserted above it and either could have been placed before it."""
    assert sr.kind_of("DIRECTOR_CONSOLE_2026-09-02.md") == sr.KIND_CONSOLE
    assert sr.kind_of("DIRECTOR_BRIEF_SOMETHING_2026-09-02.md") == sr.KIND_DIRECTIVE


# --------------------------------------------------------------------------- #
# A RECORDED finding has nothing owed                                          #
# --------------------------------------------------------------------------- #

_HEADER = "**Severity:** {} · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`\n\n# x\n"


def test_a_RECORDED_finding_is_not_offered_to_the_draw(tmp_path):
    """Eleven of thirty-six findings in the root were reports of things already fixed, ranked
    among things that are not. RECORDED is `finding_severity`'s own grade for a landed record.

    MUTATION (must fire): drop the `_is_recorded` clause from `work_queue`.
    """
    (tmp_path / "WORKER_FINDING_DONE_2026-09-03.md").write_text(_HEADER.format("RECORDED"))
    (tmp_path / "WORKER_FINDING_LIVE_2026-09-03.md").write_text(_HEADER.format("LATENT"))

    names = [i.name for i in sr.work_queue(tmp_path)]

    assert names == ["WORKER_FINDING_LIVE_2026-09-03.md"]
    assert [p.name for p in sr.recorded_findings(tmp_path)] == ["WORKER_FINDING_DONE_2026-09-03.md"]


@pytest.mark.parametrize("body", ["", "no header at all", "**Severity:** GIBBERISH · x"])
def test_an_UNREADABLE_severity_leaves_the_finding_IN_the_queue(tmp_path, body):
    """FAILS TOWARD WORK, and that direction is the whole safety of reading a body at all. The
    harmful mistake is dropping a live finding because its file could not be parsed.

    MUTATION (must fire): return True from `_is_recorded` on a parse failure.
    """
    (tmp_path / "WORKER_FINDING_UNREADABLE_2026-09-03.md").write_text(body)

    assert [i.name for i in sr.work_queue(tmp_path)] == ["WORKER_FINDING_UNREADABLE_2026-09-03.md"]


def test_the_severity_is_read_from_the_BODY_and_the_kind_from_the_NAME(tmp_path):
    """The split that keeps `kind_of` usable on a file it cannot read. A kind that had to open the
    document would go UNKNOWN — which ranks as work — the moment the disk misbehaved, flooding the
    draw exactly when it is least able to cope."""
    import inspect

    assert "read_text" not in inspect.getsource(sr.kind_of)
    assert "open(" not in inspect.getsource(sr.kind_of)


# --------------------------------------------------------------------------- #
# The folder has an alarm on itself                                            #
# --------------------------------------------------------------------------- #

def test_the_ROOT_ITSELF_is_measured_and_the_measure_is_FLOW_not_size():
    """*"If it can grow eleven-fold in six days with nothing reading it, that's the sediment alarm
    firing on you."* A size cap is a threshold and a threshold gets raised the first time it is
    inconvenient; this repository has watched that happen to a settlement ceiling. Flow needs no
    number picked — a queue is drained when as much leaves as arrives.

    MUTATION (must fire): compare the root's SIZE against a constant instead.
    """
    flow = sr.root_flow()

    assert flow["readable"], flow
    assert set(flow) >= {"filed", "dispositioned", "net", "days"}
    assert flow["net"] == flow["filed"] - flow["dispositioned"]
    assert sr.sediment_violations() == [] or flow["net"] > 0, (
        "the alarm must fire on net growth and only on net growth"
    )


def test_the_flow_counts_an_ARCHIVE_MOVE_as_a_disposition():
    """AN ARCHIVE MOVE IS A RENAME, so with rename detection on, git reports it as `R100` and
    `--diff-filter=AD` drops it entirely. The first draft of this scored the 89 archive moves
    landed minutes earlier as SIX dispositions — reporting the queue as barely draining at the
    exact moment it had drained by half.

    MUTATION (must fire): remove `--no-renames`.
    """
    import inspect

    source = inspect.getsource(sr.root_flow)

    assert "--no-renames" in source
    assert sr.root_flow()["dispositioned"] > 6, (
        "an archive move must count as a disposition; a flow that only sees deletions reports a "
        "folder being tidied as a folder being ignored"
    )


def test_UNREADABLE_FLOW_is_its_own_answer_and_not_silence(monkeypatch):
    """"I could not measure the growth" must not read as "it is not growing".

    MUTATION (must fire): return an empty violation list when git cannot be asked.
    """
    import subprocess

    def _boom(*a, **k):
        raise OSError("no git here")

    monkeypatch.setattr(subprocess, "run", _boom)

    assert sr.root_flow()["readable"] is False
    assert any("UNREADABLE" in v for v in sr.sediment_violations())


def test_the_check_EXITS_NONZERO_on_sediment_and_not_only_on_a_floor():
    """A measurement printed and not gated is a receipt. `--check` is what other lanes run.

    MUTATION (must fire): gate `--check` on the population floors alone.
    """
    import inspect

    source = " ".join(inspect.getsource(sr.main).split())

    assert "sediment_violations(args.root)" in source


# --------------------------------------------------------------------------- #
# A document TRACKED in the root that a disposition will keep moving out       #
# --------------------------------------------------------------------------- #
#
# THE CLASS THIS CLOSES, 2026-09-04. `room_for` above is asserted over NAMES, in the abstract,
# and nothing applied it to what git actually TRACKS. So the rule was right and unenforced:
# a preregistration committed into the staging root is moved to `records/` by the disposition,
# restored to the root by the next operation that touches a tracked-but-deleted path, and
# `finding_classes.room_collisions` then refuses EVERY commit in the tree until someone sweeps
# the duplicate by hand. That wedged publishing for ~7.7h across 12 consecutive failures.
#
# It was diagnosed and repaired twice in one day, both times as an INSTANCE: `4a4ac598b` (13:32)
# untracked the one path it had in front of it, and 56 minutes later `197261a2d` (14:28) committed
# a new preregistration into the same tracked root and the loop restarted. Two more were staged to
# land the same way when this was written. An absurdity is fixed as a class, not an instance.


def test_the_rule_can_flag_a_root_tracked_document_AND_leaves_the_root_kinds_alone():
    """THE REACHABILITY LEG, WRITTEN FIRST. The real-tree control below asserts an EMPTY list,
    and an empty list is exactly what a predicate that flags nothing returns — it would pass
    against a tree with the defect in it, forever, which is this project's most repeated way of
    shipping a control that cannot fail.

    So both directions are asserted over hand-built names: a preregistration (room `records/`,
    which `room_collisions` walks) MUST be flagged, and a finding (room = the root itself) must
    NOT be. The pair is what makes the empty verdict below evidence rather than a tautology.

    MUTATION (must fire): return `[]` from `self_refuelling_root_documents`; or drop the
    `in ROOM_DIRNAMES` test, which flags the findings too.
    """
    prereg = "SEAT_PREREG_SOMETHING_MEASURED_2026-09-04.md"
    finding = "SEAT_FINDING_SOMETHING_BROKE_2026-09-04.md"

    assert sr.room_for(sr.kind_of(prereg)) == sr.RECORDS_DIRNAME
    assert sr.room_for(sr.kind_of(finding)) is None

    flagged = fc.self_refuelling_root_documents([prereg, finding])

    assert flagged == [prereg], (
        "the predicate must flag a preregistration tracked in the root and spare a finding, "
        "which belongs there — a predicate that cannot tell them apart cannot fail usefully"
    )


def test_no_document_is_TRACKED_in_the_staging_root_that_a_disposition_will_move_out():
    """THE SUBJECT IS THE INDEX, and that is not an accident. `surgical_land` gates a standalone
    extract whose HEAD is the PARENT sha but whose INDEX is the tree the commit would create, so
    `git ls-files` is the only subject that judges the commit being made rather than the one
    before it. Reading `git ls-tree HEAD` here would grade every commit against its predecessor
    and go green one commit late — which is how a control keyed to the wrong tree lets the very
    commit that reintroduces the defect through.

    MUTATION (must fire): re-track any preregistration at `docs/staging/<name>.md`.
    """
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files", "docs/staging/"],
        capture_output=True,
        text=True,
        cwd=sr.REPO_ROOT,
    )
    assert tracked.returncode == 0, "git could not be asked; an unreadable tree is not a clean one"

    names = [
        path.rsplit("/", 1)[1]
        for path in tracked.stdout.split()
        if path.count("/") == 2  # docs/staging/<name> — the ROOT itself, not a room
    ]
    assert names, "no tracked documents found in the staging root — the query, not the tree, is wrong"

    assert fc.self_refuelling_root_documents(names) == [], (
        "these are tracked in the staging root but their kind sends them to a room "
        "`room_collisions` treats as mutually exclusive with it. Every disposition moves them "
        "out and every restore of the tracked path brings them back, and the pair refuses every "
        "commit in the tree until someone sweeps it by hand. Move the file to the room "
        "`staging_rooms.room_for` names and land the DELETION of the root path with it"
    )
