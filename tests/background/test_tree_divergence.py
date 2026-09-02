"""R15 proof for the tree-divergence measure (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09).

The ruling pairs "the gate's subject is a clean checkout of HEAD" with "squatting gets named
daily, never punished via the public site". Removing the punishment removes the only thing that
made uncommitted work visible, so this measure has to be able to FAIL on its own named defect --
a lane holding many source files out of HEAD for hours -- and must never be able to block a
publish.
"""
from __future__ import annotations

import subprocess

from background import tree_divergence as td


# ── the measure fires on its named defect ────────────────────────────────────────────────────
def test_breaches_fire_on_a_squatting_lane():
    """The named defect, at KNIFE2's measured shape: 19 files, hours old.

    MUTATION: raise FILE_COUNT_THRESHOLD above 19 (or drop the count check) and this fails."""
    m = {"total_files": 19, "oldest_age_hours": 1.5, "oldest_path": "simulation/x.py"}
    assert any("19 source files" in b for b in td.breaches(m))


def test_breaches_fire_on_age_even_when_the_count_is_small():
    """A single file held out of HEAD for a day is squatting too -- count is not the only axis.

    MUTATION: delete the age branch and this fails."""
    m = {"total_files": 1, "oldest_age_hours": 26.0, "oldest_path": "company/interfaces/x.py"}
    b = td.breaches(m)
    assert any("26.0h" in x for x in b)
    assert not any("source files diverge" in x for x in b), "count must not fire on 1 file"


def test_a_clean_tree_names_nobody():
    """Independence: the measure must be silent when there is nothing to name, or a daily
    naming becomes noise and stops being read."""
    # `armed_reverts: 0` is part of what "clean" MEANS since 2026-09-02, and its absence is named
    # rather than assumed silent -- this module's own rule that an omitted count must be loud.
    assert td.breaches({"total_files": 0, "oldest_age_hours": 0.0, "oldest_path": None,
                        "armed_reverts": 0}) == []


def test_a_tree_just_under_both_thresholds_is_silent():
    m = {"total_files": td.FILE_COUNT_THRESHOLD, "oldest_age_hours": td.AGE_HOURS_THRESHOLD,
         "oldest_path": "x.py", "armed_reverts": 0}
    assert td.breaches(m) == []


# ── generated churn must not drown the signal ────────────────────────────────────────────────
def test_generated_artefacts_are_excluded():
    """The publish path rewrites ~180 of these every cycle. Counting them would make the measure
    unreadable regardless of how carefully anyone looked at it.

    MUTATION: empty GENERATED_PREFIXES and this fails."""
    for rel in ("site/data/dashboard.json", "docs/observability/agent_status.json",
                "docs/reports/ANNUAL_REPORT.md", "docs/shadow/index.html"):
        assert td._is_generated(rel), rel


def test_runtime_dotfiles_are_not_squatters():
    """`.tree.lock` and `.maintenance_reminder_sent.json` each took the 'oldest divergence' slot
    on this module's first runs -- the measure was reporting its own machinery, and .tree.lock is
    the very lock the publish path holds while being measured.

    MUTATION: drop _is_runtime_state from _is_generated and this fails."""
    assert td._is_generated(".tree.lock")
    assert td._is_generated("background/.maintenance_reminder_sent.json")
    assert not td._is_generated(".claude/hooks/pull_next_work.py"), \
        "a dotted DIRECTORY is not runtime state -- that is real source"


# ── the one mixed prefix: authored prose is not churn ────────────────────────────────────────
# `docs/observability/` is both the machine's log directory and where agents write findings,
# audits, walks and director reports. The wholesale prefix exclusion hid the second kind, and did:
# DIRECTOR_REPORT_2026-08-20.md sat UNTRACKED for six days, invisible to a measure running every
# publish cycle. Both directions below, so the narrowing can FAIL (R15).

def test_an_authored_document_under_the_mixed_prefix_is_counted():
    """The named defect, at the shape it was found in.

    MUTATION: drop `_is_authored_document` from `_is_generated` and this fails."""
    for rel in ("docs/observability/DIRECTOR_REPORT_2026-08-20.md",
                "docs/observability/TREE_DIVERGENCE_WALK_2026-08-26.md",
                "docs/observability/coldwalk_findings_cro_2026-07-12.md"):
        assert not td._is_generated(rel, untracked=True), rel


def test_a_machine_log_under_the_mixed_prefix_stays_excluded():
    """The mirror. Several of these are untracked BY DESIGN, so a narrowing that swept them in
    would put the measure permanently over its own file line and name nothing.

    MUTATION: drop the `-log.md` clause and this fails."""
    for rel in ("docs/observability/supervisor-log.md", "docs/observability/delivery-seat-log.md",
                "docs/observability/fork-salvage-log.md",
                "docs/observability/trust_ledger.json",
                "docs/observability/decision_log.jsonl",
                "docs/observability/.worker_seat_status"):
        assert td._is_generated(rel, untracked=True), rel


def test_a_TRACKED_document_under_the_mixed_prefix_stays_excluded():
    """`daily-self-note.md` is rewritten in place every morning and is tracked; counting tracked
    churn here is the drowning the prefix exclusion exists to prevent. Only the untracked-and-
    authored case was ever invisible.

    MUTATION: ignore the `untracked` argument and this fails."""
    assert td._is_generated("docs/observability/daily-self-note.md", untracked=False)
    assert td._is_generated("docs/observability/DIRECTOR_REPORT_2026-08-20.md", untracked=False)


def test_the_porcelain_wiring_actually_reaches_the_predicate(tmp_path):
    """END-TO-END against a real repo, because the predicate being right proves nothing if the
    `??` flag never reaches it -- that is exactly where a fail-open lives.

    MUTATION: pass a constant for `untracked` in `_changed_paths_or_reason` and this fails."""
    import subprocess

    def git(*a):
        subprocess.run(["git", *a], cwd=str(tmp_path), capture_output=True, check=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    obs = tmp_path / "docs" / "observability"
    obs.mkdir(parents=True)
    (obs / "seed.txt").write_text("x")
    git("add", "-A")
    git("commit", "-qm", "seed")

    (obs / "DIRECTOR_REPORT_2026-08-20.md").write_text("a report to the director")
    (obs / "supervisor-log.md").write_text("- machine line")
    (obs / "trust_ledger.json").write_text("{}")

    found = td.changed_paths(tmp_path)
    assert found == ["docs/observability/DIRECTOR_REPORT_2026-08-20.md"], found


def test_real_source_is_not_excluded():
    """The mirror: an exclusion list broad enough to quieten the measure would hide the defect."""
    for rel in ("simulation/live_population.py", "company/interfaces/supply_book.py",
                "docs/design/KNIFE_HOTSPOT_PASSES.md", "tests/background/test_x.py"):
        assert not td._is_generated(rel), rel


# ── attribution is honest about what it does not know ────────────────────────────────────────
def test_lane_attribution_uses_the_declared_file_scope():
    index = {"background/supervisor.py": "H_harness"}
    assert td.lane_for("background/supervisor.py", index) == "H_harness"


def test_an_undeclared_path_is_labelled_unattributed_never_guessed():
    """Many atoms carry `file_scope: []`. A measure that guessed a lane would be inventing an
    accusation. MUTATION: make lane_for fall back to a real lane name and this fails."""
    lane = td.lane_for("simulation/whatever.py", {})
    assert lane.startswith("unattributed:"), lane


def test_the_measure_publishes_its_own_attribution_coverage():
    """If attribution is mostly guesswork the reader must be able to see that from the artefact
    itself, rather than trusting a by-lane table that covers a third of the files."""
    m = td.measure()
    assert m["attributed_files"] + m["unattributed_files"] == m["total_files"]


# ── it can never punish ──────────────────────────────────────────────────────────────────────
def test_the_publish_path_helper_returns_nothing_blockable(tmp_path):
    """"never punished via the public site": write_artifact returns a path, not a verdict, and
    swallows its own errors. Nothing here can hand the publish path a reason to refuse.

    WRITTEN TO TMP SINCE 2026-08-31, and the destination is not what this asserts. It used to write
    the LIVE `docs/observability/tree_divergence.json` -- so every run of this test replaced the
    real divergence measurement with one taken over whatever the test tree happened to look like.
    `docs/observability` became a protected surface that day, after 6,421 lines of one ledger
    turned out to be pytest output and a reader of it reported a usage limit that never existed.
    What is asserted here is that the helper RETURNS A PATH THAT EXISTS rather than a verdict; the
    real measurement of record must come from a real publish cycle."""
    m = td.measure()
    assert isinstance(m, dict)
    out = td.write_artifact(m, tmp_path / "tree_divergence.json")
    assert out.exists()


def test_write_artifact_never_raises_on_an_unwritable_path(tmp_path):
    """It runs inside the publish path; an observer that can raise into what it observes is a
    defect. MUTATION: remove the try/except and this fails."""
    bad = tmp_path / "nope" / "\x00" / "x.json"
    td.write_artifact({"total_files": 0}, bad)   # must not raise


# ── AN UNAVAILABLE CHECK IS A FAILED CHECK, NEVER A CLEAN TREE ───────────────────────────────
# WORKER_FINDING_TREE_DIVERGENCE_FAILS_OPEN_TO_A_CLEAN_TREE_2026-08-10 (BLOCKING, R15 FAIL-OPEN).
# `changed_paths` returned [] when `git status` exited non-zero, so `measure()` reported
# total_files 0, `breaches()` returned [] and the daily naming said nothing. The artefact at
# HEAD proves it fired that way: docs/observability/tree_divergence.json at measured_at
# 1786333430 recorded a clean tree that a hand re-run six minutes later measured at 346 files.
# This module is the ENTIRE accountability half of DIRECTOR_RULING_PUBLISH_GATE_SUBJECT
# 2026-08-09 ("squatting gets named daily"), so a silent clean bill of health makes the ruling's
# cost side inert. R15's third killer pattern, verbatim: an unavailable check is a FAILED check.

def test_changed_paths_says_unknown_not_nothing_when_git_cannot_answer(tmp_path):
    """UN-MOCKED, because both sides of a seam mocked is how this class hides: a real directory
    that is genuinely not a git repo, with the real subprocess call.

    MUTATION: restore `return []` in the rc!=0 branch and this fails."""
    assert not (tmp_path / ".git").exists(), "precondition: not a repo"
    assert td.changed_paths(tmp_path) is None, \
        "a git read that FAILED must not be indistinguishable from a clean tree"


def test_measure_marks_itself_unavailable_rather_than_reporting_a_clean_tree(tmp_path):
    """The observed artefact's exact shape is what must become impossible."""
    m = td.measure(project_dir=tmp_path)
    assert m["unavailable"] is True
    assert m.get("total_files") != 0, "reporting 0 IS the defect"


def test_an_unavailable_measure_omits_the_counts_so_no_reader_can_read_it_as_zero(tmp_path):
    """Omitted, not zeroed. A reader that has never heard of `unavailable` must get a loud
    KeyError, never a quiet 0 -- that asymmetry is the whole repair.

    MUTATION: emit `total_files: 0` alongside the flag and this fails."""
    m = td.measure(project_dir=tmp_path)
    for absent in ("total_files", "attributed_files", "unattributed_files", "oldest_age_hours"):
        assert absent not in m, "{} must be omitted, not zeroed".format(absent)


def test_breaches_names_the_unavailability_as_its_own_breach():
    """The daily naming still fires, saying the TRUE thing.

    MUTATION: drop the unavailable branch from breaches() and this fails."""
    found = td.breaches({"unavailable": True, "unavailable_reason": "git status rc=128"})
    assert found, "an unmeasurable tree must still be named"
    assert any("could not be measured" in b for b in found), found
    assert any("rc=128" in b for b in found), "name WHY, so the reader can act: {}".format(found)


def test_an_unavailable_measure_is_not_confusable_with_a_quiet_clean_tree():
    """Independence: the silent case and the failed case must produce different verdicts, or
    the caller cannot tell them apart -- which is the finding, restated as a test."""
    clean = td.breaches({"total_files": 0, "oldest_age_hours": 0.0, "oldest_path": None,
                         "armed_reverts": 0})
    failed = td.breaches({"unavailable": True, "unavailable_reason": "git status rc=128"})
    assert clean == [] and failed != []


def test_a_git_timeout_is_unavailable_too_not_clean(monkeypatch):
    """The finding's named live failure mode: `git status` contends with a shared index and a
    live tree lock several times an hour, so the 60s timeout is reachable. An exception escaping
    into the publish path's blanket `except` is the same silence wearing a different coat.

    MUTATION: narrow the except to CalledProcessError and this fails."""
    import subprocess as _sp

    def _timeout(*a, **kw):
        raise _sp.TimeoutExpired(cmd="git status", timeout=60)

    monkeypatch.setattr(td.subprocess, "run", _timeout)
    assert td.changed_paths(td.PROJECT_DIR) is None
    assert td.measure(project_dir=td.PROJECT_DIR)["unavailable"] is True


def test_top_squatters_survives_an_unavailable_measure():
    """It is called in the same log line as the counts; an observer that raises into the publish
    path it observes is itself a defect (this module's own docstring)."""
    assert td.top_squatters({"unavailable": True, "unavailable_reason": "x"})


def test_the_publish_path_NAMES_an_unavailable_measure_instead_of_swallowing_it(monkeypatch):
    """THE DEFECT ONE LAYER UP. `_publish_tree_divergence` logs the counts before it calls
    `breaches()`, and wraps its whole body in `except Exception` so it can never raise into the
    publish path. So a measure that omits the counts would KeyError into that blanket except and
    the naming would go silent again -- the fail-open repaired in the module and reinstated in
    its only caller. This is the consumer-verified half (R1): the notify must actually fire.

    MUTATION: restore the unconditional `m["total_files"]` log line and this fails."""
    from background import notify as notify_mod
    from background import process_run_complete as prc

    sent = []
    monkeypatch.setattr(td, "measure",
                        lambda *a, **kw: {"unavailable": True,
                                          "unavailable_reason": "git status rc=128"})
    monkeypatch.setattr(td, "write_artifact", lambda *a, **kw: None)
    monkeypatch.setattr(prc, "log", lambda *a, **kw: None)
    monkeypatch.setattr(notify_mod, "notify", lambda msg, **kw: sent.append(msg))

    prc._publish_tree_divergence()

    assert sent, "an unmeasurable tree must be NAMED, not swallowed by the observer's own except"
    assert "could not be measured" in sent[0], sent
    assert "rc=128" in sent[0], sent


def test_the_check_exit_code_fires_on_an_unmeasurable_tree(tmp_path, capsys):
    """--check is the cron/human caller. An unavailable measure must exit non-zero, or the
    failure is invisible at the only place a person looks.

    MUTATION: make main() treat unavailable as success and this fails."""
    import background.tree_divergence as mod
    monkey = mod.measure
    try:
        mod.measure = lambda *a, **kw: {"unavailable": True, "unavailable_reason": "git rc=128"}
        assert mod.main(["--check"]) == 1
        assert "could not be measured" in capsys.readouterr().out
    finally:
        mod.measure = monkey


# ── severity: how far over the line, and whether the reader hears it ─────────────────────────

def _m(files: int, age: float) -> dict:
    """A measure shaped like the real one, for the two fields severity reads."""
    return {"total_files": files, "oldest_age_hours": age, "by_lane": {},
            "attributed_files": 0, "unattributed_files": files,
            # `breaches()` names the oldest path, and the publish path calls it before notify.
            # Omitting it here made the routing tests fail inside that function's blanket
            # `except Exception` -- a fixture gap presenting exactly like a silent control.
            "oldest_path": "tests/simulation/test_policy_cost_coverage.py"}


def test_severity_is_quiet_for_an_ordinary_breach():
    """R15 BOTH WAYS. If `severe` cannot come back False it is a constant, and hoisting
    everything re-teaches the same skimming habit one volume up."""
    s = td.severity(_m(td.FILE_COUNT_THRESHOLD + 2, td.AGE_HOURS_THRESHOLD + 1))
    assert s["severe"] is False
    assert s["worst_multiple"] < td.ESCALATION_MULTIPLE


def test_severity_fires_on_the_breach_it_was_written_for():
    """The real 2026-08-26 state: 436 files against a 15 line, oldest 158.6h against 4h."""
    s = td.severity(_m(436, 158.6))
    assert s["severe"] is True
    assert s["file_multiple"] == 29.1
    assert s["age_multiple"] == 39.6
    assert "29.1x the file line" in s["reason"]
    assert "39.6x the age line" in s["reason"]


def test_either_axis_alone_is_enough():
    """A handful of files sitting for a week is the same disease as a week's worth at once --
    the age axis must be able to escalate on its own, and vice versa."""
    assert td.severity(_m(3, td.AGE_HOURS_THRESHOLD * 20))["severe"] is True
    assert td.severity(_m(td.FILE_COUNT_THRESHOLD * 20, 0.1))["severe"] is True


def test_an_unmeasurable_tree_is_severe_not_quiet():
    """The one state where the reader most needs to hear something is the state a fail-open
    swallows. It has no multiples to report and must still escalate."""
    s = td.severity({"unavailable": True, "unavailable_reason": "git rc=128"})
    assert s["severe"] is True
    assert s["worst_multiple"] is None
    assert "FAILED check" in s["reason"]


def test_a_severe_breach_leaves_the_digest_and_arrives_as_itself(monkeypatch):
    """THE WHOLE POINT (R1, consumer-verified). Severity is worth nothing if the caller still
    batches it: the six-day absorption happened because `_publish_tree_divergence` chose the
    digest on CATEGORY alone. This asserts the ROUTING, not the grading.

    MUTATION: restore the unconditional `topic_class=notification_digest.DIVERGENCE` and this
    fails on the topic_class assertion while every severity test above stays green -- which is
    exactly the gap that let a correctly-firing control go unheard."""
    from background import notify as notify_mod
    from background import process_run_complete as prc

    sent = []
    monkeypatch.setattr(td, "measure", lambda *a, **kw: _m(436, 158.6))
    monkeypatch.setattr(td, "write_artifact", lambda *a, **kw: None)
    monkeypatch.setattr(td, "top_squatters", lambda *a, **kw: "unattributed:docs (422 files)")
    monkeypatch.setattr(prc, "log", lambda *a, **kw: None)
    monkeypatch.setattr(notify_mod, "notify",
                        lambda msg, **kw: sent.append((msg, kw.get("topic_class"))))

    prc._publish_tree_divergence()

    assert sent, "a severe breach must still be named"
    msg, topic_class = sent[0]
    assert topic_class is None, (
        "a 29x breach was routed to the digest -- `is_instant(None)` is what takes it out")
    # The headline carries the WORST axis (39.6x on age), and the body carries both. The
    # age axis is the one that mattered here: 436 files landed in an afternoon would be work
    # in flight, the same 436 sitting for six and a half days is the disease.
    assert "39.6x OVER" in msg, msg
    assert "29.1x the file line" in msg and "39.6x the age line" in msg, msg
    assert "blocks nothing" in msg, "report-only must survive the escalation"


def test_an_ordinary_breach_still_goes_to_the_digest(monkeypatch):
    """The other half, and the one that keeps G-N3 intact: routing on magnitude must not turn
    every breach into a page. Without this, deleting the `severe` branch entirely would pass."""
    from background import notification_digest
    from background import notify as notify_mod
    from background import process_run_complete as prc

    sent = []
    monkeypatch.setattr(td, "measure",
                        lambda *a, **kw: _m(td.FILE_COUNT_THRESHOLD + 2,
                                            td.AGE_HOURS_THRESHOLD + 1))
    monkeypatch.setattr(td, "write_artifact", lambda *a, **kw: None)
    monkeypatch.setattr(td, "top_squatters", lambda *a, **kw: "H_harness (17 files)")
    monkeypatch.setattr(prc, "log", lambda *a, **kw: None)
    monkeypatch.setattr(notify_mod, "notify",
                        lambda msg, **kw: sent.append((msg, kw.get("topic_class"))))

    prc._publish_tree_divergence()

    assert sent
    msg, topic_class = sent[0]
    assert topic_class == notification_digest.DIVERGENCE, "an ordinary squat must stay batched"
    assert "OVER]" not in msg, "the ordinary case must not borrow the severe prefix"


# ── the base the count is measured against ───────────────────────────────────────────────────
#
# `git status` answers against local HEAD. When HEAD is behind `origin/main`, work that reached
# the trunk renders here as somebody's uncommitted draft, and the two have opposite repairs.
# Measured 2026-09-01 on the shared tree: HEAD 20 behind / 16 ahead, and 21 of the 245 files
# this measure was calling squatters were byte-identical to `origin/main`.


def _git(root):
    def git(*a):
        return subprocess.run(["git", *a], cwd=str(root), capture_output=True,
                              text=True, check=True)
    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    return git


def _repo_with_a_stale_base(tmp_path):
    """A repo whose HEAD is one commit behind `origin/main`, with the upstream copy of a source
    file sitting in the working tree. That file is "modified vs HEAD" and IS the trunk's."""
    git = _git(tmp_path)
    src = tmp_path / "tools" / "thing.py"
    src.parent.mkdir(parents=True)
    src.write_text("v1\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").stdout.strip()
    src.write_text("v2-upstream\n")
    git("add", "-A")
    git("commit", "-qm", "upstream")
    git("update-ref", "refs/remotes/origin/main", git("rev-parse", "HEAD").stdout.strip())
    git("reset", "-q", "--hard", base)
    src.write_text("v2-upstream\n")          # the trunk's bytes, on a HEAD that predates them
    return tmp_path


def test_a_file_identical_to_the_trunk_is_not_reported_as_uncommitted_work(tmp_path):
    """THE DEFECT, NAMED. `background/autonomous_runner.py` was byte-identical to `origin/main`
    and paged four reds through two consecutive operational-layer signals as uncommitted work;
    two of those four tests do not exist at local HEAD at all. The measure must be able to say
    which of its own count is that artefact."""
    m = td.measure(project_dir=_repo_with_a_stale_base(tmp_path))
    assert not m.get("unavailable"), m
    assert "tools/thing.py" in (m["already_on_origin_paths"] or []), m
    assert m["already_on_origin"] == 1, m
    assert m["total_files"] == 1, "precondition: git status still counts it"
    assert any("already on the trunk" in b or "byte-identical to the trunk" in b
               for b in td.breaches(m)), td.breaches(m)


def test_the_stale_base_is_named_even_when_the_count_is_under_the_threshold(tmp_path):
    """The reader who goes and 'finishes' a landed decision is reading a SMALL count. Keying
    this sentence to the file-count breach would make it silent in exactly that case."""
    m = td.measure(project_dir=_repo_with_a_stale_base(tmp_path))
    assert m["total_files"] <= td.FILE_COUNT_THRESHOLD, "precondition: under the file line"
    assert m["base"] == {"behind": 1, "ahead": 0}, m.get("base")
    assert any("behind origin/main" in b for b in td.breaches(m)), td.breaches(m)


def test_a_base_that_exists_but_cannot_be_read_refuses_the_count(tmp_path):
    """R15's third killer, closed the same way this module already closed it for `git status`.
    The ref is there, so this is not the no-remote case; git cannot answer against it, so the
    distance to the trunk is unknown and a confident count would be measured against nothing."""
    git = _git(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "thing.py").write_text("x\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    git("update-ref", "refs/remotes/origin/main", git("rev-parse", "HEAD").stdout.strip())
    # The trunk is there; HEAD is not resolvable, so the DISTANCE between them is unknown.
    # An unborn HEAD is the reachable shape of that: `git status` answers perfectly well, and
    # `rev-list origin/main...HEAD` cannot.
    git("checkout", "-q", "--orphan", "detached-and-unborn")

    assert td.changed_paths(tmp_path) == ["tools/thing.py"], "precondition: git status answers"
    assert td._base_state(tmp_path)[0] is None, "precondition: the base is unreadable, not absent"
    m = td.measure(project_dir=tmp_path)
    assert m.get("unavailable") is True, m
    assert "base" in m["unavailable_reason"], m["unavailable_reason"]
    assert "total_files" not in m, "an unavailable measure must omit the count, never zero it"
    assert td.breaches(m), "an unmeasurable base is its own breach"


def test_a_checkout_with_no_trunk_at_all_still_reports_its_count(tmp_path):
    """SCOPE, BOTH WAYS. The publish gate archives HEAD into a repo with no remote; refusing
    there would red every consumer over a base that does not exist to be stale. It reports the
    count -- and says `no_remote_base` rather than `behind: 0`, which would read as up to date."""
    git = _git(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "thing.py").write_text("x\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    (tmp_path / "tools" / "thing.py").write_text("y\n")

    m = td.measure(project_dir=tmp_path)
    assert not m.get("unavailable"), m
    assert m["total_files"] == 1, m
    assert m["base"] == {"no_remote_base": True}, m.get("base")
    assert m["base"].get("behind") is None, "must never read as 'up to date with the trunk'"


def test_an_untracked_path_that_is_tracked_upstream_is_compared_not_skipped(tmp_path):
    """`git diff origin/main -- <path>` IGNORES an untracked path and reports no difference,
    which would count it as already-landed without comparing anything. That is the commonest
    shape of this artefact -- a file added upstream, absent from the stale HEAD -- so it is the
    one case the cheap implementation gets exactly backwards."""
    git = _git(tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "keep.py").write_text("k\n")
    git("add", "-A")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD").stdout.strip()
    (tmp_path / "tools" / "added_upstream.py").write_text("upstream\n")
    git("add", "-A")
    git("commit", "-qm", "upstream adds a file")
    git("update-ref", "refs/remotes/origin/main", git("rev-parse", "HEAD").stdout.strip())
    git("reset", "-q", "--hard", base)

    # Untracked here, tracked upstream, DIFFERENT bytes: genuinely new work, not the trunk's.
    (tmp_path / "tools" / "added_upstream.py").write_text("mine, not the trunk's\n")
    m = td.measure(project_dir=tmp_path)
    assert m["already_on_origin"] == 0, m
    assert "tools/added_upstream.py" not in (m["already_on_origin_paths"] or []), m

    # Same path, the trunk's bytes: now it IS the trunk's, and must be recognised though untracked.
    (tmp_path / "tools" / "added_upstream.py").write_text("upstream\n")
    m2 = td.measure(project_dir=tmp_path)
    assert m2["already_on_origin"] == 1, m2


# ── the ARMED / IN-PROGRESS population split ──────────────────────────────────────────────────
# `total_files` counts two populations whose remedies are OPPOSITE: novel bytes are work in
# progress and want LANDING; bytes this path already had at an ancestor commit are an armed silent
# revert and want RESTORING. The VAT pair (2bf3ad0aa) sat in the second population and was counted
# as 1 of 272 in the first. See
# WORKER_PREREGISTRATION_WHAT_SPLITTING_DIVERGENCE_INTO_ARMED_AND_IN_PROGRESS_MUST_SHOW_2026-09-02.


def _repo_with_two_versions(tmp_path):
    """A repo where `src/a.py` has v1 then v2 committed, and `src/b.py` has one version."""
    def git(*a):
        subprocess.run(["git", *a], cwd=str(tmp_path), capture_output=True, check=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "a.py").write_text("VERSION = 1\n")
    (src / "b.py").write_text("B = 1\n")
    git("add", "-A")
    git("commit", "-qm", "v1")
    (src / "a.py").write_text("VERSION = 2\n")
    git("add", "-A")
    git("commit", "-qm", "v2 -- the fix that must not be silently reverted")
    return git


def test_a_file_written_back_to_an_ancestor_version_is_named_armed(tmp_path):
    """THE DEFECT THIS EXISTS FOR, end-to-end against a real repo: the tree holds the PARENT of a
    committed fix, so the next pathspec commit including it silently undoes that fix.

    MUTATION: drop the history-confirmation loop in `armed_revert_paths` and return `[]`, and this
    fails."""
    _repo_with_two_versions(tmp_path)
    (tmp_path / "src" / "a.py").write_text("VERSION = 1\n")  # back to the pre-fix parent

    armed, unproven = td.armed_revert_paths(tmp_path, ["src/a.py"])

    assert armed is not None, "git answered; this must not be a refusal"
    assert [r["path"] for r in armed] == ["src/a.py"], armed
    # The commit named is the one whose VERSION the tree is holding -- i.e. what it would revert
    # TO. Asserting "v2" here (the fix that would be undone) was my own first draft and it was
    # wrong about the field's semantics; kept in the record because the message wording depends
    # on which of the two commits this is.
    assert "v1" in armed[0]["subject"], \
        "the reader is told WHICH version the tree would impose, not merely that it would"
    assert unproven == []


def test_novel_in_progress_content_is_NOT_armed(tmp_path):
    """THE LOAD-BEARING LEG. A control that fires on every changed file is not a discriminator, it
    is `git status` with a scarier sentence -- and it would bury the armed file in 272 again.

    MUTATION: make `armed_revert_paths` skip the `sha in present` filter and the history
    confirmation (i.e. return every candidate), and this fails while the test above still passes.
    That pair is what proves the split is real."""
    _repo_with_two_versions(tmp_path)
    (tmp_path / "src" / "a.py").write_text("VERSION = 3  # ordinary work in progress\n")

    armed, unproven = td.armed_revert_paths(tmp_path, ["src/a.py"])

    assert armed == [], "novel bytes are work to LAND, never an armed revert"
    assert unproven == [], "a path whose history was fully searched is not 'unproven'"


def test_the_split_separates_them_in_ONE_measure(tmp_path):
    """Both populations present at once -- the real shape, and the one the count cannot express."""
    _repo_with_two_versions(tmp_path)
    (tmp_path / "src" / "a.py").write_text("VERSION = 1\n")          # armed
    (tmp_path / "src" / "b.py").write_text("B = 99  # in progress\n")  # in progress

    armed, _ = td.armed_revert_paths(tmp_path, ["src/a.py", "src/b.py"])

    assert [r["path"] for r in armed] == ["src/a.py"], armed


def test_an_untracked_file_cannot_be_armed(tmp_path):
    """With no entry at HEAD there is no version to revert TO. Counting it would be a false
    positive on the commonest kind of divergence there is."""
    _repo_with_two_versions(tmp_path)
    (tmp_path / "src" / "new.py").write_text("VERSION = 1\n")  # same bytes as a's ancestor!

    armed, _ = td.armed_revert_paths(tmp_path, ["src/new.py"])

    assert armed == [], \
        "matching bytes at a DIFFERENT path is not this path's own history -- the cheap " \
        "blob-existence filter must not be trusted as the verdict"


def test_armed_reverts_refuses_rather_than_reporting_none_armed_when_git_cannot_answer(tmp_path):
    """FAIL-CLOSED, per this module's own rule. `[]` here would mean 'nothing is armed' and would
    reinstate, one field over, the exact defect `changed_paths` was repaired for.

    MUTATION: return `[], []` instead of `None, []` on the git failure path and this fails."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x")
    assert not (tmp_path / ".git").exists(), "precondition: not a repo"

    armed, _ = td.armed_revert_paths(tmp_path, ["src/a.py"])

    assert armed is None, "an unavailable check is a FAILED check, not 'none armed'"


def test_an_unmeasurable_armed_check_is_named_as_a_failed_check():
    """The refusal has to reach the SURFACE, or failing closed is the same as saying nothing."""
    said = td.breaches({"total_files": 1, "oldest_age_hours": 0.0, "oldest_path": "x",
                        "armed_reverts": None})
    assert any("FAILED check" in s and "ARMED" in s for s in said), said


def test_one_armed_revert_is_named_with_no_threshold_to_hide_behind():
    """ARMED has no dial. One file is not a smaller version of 272; it is a different population,
    and a threshold here would hide exactly the case this exists to catch.

    MUTATION: gate the armed branch on `armed > FILE_COUNT_THRESHOLD` and this fails."""
    said = td.breaches({"total_files": 272, "oldest_age_hours": 0.0, "oldest_path": "x",
                        "armed_reverts": 1,
                        "armed_revert_paths": [{"path": "company/billing/invoice.py",
                                                "commit": "2bf3ad0aa", "subject": "the VAT fix"}]})
    assert any("company/billing/invoice.py" in s and "armed" in s for s in said), said
    assert any("restore to HEAD, do not land" in s for s in said), \
        "naming the file without naming the REMEDY leaves the reader to guess, and the " \
        "intuitive guess (commit it) is the defect"


def test_a_suspect_unproven_within_the_search_depth_is_not_reported_safe():
    """NO SILENT CAPS. A bounded search that reports 'clean' for what it never reached is the
    fail-open this module already carries a scar for."""
    said = td.breaches({"total_files": 3, "oldest_age_hours": 0.0, "oldest_path": "x",
                        "armed_reverts": 0, "armed_revert_unproven": ["src/deep.py"],
                        "armed_revert_search_depth": td.ARMED_REVERT_SEARCH_DEPTH})
    assert any("UNPROVEN, not safe" in s and "src/deep.py" in s for s in said), said
