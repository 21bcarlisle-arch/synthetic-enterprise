"""Efficiency trial E-e writes a minimal CLAUDE.md into the seat executor's worktree on half its Opus
turns. These fire if the trial cannot assign one of its arms, if the draft survives the turn, or if a
session could land the draft over the live file."""
from __future__ import annotations

import subprocess
from pathlib import Path

from background import claude_md_integrity
from background import seat_executor as se
from background.model_tier import OPUS, SONNET


def test_every_arm_is_reachable_and_the_pilot_is_not_a_second_variable():
    inside = {se.claude_md_arm(f"item-{i}", OPUS, today="2026-11-22") for i in range(64)}
    assert inside == {"minimal", "full"}
    assert se.claude_md_arm("item-1", SONNET, today="2026-11-22") == "off"
    assert se.claude_md_arm("item-1", OPUS, today="2026-11-20") == "off"
    assert se.claude_md_arm("item-1", OPUS, today=se.CLAUDE_MD_TRIAL_WINDOW[1]) == "off"


def test_the_draft_is_written_for_the_turn_and_the_base_bytes_come_back(tmp_path):
    run = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)  # noqa: E731
    run("init", "-q")
    (tmp_path / "CLAUDE.md").write_text("FULL\n")
    draft = tmp_path / se.CLAUDE_MD_TRIAL_DRAFT
    draft.parent.mkdir(parents=True)
    draft.write_text("MINIMAL\n")
    run("add", "."), run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
    assert se._apply_claude_md_arm(tmp_path, "minimal")
    assert (tmp_path / "CLAUDE.md").read_text() == "MINIMAL\n"
    se._restore_claude_md(tmp_path, "HEAD")
    assert (tmp_path / "CLAUDE.md").read_text() == "FULL\n"
    assert not se._apply_claude_md_arm(tmp_path, "full")


def test_the_draft_cannot_land_as_claude_md():
    """The pre-commit gate runs claude_md_integrity whenever CLAUDE.md is staged; the trial relies on
    it refusing the draft. Fires if the draft ever passes the full check."""
    root = Path(__file__).resolve().parents[2]
    draft = (root / se.CLAUDE_MD_TRIAL_DRAFT).read_text(encoding="utf-8")
    assert claude_md_integrity.check(draft, root)
