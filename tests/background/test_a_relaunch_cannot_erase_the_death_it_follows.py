"""Controls on the relaunch that used to delete the death it was relaunching after.

THE DEFECT THESE EXIST FOR, filed as
`docs/staging/SEAT_FINDING_A_RELAUNCH_DELETES_THE_UNSETTLED_LIVE_RECORD_OF_THE_DEATH_IT_IS_RELAUNCHING_AFTER_2026-09-16.md`.
A job dies. Its row still reads `live`, because `check()` runs on the deadman's cadence and not on
the death. Somebody relaunches -- one command, and the likeliest thing to happen inside that window.
Two independent paths then destroyed the evidence: `record()` dropped the `live` row by job name
without ever looking at `claim`, and `clear_a_corpse()`'s `reset-failed` made systemd forget the
exit record `reask()` is documented to ask for FIRST. The `[LAUNCH DIED]` page never fired and every
document asserting the run in flight was never contradicted. Four launches of one job is four
relaunches of ONE JOB NAME: this is the module's founding defect arriving through its own writer.

THE PARTITION IS ASSERTED BEFORE ANY LEG'S MEANING IS -- the rule both neighbouring suites open
with. A `record()` that superseded EVERY prior row, and one that superseded NONE, each pass most of
the per-case tests below; so `test_every_disposition_of_a_prior_row_is_reachable` comes first.

AND THE ORDERING IS TESTED AS AN ORDERING, not as an outcome. `test_the_settle_happens_before_the
_reset` reads the runner's own call log, because a launcher that settled correctly *after*
`reset-failed` would produce a correct-looking UNKNOWN on a real machine and pass any test that
only asked what the record says at the end.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from background import launch_liveness as ll
from background import launch_long_job as llj


class _Runner:
    """A fake `subprocess.run` that answers the four properties `reask()` actually reads.

    A FAKE MORE PERMISSIVE THAN ITS SUBJECT TURNS A FAIL-OPEN INTO A GREEN SUITE, so this answers
    only the two-argument `-p NAME` form the real `systemctl show` answers -- the neighbouring
    suite's fake was once loose here and nine tests sat on a launcher that could not read a live
    unit's state at all.
    """

    def __init__(self, **fields):
        #: What the user manager holds about the unit. `{}` is a real answer -- "systemd looked and
        #: has nothing" -- and is not the same as the probe failing.
        self.fields = fields
        self.calls: list[list[str]] = []

    def _requested(self, argv, prop):
        return any(argv[i] == "-p" and argv[i + 1] == prop for i in range(len(argv) - 1))

    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        if argv[:3] == ["systemctl", "--user", "show"]:
            out = [f"{k}={v}" for k, v in self.fields.items() if self._requested(argv, k)]
            return subprocess.CompletedProcess(argv, 0, "\n".join(out) + "\n", "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    def index_of(self, *prefix) -> int:
        """Where `prefix` first appears in the call log, or -1. The call log is the only place the
        ordering of two side effects is visible."""
        for i, c in enumerate(self.calls):
            if c[:len(prefix)] == list(prefix):
                return i
        return -1

    def index_of_probe(self, prop: str) -> int:
        for i, c in enumerate(self.calls):
            if c[:3] == ["systemctl", "--user", "show"] and self._requested(c, prop):
                return i
        return -1


@pytest.fixture
def records(tmp_path):
    """A register file of our own. NEVER the live one: `background/live_ledger_guard.py` refuses a
    test process writing a live observability ledger, and it is right to."""
    return tmp_path / "records.json"


def _write(records: Path, *entries) -> None:
    records.write_text(json.dumps(list(entries), indent=2) + "\n", encoding="utf-8")


def _row(job="a-long-run", *, claim=ll.LIVE, launched_at="2026-09-16T01:00:00Z", **over):
    base = {
        "job": job, "unit": llj.unit_name(job), "artefact": "/var/tmp/never-written.json",
        "log": None, "rc_path": None, "launched_at": launched_at,
        "asserted_live_by": ["docs/somewhere.md"], "claim": claim,
        "settled_at": None if claim == ll.LIVE else "2026-09-16T02:00:00Z", "evidence": None,
    }
    base.update(over)
    return base


def _rows(records: Path, job="a-long-run") -> list:
    return [r for r in json.loads(records.read_text(encoding="utf-8")) if r.get("job") == job]


def _launch(records, runner, *, job="a-long-run", **over):
    """Drive the real `launch()` through a fake runner, with the two unpatchable externals stubbed.

    `systemd-run` on PATH and the detach verification are not this suite's subject -- the
    neighbouring `test_launch_long_job.py` owns both -- but `launch()` refuses outright without
    them, so a test of the settling could not reach the settling at all.
    """
    kw = dict(artefact="/var/tmp/artefact.json", records_path=records, runner=runner,
              out=open("/dev/null", "w"))  # noqa: SIM115 -- closed by the interpreter; not a leak
    kw.update(over)
    return llj.launch(job, ["/bin/true"], **kw)


@pytest.fixture(autouse=True)
def _launchable(monkeypatch):
    monkeypatch.setattr(llj.shutil, "which", lambda name: "/usr/bin/systemd-run")
    monkeypatch.setattr(llj, "verify_detached", lambda unit, **kw: (True, "faked: detached"))


# ── the partition, first ─────────────────────────────────────────────────────────────────────────

def test_every_disposition_of_a_prior_row_is_reachable(records):
    """Three outcomes, one witness each. A `record()` that superseded everything, and one that
    superseded nothing, both pass the per-case tests below -- so the partition is asserted here
    before any of them means anything."""
    # (a) no prior run at all
    _write(records)
    ll.record("j", "u", "/tmp/a", path=records)
    no_prior = _rows(records, "j")

    # (b) a prior run that was already settled -- nothing to preserve, the page already fired
    _write(records, _row("j", claim=ll.DIED, evidence="settled earlier"))
    ll.record("j", "u", "/tmp/a", path=records)
    settled_prior = _rows(records, "j")

    # (c) a prior run still claiming `live` -- the case the whole finding is about
    _write(records, _row("j"))
    ll.record("j", "u", "/tmp/a", path=records)
    live_prior = _rows(records, "j")

    assert len(no_prior) == 1 and no_prior[0]["claim"] == ll.LIVE
    assert len(settled_prior) == 2 and settled_prior[0]["claim"] == ll.DIED
    assert len(live_prior) == 2 and live_prior[0]["claim"] == ll.SUPERSEDED, (
        "the unsettled prior row was not superseded: {}".format(
            [r["claim"] for r in live_prior]))
    # And the three are genuinely different dispositions, not one answer wearing three hats.
    assert len({tuple(r["claim"] for r in rows)
                for rows in (no_prior, settled_prior, live_prior)}) == 3


# ── leg one: the writer no longer deletes the contradiction ──────────────────────────────────────

def test_an_unsettled_live_row_survives_the_relaunch_that_takes_its_name(records):
    """THE DELETION ITSELF. `records = [r for r in load(path) if r.get("job") != job]` filtered by
    job name and never looked at `claim`, so the row carrying an unreported death was dropped by
    the relaunch that followed it."""
    _write(records, _row(asserted_live_by=["docs/the-run-is-in-flight.md"]))

    ll.record("a-long-run", llj.unit_name("a-long-run"), "/tmp/a", path=records)

    rows = _rows(records)
    assert len(rows) == 2, "the prior run's row was deleted by the relaunch"
    old = rows[0]
    assert old["claim"] == ll.SUPERSEDED
    assert old["asserted_live_by"] == ["docs/the-run-is-in-flight.md"], (
        "the address of the now-wrong documents is what made the row worth keeping")
    assert old["settled_at"] and "relaunch" in (old["evidence"] or ""), (
        "a preserved row that does not say why it can never be settled is a silent deletion that "
        "happens to leave bytes behind")


def test_a_superseded_row_is_never_re_asked_against_the_new_runs_unit(records):
    """WHY SUPERSESSION MUST BE TERMINAL. The relaunch reuses the unit name. A preserved row left
    at `live` would be re-asked by `check()` against the NEW run's systemd state and answer
    confidently about the wrong job -- trading a silent deletion for a confident lie."""
    _write(records, _row())
    ll.record("a-long-run", llj.unit_name("a-long-run"), "/tmp/a", path=records)

    # The new run is very much alive; a re-ask of the old row against it would say RUNNING.
    stale, lines, settled = ll.check(path=records, probe=lambda u: {"ActiveState": "active"})

    rows = _rows(records)
    assert rows[0]["claim"] == ll.SUPERSEDED, "the superseded row was moved by a re-ask"
    assert not any("SUPERSEDED" in ln or rows[0]["launched_at"] in ln for ln in lines), (
        "the superseded row was re-asked; its verdict would be about the run that took its name")


def test_the_run_before_last_is_dropped_so_the_register_stays_bounded(records):
    """ONE prior row per job, not a growing history. The reader this serves holds a document
    saying the LAST run is in flight; two runs ago was already contradicted by the run between."""
    _write(records,
           _row(claim=ll.DIED, launched_at="2026-09-14T00:00:00Z"),
           _row(claim=ll.DIED, launched_at="2026-09-15T00:00:00Z"),
           _row(launched_at="2026-09-16T00:00:00Z"))

    ll.record("a-long-run", llj.unit_name("a-long-run"), "/tmp/a", path=records)

    rows = _rows(records)
    assert [r["launched_at"] for r in rows[:-1]] == ["2026-09-16T00:00:00Z"], (
        "expected exactly the immediately-preceding run to be kept, got "
        f"{[r['launched_at'] for r in rows]}")


def test_a_relaunch_does_not_disturb_another_jobs_row(records):
    """The filter narrowed from `job` to `job`-plus-recency; it must not have widened to `all`."""
    _write(records, _row("other-job"), _row("a-long-run"))
    ll.record("a-long-run", llj.unit_name("a-long-run"), "/tmp/a", path=records)
    assert [r["claim"] for r in _rows(records, "other-job")] == [ll.LIVE]


# ── leg two: the ordering, which is the half no writer can fix ───────────────────────────────────

def test_the_settle_happens_before_the_reset_that_destroys_its_evidence(records):
    """THE ORDERING IS THE SUBSTANCE, and it is asserted as an ordering.

    `reset-failed` makes the user manager forget the unit's exit record. `reask()` asks systemd
    first *because* that verdict survives the kill it reports -- so run the other way round, the
    re-ask finds no `Result`, returns UNKNOWN, and `check()` by design does not settle UNKNOWN. A
    launcher that settled correctly but AFTERWARDS would pass any test that only read the final
    record on this fake, and would lose every death on a real machine.
    """
    _write(records, _row())
    runner = _Runner(ActiveState="failed", Result="oom-kill", ExecMainStatus="9")

    _launch(records, runner)

    probe_at = runner.index_of_probe("Result")
    reset_at = runner.index_of("systemctl", "--user", "reset-failed")
    assert probe_at >= 0, "the previous run was never re-asked at all"
    assert reset_at >= 0, "this test's premise is gone: no corpse was cleared"
    assert probe_at < reset_at, (
        f"the exit record was reset (call {reset_at}) before it was read (call {probe_at}); "
        "the death is unsettleable by the act of relaunching after it")


def test_the_relaunch_settles_the_previous_death_on_systemds_own_evidence(records):
    """The outcome the ordering buys: afterwards the death is SETTLED, not merely preserved."""
    _write(records, _row())
    runner = _Runner(ActiveState="failed", Result="oom-kill", ExecMainStatus="9")

    _launch(records, runner)

    rows = _rows(records)
    assert len(rows) == 2 and rows[-1]["claim"] == ll.LIVE, "the new run was not recorded"
    old = rows[0]
    assert old["claim"] == ll.DIED, (
        f"the previous run settled to {old['claim']}, not DIED -- systemd held Result=oom-kill")
    assert "oom-kill" in (old["evidence"] or ""), (
        "the settled row does not carry the evidence it was settled on")


def test_a_probe_that_could_not_be_run_settles_nothing_and_still_preserves(records):
    """FAILS CLOSED IN BOTH DIRECTIONS. A broken probe must not be read as a death -- and must not
    be an excuse to delete the row either. This is the residual case the writer exists for: the
    ordering cannot help when there was never an answer to read."""
    _write(records, _row())

    class _Blind(_Runner):
        def __call__(self, argv, **kw):
            self.calls.append(list(argv))
            if argv[:3] == ["systemctl", "--user", "show"]:
                raise OSError("systemctl is not answering")
            return subprocess.CompletedProcess(argv, 0, "", "")

    runner = _Blind()
    # An unreadable probe reads as "the name is held", so the launch is refused -- which is
    # `name_is_held`'s documented direction and not this test's subject. Ask the writer directly.
    with pytest.raises(llj.LaunchRefused):
        _launch(records, runner)
    assert [r["claim"] for r in _rows(records)] == [ll.LIVE], (
        "a refused launch must not touch the register at all")

    ll.record("a-long-run", llj.unit_name("a-long-run"), "/tmp/a", path=records)
    rows = _rows(records)
    assert len(rows) == 2 and rows[0]["claim"] == ll.SUPERSEDED, (
        "a death nobody could settle was deleted rather than preserved")
    assert rows[0]["claim"] != ll.DIED, (
        "'we could not tell' was recorded as a death; that is the guess this module refuses")


# ── leg three: the page still reaches the director ───────────────────────────────────────────────

def test_the_deadman_pages_for_a_death_the_relaunch_settled(records, monkeypatch):
    """THE REPAIR MUST NOT RE-CREATE THE DEFECT ONE MOVE ON.

    `_check_launch_liveness` only ever sees rows still claiming `live`. Once the launcher settles
    the previous run itself, the deadman's own `check()` correctly finds nothing stale -- so
    without a separate record of what is OWED, the page is suppressed by the very fix that
    preserved the death. Settled and reported are two states.
    """
    _write(records, _row())
    runner = _Runner(ActiveState="failed", Result="oom-kill", ExecMainStatus="9")
    _launch(records, runner)

    assert [r.get("pending_notice") for r in _rows(records)][0] is True, (
        "the launcher settled a death and left nothing saying anybody is owed the news")

    from background import deadmans_switch as dms
    sent = []
    monkeypatch.setattr(ll, "RECORDS_PATH", records)
    monkeypatch.setattr(dms, "notify", lambda msg, **kw: sent.append((msg, kw)))
    monkeypatch.setattr(dms, "clear_transition", lambda key: None)
    monkeypatch.setattr(dms, "log", lambda *a, **k: None)
    monkeypatch.setattr(ll, "systemd_probe", lambda unit: {"ActiveState": "active"})

    dms._check_launch_liveness()

    paged = [m for m, kw in sent if "[LAUNCH DIED]" in m]
    assert paged, f"no death was paged; the deadman sent {[m[:60] for m, _ in sent]}"
    assert "docs/somewhere.md" in paged[0], (
        "the page does not name the document the death makes wrong, which is the whole point of "
        "keeping `asserted_live_by`")
    assert any(kw.get("kind") == "real_alarm" for _, kw in sent)

    # AND IT PAGES ONCE. The notice is cleared by the send, so the next cycle is silent -- the
    # alarm is keyed to an event, and a real_alarm that repeats every cycle is how this project
    # has buried its own signal before.
    assert not _rows(records)[0].get("pending_notice")
    sent.clear()
    dms._check_launch_liveness()
    assert not [m for m, kw in sent if "[LAUNCH DIED]" in m], "the death paged a second time"


def test_deaths_settled_before_this_shipped_do_not_all_page_at_once(records, monkeypatch):
    """`pending_notice` absent means NOT OWED, not owed. The live register carries settled deaths
    written long before any of this existed; reading their missing field as a debt would page the
    whole back catalogue on the first cycle after it lands."""
    _write(records, _row(claim=ll.DIED, evidence="settled on 2026-09-10, reported then"))

    from background import deadmans_switch as dms
    sent = []
    monkeypatch.setattr(ll, "RECORDS_PATH", records)
    monkeypatch.setattr(dms, "notify", lambda msg, **kw: sent.append((msg, kw)))
    monkeypatch.setattr(dms, "clear_transition", lambda key: None)
    monkeypatch.setattr(dms, "log", lambda *a, **k: None)

    dms._check_launch_liveness()

    assert not sent, f"an already-reported death paged again: {[m[:60] for m, _ in sent]}"
