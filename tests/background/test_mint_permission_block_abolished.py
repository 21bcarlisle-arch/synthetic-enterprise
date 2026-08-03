"""A parked mint blocked ONLY on an abolished director-permission act is SELF-DRAWABLE.

THE DEFECT THIS CLOSES (observed 2026-08-03, director-caught). The 2026-07-29 rip-out taught
`_is_externally_blocked` to ignore an abolished permission `blocked_on` on a MAP ATOM, but nothing
taught the same thing to the parked PLANNER_MINTED_* docs. So the two halves of the machine
disagreed: the map said an atom was drawable while its mint doc said "waiting on the director", and
17 mints sat in `docs/staging/in_progress/` being re-enumerated as OPEN MINTS every tick, each
naming an act — a level ratification, a BUILD-open, a director word authorising activation — that
had not existed for five days.

R15 BOTH WAYS. A control that only ever unblocks is as bad as one that only ever blocks:
  * a permission-only blocker (token OR prose) -> self-drawable;
  * a GENUINE upstream/dependency blocker -> still blocked;
  * a blocker naming a RESERVED real-world consequence -> still blocked, even when it also cites a
    permission token (the reserved half is delegated to `one_way_door`, the sole enumeration).
"""
from __future__ import annotations

import pytest

from background import supervisor


def _mint(tmp_path, name: str, reason_line: str, marker: str = "blocked"):
    ip = tmp_path / "in_progress"
    ip.mkdir(parents=True, exist_ok=True)
    p = ip / f"PLANNER_MINTED_{name}.md"
    p.write_text(f"<!-- SUPERVISOR_DRAW: {marker} -->\n\n# mint {name}\n\nUNBLOCKS ON: {reason_line}\n")
    return p


def _slugs(tmp_path):
    return supervisor._in_progress_minted_slugs(tmp_path)


# ── the abolished acts, in both the token and the English forms found live ────────────────
@pytest.mark.parametrize("reason", [
    "director_level_up (R16 — no self-bump)",
    "director_build_open (H-lane BUILD demotion)",
    "a LEDGER: BUILD_OPEN entry naming this atom",
    "director ratification of the proposed deliberate-and-staying set",
    "a director word authorising live activation",
    "main-session/director design adjudication of exit-criterion §1",
    "director sign-off, console-only",
])
def test_permission_blocked_mint_is_self_drawable(tmp_path, reason):
    _mint(tmp_path, "x", reason)
    assert _slugs(tmp_path)["self_drawable"] == ["PLANNER_MINTED_x.md"]
    assert _slugs(tmp_path)["blocked"] == []


# ── the mutation: genuine blockers must SURVIVE ───────────────────────────────────────────
@pytest.mark.parametrize("reason", [
    "the merit-order / gas-first reconstruction has landed upstream",
    "depends_on SPINE_1, which is not built",
    "the coupled-triad gap for its company twin is unmeasured",
])
def test_genuine_upstream_blocker_still_blocks(tmp_path, reason):
    _mint(tmp_path, "y", reason)
    assert _slugs(tmp_path)["blocked"] == ["PLANNER_MINTED_y.md"]


def test_reserved_real_world_consequence_still_blocks_even_with_a_permission_token(tmp_path):
    """The one exception the ruling kept: if the reason describes real money / real people / a
    public claim / a real person's safety, it blocks even while citing a dead permission token."""
    _mint(tmp_path, "z", "director_build_open -- this one spends real money on the paid feed")
    assert _slugs(tmp_path)["blocked"] == ["PLANNER_MINTED_z.md"]


def test_an_explicit_self_drawable_marker_still_wins(tmp_path):
    _mint(tmp_path, "m", "anything at all", marker="self-drawable")
    assert _slugs(tmp_path)["self_drawable"] == ["PLANNER_MINTED_m.md"]


def test_unreadable_or_unstated_mint_fails_closed_to_blocked(tmp_path):
    """FAIL-CLOSED: an unmarked mint with no stated reason is NOT evidence of drawability -- it
    stays blocked rather than fabricating phantom work (the pre-existing convention, unchanged)."""
    ip = tmp_path / "in_progress"
    ip.mkdir(parents=True, exist_ok=True)
    (ip / "PLANNER_MINTED_bare.md").write_text("# a mint with no marker and no UNBLOCKS line\n")
    assert _slugs(tmp_path)["blocked"] == ["PLANNER_MINTED_bare.md"]
