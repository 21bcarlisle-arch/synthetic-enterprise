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
            if "%ct" in fmt and "%s" in fmt:  # longest_stall: %ct\t%H\t%s (checked first — it
                return "\n".join(f"{c[2]}\t{c[0]}\t{c[1]}" for c in self.commits), None  # contains %H\t%s too
            if "%H\t%s" in fmt:               # verified_work: %H\t%s
                return "\n".join(f"{c[0]}\t{c[1]}" for c in self.commits), None
            if "%ct\t%H" in fmt:              # legacy %ct\t%H
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
# WORK_DEFINITION §1 (2026-07-27) — a HARDEN re-verify NEVER counts as work
# --------------------------------------------------------------------------- #

def test_harden_reverify_excluded_from_substantive_and_split():
    """R15 MUTATION TEST (§1): a HARDEN re-verify commit that touches real code/tests (would
    otherwise class as MACHINERY, or even PRODUCT) is excluded from the substantive count AND the
    product/machinery split. Mutation proof: drop the `is_harden_commit` guard in verified_work and
    the `[HARDEN ...]` commit below (touching company/ = product) inflates product_count to 1 and
    substantive_count to 1 — these assertions go green->red."""
    fake = FakeGit([
        # HARDEN pass touching a PRODUCT path (company/) — the adversarial case: without the
        # exclusion it would count as a PRODUCT commit and read as forward progress.
        ("aaa", "[HARDEN B1_margin_bridge] Rule-0 dial-yield: re-verify + new R15 control",
         3000, ["company/billing/margin.py", "tests/company/test_margin.py"]),
        # HARDEN pass touching MACHINERY, cooldown-stamp form.
        ("bbb", "chore(harden): stamp C13_weather_normalisation cooldown", 2000,
         ["background/supervisor.py"]),
    ])
    vw, err = sm1.verified_work(_runner=fake)
    assert err is None
    assert vw["harden_count"] == 2
    assert vw["substantive_count"] == 0
    assert vw["product_count"] == 0 and vw["machinery_count"] == 0


def test_harden_exclusion_does_not_swallow_real_work():
    """R15 fail-open direction (§1): the exclusion must NOT over-reach. A genuine BUILD commit in
    the same window as HARDEN churn still counts as substantive PRODUCT — only the HARDEN commit is
    excluded, and the counts still partition the substantive set exactly."""
    fake = FakeGit([
        ("aaa", "[HARDEN A1_learn_loop_chair] re-verify exit tests", 3000,
         ["company/strategy/learn_loop.py"]),
        ("bbb", "[build] W2_2 segmentation taxonomy landed", 2000,
         ["saas/segmentation.py", "tests/saas/test_segmentation.py"]),
        ("ccc", "Auto-process run complete", 1000, ["docs/status/LATEST.md"]),
    ])
    vw, err = sm1.verified_work(_runner=fake)
    assert err is None
    assert vw["harden_count"] == 1
    assert vw["republish_count"] == 1
    assert vw["substantive_count"] == 1
    assert vw["substantive_subjects"] == ["[build] W2_2 segmentation taxonomy landed"]
    assert vw["product_count"] == 1 and vw["machinery_count"] == 0
    assert vw["product_count"] + vw["machinery_count"] == vw["substantive_count"]


def test_longest_stall_treats_harden_as_a_gap_not_a_commit():
    """§1 coherence: longest_stall IS the deadman meaningful-commit clock (reused), so a HARDEN
    re-verify must not close a stall either. Two real BUILD commits 120min apart with a HARDEN
    re-verify landing between them → the measured gap is the full 120min (the HARDEN commit does
    NOT split it). Mutation proof: stop excluding HARDEN and the gap collapses to 60min."""
    # times in seconds; newest-first like git log
    fake = FakeGit([
        ("aaa", "[build] later real work", 12000, ["company/a.py"]),
        ("hhh", "[HARDEN X] re-verify", 12000 - 60 * 60, ["company/b.py"]),  # 60min after 'bbb'
        ("bbb", "[build] earlier real work", 12000 - 120 * 60, ["company/c.py"]),
    ])
    st, err = sm1.longest_stall(_runner=fake)
    assert err is None
    assert st["substantive_commits"] == 2
    assert st["gap_minutes"] == 120.0


def test_render_note_reports_harden_exclusion(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    fake = FakeGit([
        ("aaa", "[HARDEN A1_learn_loop_chair] re-verify", 3000, ["company/strategy/learn_loop.py"]),
    ])
    note = sm1.render_note(NOW.isoformat(), _runner=fake)
    assert "1 HARDEN re-verify(s) excluded" in note
    # a HARDEN-only window shows ZERO substantive progress (not masked as work)
    assert "ZERO verified product progress" in note


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

def test_named_and_not_done_line_in_note_and_flags_residue(monkeypatch, tmp_path):
    """§5 (WORK_DEFINITION ruling 2026-07-27): the daily note carries the named-but-unminted
    enumeration as a real consumer — 🔴 when a ruling names unminted work, ✅ when residue empty."""
    _isolate(monkeypatch, tmp_path)
    note = sm1.render_note(NOW.isoformat(), _runner=FakeGit([], fail=False))
    assert "§5 named-but-unminted" in note  # wired into the note (real repo -> ✅ or 🔴)

    root, ip, done = tmp_path / "r", tmp_path / "ip", tmp_path / "dn"
    root.mkdir()
    (root / "DIRECTOR_RULING_T_2026-07-27.md").write_text(
        "# [DIRECTOR-RULING] — t\n\n## WORK THIS CREATES\n\n1. Unminted named work\n", encoding="utf-8")
    line = sm1.named_and_not_done_line(root, ip, done)
    assert "🔴" in line and "1 deliverable" in line and "Unminted named work" in line
    # Empty primary state -> ✅ CHECKED, never a flattering silence.
    assert "✅" in sm1.named_and_not_done_line(tmp_path / "empty1", tmp_path / "empty2", tmp_path / "empty3")


def test_named_and_not_done_line_fails_closed_red(monkeypatch, tmp_path):
    """R15: an unavailable primary-state read is a RED, never a silent green."""
    def boom(*a, **k):
        raise RuntimeError("disk gone")
    monkeypatch.setattr("background.primary_state_scan.named_but_unminted", boom)
    line = sm1.named_and_not_done_line()
    assert "🔴 RED" in line and "unavailable" in line


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


# --------------------------------------------------------------------------- #
# LAW C item 2 (2026-07-27, DIRECTOR_RULING_FAILURE_BIAS_LAWS): the note reports
# EFFECT + cross-checks the tick's enumeration against an INDEPENDENT read of
# in_progress/, so a false "empty / rest-legitimate" is visible from the second
# source. Both-ways: contradiction fires on false-rest; agrees otherwise.
# --------------------------------------------------------------------------- #

def _write_self_drawable(ip, slug):
    ip.mkdir(parents=True, exist_ok=True)
    (ip / f"PLANNER_MINTED_{slug}.md").write_text(
        "<!-- SUPERVISOR_DRAW: self-drawable -->\n# LAW under test\nbody\n")


def test_r17_crosscheck_flags_contradiction_when_enumeration_claims_rest(tmp_path):
    """DIRECTION A: enumeration says REST-LEGITIMATE, but the independent read finds a self-drawable
    mint undrawn -> 🔴 CONTRADICTION (the 42h-stall class, now visible from the note's second source)."""
    ip = tmp_path / "in_progress"
    _write_self_drawable(ip, "failure_bias_law_a")
    rest_line = lambda: ("TICK-NEVER-RESTS law: always-drawable lane WIRED ... REST-LEGITIMATE", None)
    line = sm1.r17_effect_crosscheck(in_progress_dir=ip, _status_fn=rest_line)
    assert "CONTRADICTION" in line and "🔴" in line
    assert "failure_bias_law_a" in line


def test_r17_crosscheck_agrees_when_no_undrawn_mint(tmp_path):
    """DIRECTION B (mutation both-ways): NO self-drawable mint on disk -> ✅ agree, never a false
    contradiction. A mutation that hard-coded the 🔴 would RED here."""
    ip = tmp_path / "in_progress"
    ip.mkdir()
    rest_line = lambda: ("TICK-NEVER-RESTS law: ... REST-LEGITIMATE", None)
    line = sm1.r17_effect_crosscheck(in_progress_dir=ip, _status_fn=rest_line)
    assert "✅" in line and "AGREES" in line
    assert "CONTRADICTION" not in line


def test_r17_crosscheck_no_false_contradiction_when_enumeration_already_flags_must_draw(tmp_path):
    """When the enumeration ITSELF reports MUST-DRAW, the two sources agree that work exists -- so a
    present undrawn mint is an EFFECT line, not a CONTRADICTION (the sources don't disagree)."""
    ip = tmp_path / "in_progress"
    _write_self_drawable(ip, "failure_bias_law_b")
    must_draw = lambda: ("AUTHORIZED-SET enumeration [...] -> MUST-DRAW: forward_discovery", None)
    line = sm1.r17_effect_crosscheck(in_progress_dir=ip, _status_fn=must_draw)
    assert "CONTRADICTION" not in line
    assert "EFFECT" in line and "failure_bias_law_b" in line


def test_r17_crosscheck_reads_independently_of_supervisor_import():
    """INDEPENDENCE: the primitive backing the cross-check imports nothing from supervisor.py."""
    src = (sm1.PROJECT_DIR / "background" / "primary_state_scan.py").read_text(encoding="utf-8")
    import_lines = [ln.strip() for ln in src.splitlines()
                    if ln.strip().startswith(("import ", "from "))]
    assert not [ln for ln in import_lines if "supervisor" in ln], \
        "LAW C independence breach: the primary-state scan imports supervisor"
