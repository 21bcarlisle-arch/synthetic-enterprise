"""SM1 daily self-note tests. Covers the two walls: §2 SEVERANCE (the note writer has no
path into the draw) and R15 FAIL-CLOSED (an unavailable source is a RED, never a silent zero),
plus the §1 honesty decision (mechanical republishes excluded) and the R17 morning-status ask.
"""
from __future__ import annotations

from datetime import datetime, timezone

import background.daily_self_note as sm1

NOW = datetime(2026, 7, 22, 7, 0, tzinfo=timezone.utc)


class FakeGit:
    """Injectable git runner keyed on the shape of the call. `commits` = list of
    (sha, subject, ct, [files]); newest-first like real `git log`."""
    def __init__(self, commits, fail=False):
        self.commits = commits
        self.fail = fail

    def __call__(self, *args):
        if self.fail:
            return None, "git rc=128: fatal: not a git repository"
        if args[0] == "log":
            fmt = args[-1]
            if "%H\t%s" in fmt:
                return "\n".join(f"{c[0]}\t{c[1]}" for c in self.commits), None
            if "%ct\t%H" in fmt:
                return "\n".join(f"{c[2]}\t{c[0]}" for c in self.commits), None
        if args[0] == "show":
            sha = args[-1]
            for c in self.commits:
                if c[0] == sha:
                    return "\n".join(c[3]), None
            return "", None
        return "", None


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(sm1, "NOTE_LOG", tmp_path / "daily-self-note.md")
    monkeypatch.setattr(sm1, "LAST_DATE_STAMP", tmp_path / ".last_date")
    monkeypatch.setattr(sm1, "RATE_LIMITS_SENSOR", tmp_path / ".rate_limits.json")


# --------------------------------------------------------------------------- #
# §2 SEVERANCE — the note writer has NO path into the draw
# --------------------------------------------------------------------------- #

def test_severance_supervisor_never_imports_the_note_writer():
    """The draw (supervisor.py) must never import daily_self_note — no number in the note may
    feed priority/selection/scheduling. Structural, greppable, and load-bearing (§2 HARD LAW)."""
    src = (sm1.PROJECT_DIR / "background" / "supervisor.py").read_text(encoding="utf-8")
    # A docstring MENTION (the R17 note names daily_self_note.py as SM1's home) is fine; an
    # IMPORT is the severance breach. Check import statements only, not prose.
    import_lines = [ln.strip() for ln in src.splitlines()
                    if ln.strip().startswith(("import ", "from "))]
    offenders = [ln for ln in import_lines if "daily_self_note" in ln]
    assert not offenders, f"SEVERANCE BREACH: the draw imports the note writer: {offenders}"


def test_severance_note_writer_only_reads_supervisor_never_the_reverse():
    """daily_self_note may READ draw state (r17_status) but writes only to its own log/stamp/NTFY —
    never to any file the draw consumes. Assert its write targets are note-local."""
    for target in (sm1.NOTE_LOG, sm1.LAST_DATE_STAMP):
        name = target.name
        assert "self_note" in name or "self-note" in name, f"unexpected write target {name}"


# --------------------------------------------------------------------------- #
# §1 — mechanical republishes EXCLUDED (the single most important honesty decision)
# --------------------------------------------------------------------------- #

def test_verified_work_excludes_mechanical_republish():
    fake = FakeGit([
        ("aaa", "Auto-process run complete: report + LATEST.md", 1000,
         ["docs/reports/ANNUAL_REPORT.md", "docs/status/LATEST.md", "site/data/dashboard.json"]),
        ("bbb", "R17 mechanise the always-drawable lane", 2000,
         ["background/supervisor.py", "tests/background/test_forward_discovery_draw.py"]),
    ])
    vw, err = sm1.verified_work(_runner=fake)
    assert err is None
    assert vw["substantive_count"] == 1
    assert vw["republish_count"] == 1
    assert vw["substantive_subjects"] == ["R17 mechanise the always-drawable lane"]


def test_empty_diff_counts_as_republish_not_substantive():
    fake = FakeGit([("ccc", "Merge branch", 1000, [])])
    vw, _ = sm1.verified_work(_runner=fake)
    assert vw["substantive_count"] == 0 and vw["republish_count"] == 1


# --------------------------------------------------------------------------- #
# DIRECTOR-RULING 2026-07-23 — PRODUCT vs MACHINERY split (the headline metric)
# --------------------------------------------------------------------------- #

def test_product_vs_machinery_classification():
    fake = FakeGit([
        ("aaa", "wholesale cover organ", 3000, ["company/wholesale/cover.py"]),
        ("bbb", "supervisor draw fix", 2000, ["background/supervisor.py"]),
        ("ccc", "sim demand curve", 1000, ["simulation/demand.py", "tests/simulation/test_demand.py"]),
    ])
    vw, err = sm1.verified_work(_runner=fake)
    assert err is None
    assert vw["product_count"] == 2 and vw["machinery_count"] == 1
    assert "supervisor draw fix" in vw["machinery_subjects"]
    assert "wholesale cover organ" in vw["product_subjects"]
    # counts partition the substantive set exactly
    assert vw["product_count"] + vw["machinery_count"] == vw["substantive_count"]


def test_file_class_test_inherits_area_and_unknown_defaults_machinery():
    assert sm1._file_class("tests/company/test_billing.py") == "product"
    assert sm1._file_class("tests/background/test_supervisor.py") == "machinery"
    assert sm1._file_class("site/index.html") == "product"
    assert sm1._file_class("some_root_script.py") == "machinery"  # unrecognised → NOT product
    assert sm1._file_class("docs/status/LATEST.md") is None  # non-substantive
    for churn in ("site/data/dashboard.json", "site/state/x.json",
                  "site/shadow/index.html", "site/snapshots/y.json"):
        assert sm1._file_class(churn) is None, f"{churn} must stay churn"  # generated subtrees


def test_site_pages_substantive_but_generated_subtrees_are_churn():
    """Ruling: site PAGES are product & substantive; the auto-process-regenerated subtrees
    (data/state/shadow/snapshots) stay churn (§1) — else auto-process republishes inflate product."""
    fake = FakeGit([
        ("aaa", "SITE V5 pages", 2000, ["site/index.html", "site/company/index.html"]),
        # a realistic auto-process commit: only generated site subtrees + docs churn
        ("bbb", "Auto-process run complete", 1000,
         ["site/data/dashboard.json", "site/state/x.json", "site/shadow/index.html",
          "docs/status/LATEST.md"]),
    ])
    vw, err = sm1.verified_work(_runner=fake)
    assert err is None
    assert vw["substantive_count"] == 1 and vw["republish_count"] == 1
    assert vw["product_count"] == 1  # the SITE V5 page build is product, the republish is not


def test_mixed_commit_is_product_if_any_file_is_product():
    # a commit touching both a machinery and a product file counts as PRODUCT (product is proven,
    # not diluted) — matches _commit_class "any product file"
    assert sm1._commit_class(["background/supervisor.py", "saas/churn.py"]) == "product"
    assert sm1._commit_class(["background/supervisor.py", "hooks/x.py"]) == "machinery"


def test_machinery_only_window_renders_failure_verdict(monkeypatch, tmp_path):
    """R15: the metric must FIRE on its own named defect — a machinery-only day. A day that fixed
    only machinery must render the ruling's 'the day FAILED' verdict, not a flattering green."""
    _isolate(monkeypatch, tmp_path)
    fake = FakeGit([("bbb", "governance meta-fix", 2000, ["background/supervisor.py"])])
    note = sm1.render_note(NOW.isoformat(), _runner=fake)
    assert "PRODUCT: 0" in note
    assert "the day FAILED" in note


def test_product_window_does_not_render_failure_verdict(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    fake = FakeGit([("aaa", "wholesale organ", 2000, ["company/wholesale/cover.py"])])
    note = sm1.render_note(NOW.isoformat(), _runner=fake)
    assert "PRODUCT: 1" in note
    assert "the day FAILED" not in note


# --------------------------------------------------------------------------- #
# R15 — FAIL-CLOSED: an unavailable source is a RED, never a silent zero
# --------------------------------------------------------------------------- #

def test_verified_work_fails_closed_on_git_error():
    vw, err = sm1.verified_work(_runner=FakeGit([], fail=True))
    assert vw is None and err is not None  # NOT (0, None) — a zero would flatter

def test_render_note_shows_red_not_zero_when_git_down(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    note = sm1.render_note(NOW.isoformat(), _runner=FakeGit([], fail=True))
    assert "🔴 RED" in note
    assert "0 substantive" not in note  # must not silently render a flattering zero


# --------------------------------------------------------------------------- #
# R17 morning status (the director's standing ask) + resource inputs
# --------------------------------------------------------------------------- #

def test_r17_status_line_included(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    note = sm1.render_note(NOW.isoformat(), _runner=FakeGit([], fail=False))
    assert "R17 — THE TICK NEVER RESTS" in note
    line, err = sm1.r17_status()
    # real supervisor import in the test env -> the live status line; fail-closed otherwise.
    assert (line and "always-drawable lane" in line) or err

def test_resource_sensor_absent_is_soft_not_red(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)  # sensor path points at a nonexistent tmp file
    res, err = sm1.resource_inputs()
    assert err is None and "not built" in res  # optional -> honest 'not built', not a hard red


# --------------------------------------------------------------------------- #
# Idempotent per day + publishes exactly one NTFY
# --------------------------------------------------------------------------- #

def test_idempotent_per_day_and_one_ntfy(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    sent = []
    fake = FakeGit([("bbb", "real work", 2000, ["background/x.py"])])
    assert sm1.run(now=NOW, send=sent.append, _runner=fake) == "published"
    assert sm1.run(now=NOW, send=sent.append, _runner=fake) == "already_ran_today"
    assert len(sent) == 1  # exactly one morning NTFY, not one per invocation
    assert sm1.NOTE_LOG.read_text().count("## Daily self-note") == 1

def test_force_reruns_same_day(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    fake = FakeGit([("bbb", "real work", 2000, ["background/x.py"])])
    sm1.run(now=NOW, send=lambda m: None, _runner=fake)
    assert sm1.run(force=True, now=NOW, send=lambda m: None, _runner=fake) == "published"
