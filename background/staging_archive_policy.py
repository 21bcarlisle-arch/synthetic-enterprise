"""Separate the machine's EXHAUST from the governance RECORD in docs/staging/
(atom AO10, from ADVISOR_PROPOSAL_CAPABILITY_INDEX_AND_DEMO_2026-08-04 §4).

THE PROBLEM. `docs/staging/done/` held 4,961 files on 2026-08-09, of which
4,345 were `run_complete_*.md` sim-run markers -- the pipeline's own heartbeat
-- and ~600 were director/advisor instructions, rulings and worker findings.
The instruction record is the thing anyone ever needs to READ, and it was
buried under a nine-to-one majority of machine exhaust. The volume was never
the problem; the FILING was. A site tile even published the combined count as
"Actioned all-time", which reads as ~5,000 instructions actioned.

THE POLICY (this module is the whole of it, and it is mechanised, not prose):

  RECORD  -- anything a human wrote or a human must be able to find again:
             director/advisor docs, rulings, steers, worker findings,
             from_rich_* messages, mint docs. Stays in docs/staging/done/,
             retained indefinitely, never touched by this module.
  EXHAUST -- run_complete_*/run_pending_* lifecycle markers the pipeline
             emits on its own schedule. Moves to docs/staging/exhaust/<YYYY-MM>/,
             partitioned by the marker's OWN stamp, retained indefinitely,
             indexed by an append-only manifest.

RETENTION IS INDEFINITE AND NOTHING IS EVER DELETED. "ARCHIVE, NEVER DELETE"
binds hardest here because this module moves thousands of files at a time: a
bug is a mass loss of the run record, not a tidy-up gone slightly wrong. So
every operation is a MOVE with the old path recorded in the manifest, the
count is proven equal before and after, and a destination collision is
REPORTED rather than overwritten. Growth is handled by the review trigger
(`retention_review_due`), which names a partition that has grown past
REVIEW_PARTITION_FILES so a compaction atom can be minted deliberately --
rather than by a deletion rule that runs unattended.

THE MIRROR RISK, named in the atom itself: 78 instructions is a manageable
record and 4,909 is an impenetrable one, but a policy that makes the exhaust
UNFINDABLE has only moved the impenetrability. Hence `locate()` (name -> path,
wherever it now lives), `iter_marker_paths()` (the union view every consumer
of the markers uses instead of globbing done/), and the manifest that maps
every old path to its new one. The two real consumers -- background_worker's
supersession frontier and process_run_complete's duplicate-run check -- read
through those helpers, so the move cannot silently wind a published clock
backwards.

FAIL-SAFE DIRECTION (R15). The harmful misclassification is an INSTRUCTION
filed as exhaust, so `classify()` defaults to RECORD in every uncertain case:
an unreadable file, an unparseable name, a marker-named file whose body
carries any record marker. Only a file that BOTH carries an exhaust prefix AND
reads like a marker is moved.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = REPO_ROOT / "docs" / "staging"
DONE_DIR = STAGING_DIR / "done"
EXHAUST_DIR = STAGING_DIR / "exhaust"
MANIFEST_NAME = "MANIFEST.jsonl"

POLICY_VERSION = 1

RECORD = "record"
EXHAUST = "exhaust"

# The ONLY names eligible to be exhaust. Deliberately a closed list of the two
# daemon marker families (sim_runner emits run_complete_*, the pipeline emits
# run_pending_*); everything else in staging is written by a person or by an
# agent acting on a person's instruction and is RECORD by default.
EXHAUST_PREFIXES = ("run_complete_", "run_pending_")

# Any of these in the body forces RECORD even under an exhaust-shaped name.
# This is the defence against the failure the atom named: a real director doc
# silently filed as exhaust. A marker is machine-written boilerplate and can
# never contain one of these; a governance doc almost always does.
RECORD_MARKERS = (
    "[DIRECTOR-RULING]",
    "[DIRECTOR",
    "[ADVISOR",
    "[STEER]",
    "[WORKER-FINDING]",
    "WORK THIS CREATES",
    "PLANNER_MINTED",
    "Source:",
    "director",
    "advisor",
)

# The shape a genuine marker has. sim_runner writes "# Simulation Run Complete"
# and a "Git:" line; a pending marker writes its own heading. Requiring one of
# these is the second half of the AND -- prefix alone is not enough to move a
# file out of the record.
MARKER_SHAPES = (
    "# Simulation Run Complete",
    "# Simulation Run Pending",
    "## Action required",
    # The OLDER sim_runner template, still on disk for runs of 2026-06-18 and
    # 2026-07-07. Found by running the classifier over the real corpus, not by
    # reading sim_runner.py -- which only ever tells you the CURRENT shape.
    "# Run complete",
)

# A partition holding more than this many files is a signal to mint a
# compaction atom -- NOT a licence for this module to delete anything.
REVIEW_PARTITION_FILES = 2000

_STAMP_RE = re.compile(r"^(\d{8})[T_]?(\d{6})?Z?$")


def _exhaust_dir_for(done_dir: Path) -> Path:
    """The exhaust tree that pairs with `done_dir`.

    Derived from the done dir's PARENT rather than the module constant so a
    test (or a worktree) that redirects the staging root gets the matching
    exhaust tree, never the real one on disk. A helper reading real
    docs/staging/exhaust from inside a tmp-dir fixture is the leak that makes
    an isolated test quietly assert on live state.
    """
    return Path(done_dir).parent / "exhaust"


def marker_stamp(name: str) -> str | None:
    """`run_complete_20260808T235122Z.md` -> `20260808T235122Z`; else None."""
    stem = Path(name).stem
    for prefix in EXHAUST_PREFIXES:
        if stem.startswith(prefix):
            stamp = stem[len(prefix):]
            return stamp or None
    return None


def partition_for(name: str) -> str:
    """`YYYY-MM` from the marker's own stamp, or "undated" if it will not parse.

    "undated" is a real partition, not an error: an unparseable marker still
    has to land somewhere findable, and dropping it would be a deletion.
    """
    stamp = marker_stamp(name)
    if not stamp:
        return "undated"
    m = _STAMP_RE.match(stamp)
    if not m:
        return "undated"
    day = m.group(1)
    return f"{day[:4]}-{day[4:6]}"


def classify(name: str, body: str | None) -> str:
    """RECORD or EXHAUST for one staged file.

    EXHAUST requires ALL of: an exhaust-family prefix, a `.md` suffix, a
    readable body, a recognised marker shape in that body, and NO record
    marker anywhere in it. Every other input -- including `body is None`,
    which is what an unreadable file yields -- is RECORD.
    """
    if not name.endswith(".md"):
        return RECORD
    if not any(name.startswith(p) for p in EXHAUST_PREFIXES):
        return RECORD
    if body is None:
        return RECORD
    if not any(shape in body for shape in MARKER_SHAPES):
        return RECORD
    if any(marker in body for marker in RECORD_MARKERS):
        return RECORD
    return EXHAUST


def classify_path(path: Path) -> str:
    """classify() for a file on disk. An unreadable file is RECORD (fail-safe:
    a read error must never authorise a move out of the record)."""
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        body = None
    return classify(path.name, body)


def plan_sweep(done_dir: Path | None = None, exhaust_dir: Path | None = None) -> list[dict]:
    """The moves this policy would make, newest-name-last. Reads only."""
    done = Path(done_dir) if done_dir is not None else DONE_DIR
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else _exhaust_dir_for(done)
    if not done.is_dir():
        return []
    moves = []
    for p in sorted(done.iterdir()):
        if not p.is_file():
            continue
        if classify_path(p) != EXHAUST:
            continue
        partition = partition_for(p.name)
        moves.append({
            "name": p.name,
            "src": p,
            "dst": exhaust / partition / p.name,
            "partition": partition,
        })
    return moves


def _count_files(*dirs: Path) -> int:
    total = 0
    for d in dirs:
        if not Path(d).is_dir():
            continue
        for _root, _sub, files in os.walk(d):
            total += sum(1 for f in files if f != MANIFEST_NAME)
    return total


def apply_sweep(
    moves: list[dict],
    manifest_path: Path | None = None,
    dry_run: bool = True,
    done_dir: Path | None = None,
    exhaust_dir: Path | None = None,
) -> dict:
    """Execute a plan. Returns a report; NEVER deletes and never overwrites.

    Count conservation is PROVEN, not assumed: files under done/ + exhaust/ are
    counted before and after and the report carries both. A destination that
    already exists with different bytes is a CONFLICT -- the source stays put
    and is named in the report, because losing one run record to a name clash
    is exactly the mass-loss failure this atom warns about.
    """
    done = Path(done_dir) if done_dir is not None else DONE_DIR
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else _exhaust_dir_for(done)
    manifest = Path(manifest_path) if manifest_path is not None else exhaust / MANIFEST_NAME

    before = _count_files(done, exhaust)
    report = {
        "planned": len(moves),
        "moved": [],
        "already_there": [],
        "conflicts": [],
        "count_before": before,
        "count_after": before,
        "dry_run": dry_run,
    }
    if dry_run:
        return report

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = []
    for mv in moves:
        outcome, entry = _execute_move(mv, now)
        if outcome is not None:
            report[outcome].append(mv["name"])
        if entry is not None:
            lines.append(json.dumps(entry, sort_keys=True))

    if lines:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        with manifest.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")

    report["count_after"] = _count_files(done, exhaust)
    return report


def _execute_move(mv: dict, now: str) -> tuple[str | None, dict | None]:
    """One move. Returns (report bucket, manifest entry) -- either may be None.

    The only place a file changes location. A destination that already exists
    is NEVER overwritten: identical bytes means it is already filed (removing
    the source would be a delete, so the source stays and a human decides),
    and different bytes is a CONFLICT -- losing one run record to a name clash
    is the mass-loss failure this atom warns about.
    """
    src, dst = Path(mv["src"]), Path(mv["dst"])
    if not src.is_file():
        return None, None
    if dst.exists():
        try:
            same = dst.read_bytes() == src.read_bytes()
        except OSError:
            same = False
        return ("already_there" if same else "conflicts"), None
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.replace(src, dst)
    except OSError:
        import shutil
        shutil.copy2(str(src), str(dst))
        src.unlink(missing_ok=True)
    return "moved", {
        "policy_version": POLICY_VERSION,
        "name": mv["name"],
        "old_path": _rel(src),
        "new_path": _rel(dst),
        "partition": mv["partition"],
        "classified": EXHAUST,
        "moved_at": now,
    }


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def read_manifest(manifest_path: Path | None = None, exhaust_dir: Path | None = None) -> list[dict]:
    """Every manifest entry, oldest first. A malformed line is skipped, not
    fatal -- an append-only log must stay readable past one bad write."""
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else EXHAUST_DIR
    manifest = Path(manifest_path) if manifest_path is not None else exhaust / MANIFEST_NAME
    if not manifest.is_file():
        return []
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue
    return entries


def locate(name: str, done_dir: Path | None = None, exhaust_dir: Path | None = None) -> Path | None:
    """Where a staged file lives NOW -- done/ or any exhaust partition.

    This is the findability half of the policy. Every consumer that used to
    ask "is it in done/?" asks this instead, so moving the exhaust cannot turn
    a known file into an unknown one.
    """
    done = Path(done_dir) if done_dir is not None else DONE_DIR
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else _exhaust_dir_for(done)
    candidate = done / name
    if candidate.is_file():
        return candidate
    partitioned = exhaust / partition_for(name) / name
    if partitioned.is_file():
        return partitioned
    if exhaust.is_dir():
        for sub in sorted(exhaust.iterdir()):
            if sub.is_dir() and (sub / name).is_file():
                return sub / name
    return None


def iter_marker_paths(
    prefix: str = "run_complete_",
    done_dir: Path | None = None,
    exhaust_dir: Path | None = None,
):
    """Every marker with `prefix`, wherever it is filed. The union view.

    Consumers that globbed `done/run_complete_*.md` MUST use this: after the
    sweep, done/ holds none of them, and a glob that silently returns nothing
    turns a supersession frontier into "no runs ever published" -- a fail-open
    that would let a stale snapshot be republished over current figures.
    """
    done = Path(done_dir) if done_dir is not None else DONE_DIR
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else _exhaust_dir_for(done)
    if done.is_dir():
        yield from sorted(done.glob(f"{prefix}*.md"))
    if exhaust.is_dir():
        for sub in sorted(exhaust.iterdir()):
            if sub.is_dir():
                yield from sorted(sub.glob(f"{prefix}*.md"))


def verify(manifest_path: Path | None = None, exhaust_dir: Path | None = None) -> list[dict]:
    """Prove nothing was lost: every manifest entry's new_path must exist.

    Returns the list of problems -- empty means the record is whole. This is
    the control that can FAIL: delete one moved file and it names it.
    """
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else EXHAUST_DIR
    problems = []
    for entry in read_manifest(manifest_path, exhaust):
        new_path = entry.get("new_path")
        if not new_path:
            problems.append({"name": entry.get("name"), "problem": "no new_path recorded"})
            continue
        p = Path(new_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.is_file():
            problems.append({"name": entry.get("name"), "problem": f"missing at {new_path}"})
    return problems


def partition_counts(exhaust_dir: Path | None = None) -> dict[str, int]:
    exhaust = Path(exhaust_dir) if exhaust_dir is not None else EXHAUST_DIR
    counts: dict[str, int] = {}
    if not exhaust.is_dir():
        return counts
    for sub in sorted(exhaust.iterdir()):
        if sub.is_dir():
            counts[sub.name] = sum(1 for p in sub.iterdir() if p.is_file())
    return counts


def retention_review_due(exhaust_dir: Path | None = None) -> list[str]:
    """Partitions past REVIEW_PARTITION_FILES, i.e. the ones worth minting a
    compaction atom for. Retention itself stays indefinite -- this names work,
    it never authorises a delete."""
    return sorted(
        name for name, n in partition_counts(exhaust_dir).items()
        if n > REVIEW_PARTITION_FILES
    )


def _cli() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Separate staging exhaust from the record.")
    ap.add_argument("--sweep", action="store_true", help="plan the move (dry run unless --apply)")
    ap.add_argument("--apply", action="store_true", help="actually move")
    ap.add_argument("--find", metavar="NAME", help="where does this staged file live now?")
    ap.add_argument("--verify", action="store_true", help="prove every moved file still exists")
    ap.add_argument("--report", action="store_true", help="counts per partition + review trigger")
    args = ap.parse_args()

    if args.find:
        found = locate(args.find)
        print(found if found else f"not found: {args.find}")
        return 0 if found else 1
    if args.verify:
        problems = verify()
        for p in problems:
            print(f"MISSING {p['name']}: {p['problem']}")
        print(f"{len(read_manifest())} manifest entries, {len(problems)} problems")
        return 1 if problems else 0
    if args.report or not (args.sweep or args.apply):
        counts = partition_counts()
        for name, n in counts.items():
            print(f"{name}: {n}")
        record = sum(1 for p in DONE_DIR.iterdir() if p.is_file()) if DONE_DIR.is_dir() else 0
        print(f"record (done/): {record} | exhaust: {sum(counts.values())}")
        due = retention_review_due()
        print(f"retention review due: {', '.join(due) if due else 'none'}")
        return 0

    moves = plan_sweep()
    report = apply_sweep(moves, dry_run=not args.apply)
    print(json.dumps({
        "planned": report["planned"],
        "moved": len(report["moved"]),
        "already_there": len(report["already_there"]),
        "conflicts": report["conflicts"][:20],
        "count_before": report["count_before"],
        "count_after": report["count_after"],
        "dry_run": report["dry_run"],
    }, indent=2))
    return 1 if report["conflicts"] else 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/staging_archive_policy.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("staging_archive_policy")
    raise SystemExit(_cli())
