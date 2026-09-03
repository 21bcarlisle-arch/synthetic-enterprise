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
