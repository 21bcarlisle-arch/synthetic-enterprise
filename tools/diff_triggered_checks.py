"""Diff-triggered checks: the third outcome of the CLAUDE.md delete-and-add-back trial.

A CLAUDE.md line whose absence shows may move here instead of staying always-loaded: an item with
a trigger read from the diff, a check, and its lineage. Only items whose trigger matches are read.

An item is a markdown file in the `.claude/rules/` shape: frontmatter `paths:` (the same key and
the same globs Claude Code path-scopes on), plus three keys `.claude/rules` ignores:

    symbols:      regexes; the item fires only if an ADDED line of a path-matching file matches one
    added_only:   true -> fires only on files the diff ADDS (a new module, a new test)
    fired_on:     a past commit that touched what the item guards; the item must fire on it
    claude_md:    phrases locating the CLAUDE.md paragraphs the item would carry (token count)

Items live in `docs/operations/diff_triggered_checks/` while trial E-e runs, where no session
loads them, so neither arm is changed. An item whose trigger is paths only becomes live by `git mv`
into `.claude/rules/`. An item with `symbols` or `added_only` has no loader yet; build one (an
edit-time hook running `match`) only when such an item earns "move" in the trial, not before.

    python3 -m tools.diff_triggered_checks --staged | --commit SHA     items the diff triggers
    python3 -m tools.diff_triggered_checks --verify                     each item fires on fired_on
    python3 -m tools.diff_triggered_checks --tokens                     CLAUDE.md chars that move
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import yaml

REPO = Path(__file__).resolve().parent.parent
CHECKLIST_DIR = REPO / "docs" / "operations" / "diff_triggered_checks"
RULES_DIR = REPO / ".claude" / "rules"
# Measured 15 Nov on this file's own content (trial E-e steer); a ratio, not a tokenizer.
TOKENS_PER_CHAR = 0.416


@dataclass
class Item:
    path: Path
    paths: list[str]
    symbols: list[re.Pattern]
    added_only: bool
    fired_on: str | None
    claude_md: list[str]
    body: str
    rows: list[int] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.stem


@dataclass
class FileChange:
    status: str  # git name-status letter: A, M, D, R...
    path: str
    added: list[str]


def _frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    return yaml.safe_load(head) or {}, body


def load(dirs: tuple[Path, ...] = (CHECKLIST_DIR, RULES_DIR)) -> list[Item]:
    items = []
    for d in dirs:
        for p in sorted(d.glob("*.md")):
            if p.name.upper() == "README.MD":
                continue
            meta, body = _frontmatter(p.read_text())
            items.append(Item(
                path=p,
                paths=list(meta.get("paths") or []),
                symbols=[re.compile(s) for s in meta.get("symbols") or []],
                added_only=bool(meta.get("added_only")),
                fired_on=str(meta["fired_on"]) if meta.get("fired_on") is not None else None,
                claude_md=list(meta.get("claude_md") or []),
                body=body.strip(),
                rows=list(meta.get("claude_md_rows") or []),
            ))
    return items


def _path_matches(path: str, globs: list[str]) -> bool:
    if not globs:
        return True
    p = PurePosixPath(path)
    return any(p.full_match(g) for g in globs)


def fires(item: Item, changes: list[FileChange]) -> bool:
    for ch in changes:
        if ch.status.startswith("D") or not _path_matches(ch.path, item.paths):
            continue
        if item.added_only and not ch.status.startswith("A"):
            continue
        if item.symbols and not any(rx.search(line) for line in ch.added for rx in item.symbols):
            continue
        return True
    return False


def match(items: list[Item], changes: list[FileChange]) -> list[Item]:
    return [i for i in items if fires(i, changes)]


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True,
                          text=True, errors="replace").stdout


def changes_from_git(diff_args: list[str]) -> list[FileChange]:
    """`diff_args` is what follows `git diff`/`git show`: e.g. ["--cached"] or a commit."""
    show = diff_args and not diff_args[0].startswith("-")
    base = ["show", "--format=", "-m", "--first-parent"] if show else ["diff"]
    out: dict[str, FileChange] = {}
    for line in _git(*base, "--name-status", "--no-renames", *diff_args).splitlines():
        status, _, path = line.partition("\t")
        if path:
            out[path] = FileChange(status, path, [])
    current = None
    for line in _git(*base, "-U0", "--no-renames", *diff_args).splitlines():
        if line.startswith("+++ "):
            current = out.get(line[6:]) if line.startswith("+++ b/") else None
        elif line.startswith("+") and current is not None:
            current.added.append(line[1:])
    return list(out.values())


def verify(items: list[Item]) -> list[str]:
    """Each checklist item must fire on the past diff it names, and must not fire on every diff."""
    problems = []
    for item in items:
        if item.path.parent != CHECKLIST_DIR:
            continue
        if not item.fired_on:
            problems.append(f"{item.name}: no fired_on commit -- a trigger never shown to fire")
        elif not fires(item, changes_from_git([item.fired_on])):
            problems.append(f"{item.name}: does not fire on its own fired_on {item.fired_on}")
    return problems


def paragraphs_for(item: Item, claude_md: str) -> list[str]:
    paras = re.split(r"\n\s*\n", claude_md)
    found = []
    for phrase in item.claude_md:
        hit = [p for p in paras if phrase in p]
        if len(hit) != 1:
            raise LookupError(f"{item.name}: {phrase!r} locates {len(hit)} CLAUDE.md paragraphs")
        if hit[0] not in found:
            found.append(hit[0])
    return found


def token_report(items: list[Item], claude_md: str) -> tuple[list[tuple[str, int]], int]:
    seen: set[str] = set()
    rows = []
    for item in items:
        n = 0
        for p in paragraphs_for(item, claude_md):
            if p not in seen:
                seen.add(p)
                n += len(p)
        rows.append((item.name, n))
    return rows, sum(n for _, n in rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staged", action="store_true")
    g.add_argument("--commit")
    g.add_argument("--verify", action="store_true")
    g.add_argument("--tokens", action="store_true")
    a = ap.parse_args(argv)
    items = load()
    if a.verify:
        problems = verify(items)
        for p in problems:
            print(p)
        n = sum(1 for i in items if i.path.parent == CHECKLIST_DIR)
        print(f"{n} checklist items; {n - len(problems)} fire on their own past diff")
        return 1 if problems else 0
    if a.tokens:
        text = (REPO / "CLAUDE.md").read_text()
        checklist = [i for i in items if i.path.parent == CHECKLIST_DIR]
        rows, total = token_report(checklist, text)
        for name, n in rows:
            print(f"{n:6,} chars  {name}")
        print(f"{total:6,} of {len(text):,} CLAUDE.md chars "
              f"(~{round(total * TOKENS_PER_CHAR):,} of ~{round(len(text) * TOKENS_PER_CHAR):,} tokens) "
              f"would load only when triggered")
        return 0
    changes = changes_from_git(["--cached"] if a.staged else [a.commit])
    hits = match(items, changes)
    for item in hits:
        print(f"## {item.name}  ({item.path.relative_to(REPO)})\n{item.body}\n")
    print(f"{len(hits)} of {len(items)} items triggered by {len(changes)} changed paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
