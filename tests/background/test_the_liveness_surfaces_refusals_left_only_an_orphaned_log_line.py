"""THE TWO SURFACES THAT EXIST TO SPEAK WHEN CONTENT CANNOT REFUSED IN SILENCE.

THE DEFECT, from `docs/staging/done/SEAT_FINDING_THE_PATH_THAT_WEDGED_THE_PUBLISHER_WAS_THE_FILE
_THE_LANE_REPAIRING_THE_PUBLISHER_WAS_HOLDING_2026-09-04.md`:

> **The paths reached the log and left the record.** `stderr_tail` joins with `\\n`; `log()` writes
> one bullet. Every line after the first is orphaned -- present in the file, attached to nothing,
> invisible to any grep keyed to the message. And the machine-readable side is worse: at HEAD only
> `git_commit_push` writes `.publish_gate_state.json`, so these two heartbeat refusals recorded no
> path anywhere.

The liveness heartbeat and the provenance banner are the surfaces whose ENTIRE JOB is to tell the
reader the system is alive or behind, and they publish precisely when content does not. On
2026-09-04 they were silenced at 19:19Z and 19:49Z in the one state they exist for, and the only
trace was a log bullet. Four separate seats then re-derived the blocking paths by hand.

THE DISCRIMINATION THIS BUYS, which is the point and not a side-effect. Both a HOT ORIGIN and an
`FF_MODIFIED` collision arrive at this refusal as the identical sentence *"origin/main is N
commit(s) AHEAD"*, and they want different people:

  * hot origin -- a state with an OWNER. `origin_reconcile` closes real forks on the deadman
    cadence (41 unaided on 2026-09-04) and the next cycle simply succeeds. Nothing to do.
  * `FF_MODIFIED` -- a WEDGE. No cadence clears it, because the holder is a lane's uncommitted
    file. It stays until that lane lands, and reading it as the first is what left this surface
    silent for six hours while every reader waited for a cadence that could not help.

WHY THE RECORD IS ITS OWN FIELD rather than the content path's cause file: they are different
subjects, and measuring one number across two populations is this project's most expensive
recurring shape. `PUBLISH_CAUSE_FILE` answers "why did the CONTENT publish not land" and is a
single record the wedge router reads on rc=77; a banner refusal written there could overwrite the
attribution of the very cycle it was reporting on.
"""
from __future__ import annotations

import contextlib
import json
import types

import pytest

from background import origin_reconcile as orc
from background import process_run_complete as prc
from background import publish_cause as pc

HOT_ORIGIN_AHEAD = 23


@pytest.fixture
def state_file(tmp_path, monkeypatch):
    """THE PATH GLOBAL GOES TO `tmp_path` FIRST, before anything can run.

    `_record_liveness_surface_refusal` writes a TRACKED production surface
    (`docs/observability/.publish_gate_state.json`). The autouse G-T2 guard would refuse the write
    anyway, but a control that relies on another control to stay harmless is one edit away from
    damaging the live thing it guards -- and this repo has already had a mutant run a real
    `Path.replace` on a tracked file that way.
    """
    path = tmp_path / ".publish_gate_state.json"
    monkeypatch.setattr(prc, "PUBLISH_GATE_STATE_FILE", path)
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    return path


def _record(state_file):
    """The refusal record as it stands on disk, or None when nothing was written."""
    if not state_file.exists():
        return None
    return json.loads(state_file.read_text()).get("liveness_surface_refusal")


def _drive(monkeypatch, tmp_path, *, ahead=0, provenance=True, commit_rc=0, commit_tail="",
           push_rc=0, remote_head="same", local_head="same", label="Liveness heartbeat"):
    """Run `_commit_and_push_paths` to one chosen exit. Returns its boolean."""
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: provenance)
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: ahead)
    monkeypatch.setattr(prc, "_record_commit_refusal_reds", lambda *a, **k: None)

    def fake_run(cmd, **kwargs):
        argv = list(cmd)
        if argv[:2] == ["git", "commit"]:
            return types.SimpleNamespace(returncode=commit_rc, stdout="", stderr=commit_tail)
        if argv[:2] == ["git", "push"]:
            return types.SimpleNamespace(returncode=push_rc, stdout="", stderr="")
        if argv[:2] == ["git", "rev-parse"]:
            return types.SimpleNamespace(returncode=0, stdout=local_head + "\n", stderr="")
        if argv[:2] == ["git", "ls-remote"]:
            return types.SimpleNamespace(returncode=0, stdout=remote_head + "\trefs/heads/main\n",
                                         stderr="")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    return prc._commit_and_push_paths(["site/data/tick_heartbeat.json"], "chore(liveness)",
                                      label=label, git_hash="abc1234")


# ── the whole partition, before any leg claims what one exit does ────────────────────────────
def test_every_refusing_exit_records_and_they_do_not_all_say_the_same_thing(state_file, tmp_path,
                                                                           monkeypatch):
    """THE REACHABILITY CONTROL. `_commit_and_push_paths` has four ways to refuse, and a recorder
    wired into the one exit where the incident was observed is this file's own most-repeated
    defect -- the function's existing comments say so three times.

    Four exits, four DIFFERENT causes, and every one of them written down.

    MUTATION: remove `_record_liveness_surface_refusal` from any single exit and that exit's entry
    becomes None, reding `all(...)`. Give them one shared cause constant and the `== 4` reds.
    """
    exits = {
        "provenance": dict(provenance=False),
        "behind_origin": dict(ahead=HOT_ORIGIN_AHEAD),
        "hook_refusal": dict(commit_rc=1, commit_tail="a gate said no"),
        "push_never_landed": dict(remote_head="old99999", local_head="new11111"),
    }
    causes = {}
    for name, kwargs in exits.items():
        state_file.unlink(missing_ok=True)
        assert _drive(monkeypatch, tmp_path, **kwargs) is False, \
            "{} must be a refusal, or this leg is grading the success path".format(name)
        record = _record(state_file)
        assert record is not None, \
            "the {} exit refused in the log alone -- which is the whole defect".format(name)
        causes[name] = record["cause"]

    assert len(set(causes.values())) == 4, \
        "four different refusals must reach the reader as four different causes, got {}".format(
            causes)
    assert set(causes.values()) <= pc.CAUSES, \
        "the shared cause vocabulary is what makes this record readable beside the content " \
        "path's; a private name here would need its own reader, got {}".format(causes)


def test_a_clean_no_op_banner_records_NOTHING(state_file, tmp_path, monkeypatch):
    """THE NULL CONTROL, and it is what stops the field filling with non-events.

    A banner byte-identical to the committed copy is the EXPECTED steady state -- a `paused_since`
    that has not re-stamped, a heartbeat that has not ticked -- and git says "nothing to commit".
    A record written for that would make every read of this field a false alarm, and a record
    nobody trusts is the same as no record.

    MUTATION: hoist the recorder out of the `"nothing to commit" not in _tail` guard and this reds
    while every other test in the file still passes.
    """
    assert _drive(monkeypatch, tmp_path, commit_rc=1,
                  commit_tail="nothing to commit, working tree clean") is False
    assert _record(state_file) is None, \
        "the steady state is not a refusal worth recording, and recording it would drown the " \
        "three that are"


# ── the discrimination the finding actually asked for ────────────────────────────────────────
def _behind_origin_record(state_file, tmp_path, monkeypatch, blocking):
    state_file.unlink(missing_ok=True)
    monkeypatch.setattr(orc, "paths_blocking_fast_forward", lambda _p=None: blocking)
    _drive(monkeypatch, tmp_path, ahead=HOT_ORIGIN_AHEAD)
    return _record(state_file)


def test_a_wedged_tree_and_a_hot_origin_are_told_apart_in_the_record(state_file, tmp_path,
                                                                     monkeypatch):
    """THE POINT OF THE REPAIR. Both states produce the identical "origin/main is N commit(s)
    AHEAD" sentence, and until now the record carried that sentence and nothing else -- so a wedge
    that no cadence can clear was indistinguishable from a fork that clears itself in minutes.

    KEYED TO THE DISCRIMINATION, not to today's blocking set: the assertion is that the two
    readings DIFFER and that the wedge names its holder, never that the live tree has N blockers.

    MUTATION: drop `_refused_advance_cause` from the behind-origin exit and both records collapse
    to the same sentence, reding the inequality.
    """
    wedged = _behind_origin_record(
        state_file, tmp_path, monkeypatch,
        [{"path": "background/process_run_complete.py", "kind": orc.FF_MODIFIED}])
    hot = _behind_origin_record(state_file, tmp_path, monkeypatch, [])

    assert wedged["evidence"] != hot["evidence"], \
        "a wedge with an owner and a fork that closes itself must not read the same, or the " \
        "reader waits for a cadence that cannot help -- which cost six hours on 2026-09-04"
    assert "background/process_run_complete.py" in wedged["evidence"], \
        "the record must NAME the holder; four seats re-derived it by hand because it did not"
    assert orc.FF_MODIFIED in wedged["evidence"], \
        "the KIND is what decides who clears it, so it travels with the path"
    assert "NOTHING local collides" in hot["evidence"], \
        "a hot origin must say that nothing local is holding it, or it reads as an unexamined wedge"


def test_an_unreadable_blocking_state_is_not_reported_as_a_clean_hot_origin(state_file, tmp_path,
                                                                           monkeypatch):
    """FAIL-CLOSED. `None` is "I could not look" and `[]` is "I looked and nothing collides".
    Collapsing them here would tell the reader the tree is merely behind a hot origin at exactly
    the moment nobody established that -- the fail-open that reads as a clean bill.

    MUTATION: delete the `blocking is None` branch in `_refused_advance_cause` and this record
    starts claiming NOTHING collides, reding both assertions.
    """
    unread = _behind_origin_record(state_file, tmp_path, monkeypatch, None)
    assert "NOT established" in unread["evidence"]
    assert "NOTHING local collides" not in unread["evidence"]


# ── the record has to still be there when someone reads it ───────────────────────────────────
def test_the_record_survives_the_failure_write_that_immediately_follows_it(state_file, tmp_path,
                                                                          monkeypatch):
    """THE ONE THAT WOULD HAVE MADE THIS WHOLE REPAIR A NO-OP IN PRODUCTION.

    `_write_publish_gate_state` rebuilds its output from a FIXED key list, so any field written by
    anyone else is dropped by the next writer -- and the next writer is
    `record_publish_gate_failure`, which runs on exactly the cycles this record is about. Without
    the carry-forward the record would be erased milliseconds after being written, by the failure
    it exists to explain, and every other test in this file would still pass.

    MUTATION: delete the `liveness_surface_refusal` carry block in `_write_publish_gate_state` and
    this reds alone.
    """
    _drive(monkeypatch, tmp_path, ahead=HOT_ORIGIN_AHEAD)
    written = _record(state_file)
    assert written is not None

    prc.record_publish_gate_failure("a red on the shared tree", rc=1, git_hash="abc1234",
                                    now=1_788_000_000, send_ntfy_fn=lambda _m: "sent")

    survived = _record(state_file)
    assert survived == written, \
        "the failure write that follows a liveness refusal must not erase the explanation of it " \
        "-- got {!r} after {!r}".format(survived, written)


def test_an_evidenced_episode_close_clears_it_so_it_cannot_haunt_the_next_one(state_file, tmp_path,
                                                                              monkeypatch):
    """The carry-forward must not become a leak. A record kept across an episode boundary is
    evidence about a CLOSED episode presented beside a new one -- the carried-forward-blocking-list
    defect this repo has already paid four clocks for.

    MUTATION: carry the field unconditionally (drop `not episode_closed`) and this reds.
    """
    _drive(monkeypatch, tmp_path, ahead=HOT_ORIGIN_AHEAD)
    assert _record(state_file) is not None, "reachability: there must be a record to clear"

    prc._write_publish_gate_state({"failures": [], "alerted_at": None, "wedge_since": None},
                                  episode_closed=True)
    assert _record(state_file) is None, \
        "an evidenced close ends the episode this record belongs to, so it must not survive into " \
        "the next one"


def test_a_recording_failure_never_becomes_a_publish_failure(state_file, tmp_path, monkeypatch):
    """This runs on a path that has ALREADY decided to refuse, so the only thing its own failure
    may cost is the explanation of a refusal that was happening anyway. Turning that into a crash
    would convert an observation into a fault -- the shape this pipeline paid for at the commit in
    2026-08-03.

    MUTATION: remove the try/except from `_record_liveness_surface_refusal` and this raises
    instead of returning False.
    """
    def _explode(*_a, **_k):
        raise OSError("the observability directory went away")

    monkeypatch.setattr(prc, "_write_publish_gate_state", _explode)
    assert _drive(monkeypatch, tmp_path, ahead=HOT_ORIGIN_AHEAD) is False, \
        "the refusal must still be a refusal, reported the same way, when its own record cannot " \
        "be written"


def test_the_record_carries_which_surface_and_which_commit_it_is_about(state_file, tmp_path,
                                                                       monkeypatch):
    """Two callers share this primitive, and "the banner was refused" and "the heartbeat was
    refused" are different facts about different surfaces. A record that named neither the surface
    nor the commit would be a fact with nothing to attach it to -- which is what `read_cause`
    refuses a stale record for.

    MUTATION: drop `label` or `git_hash` from the stored dict and this reds.
    """
    _drive(monkeypatch, tmp_path, ahead=HOT_ORIGIN_AHEAD, label="Provenance banner")
    record = _record(state_file)
    assert record["label"] == "Provenance banner"
    assert record["git_hash"] == "abc1234"
    assert record["ts"] > 0, \
        "a refusal with no clock cannot be told from one recorded last week"
