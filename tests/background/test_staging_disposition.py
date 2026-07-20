"""R15 for the canonical mis-park detection (background/staging_disposition) — the ONE definition
both the supervisor draw and the deadman [BLOCKED] net use (2026-07-20 3-hour silent-stall fix)."""
from background.staging_disposition import misparked_actionable_in_progress


def test_detects_worker_misparked_actionable_but_not_blocked_or_director_parked(tmp_path):
    d = tmp_path / "in_progress"
    d.mkdir()
    # mis-parked: worker banner + actionable-now -> FLAGGED (the anti-pattern)
    (d / "MISPARK.md").write_text(
        "> **[IN-PROGRESS DISPOSITION -- 2026-07-20 worker tick]**\n"
        "> Open sub-item (DISCOVER/FRAME, authorised NOW): build the value frontier.\n")
    # genuinely blocked worker park: real wall, no 'authorised NOW' -> NOT flagged
    (d / "BLOCKED.md").write_text(
        "> **[IN-PROGRESS DISPOSITION -- worker tick]**\n"
        "> AWAITING DIRECTOR: generator wiring is director-reserved; blocked on his act.\n")
    # director-parked multi-part: no worker banner at all -> NOT flagged
    (d / "DIRECTOR.md").write_text("# DIRECTOR STEER\n> Open sub-item: awaiting the director.\n")
    assert misparked_actionable_in_progress(d) == ["MISPARK.md"]


def test_missing_dir_and_empty_are_safe(tmp_path):
    assert misparked_actionable_in_progress(tmp_path / "nope") == []
    (tmp_path / "in_progress").mkdir()
    assert misparked_actionable_in_progress(tmp_path / "in_progress") == []
