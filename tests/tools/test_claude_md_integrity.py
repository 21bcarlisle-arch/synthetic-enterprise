"""Tests for background/claude_md_integrity.py — the CLAUDE.md decay-resistance
control (H7_skills_and_rules HARDEN, 2026-07-16).

Two roles, both required by R15 ("controls must be able to FAIL"):

  * The LIVE-STATE assertions (test_real_claude_md_*) are the actual control:
    they fail the green suite if the real CLAUDE.md ever breaches its hard
    limit or grows a dangling skill/rule pointer. This is the mechanism that
    replaces the prose-only "hard limit" rule.

  * The MUTATION tests (test_*_fires_on_*) prove each check fires on its own
    named defect — a synthetic over-limit doc, and a synthetic doc pointing at
    a missing skill. A control that cannot fail is worse than none; these show
    it can.
"""
from pathlib import Path

import pytest

from background import claude_md_integrity as integ

REPO_ROOT = Path(__file__).resolve().parents[2]


# --- The live control: the real CLAUDE.md must stay healthy -----------------

def test_real_claude_md_within_hard_limit():
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    violations = integ.size_violations(text)
    assert violations == [], (
        "CLAUDE.md breached its own declared 35k-char / 200-line hard limit — "
        "trim it (move procedure into a skill) before adding more: " + "; ".join(violations)
    )


def test_real_claude_md_has_no_dangling_harness_pointers():
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    missing = integ.dangling_pointers(text, REPO_ROOT)
    assert missing == [], (
        "CLAUDE.md references skills/rules that no longer exist on disk "
        "(the moved-out procedure is silently lost): " + ", ".join(missing)
    )


def test_real_claude_md_actually_references_the_moved_out_skills():
    """Guard against the auto-discovery becoming vacuously true: CLAUDE.md must
    still point at the skills H7 moved its procedure into (if the references
    vanish, dangling_pointers passes trivially and the control checks nothing)."""
    refs = integ.referenced_harness_paths((REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8"))
    assert ".claude/skills/phase-close/SKILL.md" in refs
    assert len(refs) >= 4  # the four skills the atom's own evidence names


def test_full_check_passes_on_real_repo():
    assert integ.check(root=REPO_ROOT) == []


# --- Mutation tests: prove each check FIRES on its named defect (R15) --------

def test_size_check_fires_on_oversize_chars():
    oversize = "x" * (integ.MAX_CHARS + 1)
    violations = integ.size_violations(oversize)
    assert any("char" in v for v in violations), "char-limit check failed to fire"


def test_size_check_fires_on_too_many_lines():
    many_lines = "\n".join(["line"] * (integ.MAX_LINES + 1))
    violations = integ.size_violations(many_lines)
    assert any("line" in v for v in violations), "line-limit check failed to fire"


def test_size_check_passes_at_exactly_the_limit():
    """FAIL-CLOSED edge: the limit itself is allowed, one over is not."""
    at_limit = "a" * integ.MAX_CHARS
    assert integ.size_violations(at_limit) == []
    assert integ.size_violations(at_limit + "a") != []


def test_dangling_pointer_check_fires_on_missing_skill(tmp_path):
    text = "See `.claude/skills/does-not-exist/SKILL.md` for the procedure."
    missing = integ.dangling_pointers(text, tmp_path)
    assert missing == [".claude/skills/does-not-exist/SKILL.md"]


def test_dangling_pointer_check_passes_when_referenced_file_exists(tmp_path):
    skill = tmp_path / ".claude" / "skills" / "real" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("procedure")
    text = "See `.claude/skills/real/SKILL.md`."
    assert integ.dangling_pointers(text, tmp_path) == []


def test_full_check_fires_when_a_referenced_skill_is_missing(tmp_path):
    """End-to-end mutation: a CLAUDE.md-shaped doc pointing at a missing skill
    makes the whole control report a problem, not just the sub-function."""
    (tmp_path / "CLAUDE.md").write_text(
        "Invoke `.claude/skills/phantom/SKILL.md` before closing.", encoding="utf-8"
    )
    problems = integ.check(root=tmp_path)
    assert any("do not exist" in p for p in problems)


def test_bare_directory_reference_is_not_treated_as_a_file(tmp_path):
    """A bare `.claude/rules/` mention (no filename) must not be flagged as a
    dangling pointer — there is no single intended file to resolve."""
    text = "Path-scoped rules fire automatically from `.claude/rules/`."
    assert integ.referenced_harness_paths(text) == []
    assert integ.dangling_pointers(text, tmp_path) == []


# --- inert_rules: close the rules blind spot dangling_pointers can't cover ----
# (2026-07-27 HARDEN red-team: CLAUDE.md references its path-scoped rules ONLY
# as a bare `.claude/rules/` directory, so deleting/emptying/de-frontmattering
# them was invisible to check() — a fail-open on the atom's own moved-out
# procedure. These are the R15 both-ways controls for the new inert_rules check.)

_RULE_CLAIM = "Path-scoped rules fire automatically from `.claude/rules/`."


def _write_rule(dirpath: Path, name: str, body: str):
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / name).write_text(body, encoding="utf-8")


def test_real_claude_md_rules_all_fire():
    """LIVE control: every rule file in the real repo actually fires (has firing
    `paths:` frontmatter) and the real CLAUDE.md's rules claim is backed."""
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert integ.inert_rules(text, REPO_ROOT) == []


def test_inert_rules_silent_when_claude_md_makes_no_rules_claim(tmp_path):
    """No false positive: a doc that never mentions `.claude/rules/` triggers no
    rules check, even if the directory is absent."""
    assert integ.inert_rules("No mention of the rules directory here.", tmp_path) == []


def test_inert_rules_fires_when_rules_dir_missing(tmp_path):
    assert integ.inert_rules(_RULE_CLAIM, tmp_path) != []
    assert any("missing" in v for v in integ.inert_rules(_RULE_CLAIM, tmp_path))


def test_inert_rules_fires_when_rules_dir_empty(tmp_path):
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    problems = integ.inert_rules(_RULE_CLAIM, tmp_path)
    assert any("no rule files" in v for v in problems)


def test_inert_rules_fires_on_rule_with_no_frontmatter(tmp_path):
    """FAIL-SILENT mutation: a rule file present but with NO frontmatter is inert
    — it fires on nothing yet passes every existence check."""
    _write_rule(tmp_path / ".claude" / "rules", "wall.md", "# A rule with no frontmatter\nbody")
    problems = integ.inert_rules(_RULE_CLAIM, tmp_path)
    assert any("INERT" in v and "wall.md" in v for v in problems)


def test_inert_rules_fires_on_rule_with_empty_paths(tmp_path):
    """FAIL-SILENT mutation: frontmatter present but `paths:` has no globs — the
    rule matches no path and never fires."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        "---\npaths:\n---\n\n# Body\n",
    )
    assert any("INERT" in v for v in integ.inert_rules(_RULE_CLAIM, tmp_path))


def test_inert_rules_passes_on_valid_firing_rule(tmp_path):
    """A rule with a real `paths:` glob fires — no violation (list form)."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "company/**/*.py"\n---\n\n# Body\n',
    )
    assert integ.inert_rules(_RULE_CLAIM, tmp_path) == []


def test_inert_rules_passes_on_inline_paths_form(tmp_path):
    """Inline `paths: ["a", "b"]` frontmatter also counts as firing."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths: ["sim/**/*.py"]\n---\n\n# Body\n',
    )
    assert integ.inert_rules(_RULE_CLAIM, tmp_path) == []


def test_full_check_fires_on_inert_rule(tmp_path):
    """End-to-end: check() surfaces an inert rule, not just the sub-function."""
    (tmp_path / "CLAUDE.md").write_text(_RULE_CLAIM, encoding="utf-8")
    _write_rule(tmp_path / ".claude" / "rules", "wall.md", "# no frontmatter\n")
    assert any("INERT" in p for p in integ.check(root=tmp_path))
