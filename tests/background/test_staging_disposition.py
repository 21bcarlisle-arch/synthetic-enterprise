"""R15 for the canonical mis-park detection (background/staging_disposition) — the ONE definition
both the supervisor draw and the deadman [BLOCKED] net use (2026-07-20 3-hour silent-stall fix)."""
from pathlib import Path

from background.staging_disposition import (
    BLOCKED_MARKER,
    MINT_RELEASER_TOKENS,
    SELF_DRAWABLE_MARKER,
    misparked_actionable_in_progress,
    mint_block_hygiene_violations,
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


# ── MINT-MARKER BLOCK HYGIENE (unstated_reason_block_impossible §3, sibling of the map check) ──
#
# R15 both-ways: the check must FIRE on its own named defects (missing marker / unresolvable releaser
# / empty reason) and must PASS a well-formed block; FAIL-CLOSED on missing/empty; FAIL-SILENT on an
# unreadable doc; and a self-drawable mint is exempt (it is not a block).

_ATOMS = {"W1_6b_merit_order_reconstruction", "E4_something"}


def _mint(d: Path, name: str, body: str) -> Path:
    p = d / name
    p.write_text(body, encoding="utf-8")
    return p


def test_mint_hygiene_passes_wellformed_block(tmp_path):
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_ok_2026-07-28.md",
          f"{BLOCKED_MARKER}\n<!-- BLOCK_RELEASE: director_level_up -- lands at build-quality, level is director's -->\n# body")
    assert mint_block_hygiene_violations(d, known_atom_ids=_ATOMS) == []


def test_mint_hygiene_fires_on_missing_marker(tmp_path):
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_nomarker_2026-07-28.md", f"{BLOCKED_MARKER}\n# blocked but no BLOCK_RELEASE")
    v = mint_block_hygiene_violations(d, known_atom_ids=_ATOMS)
    assert v and "no `<!-- BLOCK_RELEASE" in v[0]


def test_mint_hygiene_fires_on_unmarked_block(tmp_path):
    # an UNMARKED mint is fail-closed to blocked by the draw -> hygiene must require a release marker
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_unmarked_2026-07-28.md", "# no draw marker at all, no BLOCK_RELEASE")
    assert mint_block_hygiene_violations(d, known_atom_ids=_ATOMS)


def test_mint_hygiene_fires_on_unresolvable_releaser(tmp_path):
    # feedback_nonempty_config_referent_existence: a release condition that resolves to nothing
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_bogus_2026-07-28.md",
          f"{BLOCKED_MARKER}\n<!-- BLOCK_RELEASE: someday_maybe -- vague -->\n# body")
    v = mint_block_hygiene_violations(d, known_atom_ids=_ATOMS)
    assert v and "resolves to no known releaser" in v[0]


def test_mint_hygiene_fires_on_empty_reason(tmp_path):
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_noreason_2026-07-28.md",
          f"{BLOCKED_MARKER}\n<!-- BLOCK_RELEASE: director_level_up -->\n# releaser but no reason")
    v = mint_block_hygiene_violations(d, known_atom_ids=_ATOMS)
    assert v and "no reason after the dash" in v[0]


def test_mint_hygiene_resolves_atom_id_releaser(tmp_path):
    # an atom-landing releaser (e.g. ssp -> W1_6b) resolves via the live atom-id set...
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_atomdep_2026-07-28.md",
          f"{BLOCKED_MARKER}\n<!-- BLOCK_RELEASE: W1_6b_merit_order_reconstruction -- unblocks when W1_6b lands -->\n# body")
    assert mint_block_hygiene_violations(d, known_atom_ids=_ATOMS) == []
    # ...and FAILS CLOSED when the map cannot be read (empty id set) -> the atom id resolves to nothing
    assert mint_block_hygiene_violations(d, known_atom_ids=set())


def test_mint_hygiene_resolves_propose_then_proceed(tmp_path):
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_window_2026-07-28.md",
          f"{BLOCKED_MARKER}\n<!-- BLOCK_RELEASE: propose_then_proceed -- window closes 2026-07-29 -->\n# body")
    assert mint_block_hygiene_violations(d, known_atom_ids=_ATOMS) == []


def test_mint_hygiene_exempts_self_drawable(tmp_path):
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_selfd_2026-07-28.md", f"{SELF_DRAWABLE_MARKER}\n# drawable now, not a block")
    assert mint_block_hygiene_violations(d, known_atom_ids=_ATOMS) == []


def test_mint_hygiene_blocked_wins_over_selfdrawable(tmp_path):
    # if BOTH markers are present, blocked wins (mirrors selfdrawable_mint_in_progress) -> needs release
    d = tmp_path / "in_progress"; d.mkdir()
    _mint(d, "PLANNER_MINTED_both_2026-07-28.md", f"{SELF_DRAWABLE_MARKER}\n{BLOCKED_MARKER}\n# both")
    assert mint_block_hygiene_violations(d, known_atom_ids=_ATOMS)


def test_mint_hygiene_fail_silent_unreadable_is_a_violation(tmp_path):
    # an undecodable doc is a FAILED check (FAIL-SILENT closed), never a silent pass
    d = tmp_path / "in_progress"; d.mkdir()
    (d / "PLANNER_MINTED_badbytes_2026-07-28.md").write_bytes(b"\xff\xfe not utf-8 " + BLOCKED_MARKER.encode())
    v = mint_block_hygiene_violations(d, known_atom_ids=_ATOMS)
    assert v and "unreadable" in v[0].lower()


def test_mint_hygiene_missing_dir_and_empty_are_safe(tmp_path):
    assert mint_block_hygiene_violations(tmp_path / "nope", known_atom_ids=_ATOMS) == []
    (tmp_path / "in_progress").mkdir()
    assert mint_block_hygiene_violations(tmp_path / "in_progress", known_atom_ids=_ATOMS) == []


def test_mint_releaser_tokens_superset_of_map():
    # drift guard: every canonical map releaser is a valid mint releaser (mint adds a few, never drops)
    from tests.design.test_maturity_map_facets import KNOWN_RELEASER_TOKENS
    assert set(KNOWN_RELEASER_TOKENS) <= set(MINT_RELEASER_TOKENS)


def test_live_in_progress_mints_are_block_hygienic():
    # the phase-close/commit-gate assertion: every blocked mint parked live carries a resolvable
    # release marker. GREEN after this atom's backfill; a future reason-less mint reds this + its commit.
    ip = Path(__file__).resolve().parents[2] / "docs" / "staging" / "in_progress"
    v = mint_block_hygiene_violations(ip)
    assert not v, "live mint block hygiene:\n  " + "\n  ".join(v)
