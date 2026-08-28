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


# --- rules_targeting_missing_paths: dead-target glob (one level below inert) ---
# (2026-07-28 HARDEN red-team: inert_rules closed present-but-empty `paths:`, but
# `_rule_fires` returns True on ANY non-empty glob without checking the glob
# targets a real tree. A rule declaring `simulation/**/*.py` after `simulation/`
# is renamed (the portability doctrine permits renames) fires on nothing yet
# passes inert_rules — proven fail-open below. R15 both-ways.)


def test_real_claude_md_rule_globs_all_resolve():
    """LIVE control: every firing rule's `paths:` glob in the real repo points at
    a directory that actually exists (company/ saas/ sim/ simulation/)."""
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert integ.rules_targeting_missing_paths(text, REPO_ROOT) == []


def test_dead_target_glob_fires(tmp_path):
    """FAIL-SILENT mutation: a rule whose glob targets a non-existent tree fires
    on nothing (matches zero files) yet inert_rules passes it — this check must
    catch it."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "simulation_RENAMED/**/*.py"\n---\n\n# Body\n',
    )
    # inert_rules is blind to it (the gap this check closes):
    assert integ.inert_rules(_RULE_CLAIM, tmp_path) == []
    problems = integ.rules_targeting_missing_paths(_RULE_CLAIM, tmp_path)
    assert any("simulation_RENAMED" in p and "does not exist" in p for p in problems)


def test_dead_target_glob_passes_when_tree_exists(tmp_path):
    """The restore direction: the same rule glob passes once its target dir is
    real on disk."""
    (tmp_path / "company").mkdir()
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "company/**/*.py"\n---\n\n# Body\n',
    )
    assert integ.rules_targeting_missing_paths(_RULE_CLAIM, tmp_path) == []


def test_dead_target_check_covers_inline_paths_form(tmp_path):
    """Inline `paths: ["x/**/*.py"]` with a dead target is caught too."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths: ["gone_tree/**/*.py"]\n---\n\n# Body\n',
    )
    assert any("gone_tree" in p for p in integ.rules_targeting_missing_paths(_RULE_CLAIM, tmp_path))


def test_dead_target_check_ignores_leading_wildcard_glob(tmp_path):
    """No false positive: a glob whose first segment is a wildcard ('**/*.py')
    has no static target directory and must not be reported as dead."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "**/*.py"\n---\n\n# Body\n',
    )
    assert integ.rules_targeting_missing_paths(_RULE_CLAIM, tmp_path) == []


def test_dead_target_check_silent_when_no_rules_claim(tmp_path):
    """No claim in CLAUDE.md ⇒ nothing to verify (even with a dead-target rule)."""
    _write_rule(tmp_path / ".claude" / "rules", "wall.md", '---\npaths:\n  - "nope/**/*.py"\n---\n')
    assert integ.rules_targeting_missing_paths("no rules mention", tmp_path) == []


def test_full_check_fires_on_dead_target_glob(tmp_path):
    """End-to-end: check() surfaces a firing-but-dead-target rule."""
    (tmp_path / "CLAUDE.md").write_text(_RULE_CLAIM, encoding="utf-8")
    _write_rule(tmp_path / ".claude" / "rules", "wall.md", '---\npaths:\n  - "ghost/**/*.py"\n---\n')
    assert any("ghost" in p and "does not exist" in p for p in integ.check(root=tmp_path))


def test_glob_prefix_dir_extraction():
    """Unit: static prefix stops at the first wildcard segment."""
    assert integ._glob_prefix_dir("company/**/*.py") == "company"
    assert integ._glob_prefix_dir("a/b/c/*.py") == "a/b/c"
    assert integ._glob_prefix_dir("**/*.py") == ""
    assert integ._glob_prefix_dir("sim/*.py") == "sim"


# --- rules_matching_no_files: zero-match glob (one level below dead-prefix) ----
# (2026-07-28 HARDEN red-team: rules_targeting_missing_paths checks the glob's
# static PREFIX dir exists, but not that the glob matches ≥1 file. A rule glob
# 'company/**/*.rs' (or 'company/**/*.py' after every .py is moved out) has a
# live prefix yet matches zero files — fires on nothing while both prior checks
# pass. Proven fail-open below; this closes the same "fires on nothing"
# invariant those checks assert. R15 both-ways.)


def test_real_claude_md_rule_globs_all_match_files():
    """LIVE control: every firing rule's `paths:` glob in the real repo matches
    at least one file on disk (company/ saas/ sim/ simulation/ are populated)."""
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert integ.rules_matching_no_files(text, REPO_ROOT) == []


def test_zero_match_glob_fires(tmp_path):
    """FAIL-SILENT mutation: a rule whose glob's prefix dir EXISTS but matches no
    files fires on nothing — and BOTH prior checks are blind to it (the gap this
    check closes)."""
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "x.py").write_text("pass")  # prefix populated, but not with .rs
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "company/**/*.rs"\n---\n\n# Body\n',
    )
    # Both prior checks are blind to it:
    assert integ.inert_rules(_RULE_CLAIM, tmp_path) == []
    assert integ.rules_targeting_missing_paths(_RULE_CLAIM, tmp_path) == []
    problems = integ.rules_matching_no_files(_RULE_CLAIM, tmp_path)
    assert any("company/**/*.rs" in p and "ZERO files" in p for p in problems)


def test_zero_match_glob_passes_when_files_present(tmp_path):
    """The restore direction: the same-shape rule passes once a matching file
    exists under the prefix."""
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "x.py").write_text("pass")
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "company/**/*.py"\n---\n\n# Body\n',
    )
    assert integ.rules_matching_no_files(_RULE_CLAIM, tmp_path) == []


def test_zero_match_check_does_not_double_report_dead_prefix(tmp_path):
    """A rule whose PREFIX dir is missing is rules_targeting_missing_paths' job —
    rules_matching_no_files stays silent so the two never double-count."""
    _write_rule(
        tmp_path / ".claude" / "rules",
        "wall.md",
        '---\npaths:\n  - "ghost/**/*.py"\n---\n\n# Body\n',
    )
    assert integ.rules_matching_no_files(_RULE_CLAIM, tmp_path) == []          # silent here
    assert integ.rules_targeting_missing_paths(_RULE_CLAIM, tmp_path) != []    # owned there


def test_zero_match_check_silent_when_no_rules_claim(tmp_path):
    """No claim in CLAUDE.md ⇒ nothing to verify (even with a zero-match rule)."""
    (tmp_path / "company").mkdir()
    _write_rule(tmp_path / ".claude" / "rules", "wall.md", '---\npaths:\n  - "company/**/*.rs"\n---\n')
    assert integ.rules_matching_no_files("no rules mention", tmp_path) == []


def test_full_check_fires_on_zero_match_glob(tmp_path):
    """End-to-end: check() surfaces a firing rule whose glob matches no files."""
    (tmp_path / "CLAUDE.md").write_text(_RULE_CLAIM, encoding="utf-8")
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "x.py").write_text("pass")
    _write_rule(tmp_path / ".claude" / "rules", "wall.md", '---\npaths:\n  - "company/**/*.rs"\n---\n')
    assert any("ZERO files" in p for p in integ.check(root=tmp_path))


# --- inert_skills: sibling-half of inert_rules on the SKILLS side -------------
# (2026-07-27 HARDEN red-team, "audit sibling half for hardened class": the
# 2026-07-27 pass closed present-but-INERT for RULES; dangling_pointers verifies
# a referenced SKILL.md EXISTS but is blind to an empty/de-frontmattered one, so
# an emptied phase-close/SKILL.md — the checklist moved verbatim out of CLAUDE.md
# — passed check() silently. Proven fail-open before the fix. R15 both-ways below.)

_SKILL_CLAIM = "Invoke `.claude/skills/phase-close/SKILL.md` before closing."


def _write_skill(root: Path, name: str, body: str):
    d = root / ".claude" / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(body, encoding="utf-8")


def test_real_claude_md_skills_all_fire():
    """LIVE control: every SKILL.md the real CLAUDE.md references actually fires
    (has frontmatter with a non-empty name + description)."""
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert integ.inert_skills(text, REPO_ROOT) == []


def test_inert_skills_silent_when_no_skill_referenced(tmp_path):
    """No false positive: a doc referencing no SKILL.md triggers no skills check."""
    assert integ.inert_skills("Path-scoped rules fire from `.claude/rules/`.", tmp_path) == []


def test_inert_skills_fires_on_empty_skill_file(tmp_path):
    """FAIL-SILENT mutation: an emptied SKILL.md is inert yet passes is_file()."""
    _write_skill(tmp_path, "phase-close", "")
    problems = integ.inert_skills(_SKILL_CLAIM, tmp_path)
    assert any("INERT" in v and "phase-close" in v for v in problems)


def test_inert_skills_fires_on_skill_with_no_frontmatter(tmp_path):
    _write_skill(tmp_path, "phase-close", "# Phase-close checklist\nbody only, no frontmatter\n")
    assert any("INERT" in v for v in integ.inert_skills(_SKILL_CLAIM, tmp_path))


def test_inert_skills_fires_when_name_or_description_missing(tmp_path):
    """Frontmatter present but missing name (or description) => cannot register/route."""
    _write_skill(tmp_path, "phase-close", "---\ndescription: has a desc but no name\n---\n# Body\n")
    assert any("INERT" in v for v in integ.inert_skills(_SKILL_CLAIM, tmp_path))
    _write_skill(tmp_path, "phase-close", "---\nname: phase-close\n---\n# Body\n")
    assert any("INERT" in v for v in integ.inert_skills(_SKILL_CLAIM, tmp_path))


def test_inert_skills_passes_on_valid_skill(tmp_path):
    _write_skill(
        tmp_path, "phase-close",
        "---\nname: phase-close\ndescription: the phase-close checklist procedure\n---\n\n# Body\n",
    )
    assert integ.inert_skills(_SKILL_CLAIM, tmp_path) == []


def test_inert_skills_does_not_double_report_missing_skill(tmp_path):
    """A missing SKILL.md is dangling_pointers' job, not inert_skills' — the
    latter only judges files that exist, so the two never double-count."""
    assert integ.inert_skills(_SKILL_CLAIM, tmp_path) == []  # file absent => silent here
    assert integ.dangling_pointers(_SKILL_CLAIM, tmp_path)   # dangling reports it


def test_full_check_fires_on_inert_skill(tmp_path):
    """End-to-end: check() surfaces an inert (present-but-empty) skill."""
    (tmp_path / "CLAUDE.md").write_text(_SKILL_CLAIM, encoding="utf-8")
    _write_skill(tmp_path, "phase-close", "")  # exists (not dangling) but inert
    problems = integ.check(root=tmp_path)
    assert any("INERT" in p for p in problems)
    assert not any("do not exist" in p for p in problems)  # not a dangling report


# --- hollow_skills: sibling-half red-team of the RULES zero-match hardening ----
# (2026-07-28 HARDEN: the rules half now catches "fires on nothing" at three
# depths — no/empty paths, dead prefix, zero-match glob. The skills half stopped
# one depth shallower: inert_skills only checks the frontmatter fires, so a
# SKILL.md truncated to JUST its frontmatter (valid name+description, empty body)
# passed check() while the moved-out checklist was gone. Proven fail-open against
# inert_skills before the fix. R15 both-ways below.)


def test_real_claude_md_skills_all_have_body():
    """LIVE control: every referenced SKILL.md has non-empty procedure body."""
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert integ.hollow_skills(text, REPO_ROOT) == []


def test_hollow_skills_silent_when_no_skill_referenced(tmp_path):
    assert integ.hollow_skills("Path-scoped rules fire from `.claude/rules/`.", tmp_path) == []


def test_hollow_skills_fires_on_frontmatter_only_body(tmp_path):
    """FAIL-OPEN mutation: valid frontmatter but empty body passes inert_skills
    yet loads no procedure — hollow_skills must fire where inert_skills is blind."""
    _write_skill(tmp_path, "phase-close", "---\nname: phase-close\ndescription: the checklist\n---\n\n")
    assert integ.inert_skills(_SKILL_CLAIM, tmp_path) == []            # blind here (frontmatter fires)
    problems = integ.hollow_skills(_SKILL_CLAIM, tmp_path)             # owned here
    assert any("EMPTY body" in v and "phase-close" in v for v in problems)


def test_hollow_skills_passes_on_skill_with_body(tmp_path):
    _write_skill(
        tmp_path, "phase-close",
        "---\nname: phase-close\ndescription: the phase-close checklist procedure\n---\n\n# Body\n1. step\n",
    )
    assert integ.hollow_skills(_SKILL_CLAIM, tmp_path) == []


def test_hollow_skills_does_not_double_report_inert_skill(tmp_path):
    """No frontmatter => inert_skills owns it; hollow_skills stays silent so the
    two never double-count the same file."""
    _write_skill(tmp_path, "phase-close", "# body only, no frontmatter\n")
    assert any("INERT" in v for v in integ.inert_skills(_SKILL_CLAIM, tmp_path))  # owned there
    assert integ.hollow_skills(_SKILL_CLAIM, tmp_path) == []                       # silent here


def test_hollow_skills_does_not_double_report_missing_skill(tmp_path):
    assert integ.hollow_skills(_SKILL_CLAIM, tmp_path) == []          # file absent => silent here
    assert integ.dangling_pointers(_SKILL_CLAIM, tmp_path)            # dangling reports it


def test_full_check_fires_on_hollow_skill(tmp_path):
    """End-to-end: check() surfaces a frontmatter-only (hollow) skill without
    double-reporting it as inert or dangling."""
    (tmp_path / "CLAUDE.md").write_text(_SKILL_CLAIM, encoding="utf-8")
    _write_skill(tmp_path, "phase-close", "---\nname: phase-close\ndescription: the checklist\n---\n")
    problems = integ.check(root=tmp_path)
    assert any("EMPTY body" in p for p in problems)
    assert not any("INERT" in p for p in problems)        # not double-reported as inert
    assert not any("do not exist" in p for p in problems)  # not a dangling report


# ── the unit is the claim ────────────────────────────────────────────────────────────────────
#
# DIRECTOR, 2026-08-28: "CLAUDE.md is 35,235 bytes against its own 35,000 hard limit. Either the
# gate didn't fire or the limit moved without me." Neither: the gate fired green, MAX_CHARS has one
# commit in its whole history, and the file was 34,988 CHARACTERS. `wc -c` counts bytes, the
# doctrine says chars, and the two differ by every non-ASCII character in the file.

def test_the_violation_message_names_both_units():
    """A breach message that says only "chars" sends a reader to `wc -c`, which disagrees.

    Fires on: dropping the byte count, or dropping the word CHARS from the limit.
    """
    over = "x" * (integ.MAX_CHARS + 1)
    message = integ.size_violations(over)[0]
    assert "chars" in message and "bytes" in message
    assert "{}-char hard limit".format(integ.MAX_CHARS) in message


def test_the_report_states_the_unit_and_both_counts():
    """Fires on: a report that gives one number, which is how the ambiguity got here."""
    text = "a" * 100 + "£—×" + "\n" * 3
    report = integ.size_report(text)
    assert "chars" in report and "bytes" in report and "lines" in report
    assert "CHARS" in report, "the report does not say which unit the limit is on"
    assert "the limit is not on bytes" in report


def test_bytes_exceed_chars_on_the_real_file_and_the_limit_is_still_chars():
    """THE LIVE STATE that raised the question, pinned so the answer is reproducible.

    Not pinning the exact counts: they move with every edit. Pinning the RELATIONSHIP -- the real
    file contains non-ASCII, so bytes strictly exceed chars, so a byte-based hand-check will keep
    reading high. Fires on: a claim that the two are interchangeable.
    """
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    n_chars = len(text)
    n_bytes = len(text.encode("utf-8"))
    assert n_bytes > n_chars, (
        "CLAUDE.md is pure ASCII, so this test's subject is gone -- if that is deliberate, the "
        "byte/char ambiguity is gone with it and this test should be deleted rather than relaxed")
    assert integ.size_violations(text) == [], integ.size_report(text)
    assert n_chars <= integ.MAX_CHARS < n_bytes or n_bytes <= integ.MAX_CHARS, (
        "the file is over the limit in chars, which is a real breach and not a unit confusion")
