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


def _rule_globs(rule_text: str) -> list[str]:
    """Every non-empty glob declared in a rule file's top-of-file `paths:`
    frontmatter block (YAML list form or inline `paths: ["a", "b"]`). Empty
    list ⇒ the rule fires on nothing (see `_rule_fires`).
    """
    m = _FRONTMATTER.match(rule_text)
    if not m:
        return []
    globs: list[str] = []
    in_paths = False
    for line in m.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("paths:"):
            in_paths = True
            inline = stripped[len("paths:"):].strip()  # inline form: paths: ["a", "b"]
            if inline and inline not in ("[]", "[ ]"):
                for part in inline.strip("[]").split(","):
                    g = part.strip().strip("'\"")
                    if g:
                        globs.append(g)
                in_paths = False  # inline form is self-contained on this line
            continue
        if in_paths:
            if stripped.startswith("-"):
                g = stripped[1:].strip().strip("'\"")
                if g:
                    globs.append(g)
            elif stripped and not stripped.startswith("#"):
                in_paths = False  # a new top-level key ended the paths: block
    return globs


def _rule_fires(rule_text: str) -> bool:
    """True iff a path-scoped rule file would actually FIRE: it has a top-of-file
    frontmatter block declaring at least one non-empty `paths:` glob. A rule that
    lost (or never had) its `paths:` frontmatter is INERT — present on disk, firing
    on nothing. That is the FAIL-SILENT decay this atom exists to kill, and it
    survives every naive `is_file()` existence check.
    """
    return bool(_rule_globs(rule_text))


def _glob_prefix_dir(glob: str) -> str:
    """The static directory prefix of a glob — the path up to (not including) the
    first segment containing a wildcard. 'company/**/*.py' -> 'company'. A glob
    whose FIRST segment is already a wildcard ('**/*.py') has no static target
    directory and returns '' (it matches broadly, so it cannot be a dead target).
    """
    parts: list[str] = []
    for seg in glob.split("/"):
        if any(ch in seg for ch in "*?[]"):
            break
        parts.append(seg)
    return "/".join(parts)


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


def rules_targeting_missing_paths(text: str, root: Path = PROJECT_DIR) -> list[str]:
    """A FIRING rule whose `paths:` glob targets a directory that does not exist
    is INERT one level deeper than `inert_rules` catches: its frontmatter is
    non-empty (so `_rule_fires` is True) yet the glob matches ZERO files on disk,
    so the path-scoped reminder never actually loads.

    This is the exact decay H7 exists to guard against — a protected tree
    renamed or removed (the portability doctrine, PORTABILITY_DESIGN_CONSTRAINTS,
    explicitly permits directory renames) leaves the rule glob dangling and the
    epistemic-wall reminder silently dead, with every existence/frontmatter check
    still green. Red-teamed 2026-07-27: a rule declaring `simulation/**/*.py`
    after `simulation/` is renamed passes `inert_rules` today.

    Independence (R15, anti-tautology): the checked value is the real filesystem
    (does the glob's static prefix resolve to a directory), the oracle is the
    glob string the rule itself declares — two independent sources; drift fires.
    Empty list ⇒ every firing rule's glob prefix resolves to a real directory.
    A missing/empty rules directory is `inert_rules`' job (no double-report).
    """
    if not _RULES_DIR_REF.search(text):
        return []
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return []  # inert_rules already reports a missing rules directory
    problems: list[str] = []
    for f in sorted(rules_dir.glob("*.md")):
        for glob in _rule_globs(f.read_text(encoding="utf-8")):
            prefix = _glob_prefix_dir(glob)
            if not prefix:
                continue  # leading-wildcard glob matches broadly; not a dead target
            if not (root / prefix).is_dir():
                problems.append(
                    f".claude/rules/{f.name} declares `paths:` glob '{glob}' whose target "
                    f"directory '{prefix}/' does not exist — the rule fires on nothing "
                    "(a renamed/removed protected tree silently killed the reminder)"
                )
    return problems


def rules_matching_no_files(text: str, root: Path = PROJECT_DIR) -> list[str]:
    """A FIRING rule whose `paths:` glob's static prefix directory EXISTS but
    whose full glob matches ZERO files is INERT one level deeper than
    `rules_targeting_missing_paths` catches: its prefix resolves (so that check
    passes) yet the leaf pattern matches nothing on disk, so the path-scoped
    reminder never actually loads.

    This closes a completeness gap in the *same invariant* the two checks above
    assert — "the rule fires on nothing". `inert_rules` covers no/empty `paths:`;
    `rules_targeting_missing_paths` covers a dead prefix directory; but a glob
    like `company/**/*.py` after every matching file is moved/renamed out (the
    portability doctrine permits reorganisation, not only top-level renames)
    leaves the prefix dir intact while the reminder silently dies — proven
    fail-open against both prior checks, 2026-07-28.

    Independence (R15, anti-tautology): the checked value is the real filesystem
    (does the glob match ≥1 file), the oracle is the glob string the rule itself
    declares — two independent sources. A dead PREFIX is
    `rules_targeting_missing_paths`' job: this check only judges globs whose
    prefix resolves (no double-report). Empty list ⇒ every firing rule's glob
    matches at least one real file.
    """
    if not _RULES_DIR_REF.search(text):
        return []
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return []  # inert_rules already reports a missing rules directory
    problems: list[str] = []
    for f in sorted(rules_dir.glob("*.md")):
        for glob in _rule_globs(f.read_text(encoding="utf-8")):
            prefix = _glob_prefix_dir(glob)
            if prefix and not (root / prefix).is_dir():
                continue  # dead prefix => rules_targeting_missing_paths owns it
            if next(iter(root.glob(glob)), None) is None:
                problems.append(
                    f".claude/rules/{f.name} declares `paths:` glob '{glob}' that matches "
                    "ZERO files on disk — the rule fires on nothing (its target tree was "
                    "reorganised/emptied while the directory itself survived)"
                )
    return problems


def _skill_fires(skill_text: str) -> bool:
    """True iff a SKILL.md would actually register/route: it has a top-of-file
    frontmatter block declaring a non-empty `name:` AND a non-empty
    `description:`. The harness surfaces skills by name (the Skill tool requires
    an EXACT name) and routes to them on description — a SKILL.md present on disk
    but empty, truncated, or missing either field is INERT: the loader cannot
    register or match it, so the procedure moved out of CLAUDE.md into it is
    silently lost. is_file() alone (dangling_pointers) never catches this.
    """
    m = _FRONTMATTER.match(skill_text)
    if not m:
        return False
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        stripped = line.strip()
        for key in ("name:", "description:"):
            if stripped.startswith(key):
                fields[key] = stripped[len(key):].strip()
    return bool(fields.get("name:")) and bool(fields.get("description:"))


def inert_skills(text: str, root: Path = PROJECT_DIR) -> list[str]:
    """Sibling-half of `inert_rules`: a referenced SKILL.md present on disk but
    INERT (no frontmatter, or missing name/description) fires on nothing.

    `dangling_pointers` verifies a referenced SKILL.md EXISTS; it cannot tell a
    live skill from an empty/de-frontmattered file. That is the exact FAIL-SILENT
    decay class `inert_rules` closed for path-scoped rules, on the untested
    SKILLS half — an emptied phase-close/SKILL.md (the phase-close checklist
    moved verbatim OUT of CLAUDE.md) passes is_file() silently while the
    procedure is gone. Only referenced-and-existing skills are checked here; a
    missing skill is `dangling_pointers`' job (no double-report).
    """
    problems: list[str] = []
    for p in referenced_harness_paths(text):
        if "/skills/" not in p:
            continue  # rules are covered by inert_rules; skills only here
        f = root / p
        if not f.is_file():
            continue  # missing => dangling_pointers reports it
        if not _skill_fires(f.read_text(encoding="utf-8")):
            problems.append(
                f"{p} is present but INERT (no frontmatter name/description) — "
                "the harness cannot register or route to it, silently losing its moved-out procedure"
            )
    return problems


def hollow_skills(text: str, root: Path = PROJECT_DIR) -> list[str]:
    """A referenced SKILL.md whose frontmatter FIRES (valid name+description, so
    `inert_skills` passes it) but whose BODY is empty/whitespace-only is INERT
    one level deeper than `inert_skills` catches: the harness registers and
    routes to it on its frontmatter, yet invoking it loads NO procedure — the
    exact "fires on nothing" fail-open, on the skills half.

    This closes a completeness gap in the *same invariant* the rules half now
    asserts at three depths (`inert_rules` no/empty `paths:`,
    `rules_targeting_missing_paths` dead prefix, `rules_matching_no_files` zero
    match). The skills half stopped one depth shallower: a phase-close SKILL.md
    truncated to just its frontmatter (a bad merge/edit emptying the moved-out
    checklist while keeping the header) passes `_skill_fires` — proven fail-open
    against `inert_skills`, 2026-07-28. Sibling-half red-team of the rules
    zero-match hardening (audit the other half of a split mechanism for the same
    class).

    Independence (R15, anti-tautology): the checked value is the real file body
    (does any non-whitespace procedure text exist after the frontmatter), the
    oracle is the frontmatter-fires judgement `_skill_fires` makes from the
    header — two independent regions of the file; an emptied body fires. A
    missing skill is `dangling_pointers`', an unfired-frontmatter skill is
    `inert_skills`' (no double-report). Empty list ⇒ every firing skill has body.
    """
    problems: list[str] = []
    for p in referenced_harness_paths(text):
        if "/skills/" not in p:
            continue  # rules covered by inert_rules; skills only here
        f = root / p
        if not f.is_file():
            continue  # missing => dangling_pointers reports it
        content = f.read_text(encoding="utf-8")
        if not _skill_fires(content):
            continue  # unfired frontmatter => inert_skills owns it (no double-report)
        m = _FRONTMATTER.match(content)
        body = content[m.end():] if m else content
        if not body.strip():
            problems.append(
                f"{p} has firing frontmatter but an EMPTY body — the harness registers "
                "and routes to it yet invoking it loads no procedure (fires on nothing; "
                "its moved-out checklist was truncated/emptied while the header survived)"
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
    problems += rules_targeting_missing_paths(text, root)
    problems += rules_matching_no_files(text, root)
    problems += inert_skills(text, root)
    problems += hollow_skills(text, root)
    return problems


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/claude_md_integrity.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("claude_md_integrity")
    import sys

    issues = check()
    if issues:
        print("CLAUDE.md INTEGRITY FAIL:")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    print("CLAUDE.md integrity OK")
    sys.exit(0)
