#!/usr/bin/env python3
"""CLAUDE.md decay-resistance control (H7_skills_and_rules HARDEN, 2026-07-16).

H7's whole purpose is DECAY-RESISTANCE: procedure moved OUT of CLAUDE.md into
loadable skills/rules so it cannot silently rot as accumulating prose
(MAKE_IT_STICK: "a rule lives in CLAUDE.md AND as enforced code, or not at
all"). But until now the two ACTUAL decay failure modes had no control that
could FAIL on them (R15):

  1. CLAUDE.md re-accumulating past its own declared hard limit
     (35k chars / 200 lines) — the limit was PROSE-ONLY, the exact
     decay-prone form the doctrine warns against. The atom moved ~4k chars
     out to buy headroom; nothing stopped it creeping straight back.
  2. A skill/rule that CLAUDE.md references BY PATH going missing/renamed —
     a dangling pointer silently loses the moved-out procedure, which is
     precisely the "procedure is remembered" illusion this atom exists to
     kill.

This module is the mechanism. It is AUTO-DISCOVERING (R10 class-level): it
does not hardcode which skills/rules to check — it extracts every harness
path CLAUDE.md actually references and verifies each exists, so a NEW
reference added tomorrow is covered with no code change.

Independence (R15, anti-tautology): the checked value is the MEASURED file
(its real char/line count, its real referenced paths resolved against the
real filesystem); the thresholds are fixed DOCTRINE CONSTANTS below, not
derived from the file being checked.

The primary control is the pytest test in
tests/tools/test_claude_md_integrity.py, which fails the green suite on any
violation — so a wrong answer demotes freely and R15's mutation test proves
each check fires on its own named defect.
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CLAUDE_MD = PROJECT_DIR / "CLAUDE.md"

# Doctrine constants (CLAUDE.md "Key learnings": "hard limit: 35k chars /
# 200 lines"). Fixed here, independent of the file measured against them.
MAX_CHARS = 35_000
MAX_LINES = 200

# Matches a concrete harness artefact reference: a skill's SKILL.md or a
# path-scoped rule .md file. Bare-directory mentions (".claude/rules/") are
# intentionally NOT matched here — there is no single intended file to resolve
# for `dangling_pointers`. The bare-directory CLAIM is instead covered by
# `inert_rules` below (see its docstring for why that blind spot mattered).
_HARNESS_REF = re.compile(
    r"\.claude/(?:skills/[A-Za-z0-9_.-]+/SKILL\.md|rules/[A-Za-z0-9_.-]+\.md)"
)

# A bare mention of the path-scoped rules directory. CLAUDE.md references its
# rules ONLY this way ("...fire automatically from `.claude/rules/`..."), never
# by concrete filename — so `dangling_pointers` (concrete-path only) never
# covered them, a fail-open blind spot on exactly the moved-out procedure H7
# built. `inert_rules` closes it.
_RULES_DIR_REF = re.compile(r"\.claude/rules/")

# Frontmatter block at the very top of a rule file: `---\n...\n---`.
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)


def size_violations(text: str) -> list[str]:
    """Return human-readable violations if `text` breaches the hard limit.

    Measures characters (unicode code points, matching the doctrine's "chars"
    — CLAUDE.md contains non-ASCII em-dashes/arrows/£, so bytes != chars) and
    physical lines. Empty list ⇒ within limits.
    """
    violations: list[str] = []
    n_chars = len(text)
    n_lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    if n_chars > MAX_CHARS:
        violations.append(f"CLAUDE.md is {n_chars} chars, over the {MAX_CHARS} hard limit")
    if n_lines > MAX_LINES:
        violations.append(f"CLAUDE.md is {n_lines} lines, over the {MAX_LINES} hard limit")
    return violations


def referenced_harness_paths(text: str) -> list[str]:
    """Every concrete .claude/skills|rules artefact path CLAUDE.md references.

    Auto-discovering: whatever CLAUDE.md points at is what gets checked. Sorted
    + de-duplicated for stable output.
    """
    return sorted(set(_HARNESS_REF.findall(text)))


def dangling_pointers(text: str, root: Path = PROJECT_DIR) -> list[str]:
    """Referenced harness paths that do NOT exist on disk (silent decay)."""
    return [p for p in referenced_harness_paths(text) if not (root / p).is_file()]


def _rule_fires(rule_text: str) -> bool:
    """True iff a path-scoped rule file would actually FIRE: it has a top-of-file
    frontmatter block declaring at least one non-empty `paths:` glob. A rule that
    lost (or never had) its `paths:` frontmatter is INERT — present on disk, firing
    on nothing. That is the FAIL-SILENT decay this atom exists to kill, and it
    survives every naive `is_file()` existence check.
    """
    m = _FRONTMATTER.match(rule_text)
    if not m:
        return False
    in_paths = False
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("paths:"):
            in_paths = True
            inline = stripped[len("paths:"):].strip()  # inline form: paths: ["a", "b"]
            if inline and inline not in ("[]", "[ ]"):
                return True
            continue
        if in_paths:
            if stripped.startswith("-"):
                glob = stripped[1:].strip().strip("'\"")
                if glob:
                    return True
            elif stripped and not stripped.startswith("#"):
                in_paths = False  # a new top-level key ended the paths: block
    return False


def inert_rules(text: str, root: Path = PROJECT_DIR) -> list[str]:
    """Verify the bare-directory rules CLAIM in CLAUDE.md is actually LIVE.

    When CLAUDE.md asserts path-scoped rules "fire automatically from
    `.claude/rules/`", that claim is unbacked unless the directory exists, holds
    at least one rule file, and each rule file actually fires (has firing
    `paths:` frontmatter). Concrete-path discovery (`dangling_pointers`) can't
    cover this — CLAUDE.md never names the rule files — so without this check a
    deleted, emptied, or de-frontmattered rules directory passes silently while
    the claim in CLAUDE.md becomes a lie. Empty list ⇒ the claim holds (or
    CLAUDE.md makes no such claim, in which case there is nothing to verify).
    """
    if not _RULES_DIR_REF.search(text):
        return []
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return ["CLAUDE.md claims path-scoped rules fire from .claude/rules/ but the directory is missing"]
    md_files = sorted(rules_dir.glob("*.md"))
    if not md_files:
        return ["CLAUDE.md claims path-scoped rules fire from .claude/rules/ but it contains no rule files"]
    problems: list[str] = []
    for f in md_files:
        if not _rule_fires(f.read_text(encoding="utf-8")):
            problems.append(
                f".claude/rules/{f.name} is present but INERT (no firing `paths:` frontmatter) — "
                "it fires on nothing, silently losing its path-scoped procedure"
            )
    return problems


def check(text: str | None = None, root: Path = PROJECT_DIR) -> list[str]:
    """Full integrity check. Empty list ⇒ healthy; else the violations."""
    if text is None:
        text = (root / "CLAUDE.md").read_text(encoding="utf-8")
    problems = size_violations(text)
    missing = dangling_pointers(text, root)
    if missing:
        problems.append(
            "CLAUDE.md references harness artefacts that do not exist: "
            + ", ".join(missing)
        )
    problems += inert_rules(text, root)
    return problems


if __name__ == "__main__":
    import sys

    issues = check()
    if issues:
        print("CLAUDE.md INTEGRITY FAIL:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    print("CLAUDE.md integrity OK")
    sys.exit(0)
