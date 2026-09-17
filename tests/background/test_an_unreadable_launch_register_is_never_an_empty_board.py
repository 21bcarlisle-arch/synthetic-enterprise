"""Controls on the five priors the launch register's loader read as "no launches".

THE DEFECT THESE EXIST FOR, filed as
`docs/staging/WORKER_FINDING_THE_LAUNCH_REGISTERS_LOADER_READS_FIVE_PRIORS_AS_NO_LAUNCHES_AND_THE_NEXT_RECORD_DESTROYS_THE_REST_2026-09-16.md`.
`load()` was `try: json.loads(...) except: return []`, so ABSENT, a zero-byte file (the signature of
an interrupted write), truncated JSON, a bare `null` (which PARSES, so no `except` ever saw it) and
a non-list object all returned the same answer, and it was the flattering one. Two paths spent that:

* `record()` is load -> supersede -> append -> save, so on an unreadable prior it wrote a
  ONE-ELEMENT register over whatever was there. Measured before the repair, on a truncated register
  holding a `live` row for `longjob-A`: `record('longjob-B')` left the file holding `['longjob-B']`
  and A's bytes preserved nowhere. **A destroyed `live` record is a claim that can never be
  contradicted**, which is the one thing this module exists to abolish.
* `check()` returned `stale=0` -- not "we could not tell" but the CLEAN board -- and
  `deadmans_switch._check_launch_liveness` reads `if not stale: clear_transition`. So the register
  losing its own contents read, all the way to the alarm, as every launch accounted for.

THE PARTITION IS ASSERTED BEFORE ANY LEG'S MEANING IS, the rule the two neighbouring suites open
with, and here it is load-bearing in a specific way: **a loader that graded EVERYTHING UNREADABLE
would pass every per-leg refusal below.** It would also wedge the deadman permanently and page for a
register that is merely empty, which is the mirror defect and the one a fail-closed repair reaches
for. `test_every_prior_the_register_can_be_in_is_REACHABLE` is what refuses it, and
`test_an_EMPTY_REGISTER_is_a_clean_board` is what keeps the ordinary case ordinary.

AND THE CALLER LEGS ARE TESTED AT THE CALLER. The cost was never in `check()`'s return value; it was
in `_check_launch_liveness` reaching `clear_transition`, and in `launch_long_job` still needing to
launch. A suite that only asserted the loader's verdict would grade the half that never misled
anybody.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from background import episode_prior
from background import launch_liveness as ll
from background import launch_long_job as llj

#: Every shape that is NOT a usable register but IS a file. `null` and `{"job": ...}` are the two no
#: `except` clause can see, and `[{...}, "x"]` is the partly-right one: a register we cannot fully
#: account for cannot answer "what became of the run this document says is in flight".
CORRUPT_PRIORS = {
    "empty": "",
    "truncated": '[{"job": "longjob-A", "claim": "li',
    "null": "null",
    "not_a_list": '{"job": "longjob-A"}',
    "partly_right": '[{"job": "longjob-A"}, "longjob-B"]',
}


def _register(room: Path, raw: str | None) -> Path:
    """A register in its OWN directory, because `preserve_unreadable` writes a sidecar beside it
    and two cases sharing a directory would let one case's sidecar satisfy another's assertion."""
    room.mkdir(parents=True, exist_ok=True)
    p = room / ".launch_records.json"
    if raw is not None:
        p.write_text(raw, encoding="utf-8")
    return p


def _live_row(job: str = "longjob-A") -> dict:
    return {"job": job, "unit": f"{job}.service", "artefact": f"/tmp/{job}.json",
            "log": None, "rc_path": None, "launched_at": "2026-09-16T00:00:00Z",
            "asserted_live_by": ["docs/staging/A_DOCUMENT_SAYING_IT_IS_IN_FLIGHT.md"],
            "claim": ll.LIVE, "settled_at": None, "evidence": None}


def _no_probe(*a, **k):
    """A probe that is never reached. Every refusal in this file fires at the LOADER, one frame
    before any unit is asked about -- and a probe that answered would hide a refusal that did not
    fire by settling the rows itself."""
    raise AssertionError("the probe was reached: the loader did not refuse")


# --------------------------------------------------------------- the partition, before any leg


def test_every_prior_the_register_can_be_in_is_REACHABLE(tmp_path):
    """ABSENT, READABLE and UNREADABLE are all reachable and they do not all read the same.

    ONE CONTROL OVER THE WHOLE ROOM rather than a leg per prior, because the failure this refuses
    is not "one prior is misgraded" -- it is a loader that collapses the partition, in EITHER
    direction. The old one collapsed everything to ABSENT; a fail-closed repair collapses
    everything to UNREADABLE and passes every other refusal in this file.
    """
    absent, absent_verdict = ll.load_register(tmp_path / "never-written.json")
    readable, readable_verdict = ll.load_register(
        _register(tmp_path / "ok", json.dumps([_live_row()])))
    corrupt = {name: ll.load_register(_register(tmp_path / name, raw))[1]
               for name, raw in CORRUPT_PRIORS.items()}

    assert (absent, absent_verdict) == ([], episode_prior.ABSENT)
    assert readable_verdict == episode_prior.READABLE and len(readable) == 1
    assert set(corrupt.values()) == {episode_prior.UNREADABLE}, corrupt
    # Three DISTINCT values, so no caller can conflate two of them by comparing.
    assert len({absent_verdict, readable_verdict, episode_prior.UNREADABLE}) == 3


def test_an_EMPTY_REGISTER_is_a_clean_board_and_an_EMPTY_FILE_is_not(tmp_path):
    """The anti-tautology for every refusal below: `[]` on disk is a FACT and must still pass.

    An empty record is not an empty FILE. A repair that refused both would page on the ordinary
    state of a machine that has launched nothing, which is how this channel buries its own signal.
    The two differ by two characters and by everything.
    """
    empty_list = _register(tmp_path / "list", "[]")
    assert ll.load_register(empty_list) == ([], episode_prior.READABLE)
    assert ll.check(path=empty_list, probe=_no_probe) == (0, [], [])

    with pytest.raises(ll.RegisterUnreadable):
        ll.check(path=_register(tmp_path / "zero", ""), probe=_no_probe)


# ------------------------------------------------------------------- the write path: record()


@pytest.mark.parametrize("name", sorted(CORRUPT_PRIORS))
def test_a_relaunch_over_an_unreadable_register_PRESERVES_the_bytes_it_rebuilds_over(
        tmp_path, name):
    """`record()` must still write -- and the bytes it cannot parse must survive it somewhere.

    Keyed to the BYTES and not to the sidecar's name: `episode_prior` owns the naming, and a
    control pinned to today's suffix goes red when that becomes more careful, which is backwards.
    """
    raw = CORRUPT_PRIORS[name]
    room = tmp_path / name
    register = _register(room, raw)

    entry = ll.record("longjob-B", "longjob-B.service", "/tmp/b.json", path=register)

    assert entry["claim"] == ll.LIVE, "the launch must still be recorded"
    assert json.loads(register.read_text()) == [entry], "the register rebuilds from this launch"
    survivors = [p for p in room.iterdir()
                 if p != register and p.read_text(encoding="utf-8", errors="replace") == raw]
    assert survivors, f"the unparseable bytes of the {name} prior were destroyed, not preserved"


def test_the_record_written_over_an_unreadable_register_SAYS_the_rest_is_gone(tmp_path):
    """Preserving is half an answer: a reader of the REGISTER must be able to see the loss.

    The sidecar sits beside the file, and the reader this serves is holding a document that says a
    run is in flight and is looking in the register for it. `prior_register` is the only surface
    that tells them the register they are reading is not the one their claim went into.
    """
    register = _register(tmp_path / "corrupt", CORRUPT_PRIORS["truncated"])
    entry = ll.record("longjob-B", "longjob-B.service", "/tmp/b.json", path=register)

    assert entry["prior_register"]["verdict"] == episode_prior.UNREADABLE
    assert entry["prior_register"]["preserved_as"], (
        "a preserved copy that is not named is not evidence a reader can follow")

    ordinary = ll.record("longjob-C", "longjob-C.service", "/tmp/c.json",
                         path=_register(tmp_path / "clean", "[]"))
    assert "prior_register" not in ordinary, (
        "the field must mark the LOSS, not every record -- a marker every row carries marks nothing")


def test_a_readable_priors_rows_are_still_carried_across_a_relaunch(tmp_path):
    """The equivalence leg. The repair changed `record`'s loader; it must not have changed what
    `record` does on the ordinary path, which is the founding defect's own control one file over."""
    register = _register(tmp_path / "ok", json.dumps([_live_row()]))
    ll.record("longjob-B", "longjob-B.service", "/tmp/b.json", path=register)
    rows = json.loads(register.read_text())
    assert [r["job"] for r in rows] == ["longjob-A", "longjob-B"]
    assert rows[0]["claim"] == ll.LIVE, "another job's live row is not this launch's business"


# --------------------------------------------------------------------- the read path: check()


def test_check_REFUSES_an_unreadable_register_rather_than_reporting_a_clean_board(tmp_path):
    """`(0, lines, [])` cannot carry this refusal: a COUNT is what the caller branches on and zero
    is the flattering value. The refusal has to be a control-flow event the caller cannot spend by
    ignoring a field."""
    register = _register(tmp_path / "corrupt", CORRUPT_PRIORS["truncated"])
    with pytest.raises(ll.RegisterUnreadable) as caught:
        ll.check(path=register, probe=_no_probe)
    assert str(register) in str(caught.value)
    assert caught.value.preserved, "the bytes must be kept before the refusal, not after it"


def test_check_leaves_the_unreadable_register_ON_DISK_so_the_condition_STANDS(tmp_path):
    """The opposite of `record`'s choice, and deliberately.

    This runs on the deadman's cadence. Moving the file aside would make the next cycle read ABSENT
    and go quiet -- turning a standing condition into a single page nobody was awake for.
    """
    register = _register(tmp_path / "corrupt", CORRUPT_PRIORS["truncated"])
    for _ in range(2):
        with pytest.raises(ll.RegisterUnreadable):
            ll.check(path=register, probe=_no_probe)
    assert register.read_text() == CORRUPT_PRIORS["truncated"], (
        "a check that consumes its own subject reports the incident once and is then silent")


# --------------------------------------------------------- the caller legs, where the cost was


def _deadman(monkeypatch, register: Path):
    """Drive the real `_check_launch_liveness` with its two outputs captured.

    `RECORDS_PATH` is patched rather than a path passed, because the deadman calls `check()` with
    no arguments -- which is the call that was misled, and a test that passed a path would grade a
    call site production does not have.
    """
    from background import deadmans_switch as dms

    monkeypatch.setattr(ll, "RECORDS_PATH", register)
    cleared: list[str] = []
    sent: list[tuple] = []
    monkeypatch.setattr(dms, "clear_transition", lambda key: cleared.append(key))
    monkeypatch.setattr(dms, "notify", lambda msg, **kw: sent.append((msg, kw)))
    monkeypatch.setattr(dms, "log", lambda *a, **k: None)
    dms._check_launch_liveness()
    return dms, cleared, sent


def test_the_deadman_PAGES_on_an_unreadable_register_and_never_clears_the_alarm(
        tmp_path, monkeypatch):
    """THE LEG THE WHOLE FINDING IS ABOUT. Before the repair this path reached `clear_transition`.

    A blanket `except Exception` here would be a silent pass with a log line -- correct for "we did
    not look", wrong for "every live claim just became unreachable" -- so the branch is asserted to
    NOTIFY, not merely to avoid clearing.
    """
    dms, cleared, sent = _deadman(
        monkeypatch, _register(tmp_path / "corrupt", CORRUPT_PRIORS["truncated"]))

    assert dms._LAUNCH_REGISTER_KEY not in cleared
    assert dms._LAUNCH_LIVENESS_KEY not in cleared, (
        "the liveness alarm must not read a register it cannot open as a settled board either")
    assert [kw["kind"] for _, kw in sent] == ["real_alarm"]
    assert sent[0][1]["transition_key"] == dms._LAUNCH_REGISTER_KEY, (
        "sharing a key with the death page lets either one clear the other")
    assert sent[0][1].get("re_escalate_after"), "a standing condition that pages once is silent"


def test_a_READABLE_register_CLEARS_the_unreadable_alarm(tmp_path, monkeypatch):
    """The fail-closed half needs a way out or it is a wedge. Only a register that PARSES can clear
    it, so the clear sits on the branch that proves the condition ended."""
    dms, cleared, sent = _deadman(monkeypatch, _register(tmp_path / "ok", "[]"))

    assert dms._LAUNCH_REGISTER_KEY in cleared
    assert not sent, "an empty register is a clean board and must page for nothing"


def test_BOTH_sides_of_the_register_route_through_the_resolver_and_agree(tmp_path, monkeypatch):
    """The read AND the write resolve to ONE file, which is what let the write side be decided.

    OWED BY A NEIGHBOUR AND LANDED HERE. `SEAT_FINDING_THE_LIVE_RECORD_RESOLVER_WAS_NOT_EVEN_WIRED_
    INTO_THE_OTHER_TWO_READERS_OF_THE_FILE_IT_WAS_NAMED_FOR_2026-09-16.md` surveyed eleven readers
    of the live records and left this one UNDECIDED, for a precise reason: `record()` is `load()`
    then `save()`, so resolving the READ without the WRITE makes a linked worktree read the shared
    book and write it into its own copy, where the next read ignores it -- trading a stale read for
    a LOST write, which is strictly worse. `launch_liveness` resolves both, through the single
    `_resolved_path`, and HEAD carries no control saying so.

    ASSERTED AS AGREEMENT, not as two routings. Two functions that each call the resolver but
    disagree about their argument would pass a pair of per-side tests and still lose every write:
    the property is that a record written from here is a record read from here.
    """
    shared = tmp_path / "shared" / ".launch_records.json"
    shared.parent.mkdir(parents=True)
    shared.write_text(json.dumps([_live_row(f"j{i}") for i in range(12)]), encoding="utf-8")
    worktrees_own = tmp_path / "own" / ".launch_records.json"
    worktrees_own.parent.mkdir(parents=True)
    monkeypatch.setattr(ll, "shared_tree_live_record", lambda _p: shared)

    assert len(ll.load(worktrees_own)) == 12, (
        "the READ did not resolve: in a linked worktree twelve live claims do not exist to be "
        "contradicted, and `check` cannot contradict what it cannot see")
    ll.record("longjob-B", "longjob-B.service", "/tmp/b.json", path=worktrees_own)
    assert not worktrees_own.exists(), (
        "the WRITE went to this tree's own copy -- a stale read traded for a LOST write, which is "
        "the strictly worse half and the reason the read could not be wired alone")
    assert [r["job"] for r in json.loads(shared.read_text())][-1] == "longjob-B"


def test_the_launcher_STILL_LAUNCHES_over_an_unreadable_register(tmp_path, monkeypatch):
    """A launch that is not recorded is the state `launch_long_job` kills a healthy job to avoid.

    Fail-closed on the ALARM and fail-open on the LAUNCH is not an inconsistency: refusing here
    would let a damaged file stop all work, which is strictly worse than an unattributed death --
    and the launcher's own `record()` is what rebuilds the register, so the launch IS the repair.
    """
    monkeypatch.setattr(llj.shutil, "which", lambda name: "/usr/bin/systemd-run")
    monkeypatch.setattr(llj, "verify_detached", lambda unit, **kw: (True, "faked: detached"))
    register = _register(tmp_path / "corrupt", CORRUPT_PRIORS["truncated"])
    calls: list[list[str]] = []

    def runner(argv, **kw):
        calls.append(list(argv))
        return subprocess.CompletedProcess(argv, 0, "", "")

    with open("/dev/null", "w") as devnull:  # noqa: SIM115 -- context-managed, unlike the neighbour
        llj.launch("longjob-B", ["/bin/true"], artefact=str(tmp_path / "b.json"),
                   records_path=register, runner=runner, out=devnull)

    assert any(a and a[0] == "systemd-run" for a in calls), "the job was never started"
    assert [r["job"] for r in json.loads(register.read_text())] == ["longjob-B"]
