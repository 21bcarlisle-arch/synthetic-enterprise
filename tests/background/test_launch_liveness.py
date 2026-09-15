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


# ---------------------------------------------------------------------------
# Did the file the job wrote reach git? (`landing_verdict` / `landed_check`)
#
# THE DEFECT THESE EXIST FOR. `finished` is a claim about a PROCESS. The reader's question is about
# a FILE, and twice in three days a run of machine-hours finished, wrote its output into this tree,
# and that output sat in no commit while the register said the work was done. The first instance
# this control caught on the real register was a `log` -- the only surviving local trace of a
# six-hour run -- which is why every field the record names is graded and not just `artefact`.
# ---------------------------------------------------------------------------


def _repo(tmp_path):
    """A real git repository, because the subject of these legs is what git actually answers."""
    import subprocess as sp
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    for cmd in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"],
                ["config", "user.name", "t"]):
        sp.run(["git", "-C", str(root), *cmd], check=True, capture_output=True)
    (root / "docs" / "seed.txt").write_text("seed\n", encoding="utf-8")
    sp.run(["git", "-C", str(root), "add", "docs/seed.txt"], check=True, capture_output=True)
    sp.run(["git", "-C", str(root), "commit", "-qm", "seed"], check=True, capture_output=True)
    return root


def _written(root, rel, *, stage=False, commit=False):
    import subprocess as sp
    (root / rel).write_text("{}\n", encoding="utf-8")
    if stage or commit:
        sp.run(["git", "-C", str(root), "add", rel], check=True, capture_output=True)
    if commit:
        sp.run(["git", "-C", str(root), "commit", "-qm", rel], check=True, capture_output=True)
    return rel


def _ignored(root, rel):
    """A file git is under standing orders not to hold, which is not a file git has lost."""
    (root / ".gitignore").write_text("docs/*.log\n", encoding="utf-8")
    return _written(root, rel)


def _landing(root, artefact, probe=None, membership=ll.git_membership):
    entry = {"job": "a-long-run", "unit": "a-long-run.service", "artefact": artefact,
             "claim": ll.FINISHED}
    return ll.landing_verdict(entry, repo=root, membership=membership,
                              probe=probe or _probe(ActiveState="inactive", Result="success"))


def test_every_landing_verdict_is_reachable(tmp_path):
    """THE PARTITION FIRST. A grader whose every branch says LANDED passes every per-branch leg
    below, and a grader whose every branch REFUSES passes every refusal leg. Neither is caught by
    anything except asserting the whole partition can be reached from one witness each."""
    root = _repo(tmp_path)
    seen = {
        ll.LANDED: _landing(root, _written(root, "docs/landed.json", commit=True))["verdict"],
        ll.STAGED: _landing(root, _written(root, "docs/staged.json", stage=True))["verdict"],
        ll.UNTRACKED: _landing(root, _written(root, "docs/loose.json"))["verdict"],
        ll.IGNORED: _landing(root, _ignored(root, "docs/run.log"))["verdict"],
        ll.ABSENT: _landing(root, "docs/never_written.json")["verdict"],
        ll.OUTSIDE: _landing(root, "/var/tmp/elsewhere.json")["verdict"],
        ll.RUNNING: _landing(root, _written(root, "docs/half.json"),
                             probe=_probe(ActiveState="active"))["verdict"],
        ll.UNREADABLE: _landing(root, _written(root, "docs/unaskable.json"),
                                membership=lambda rel, repo: None)["verdict"],
    }
    for expected, got in seen.items():
        assert got == expected, "{} is unreachable; the witness returned {}".format(expected, got)


def test_the_stranded_artefact_is_refused_and_the_landed_one_is_not(tmp_path):
    """THE INSTANCE. The same file, the same record, differing only in whether a commit holds it --
    so a grader that refused (or passed) regardless of git cannot survive both halves."""
    root = _repo(tmp_path)
    import subprocess as sp
    loose = _written(root, "docs/result.json")
    assert _landing(root, loose)["verdict"] == ll.UNTRACKED
    sp.run(["git", "-C", str(root), "add", loose], check=True, capture_output=True)
    sp.run(["git", "-C", str(root), "commit", "-qm", "land"], check=True, capture_output=True)
    assert _landing(root, loose)["verdict"] == ll.LANDED, (
        "landing the file did not change the verdict, so the verdict was never about git")


def test_a_path_in_the_index_alone_is_not_landed(tmp_path):
    """`git ls-files` reads the INDEX. A control asking only that would call a path tracked that no
    commit holds and no clone has seen -- the exact reading that has already made one control here
    green while its subject was absent from every commit. It is named, not refused: a lane
    mid-landing looks like this and refusing would wedge every other lane."""
    root = _repo(tmp_path)
    staged = _written(root, "docs/mid_landing.json", stage=True)
    answer = _landing(root, staged)
    assert answer["verdict"] == ll.STAGED
    assert ll.git_membership(staged, root) == {"head": False, "index": True, "ignored": False}
    refusals, _ = ll.landed_check(_register(tmp_path, artefact=staged), repo=root,
                                  probe=_probe(ActiveState="inactive", Result="success"))
    assert refusals == 0, "a lane mid-landing was refused, which wedges every other lane"


def test_an_absolute_artefact_path_inside_the_repo_is_the_same_file_as_the_relative_one(tmp_path):
    """Some launches record `docs/x.json` and others `/home/rich/.../docs/x.json`. They are one
    file. A check that read either literally would be blind to half its own subjects -- and the
    real register holds both spellings today."""
    root = _repo(tmp_path)
    rel = _written(root, "docs/spelled_two_ways.json")
    assert _landing(root, rel)["verdict"] == ll.UNTRACKED
    assert _landing(root, str(root / rel))["verdict"] == ll.UNTRACKED, (
        "the absolute spelling of the same file was not graded, so half the register is unseen")


def test_a_broken_git_probe_refuses_rather_than_passing(tmp_path):
    """FAIL CLOSED. `cat-file -e` exits non-zero for an absent path and an unreadable repository
    alike; reading the second as the first is a clean bill issued without looking."""
    root = _repo(tmp_path)
    loose = _written(root, "docs/result.json")
    refusals, lines = ll.landed_check(
        _register(tmp_path, artefact=loose), repo=root,
        membership=lambda rel, repo: None,
        probe=_probe(ActiveState="inactive", Result="success"))
    assert refusals == 1, "git could not be asked and the check passed anyway"
    assert any("UNREADABLE" in line for line in lines)


def test_a_still_running_job_is_never_told_to_land_its_half_written_file(tmp_path):
    """The skip is keyed to the PROBE, not to the record's `claim`. A record whose unit was
    collected sits at `live` forever, and keying to the claim would let exactly the stranded case
    escape by never being settled."""
    root = _repo(tmp_path)
    half = _written(root, "docs/half_written.json")
    assert _landing(root, half, probe=_probe(ActiveState="active"))["verdict"] == ll.RUNNING
    still_live = {"job": "a-long-run", "unit": "a-long-run.service", "artefact": half,
                  "claim": ll.LIVE}
    assert ll.landing_verdict(still_live, repo=root,
                              probe=_probe(ActiveState="", LoadState="not-found"),
                              )["verdict"] == ll.UNTRACKED, (
        "a record left at `live` by a collected unit was excused, which is the stranded case")


def test_the_log_and_the_rc_file_are_graded_too(tmp_path):
    """THE FIRST REAL INSTANCE. On the live register the artefact was in HEAD and the `log` --
    the only surviving trace of a run of machine-hours -- was in no commit. An artefact-only
    reading called that record clean."""
    root = _repo(tmp_path)
    landed = _written(root, "docs/result.json", commit=True)
    loose_log = _written(root, "docs/run.log")
    register = _register(tmp_path, artefact=landed, log=loose_log)
    refusals, lines = ll.landed_check(register, repo=root,
                                      probe=_probe(ActiveState="inactive", Result="success"))
    assert refusals == 1, "the stranded log was not graded, so the real instance would pass"
    assert any("[log]" in line and "UNTRACKED" in line for line in lines)


def test_the_output_names_what_it_cannot_see(tmp_path):
    """A run whose output goes to /var/tmp is invisible to this check BY CONSTRUCTION, and a
    reader who could not see that in the output would take silence for coverage."""
    root = _repo(tmp_path)
    refusals, lines = ll.landed_check(
        _register(tmp_path, artefact="/var/tmp/nowhere_near_git.json"), repo=root,
        probe=_probe(ActiveState="inactive", Result="success"))
    assert refusals == 0
    assert any("OUTSIDE" in line for line in lines), (
        "a record this check cannot grade produced no line at all, which reads as a pass")


def test_an_ignored_file_is_not_a_stranded_one(tmp_path):
    """THE FALSE POSITIVE THIS CONTROL'S OWN FIRST DRAFT PRODUCED. Run against the live register it
    called a 247MB run log stranded; `.gitignore` holds `docs/observability/*.log`, so that file is
    absent from git by a standing decision. "Not in git" and "must not be in git" are identical
    from the index and opposite in meaning, and only a third question tells them apart."""
    root = _repo(tmp_path)
    log = _ignored(root, "docs/run.log")
    assert ll.git_membership(log, root)["ignored"] is True
    refusals, lines = ll.landed_check(
        _register(tmp_path, artefact=log), repo=root,
        probe=_probe(ActiveState="inactive", Result="success"))
    assert refusals == 0, "a deliberately ignored file was reported as work that failed to land"
    assert any("IGNORED" in line for line in lines), (
        "the ignored file produced no line, so a reader cannot see the run left no landable trace")


def _register(tmp_path, **fields):
    """A one-record register on disk, since `landed_check` reads a path and not a list."""
    path = tmp_path / "records.json"
    entry = {"job": "a-long-run", "unit": "a-long-run.service", "claim": ll.FINISHED}
    entry.update(fields)
    path.write_text(json.dumps([entry]), encoding="utf-8")
    return path


def test_the_deadman_reports_unlanded_files_as_drift_and_clears_when_they_land(monkeypatch):
    """THE WIRING, and the reason it is a second check rather than a branch of the first.

    A settled liveness claim is an EVENT -- it pages once and is then correctly silent for ever.
    An artefact in no commit is a STANDING condition, still true tomorrow. Sharing the alarm key
    would announce it once and then read as resolved, so the two keys and the two lifetimes are
    the property under test here.
    """
    dms, sent, cleared = _deadman(monkeypatch)
    monkeypatch.setattr(
        ll, "landed_check",
        lambda: (1, ["a-long-run [artefact]: UNTRACKED -- the job finished and wrote `docs/r.json`"]))
    dms._check_launch_artefacts_landed()
    assert len(sent) == 1, "a finished run's output was in no commit and nothing said so"
    msg, kw = sent[0]
    assert "docs/r.json" in msg, (
        "the message named no file, so the reader inherits the search that was the whole cost")
    assert kw.get("kind") != "real_alarm", (
        "an unlanded file paged as an incident; nothing is dying and this is the channel-burying "
        "shape the sibling check was already corrected for")
    assert kw.get("transition_key") != dms._LAUNCH_LIVENESS_KEY, (
        "the standing condition shares the event's alarm key, so it announces once and then reads "
        "as resolved while it still stands")
    assert kw.get("re_escalate_after"), "a standing condition that never re-escalates is a whisper"

    sent.clear()
    monkeypatch.setattr(ll, "landed_check", lambda: (0, ["a-long-run [artefact]: LANDED"]))
    dms._check_launch_artefacts_landed()
    assert sent == [] and dms._LAUNCH_LANDED_KEY in cleared, (
        "landing the files did not silence or clear the alarm")


def test_the_deadman_is_silent_when_it_could_not_ask_git(monkeypatch):
    """"We did not look" must not clear the alarm: that reports an answer we never had."""
    dms, sent, cleared = _deadman(monkeypatch)

    def _boom():
        raise OSError("git is not on this box")
    monkeypatch.setattr(ll, "landed_check", _boom)
    dms._check_launch_artefacts_landed()
    assert sent == [], "a check that could not run reported stranded work"
    assert cleared == [], (
        "a check that could not run CLEARED the alarm -- 'we did not look' rendered as 'nothing "
        "is wrong', which is the fail-open this whole module refuses")


# --------------------------------------------------------------------------------------------
# Coverage: is every RUNNING job in the register at all? `check()` re-asks the register, so a job
# that was never recorded is not a claim it can settle -- and its PASS reads as a clean bill.
# --------------------------------------------------------------------------------------------

def _units(*rows) -> object:
    """A stub `systemctl --user list-units --no-legend` result, in the real column order."""
    class _Res:
        returncode = 0
        stdout = "".join(f"  {u} loaded {state} running some description here\n"
                         for u, state in rows)
    return lambda *a, **k: _Res()


def _reg(tmp_path, *entries):
    path = tmp_path / "records.json"
    path.write_text(json.dumps(list(entries)), encoding="utf-8")
    return path


def test_a_running_job_the_register_never_heard_of_is_refused(tmp_path):
    """THE DEFECT: `longjob-noise-floor-20260910` ran for hours while `--check` printed PASS.

    Both branches are asserted in ONE call over the whole partition, because a rule that refused
    everything would pass a test that only ever showed it one uncovered unit -- and a rule that
    refused nothing would pass a test that only ever showed it a covered one.
    """
    path = _reg(tmp_path, {"job": "covered", "unit": "longjob-covered", "claim": ll.LIVE})
    refusals, lines = ll.unregistered_live_units(
        path, runner=_units(("longjob-covered.service", "active"),
                            ("longjob-orphan.service", "active")))

    assert refusals == 1, (
        "the check did not separate the covered job from the unregistered one -- it either "
        "refuses everything or nothing, and both pass a single-subject test")
    assert any("longjob-orphan.service: UNREGISTERED" in ln for ln in lines)
    assert any("longjob-covered.service: COVERED" in ln for ln in lines)


def test_the_refusal_tells_the_reader_how_to_clear_it(tmp_path):
    """A refusal that names no remedy gets routed around; this one has to name the record command."""
    _, lines = ll.unregistered_live_units(
        _reg(tmp_path), runner=_units(("longjob-orphan.service", "active")))
    said = " ".join(lines)
    assert "--record" in said and "--launched-at" in said, (
        "the refusal does not say how to register the job, so the next reader has to go and read "
        "this module to clear it")


def test_a_broken_probe_refuses_rather_than_reporting_full_coverage(tmp_path):
    """"We could not look" must never render as "everything is covered"."""
    def _boom(*a, **k):
        raise OSError("systemctl is not on this box")
    refusals, lines = ll.unregistered_live_units(_reg(tmp_path), runner=_boom)
    assert refusals == ll.UNREGISTERED_UNREADABLE, (
        "a broken probe was counted as zero uncovered jobs, which is the fail-open that would "
        "make this check worse than no check")
    assert "UNREADABLE" in " ".join(lines)
    assert ll.live_units(runner=_boom) is None, (
        "a probe that could not run returned an empty list -- 'nothing is running' and 'we could "
        "not look' are opposite claims and must not share a value")


def test_a_unit_named_with_and_without_the_service_suffix_is_the_same_job(tmp_path):
    """The launcher writes `longjob-x`; systemd reports `longjob-x.service`. Both name one job.

    This is not hypothetical: on 2026-09-10 every record in the live register was written without
    the suffix, so a check that compared literally would have called EVERY running job orphaned.
    """
    refusals, _ = ll.unregistered_live_units(
        _reg(tmp_path, {"job": "x", "unit": "longjob-x", "claim": ll.LIVE}),
        runner=_units(("longjob-x.service", "active")))
    assert refusals == 0, "a suffix spelling difference was read as an unregistered job"


def test_a_settled_record_does_not_cover_a_unit_that_is_running(tmp_path):
    """The rare branch, asserted reachable: a record settled once is never re-asked again.

    A job whose record says `finished` while its unit is active is not covered by that record --
    settling is one-way, so nothing will ever grade this run.
    """
    refusals, lines = ll.unregistered_live_units(
        _reg(tmp_path, {"job": "x", "unit": "longjob-x", "claim": ll.FINISHED}),
        runner=_units(("longjob-x.service", "active")))
    assert refusals == 1, "a settled record was accepted as cover for a job running now"
    assert any("STALE RECORD" in ln and "finished" in ln for ln in lines), (
        "the stale-record case is reported as if the job had never been registered, which sends "
        "the reader to the wrong remedy")


def test_a_unit_that_is_not_running_is_not_this_checks_business(tmp_path):
    """Coverage is asked of RUNNING jobs. A corpse with no record is not this control's finding."""
    refusals, _ = ll.unregistered_live_units(
        _reg(tmp_path), runner=_units(("longjob-done.service", "inactive")))
    assert refusals == 0, (
        "an inactive unit was refused, so this check fires on every job that ever ran and its "
        "output is noise")


def test_the_bare_pass_no_longer_claims_coverage_it_does_not_have(tmp_path, monkeypatch, capsys):
    """THE INSTANCE: `--check` printed `PASS (no stale liveness claim)` while the floor ran
    unregistered beside a near-identically-named sibling that WAS registered. The PASS was true
    and about the other job. A green that does not prompt the second question is worse here than
    an empty answer."""
    monkeypatch.setattr(ll, "check", lambda: (0, [], []))
    monkeypatch.setattr(ll, "unregistered_live_units",
                        lambda *a, **k: (1, ["longjob-orphan.service: UNREGISTERED -- ..."]))
    assert ll.main(["--check"]) == 0, (
        "the report leg started refusing; `deadmans_switch` calls `check()` on this path and a "
        "new refusal there pages for a state no lane can clear mid-run")
    said = capsys.readouterr().out
    assert "RUNNING job(s) are covered by no record" in said, (
        "the PASS still claims a clean bill it cannot support")
    assert "--unregistered" in said, "the reader is not pointed at the leg that refuses"


def test_the_refusing_leg_exits_non_zero(tmp_path, monkeypatch, capsys):
    """`--unregistered` is the leg with teeth; a control that only ever prints is a comment."""
    monkeypatch.setattr(ll, "unregistered_live_units", lambda *a, **k: (1, ["x: UNREGISTERED"]))
    assert ll.main(["--unregistered"]) == 1
    monkeypatch.setattr(ll, "unregistered_live_units",
                        lambda *a, **k: (ll.UNREGISTERED_UNREADABLE, ["x: UNREADABLE"]))
    assert ll.main(["--unregistered"]) == 1, (
        "an unreadable probe passed the refusing leg -- fail-open on the one leg that refuses")
    monkeypatch.setattr(ll, "unregistered_live_units", lambda *a, **k: (0, ["x: COVERED"]))
    assert ll.main(["--unregistered"]) == 0
    assert "PASS" in capsys.readouterr().out
