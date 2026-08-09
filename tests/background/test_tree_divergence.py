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
