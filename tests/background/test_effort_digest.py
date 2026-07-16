"""Tests for background/effort_digest.py -- the LATEST.md digest sink for
G5_effort_sizing_discipline's L2 views (remaining effort, estimate-vs-actual
per lane, XL-decompose signal). Uses a synthetic git repo (same pattern as
tests/tools/test_effort_calibration.py's `synthetic_repo` fixture) carrying
FIXTURE atoms with a `size` field -- real atoms in the live map carry no
`size` yet, so none of this depends on that changing.

Also covers the process_run_complete.py wiring: the 'EFFORT SIZING' block is
managed between HTML-comment markers in LATEST.md, same shape as the
existing 'NAIVE ORGAN asks:' block, and must never be able to break
publishing even if the underlying computation raises.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
import yaml

from background import effort_digest


def _run_git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _commit(cwd, message, timestamp):
    env_ts = f"@{timestamp} +0000"
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        cwd=cwd, check=True, capture_output=True, text=True,
        env={**os.environ, "GIT_AUTHOR_DATE": env_ts, "GIT_COMMITTER_DATE": env_ts},
    )


def _write_map(map_path, atoms):
    map_path.write_text(yaml.safe_dump(atoms, sort_keys=False))


@pytest.fixture
def sized_repo(tmp_path):
    """A tiny synthetic repo with a real level-transition history AND `size`/
    `level_target`/`depends_on` fields set on its fixture atoms -- enough for
    render_digest_section() to exercise the real calibration + sizing path
    end-to-end without touching the live project map."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init", "-q"], repo)
    _run_git(["config", "user.email", "test@example.com"], repo)
    _run_git(["config", "user.name", "Test"], repo)

    design_dir = repo / "docs" / "design"
    design_dir.mkdir(parents=True)
    map_path = design_dir / "maturity_map.yaml"

    atoms = [
        {"id": "Z1_alpha", "lane": "H_harness", "size": "M",
         "level_current": 0, "level_target": 2, "loop_stage": "build",
         "depends_on": []},
        {"id": "Z2_beta", "lane": "H_harness", "size": "S",
         "level_current": 2, "level_target": 2, "loop_stage": "harden",
         "depends_on": []},  # AT target -- excluded from remaining-effort
        {"id": "Z3_big", "lane": "H_harness", "size": "XL",
         "level_current": 0, "level_target": 1, "loop_stage": "build",
         "depends_on": []},  # undecomposed XL -- should flag
    ]
    _write_map(map_path, atoms)
    _run_git(["add", "docs/design/maturity_map.yaml"], repo)
    _commit(repo, "seed map at L0/L2", 2_000_000)

    # Real transitions so calibration_by_lane has something to report.
    atoms[0]["level_current"] = 1
    _write_map(map_path, atoms)
    _run_git(["add", "docs/design/maturity_map.yaml"], repo)
    _commit(repo, "Z1_alpha -> L1", 2_000_000 + 3600 * 3)

    return repo, map_path


def test_render_digest_section_reports_remaining_effort_and_xl_flag(sized_repo):
    repo, map_path = sized_repo
    section = effort_digest.render_digest_section(map_path=map_path, repo_root=repo)
    assert section.startswith("**EFFORT SIZING**")
    assert "R12 anti-goal-seek" in section
    # Z1 (below target, sized M, has a real 3h calibrated actual) and Z3
    # (below target, sized XL -- excluded from the hours total, flagged
    # separately as a decompose signal instead).
    assert "Remaining effort:" in section
    assert "XL decompose signal" in section
    assert "Z3_big" in section


def test_render_digest_section_no_below_target_atoms(tmp_path):
    repo = tmp_path / "repo2"
    repo.mkdir()
    _run_git(["init", "-q"], repo)
    _run_git(["config", "user.email", "test@example.com"], repo)
    _run_git(["config", "user.name", "Test"], repo)
    design_dir = repo / "docs" / "design"
    design_dir.mkdir(parents=True)
    map_path = design_dir / "maturity_map.yaml"
    _write_map(map_path, [
        {"id": "Z1_done", "lane": "H_harness", "level_current": 2, "level_target": 2},
    ])
    _run_git(["add", "docs/design/maturity_map.yaml"], repo)
    _commit(repo, "seed", 3_000_000)

    section = effort_digest.render_digest_section(map_path=map_path, repo_root=repo)
    assert "No below-target atoms." in section


def test_render_digest_section_degrades_when_map_unreadable(tmp_path):
    missing = tmp_path / "does_not_exist.yaml"
    assert effort_digest.render_digest_section(map_path=missing) == ""


# ---------------------------------------------------------------------------
# process_run_complete.py wiring: the EFFORT_SIZING_DIGEST block is managed
# between markers, appended on first run, replaced in place thereafter, and
# NEVER allowed to break publishing even if the underlying computation raises.
# ---------------------------------------------------------------------------
def test_effort_digest_block_appended_and_replaced(tmp_path, monkeypatch):
    from background import process_run_complete as prc

    latest = tmp_path / "LATEST.md"
    latest.write_text("# Status\n\nSome existing content.\n")
    monkeypatch.setattr(prc, "LATEST_MD", latest)

    import background.effort_digest as ed
    monkeypatch.setattr(ed, "render_digest_section", lambda: "**EFFORT SIZING** stub one")

    prc._update_latest_md_effort_section()
    text = latest.read_text()
    assert prc.EFFORT_BLOCK_START in text
    assert "stub one" in text

    monkeypatch.setattr(ed, "render_digest_section", lambda: "**EFFORT SIZING** stub two")
    prc._update_latest_md_effort_section()
    text = latest.read_text()
    assert text.count(prc.EFFORT_BLOCK_START) == 1  # replaced, not duplicated
    assert "stub two" in text
    assert "stub one" not in text


def test_effort_digest_step_never_raises_on_failure(tmp_path, monkeypatch):
    from background import process_run_complete as prc

    latest = tmp_path / "LATEST.md"
    latest.write_text("# Status\n")
    monkeypatch.setattr(prc, "LATEST_MD", latest)
    # Isolate from the real sim-runner-log.md (repo convention -- see e.g.
    # tests/tools/test_website_integrity_fix.py's identical comment).
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")

    import background.effort_digest as ed

    def _boom(*a, **kw):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr(ed, "render_digest_section", _boom)
    # Must swallow the failure -- the digest can never break the publish cycle.
    prc.run_effort_digest_step()
