"""THE TWO SURFACES THAT READ 29 EMPTY MERGES AS HEALTH, and what each now does instead.

Director, 2026-09-02: *"Give the delivery seat that vantage: every orientation reads the last
stretch of commits as a list a person would read -- what landed, what it was, whether the shape is
right -- and treats a run of identical commits, or a stretch with nothing substantive, as a finding
about the machine rather than a sign of health."*

The instrument itself is held by
`test_a_daemon_producing_empty_merges_lit_up_every_liveness_surface.py`. This file holds the two
places that CONSUME it, because a correct instrument nobody reads is the shape that let a reaper
sit unwired from July to September.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import background.deadmans_switch as dms
import background.delivery_seat as seat

# ── the liveness clock ──────────────────────────────────────────────────────────────────────
_LOOP = "merge origin/main: automatic reconciliation in an isolated worktree"


def test_an_empty_commit_does_not_refresh_the_liveness_clock(monkeypatch):
    """THE STALL ALARM STAYED CLEAR FOR THE WHOLE OUTAGE.

    `_is_non_progress_commit` is a denylist of subject PREFIXES -- `chore(`, auto-process, HARDEN.
    The loop's subject matched none of them, so 29 commits that changed nothing whatsoever counted
    as forward progress and the watchdog reported a healthy machine.

    MUTATION: drop the `_commits_that_changed_nothing` leg and this returns 2000.0 -- the empty
    merge -- which is exactly what it did all afternoon.
    """
    monkeypatch.setattr(dms, "_recent_commits",
                        lambda n=200: [(2000.0, _LOOP), (1000.0, "a real change")])
    monkeypatch.setattr(dms, "_commits_that_changed_nothing", lambda: {(2000.0, _LOOP)})
    assert dms._last_meaningful_commit_epoch() == 1000.0


def test_the_subject_leg_is_still_load_bearing(monkeypatch):
    """BOTH LEGS, because neither implies the other: a `chore(` commit that really does write
    files is still not forward progress. Removing the old leg must not be a way to pass."""
    monkeypatch.setattr(dms, "_recent_commits",
                        lambda n=200: [(2000.0, "chore(provenance): banner"), (1000.0, "work")])
    monkeypatch.setattr(dms, "_commits_that_changed_nothing", lambda: set())
    assert dms._last_meaningful_commit_epoch() == 1000.0


def test_an_unreadable_history_leaves_the_subject_leg_standing_alone(monkeypatch):
    """THE LIMIT, ASSERTED SO IT IS DECLARED RATHER THAN DISCOVERED. When the content of the
    history cannot be read, this leg contributes nothing and behaviour is exactly what it was
    before -- not better, and importantly not worse."""
    monkeypatch.setattr(dms, "_recent_commits", lambda n=200: [(2000.0, _LOOP), (1000.0, "work")])
    monkeypatch.setattr(dms, "_commits_that_changed_nothing", lambda: set())
    assert dms._last_meaningful_commit_epoch() == 2000.0


def test_the_leg_never_takes_the_watchdog_down(monkeypatch):
    """A watchdog that dies of its own instrument is worse than one without it."""
    import background.commit_narrative as cn

    def _boom(*a, **kw):
        raise RuntimeError("git exploded")

    monkeypatch.setattr(cn, "read_commits", _boom)
    assert dms._commits_that_changed_nothing() == set()


def test_it_reads_the_real_history_without_raising():
    """The wire, against the actual repository -- `an_unwired_mechanism_has_no_red_state`: an
    ARMED-looking function that never successfully runs reads as "found nothing"."""
    assert isinstance(dms._commits_that_changed_nothing(), set)


# ── the seat's vantage ──────────────────────────────────────────────────────────────────────
def _brief(**over):
    base = {"substantive_count": 0, "levels_recorded": [], "levels_moved": {},
            "director_inputs": [], "findings": {}, "live_direction_age_hours": 1.0,
            "shape": {"available": True, "shape_is_wrong": False, "count": 3,
                      "carrying_work": 3, "changed_nothing": 0, "findings": []}}
    base.update(over)
    return base


def test_a_spinning_machine_is_material_where_it_used_to_read_as_a_quiet_night(monkeypatch):
    """THE INVERSION. `commits_since` classifies substantive BY FILENAME, and `git log
    --name-only` prints no filenames for a merge -- so all 29 scored non-substantive,
    `substantive_count` was 0, and the seat SKIPPED orienting. A machine committing every six
    minutes produced the identical brief to a machine doing nothing.

    MUTATION: remove the `shape_is_wrong` clause and this returns (False, "nothing to orient on").
    """
    material, why = seat.is_material(_brief(shape={
        "available": True, "shape_is_wrong": True, "count": 29, "carrying_work": 0,
        "changed_nothing": 29,
        "findings": [{"kind": "NO_WORK", "detail": "d", "commits": ["a"]},
                     {"kind": "METRONOME", "detail": "d", "commits": ["a"]}]}))
    assert material is True
    assert "NO_WORK" in why and "METRONOME" in why
    assert "machine fault" in why


def test_a_genuinely_quiet_stretch_is_still_not_material():
    """The floor. If this went material on every empty stretch the seat would orient hourly on
    nothing, and the finding would be noise inside a week."""
    material, why = seat.is_material(_brief())
    assert material is False and "nothing this stretch to orient on" in why


def test_a_sound_stretch_of_real_work_is_material_for_the_ORDINARY_reason():
    material, why = seat.is_material(_brief(substantive_count=4))
    assert material is True and "substantive" in why


# ── and the seat must actually SEE it ───────────────────────────────────────────────────────
def test_the_rendered_list_is_above_the_json_and_outside_its_truncation():
    """`brief` is dumped with a 60k cap and `commits` is the first big key, so a long stretch can
    push everything after it off the end -- including the one part meant to be READ. A vantage a
    truncation can silently remove is not a vantage.

    MUTATION: move `rendered` inside the `json.dumps(...)[:60_000]` and this fails, because the
    filler below is larger than the cap.
    """
    brief = _brief(commits=[{"sha": "x" * 40, "subject": "y" * 200} for _ in range(2000)])
    brief["shape"]["rendered"] = "!! 10:25 abcdef123 the loop's own commit"
    text = seat._prompt(brief)
    assert "abcdef123" in text
    assert text.index("abcdef123") < text.index("THE STRETCH, assembled from git")


def test_an_unreadable_shape_says_so_rather_than_reading_as_sound():
    """`fail_closed_on_unreadable_input`. A brief that silently omits the list would read as "the
    shape was checked and was fine", which is the reassuring answer and the wrong one."""
    text = seat._prompt(_brief(shape={"available": False, "why": "ImportError"}))
    assert "COULD NOT BE READ" in text and "ImportError" in text


def test_the_shape_is_built_from_the_real_stretch_and_never_raises():
    """The wire again, on the real repository."""
    since = datetime.now(timezone.utc) - timedelta(hours=6)
    shape = seat.commit_shape(since)
    assert shape["available"] is True
    assert isinstance(shape["count"], int) and "rendered" in shape
