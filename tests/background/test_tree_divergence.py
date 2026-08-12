"""R15 proof for the tree-divergence measure (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09).

The ruling pairs "the gate's subject is a clean checkout of HEAD" with "squatting gets named
daily, never punished via the public site". Removing the punishment removes the only thing that
made uncommitted work visible, so this measure has to be able to FAIL on its own named defect --
a lane holding many source files out of HEAD for hours -- and must never be able to block a
publish.
"""
from __future__ import annotations

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
    assert td.breaches({"total_files": 0, "oldest_age_hours": 0.0, "oldest_path": None}) == []


def test_a_tree_just_under_both_thresholds_is_silent():
    m = {"total_files": td.FILE_COUNT_THRESHOLD, "oldest_age_hours": td.AGE_HOURS_THRESHOLD,
         "oldest_path": "x.py"}
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
def test_the_publish_path_helper_returns_nothing_blockable():
    """"never punished via the public site": write_artifact returns a path, not a verdict, and
    swallows its own errors. Nothing here can hand the publish path a reason to refuse."""
    m = td.measure()
    assert isinstance(m, dict)
    out = td.write_artifact(m, td.PROJECT_DIR / "docs" / "observability" / "tree_divergence.json")
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
    clean = td.breaches({"total_files": 0, "oldest_age_hours": 0.0, "oldest_path": None})
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
    from background import process_run_complete as prc
    from background import notify as notify_mod

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
