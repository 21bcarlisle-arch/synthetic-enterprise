"""Controls on the launch-record re-ask.

THE DEFECT THESE EXIST FOR. Four launches of one job, three deaths, and every death asserted alive
in a document for hours afterwards -- caught each time only because a person went and looked at a
pid. The mechanism under test answers the question a document cannot: *is that still true?*

THE PARTITION IS ASSERTED BEFORE ANY LEG'S MEANING IS. A verdict function whose every branch
refuses, or whose every branch says RUNNING, passes any per-branch test written against it; so
`test_every_verdict_is_reachable` comes first and the rest build on it. (The rule was learned by
entering that trap three times in one afternoon through three different doors.)
"""
from __future__ import annotations

import json

import pytest

from background import launch_liveness as ll


def _entry(tmp_path, **over):
    base = {
        "job": "a-long-run", "unit": "a-long-run.service",
        "artefact": str(tmp_path / "artefact.json"), "rc_path": None,
        "launched_at": "2026-09-08T00:32:23Z", "asserted_live_by": ["docs/somewhere.md"],
        "claim": ll.LIVE, "settled_at": None, "evidence": None,
    }
    base.update(over)
    return base


def _probe(**fields):
    return lambda unit: dict(fields)


def test_every_verdict_is_reachable(tmp_path):
    """All five outcomes, from one witness each. A verdict nothing can produce is not a verdict."""
    artefact = tmp_path / "artefact.json"
    seen = {
        ll.RUNNING: ll.reask(_entry(tmp_path), _probe(ActiveState="active"))["verdict"],
        ll.DIED: ll.reask(_entry(tmp_path),
                          _probe(ActiveState="failed", Result="oom-kill"))["verdict"],
        ll.UNKNOWN: ll.reask(_entry(tmp_path),
                             _probe(ActiveState="", LoadState="not-found"))["verdict"],
        ll.UNREADABLE: ll.reask(_entry(tmp_path), lambda unit: None)["verdict"],
    }
    artefact.write_text("{}", encoding="utf-8")
    seen[ll.FINISHED] = ll.reask(
        _entry(tmp_path), _probe(ActiveState="inactive", Result="success",
                                 ExecMainStatus="0"))["verdict"]
    for expected, got in seen.items():
        assert got == expected, "{} is unreachable; the witness returned {}".format(expected, got)


def test_a_group_kill_is_diagnosed_with_no_rc_file_and_no_artefact(tmp_path):
    """THE CASE THREE DEATHS COULD NOT DIAGNOSE, and the reason this module asks systemd first.

    The 09-07 relaunch wrote an rc file so "gone" could be told from "gone with rc=137". A SIGKILL
    to the cgroup takes the wrapper that would have written it, so the rc file is absent in exactly
    the case it was built for. Here there is no rc file, no artefact and no exit code -- only the
    user manager's `Result`, which is held outside the job -- and that must be enough.
    """
    entry = _entry(tmp_path, rc_path=str(tmp_path / "never_written.rc"))
    answer = ll.reask(entry, _probe(ActiveState="failed", Result="oom-kill", ExecMainStatus=""))
    assert answer["verdict"] == ll.DIED, (
        "a job the user manager reports oom-killed reads as anything but dead when its own rc "
        "file is missing, which is the only case that matters: " + answer["why"])
    assert "oom-kill" in answer["why"], "the diagnosis systemd held did not reach the reader"


def test_a_broken_probe_is_not_a_death(tmp_path):
    """FAIL CLOSED. "We could not look" must never render as "it died"; that is worse than the
    hand-check this replaces, because it would settle a live claim on no evidence."""
    entry = _entry(tmp_path)
    assert ll.reask(entry, lambda unit: None)["verdict"] == ll.UNREADABLE

    ll.save([entry], tmp_path / "records.json")
    stale, lines, _ = ll.check(tmp_path / "records.json", probe=lambda unit: None)
    assert stale == 0, "an unreadable probe settled a live claim"
    assert json.loads((tmp_path / "records.json").read_text())[0]["claim"] == ll.LIVE
    assert any("not evidence the job ended" in line for line in lines)


def test_the_check_names_the_documents_that_are_now_wrong(tmp_path):
    """The contradiction has to carry an ADDRESS. A check that says "a claim went stale" and not
    WHICH pages now read false leaves the reader doing the search that was the whole cost."""
    (tmp_path / "artefact.json").write_text("{}", encoding="utf-8")
    store = tmp_path / "records.json"
    ll.save([_entry(tmp_path, asserted_live_by=["docs/prereg.md", "docs/correction.md"])], store)

    stale, lines, _ = ll.check(store, probe=_probe(ActiveState="inactive", Result="success",
                                                   ExecMainStatus="0"))
    assert stale == 1
    joined = "\n".join(lines)
    for doc in ("docs/prereg.md", "docs/correction.md"):
        assert "CONTRADICTS {}".format(doc) in joined, doc

    settled = json.loads(store.read_text())[0]
    assert settled["claim"] == ll.FINISHED and settled["settled_at"] and settled["evidence"], (
        "the record was not settled, so the next reader meets the launch-time claim again and "
        "this check nags forever instead of holding the answer")
    # GREEN THE SECOND TIME IS THE POINT, not a leak: the claim is no longer stale.
    assert ll.check(store, probe=_probe(ActiveState="inactive", Result="success",
                                        ExecMainStatus="0"))[0] == 0


def test_a_settled_record_never_returns_to_live(tmp_path):
    """Settling is one-way. A record that could be re-opened by a probe answering differently
    tomorrow would let a dead job read as live again -- the original defect, restored."""
    store = tmp_path / "records.json"
    ll.save([_entry(tmp_path, claim=ll.DIED, settled_at="2026-09-08T01:00:00Z",
                    evidence="Result=oom-kill")], store)
    stale, lines, _ = ll.check(store, probe=_probe(ActiveState="active"))
    assert (stale, lines) == (0, []), "a settled record was re-asked and could have been re-opened"
    assert json.loads(store.read_text())[0]["claim"] == ll.DIED


def test_a_retrofitted_record_keeps_the_real_launch_time(tmp_path, monkeypatch):
    """A job recorded LATE must not be stamped with the moment it was recorded.

    THE DEFECT THIS CAUGHT, on the module's first real use: the live floor leg was launched at
    01:39:56Z and recorded three hours later, because the module was written after the launch. With
    `launched_at` defaulting to now, the record said the run had been going for zero minutes --
    and how long a claim has stood is precisely what a later reader judges it by. A record whose
    age is the age of the RECORD rather than of the RUN understates every stale claim it holds.

    THROUGH `main`, NOT `record`. The first draft of this control called `record(launched_at=...)`
    directly and stayed green when the CLI was mutated to pass `None` -- it graded the function and
    was blind to the wiring, which is the only part that changed. The argv is the subject.
    """
    store = tmp_path / "records.json"
    monkeypatch.setattr(ll, "RECORDS_PATH", store)

    assert ll.main(["--record", "floor", "--unit", "floor.service",
                    "--artefact", str(tmp_path / "a.json"),
                    "--launched-at", "2026-09-08T01:39:56Z"]) == 0
    assert json.loads(store.read_text())[0]["launched_at"] == "2026-09-08T01:39:56Z"

    # And the default still holds for a genuinely fresh launch -- the flag must not become the
    # only way to get a launch time, or every caller that omits it writes None.
    monkeypatch.setattr(ll, "_now", lambda: "2026-09-08T04:40:00Z")
    assert ll.main(["--record", "fresh", "--unit", "fresh.service",
                    "--artefact", str(tmp_path / "b.json")]) == 0
    fresh = [r for r in json.loads(store.read_text()) if r["job"] == "fresh"][0]
    assert fresh["launched_at"] == "2026-09-08T04:40:00Z"


def _deadman(monkeypatch):
    """The deadman check with every live-effect path stubbed. Never touches the real log, the real
    ntfy route or the real record store."""
    from background import deadmans_switch as dms
    sent, cleared = [], []
    monkeypatch.setattr(dms, "notify", lambda msg, **kw: sent.append((msg, kw)))
    monkeypatch.setattr(dms, "log", lambda msg, path=None: None)
    monkeypatch.setattr(dms, "clear_transition", lambda key: cleared.append(key))
    return dms, sent, cleared


def test_the_deadman_pages_the_documents_a_stale_claim_makes_wrong(monkeypatch):
    """THE POINT OF THE WHOLE MODULE: the contradiction has to ARRIVE, not wait to be asked for.

    A `--check` that only runs when someone types it is still a person checking, one indirection
    along -- and every one of the four launches was caught by a person going to look. This is the
    leg that makes the arrival automatic, so it is the leg worth a control.
    """
    dms, sent, _ = _deadman(monkeypatch)
    dead = {"job": "a-long-run", "claim": ll.DIED, "asserted_live_by": ["docs/prereg.md"]}
    monkeypatch.setattr(ll, "check", lambda: (1, ["a-long-run: DIED -- Result=oom-kill"], [dead]))
    dms._check_launch_liveness()

    assert len(sent) == 1, "a stale liveness claim did not page"
    msg, kw = sent[0]
    assert "docs/prereg.md" in msg, (
        "the page named no document, so the reader inherits the search that was the whole cost")
    assert kw.get("kind") == "real_alarm"


def test_a_run_that_SUCCEEDED_is_batched_and_never_paged(monkeypatch):
    """A DEATH AND A COMPLETION ARE NOT THE SAME EVENT, and the first draft of the wiring paged an
    identical `real_alarm` for both.

    Both contradict a document reading "in flight", so both are stale -- but one is an incident and
    the other is the good news the run was launched for. Paging him for success is how this
    project's one inbound channel has buried its own signal before, so the split is a control and
    not a preference. Caught before it ever fired: the floor leg was minutes from finishing
    successfully when this was written.
    """
    dms, sent, cleared = _deadman(monkeypatch)
    done = {"job": "floor", "claim": ll.FINISHED, "asserted_live_by": ["docs/result.md"]}
    monkeypatch.setattr(ll, "check", lambda: (1, ["floor: FINISHED -- rc=0"], [done]))
    dms._check_launch_liveness()

    assert len(sent) == 1, "a completed run said nothing at all; the document stays wrong silently"
    msg, kw = sent[0]
    assert kw.get("kind") != "real_alarm", (
        "a run that SUCCEEDED paged the director as an alarm: " + msg)
    assert kw.get("kind") == "work_done" and kw.get("topic_class") == "routine_landing", (
        "a completion must go to the batched digest, not the instant route: " + repr(kw))
    assert "docs/result.md" in msg, "the batched note still has to name what is now wrong"
    assert cleared, "no death stood, so the alarm key must be cleared rather than left armed"


def test_a_death_and_a_completion_in_one_pass_both_get_their_own_route(monkeypatch):
    """The partition asserted over the whole set, not one leg at a time. A branch that handled only
    whichever came first would pass both single-verdict tests above."""
    dms, sent, cleared = _deadman(monkeypatch)
    monkeypatch.setattr(ll, "check", lambda: (2, ["two"], [
        {"job": "dead-one", "claim": ll.DIED, "asserted_live_by": ["docs/a.md"]},
        {"job": "done-one", "claim": ll.FINISHED, "asserted_live_by": ["docs/b.md"]}]))
    dms._check_launch_liveness()

    kinds = {kw.get("kind") for _, kw in sent}
    assert kinds == {"real_alarm", "work_done"}, (
        "one verdict swallowed the other; got " + repr(kinds))
    assert not cleared, "a real death stood, and its alarm key was cleared anyway"


def test_the_deadman_is_silent_when_nothing_is_stale_and_when_it_could_not_look(monkeypatch):
    """Two silences with different meanings, and neither may page.

    A run that is simply still going is the ordinary state -- paging on it would make this the
    third channel that buries its own signal. A check that RAISED did not look, and "we did not
    look" must not clear the alarm either: that would report an answer we never had.
    """
    dms, sent, cleared = _deadman(monkeypatch)
    monkeypatch.setattr(ll, "check", lambda: (0, ["floor: RUNNING -- ActiveState=active"], []))
    dms._check_launch_liveness()
    assert sent == [] and cleared, "a live run paged, or the settled alarm was never cleared"

    def _boom():
        raise OSError("systemctl is not on this box")
    monkeypatch.setattr(ll, "check", _boom)
    cleared.clear()
    dms._check_launch_liveness()
    assert sent == [], "a check that could not run reported a death"
    assert cleared == [], (
        "a check that could not run CLEARED the alarm -- that is 'we did not look' rendered as "
        "'nothing is wrong', which is the fail-open this module exists to refuse")


@pytest.mark.parametrize("state", ["active", "activating", "deactivating", "reloading"])
def test_a_unit_that_has_not_finished_is_never_settled(tmp_path, state):
    """`deactivating` is the one worth naming: a job inside its own teardown has produced no exit
    record yet, and calling that dead is the guess this module exists to refuse."""
    assert ll.reask(_entry(tmp_path), _probe(ActiveState=state))["verdict"] == ll.RUNNING
