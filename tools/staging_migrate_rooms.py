#!/usr/bin/env python3
"""ONE-TIME migration: put docs/staging/ into the rooms `background/staging_rooms.py` names,
and collapse the alarm documents that one condition filed many times.

REUSE: tools/staging_migrate_rooms.py
CLASS: CUSTOM
INDEX: searched "migrat", "collapse", "consolidat", "merge", "move", "staging".
       `background/staging_two_rooms_repair.py` is the nearest analogue and is deliberately
       NOT extended: it resolves a root/done DUPLICATE by deleting the redundant copy, and
       its whole design argument is that a module which deletes must be timid and act on one
       provably-redundant case. This module deletes nothing -- every collapse is a MERGE whose
       output contains every input's instance line, and every relocation is a `git mv`.
       `background/staging_archive_policy.py` moves exhaust into dated partitions and proves
       the count equal before and after; that proof shape is REUSED here (`--check` re-reads
       the tree after the move and refuses a net loss).
       `background/alarm_repetition.py` owns `family()`/`instance()` and they are IMPORTED,
       never re-derived -- if the migration grouped documents by a different rule from the one
       that will file the next document, the collapse would come apart on the next firing.

WHAT IT DOES, AND WHY EACH PART IS SAFE.

1. CLASS_*.md          -> reference/   Standing registers. Never work, never drain.
2. DIRECTOR_CONSOLE_*  -> console/     Verbatim transcripts. Record, not work.
3. Alarm documents     -> collapsed    Grouped by the declared family, merged into the
                                       OLDEST document of each group, which keeps the
                                       original first-seen date and every instance name.

ARCHIVE, NEVER DELETE, binds hardest on step 3, because it is the only one that reduces a
file count. So the merge is additive by construction: the surviving document gains one
`- \\`instance\\` (first seen ...)` line per document folded into it, and the folded documents
move to `done/` with their text intact rather than being removed. A reader who wants the
original sixteen still has all sixteen; what changes is that the QUEUE has one.

IDEMPOTENT. Running it twice moves nothing the second time: relocation skips a file already
in its room, and the collapse skips a group of one.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from background import alarm_repetition as ar  # noqa: E402
from background import staging_rooms as rooms  # noqa: E402

STAGING = REPO_ROOT / "docs" / "staging"


def _git_mv(src: Path, dst: Path, *, dry_run: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return f"WOULD MOVE {src.name} -> {dst.parent.name}/"
    r = subprocess.run(["git", "mv", str(src), str(dst)], cwd=REPO_ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        # A file git does not track cannot be `git mv`'d; a plain rename is the same outcome
        # and the next `git add` picks it up. Reported either way -- a silent fallback is how
        # a migration ends up half-done with nothing saying so.
        src.rename(dst)
        return f"MOVED (untracked) {src.name} -> {dst.parent.name}/"
    return f"MOVED {src.name} -> {dst.parent.name}/"


def relocate(staging: Path = STAGING, *, dry_run: bool = False) -> list[str]:
    """Steps 1 and 2: reference and console documents into their rooms."""
    out: list[str] = []
    for p in sorted(staging.iterdir()):
        if not p.is_file() or p.suffix != ".md":
            continue
        room = rooms.room_for(rooms.kind_of(p.name))
        if room is None:
            continue
        out.append(_git_mv(p, staging / room / p.name, dry_run=dry_run))
    return out


def _alarm_key_of(path: Path) -> str | None:
    """The alarm's DECLARED key, read off the document's own `Signature:` line.

    Read from the document rather than re-derived from its title, because the title is what
    was wrong: `_slug` built it from a message whose prose payload varied, which is the defect
    being migrated. The signature line was written by `escalate()` from the caller's key and
    is the only record in the file of what the caller actually declared.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        if line.strip().startswith("- Signature: `"):
            return line.split("`")[1]
    # NO SIGNATURE LINE IS NOT NO KEY. `seat_continuity` calls `escalate()` and then
    # OVERWRITES the returned document with its own handoff text, which drops the signature
    # line `escalate()` wrote. Nine of the twenty-eight alarm documents are that shape -- the
    # ones the director counted as "ten of them the identical finding" -- so grouping that
    # only understood the signature line would have collapsed the sixteen and left the ten.
    # The filing module is named in the body and IS the family for these: one module, one
    # condition, one declared key. Narrow on purpose -- a module that ever emits two families
    # would need its key here, and would be caught by its second document appearing.
    for module, key in _MODULE_KEYS.items():
        if f"background/{module}.py" in text:
            return key
    return None


#: Modules that overwrite the escalation document with their own body, losing the signature
#: line, mapped to the key they pass to `escalate()`. Read from the call sites, not guessed.
_MODULE_KEYS = {"seat_continuity": "seat-continuity"}


def collapse_alarms(staging: Path = STAGING, *, dry_run: bool = False) -> list[str]:
    """Step 3: one document per family, keeping every instance name."""
    out: list[str] = []
    groups: dict[str, list[Path]] = defaultdict(list)
    unkeyed: list[Path] = []
    for p in sorted(staging.glob("WORKER_FINDING_REPEATING_ALARM_*.md")):
        key = _alarm_key_of(p)
        if key is None:
            unkeyed.append(p)
            continue
        groups[ar.family(key)].append(p)

    for p in unkeyed:
        out.append(f"SKIPPED (no signature line, cannot group safely) {p.name}")

    for fam, paths in sorted(groups.items()):
        if len(paths) == 1:
            continue
        # The OLDEST document survives: it carries the earliest first-seen date, and an
        # episode that keeps its start is the one whose "how long has this been true" is
        # right. Ties break on name so the choice is deterministic and re-runnable.
        paths.sort(key=lambda q: (q.stat().st_mtime, q.name))
        survivor, folded = paths[0], paths[1:]
        out.append(f"COLLAPSE family={fam}: {len(paths)} documents -> {survivor.name}")
        for p in folded:
            key = _alarm_key_of(p) or fam
            name = ar.instance(key, _title_of(p))
            date = p.name.rsplit("_", 1)[-1].removesuffix(".md")
            text = "" if dry_run else survivor.read_text(encoding="utf-8", errors="replace")
            # THE ENUMERATION MUST NOT COLLAPSE TOO. `seat_continuity` writes an IDENTICAL
            # title on every one of its nine documents ("The interactive seat stopped
            # mid-work..."), so a title-derived instance name makes nine members into one
            # line and the collapse becomes a deletion. The filename is what distinguishes
            # them -- it is where the 2026-08-25 fix put the held areas -- so it is the
            # fallback identity, and the archived document it names is one `git log` away.
            if f"- `{name}` (" in text:
                name = p.stem
            if not dry_run and f"- `{name}` (" not in text:
                survivor.write_text(
                    ar._append_under(text, ar.INSTANCES_HEADING,
                                     f"- `{name}` (first seen {date})"),
                    encoding="utf-8")
            out.append(f"  folded {p.name} as instance `{name}`")
            out.append("  " + _git_mv(p, staging / "done" / p.name, dry_run=dry_run))
        # The survivor is renamed to the family stem so the NEXT firing finds it by the new
        # rule and does not file a sibling. Its date is kept -- the document is not new.
        date = survivor.name.rsplit("_", 1)[-1].removesuffix(".md")
        target = staging / (
            f"WORKER_FINDING_REPEATING_ALARM_"
            f"{ar._family_slug(_alarm_key_of(survivor) or fam, _title_of(survivor))}_{date}.md"
        )
        if target != survivor:
            out.append("  " + _git_mv(survivor, target, dry_run=dry_run))
    return out


def _title_of(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="actually move files")
    parser.add_argument("--root", default=str(STAGING))
    args = parser.parse_args(argv)
    staging = Path(args.root)
    dry = not args.apply

    before = sum(1 for p in staging.rglob("*.md"))
    lines = relocate(staging, dry_run=dry) + collapse_alarms(staging, dry_run=dry)
    for line in lines:
        print(line)
    after = sum(1 for p in staging.rglob("*.md"))
    print(f"\ndocs/staging/**/*.md: {before} before, {after} after"
          + ("  (dry run)" if dry else ""))
    if not dry and after < before:
        # ARCHIVE, NEVER DELETE, proven rather than asserted -- the same before/after equality
        # `staging_archive_policy` proves for its own thousands-of-files moves.
        print(f"REFUSED-SHAPED RESULT: {before - after} document(s) went missing. "
              f"Nothing here deletes; investigate before committing.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
