"""R15 for the canonical mis-park detection (background/staging_disposition) — the ONE definition
both the supervisor draw and the deadman [BLOCKED] net use (2026-07-20 3-hour silent-stall fix)."""
from background.staging_disposition import (
    BLOCKED_MARKER,
    SELF_DRAWABLE_MARKER,
    misparked_actionable_in_progress,
    selfdrawable_mint_in_progress,
)


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


# --- R15 both-ways for the waived-mint self-drawable-next-step net (2026-07-24) ---

def test_selfdrawable_mint_fires_and_fails_closed(tmp_path):
    """FIRES: a mint parked with the self-drawable marker (no blocked marker) is surfaced so the draw
    can advance it instead of rung-7 over-minting. FAILS-CLOSED four ways: a mint marked blocked, one
    carrying BOTH markers (blocked wins), and one with NO marker all stay parked."""
    d = tmp_path / "in_progress"
    d.mkdir()
    # FIRES: self-drawable next step, no wall
    (d / "MINT_SELF.md").write_text(
        f"{SELF_DRAWABLE_MARKER}\n# [PLANNER-MINTED] scope-2 BUILD\n"
        "> UNBLOCKS: self — no wall; next drawable step is the scope-2 BUILD.\n")
    # FAILS-CLOSED: explicitly marked blocked (director-reserved / CDN wait) -> parked
    (d / "MINT_BLOCKED.md").write_text(
        f"{BLOCKED_MARKER}\n# [PLANNER-MINTED] activation\n"
        "> UNBLOCKS ON: a director word authorising live activation.\n")
    # FAILS-CLOSED: both markers present -> blocked wins -> parked
    (d / "MINT_BOTH.md").write_text(
        f"{SELF_DRAWABLE_MARKER}\n{BLOCKED_MARKER}\n# ambiguous\n")
    # FAILS-CLOSED: no marker at all -> parked (unmarked default is quiet)
    (d / "MINT_UNMARKED.md").write_text(
        "# [PLANNER-MINTED]\n> UNBLOCKS: self; next drawable BUILD step.\n")
    assert selfdrawable_mint_in_progress(d) == ["MINT_SELF.md"]


def test_selfdrawable_mint_excludes_open_campaign_tracked(tmp_path):
    """A doc already drawn via an OPEN campaign in the register must not double-surface."""
    d = tmp_path / "in_progress"
    d.mkdir()
    (d / "TRACKED.md").write_text(f"{SELF_DRAWABLE_MARKER}\n# tracked by an open campaign\n")
    reg = tmp_path / "reg.yaml"
    reg.write_text(
        "campaigns:\n  - status: open\n    doc: docs/staging/in_progress/TRACKED.md\n")
    assert selfdrawable_mint_in_progress(d, reg) == []


def test_selfdrawable_mint_missing_dir_and_empty_are_safe(tmp_path):
    assert selfdrawable_mint_in_progress(tmp_path / "nope") == []
    (tmp_path / "in_progress").mkdir()
    assert selfdrawable_mint_in_progress(tmp_path / "in_progress") == []
