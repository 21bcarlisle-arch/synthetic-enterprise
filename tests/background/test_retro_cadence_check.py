"""Tests for background/retro_cadence_check.py.

Discharges A1_learn_loop_chair's own named L2->L3 gap: the retro/learn-loop
cadence trigger ("~50 phases / 2 weeks since the last retro") was previously
EXHORTATION-ONLY (embedded in .claude/skills/incident-retro/SKILL.md's own
prose + the phase-close checklist), with zero automated staleness check
anywhere in background/. These tests prove the mechanism actually holds:
both thresholds fire independently, the "phase-count proxy" genuinely
distinguishes real level_current promotions from unrelated commit noise
(the atom's own 2026-07-13 follow-up's precise concern), and the module
never crashes on a missing/malformed retrospectives directory or a git
failure -- it fails quiet/informational, matching health_check.py's own
_check_stale_dependencies() posture, never fail-open-silent on a real
stale condition.
"""

import subprocess
from datetime import date, timedelta
from pathlib import Path

import pytest

from background import retro_cadence_check as rcc


def _git(repo: Path, *args: str, env: dict | None = None) -> None:
    import os
    full_env = None
    if env:
        full_env = {**os.environ, **env}
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True, env=full_env,
    )


def _git_commit_backdated(repo: Path, message: str, iso_date: str) -> None:
    """Commit with both author/committer date forced to `iso_date`, so
    git log --since can reliably exclude/include it by design rather than
    depending on real wall-clock timing within a fast test run."""
    _git(
        repo, "commit", "-q", "-m", message,
        env={"GIT_AUTHOR_DATE": iso_date, "GIT_COMMITTER_DATE": iso_date},
    )


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")


class TestLastRetro:
    def test_empty_dir_returns_none(self, tmp_path):
        d = tmp_path / "retrospectives"
        d.mkdir()
        assert rcc.last_retro(d) is None

    def test_missing_dir_returns_none(self, tmp_path):
        assert rcc.last_retro(tmp_path / "does_not_exist") is None

    def test_picks_the_most_recent_dated_file(self, tmp_path):
        d = tmp_path / "retrospectives"
        d.mkdir()
        (d / "2026-07-04-verification-week.md").write_text("x")
        (d / "2026-07-14-evaporated-director-decision.md").write_text("x")
        (d / "2026-07-08-tmux-leak.md").write_text("x")
        path, found_date = rcc.last_retro(d)
        assert path.name == "2026-07-14-evaporated-director-decision.md"
        assert found_date == date(2026, 7, 14)

    def test_ignores_files_not_matching_naming_convention(self, tmp_path):
        d = tmp_path / "retrospectives"
        d.mkdir()
        (d / "README.md").write_text("x")
        (d / "notes.md").write_text("x")
        assert rcc.last_retro(d) is None

    def test_malformed_date_prefix_ignored(self, tmp_path):
        d = tmp_path / "retrospectives"
        d.mkdir()
        (d / "2026-13-99-bad-date.md").write_text("x")
        (d / "2026-07-10-good.md").write_text("x")
        path, found_date = rcc.last_retro(d)
        assert path.name == "2026-07-10-good.md"


class TestPromotionsSince:
    def test_no_maturity_map_returns_zero(self, tmp_path):
        assert rcc.promotions_since(date(2026, 1, 1), tmp_path) == 0

    def test_not_a_git_repo_fails_quiet_returns_zero(self, tmp_path):
        design = tmp_path / "docs" / "design"
        design.mkdir(parents=True)
        (design / "maturity_map.yaml").write_text("- id: x\n  level_current: 1\n")
        # tmp_path is not a git repo -- must not raise.
        assert rcc.promotions_since(date(2026, 1, 1), tmp_path) == 0

    def test_counts_real_promotion_lines_not_raw_commits(self, tmp_path):
        """The atom's own 2026-07-13 follow-up's precise concern: raw commit
        count over-counts against unrelated doc-churn commits. A commit that
        never touches maturity_map.yaml's level_current lines must contribute
        ZERO to the proxy, even though it is a real commit in the window."""
        repo = tmp_path / "repo"
        _init_repo(repo)
        design = repo / "docs" / "design"
        design.mkdir(parents=True)
        map_file = design / "maturity_map.yaml"

        map_file.write_text("- id: atom_a\n  level_current: 0\n")
        _git(repo, "add", "docs/design/maturity_map.yaml")
        # Backdated well BEFORE the `since` cutoff -- this is the baseline
        # state as of the last retro, not itself a promotion to be counted.
        _git_commit_backdated(repo, "seed", "2020-01-01T00:00:00")

        # An unrelated commit (real commit, but must not count) touching a
        # DIFFERENT file -- also backdated before the cutoff for clarity,
        # though its exclusion is really because it never touches
        # maturity_map.yaml's level_current lines at all.
        other = repo / "README.md"
        other.write_text("unrelated churn\n")
        _git(repo, "add", "README.md")
        _git_commit_backdated(repo, "unrelated doc churn", "2020-01-02T00:00:00")

        # A real promotion: level_current 0 -> 1, AFTER the cutoff.
        map_file.write_text("- id: atom_a\n  level_current: 1\n")
        _git(repo, "add", "docs/design/maturity_map.yaml")
        _git_commit_backdated(repo, "promote atom_a to L1", "2026-01-10T00:00:00")

        # A second real promotion in a later commit, also after the cutoff.
        map_file.write_text("- id: atom_a\n  level_current: 2\n")
        _git(repo, "add", "docs/design/maturity_map.yaml")
        _git_commit_backdated(repo, "promote atom_a to L2", "2026-01-11T00:00:00")

        since = date(2026, 1, 1)
        count = rcc.promotions_since(since, repo)
        assert count == 2, f"expected exactly the 2 real promotions, got {count}"

    def test_since_in_the_future_excludes_all_commits(self, tmp_path):
        repo = tmp_path / "repo"
        _init_repo(repo)
        design = repo / "docs" / "design"
        design.mkdir(parents=True)
        (design / "maturity_map.yaml").write_text("- id: a\n  level_current: 1\n")
        _git(repo, "add", "docs/design/maturity_map.yaml")
        _git(repo, "commit", "-q", "-m", "seed")

        far_future = date.today() + timedelta(days=365)
        assert rcc.promotions_since(far_future, repo) == 0


class TestCheckRetroStaleness:
    def test_no_retro_at_all_is_stale(self, tmp_path):
        retro_dir = tmp_path / "retrospectives"
        retro_dir.mkdir()
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        result = rcc.check_retro_staleness(
            today=date(2026, 7, 16), retro_dir=retro_dir, project_dir=project_dir,
        )
        assert result is not None
        assert "never fired" in result

    def test_recent_retro_no_promotions_is_not_stale(self, tmp_path):
        repo = tmp_path / "repo"
        _init_repo(repo)
        retro_dir = repo / "docs" / "retrospectives"
        retro_dir.mkdir(parents=True)
        (retro_dir / "2026-07-14-something.md").write_text("x")
        design = repo / "docs" / "design"
        design.mkdir(parents=True)
        (design / "maturity_map.yaml").write_text("- id: a\n  level_current: 1\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "seed")

        result = rcc.check_retro_staleness(
            today=date(2026, 7, 16), retro_dir=retro_dir, project_dir=repo,
        )
        assert result is None

    def test_stale_by_days_threshold(self, tmp_path):
        repo = tmp_path / "repo"
        _init_repo(repo)
        retro_dir = repo / "docs" / "retrospectives"
        retro_dir.mkdir(parents=True)
        (retro_dir / "2026-06-01-old-retro.md").write_text("x")
        design = repo / "docs" / "design"
        design.mkdir(parents=True)
        (design / "maturity_map.yaml").write_text("- id: a\n  level_current: 1\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "seed")

        # 2026-07-16 is 45 days after 2026-06-01 -- comfortably over the
        # 14-day threshold.
        result = rcc.check_retro_staleness(
            today=date(2026, 7, 16), retro_dir=retro_dir, project_dir=repo,
        )
        assert result is not None
        assert "STALE" in result
        assert "d since last retro" in result

    def test_stale_by_promotion_count_threshold(self, tmp_path):
        repo = tmp_path / "repo"
        _init_repo(repo)
        retro_dir = repo / "docs" / "retrospectives"
        retro_dir.mkdir(parents=True)
        (retro_dir / "2026-07-01-recent-retro.md").write_text("x")
        design = repo / "docs" / "design"
        design.mkdir(parents=True)
        map_file = design / "maturity_map.yaml"
        map_file.write_text("- id: a\n  level_current: 0\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "seed")

        # Manufacture 51 real promotion commits (over the 50 threshold)
        # while staying well within the 14-day time threshold.
        for i in range(1, 52):
            map_file.write_text(f"- id: a\n  level_current: {i}\n")
            _git(repo, "add", "docs/design/maturity_map.yaml")
            _git(repo, "commit", "-q", "-m", f"promotion {i}")

        result = rcc.check_retro_staleness(
            today=date(2026, 7, 3), retro_dir=retro_dir, project_dir=repo,
        )
        assert result is not None
        assert "STALE" in result
        assert "maturity-map promotions since last retro" in result

    def test_within_both_thresholds_returns_none_even_with_some_promotions(self, tmp_path):
        repo = tmp_path / "repo"
        _init_repo(repo)
        retro_dir = repo / "docs" / "retrospectives"
        retro_dir.mkdir(parents=True)
        (retro_dir / "2026-07-10-retro.md").write_text("x")
        design = repo / "docs" / "design"
        design.mkdir(parents=True)
        map_file = design / "maturity_map.yaml"
        map_file.write_text("- id: a\n  level_current: 0\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "seed")
        map_file.write_text("- id: a\n  level_current: 1\n")
        _git(repo, "add", "docs/design/maturity_map.yaml")
        _git(repo, "commit", "-q", "-m", "one real promotion")

        result = rcc.check_retro_staleness(
            today=date(2026, 7, 12), retro_dir=retro_dir, project_dir=repo,
        )
        assert result is None


class TestMain:
    def test_main_returns_zero_when_not_stale(self, monkeypatch, capsys):
        monkeypatch.setattr(rcc, "check_retro_staleness", lambda: None)
        monkeypatch.setattr("sys.argv", ["retro_cadence_check.py"])
        assert rcc.main() == 0
        out = capsys.readouterr().out
        assert "OK" in out

    def test_main_returns_one_when_stale_without_ntfy_flag(self, monkeypatch, capsys):
        monkeypatch.setattr(rcc, "check_retro_staleness", lambda: "Retro cadence STALE: fake reason")
        monkeypatch.setattr("sys.argv", ["retro_cadence_check.py"])
        assert rcc.main() == 1
        out = capsys.readouterr().out
        assert "STALE" in out

    def test_main_with_ntfy_flag_never_raises_even_if_ntfy_unavailable(self, monkeypatch, capsys):
        """The real environment may not have SE_NTFY_TOPIC set (ntfy_utils
        raises loudly at import time in that case) -- main() must catch that
        and degrade to a printed non-fatal notice, never crash the caller."""
        monkeypatch.setattr(rcc, "check_retro_staleness", lambda: "Retro cadence STALE: fake reason")
        monkeypatch.setattr("sys.argv", ["retro_cadence_check.py", "--ntfy"])
        result = rcc.main()
        assert result == 1
        out = capsys.readouterr().out
        assert "STALE" in out
