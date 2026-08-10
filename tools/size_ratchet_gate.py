#!/usr/bin/env python3
"""SP3 -- the size + clone ratchet GATE: the pre-commit skin over `tools/size_ratchet.py`.

WARN-THEN-GATE (ruling s8, the mitigation that makes this safe to land)
-----------------------------------------------------------------------
`rollout_state` lives in the baseline artefact and has exactly two values:

  "warn"  -- violations are printed loudly and appended to
             docs/observability/size_ratchet_warnings.jsonl, and the gate EXITS 0.
  "gate"  -- identical detection, identical payload, EXITS 1 (blocks the commit).

The transition is a deliberate, git-visible one-line diff to the artefact, made no earlier than one
retro cadence after `warn_started_at` and only after reading the warn-log for the cycle. There is
NO auto-flip: a timer that flipped itself would reproduce the silent-state-change class R2/R7
already forbid. Detection is identical in both states by construction -- `size_ratchet.evaluate()`
is pure and is called once, so warn and gate can never become two divergently-buggy code paths
(R15 test 7 pins that).

STAGING-AWARE: with no in-scope .py file staged, nothing this ratchet governs can have changed, so
the gate exits 0 immediately and an unrelated commit pays nothing.

NO BYPASS FLAG. There is deliberately no `--skip-ratchet`: a flag is silent-by-construction the
moment someone reaches for it under time pressure. The only way past a violation is a named, logged
override (`tools/size_ratchet_override.py`), scoped to one file at one line count, which expires the
moment that file grows again.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.size_ratchet import (  # noqa: E402
    BASELINE_PATH,
    NEW_FILE_LINE_CAP,
    NEW_FUNCTION_LINE_CAP,
    SCOPE_ROOTS,
    WARN_LOG_PATH,
    Finding,
    RatchetUnavailable,
    _blob_shas,
    _git,
    _read_blobs,
    census_at,
    evaluate,
    in_scope,
    load_baseline,
)

# The ruling's own s0 census figure. Carried as a HISTORICAL REFERENCE only -- never the live
# ceiling (see size_ratchet.py's docstring for why 223 was measured and refused).
RULING_S0_CLONE_COUNT = 223


def staged_paths(project_dir: Path) -> set[str]:
    raw = _git("diff", "--cached", "--name-only", "--diff-filter=ACMR", project_dir=project_dir)
    return {p for p in raw.splitlines() if in_scope(p)}


def staged_renames(project_dir: Path) -> dict[str, str]:
    """Staged path -> the path that content had at HEAD, from git's own rename detection (`-M`).

    Only in-scope pairs are returned; a rename that leaves or enters the scope roots has no
    comparable prior state inside the ratchet's world and is correctly treated as new.
    """
    raw = _git("diff", "--cached", "--name-status", "-M", "--diff-filter=R",
               project_dir=project_dir)
    out: dict[str, str] = {}
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or not parts[0].startswith("R"):
            continue
        old, new = parts[1], parts[2]
        if in_scope(old) and in_scope(new):
            out[new] = old
    return out


def _head_state(project_dir: Path) -> tuple[dict[str, int], dict[str, str]]:
    """Line counts and texts at HEAD. An empty repo (no HEAD) yields empty state -- every file is
    then new, which is the correct reading for an initial commit."""
    try:
        shas = _blob_shas("HEAD", project_dir=project_dir)
    except RatchetUnavailable:
        return {}, {}
    contents = _read_blobs(shas.values(), project_dir=project_dir)
    texts = {path: contents[sha] for path, sha in shas.items()}
    return {path: len(text.splitlines()) for path, text in texts.items()}, texts


def _index_texts(project_dir: Path, paths: set[str]) -> dict[str, str]:
    shas = {p: s for p, s in _blob_shas(None, project_dir=project_dir).items() if p in paths}
    contents = _read_blobs(shas.values(), project_dir=project_dir)
    return {path: contents[sha] for path, sha in shas.items()}


# ------------------------------------------------------------------------------- the override
def active_overrides() -> dict[str, int]:
    """Read logged overrides from the decision log: path -> the highest authorised line count.

    An override is SCOPED TO THE COUNT IT AUTHORISED, not to the file: growing the same file again
    later needs a fresh logged override. That closes the obvious fail-open ("one override silently
    exempts the file forever"). FAIL-CLOSED: an unreadable decision log yields NO overrides, so a
    corrupt log makes the gate stricter, never laxer.
    """
    try:
        from background.decision_log import read_decision_log

        entries = read_decision_log()
    except Exception:  # noqa: BLE001 -- an unavailable log must not grant an override
        return {}
    out: dict[str, int] = {}
    for entry in entries:
        what = str(entry.get("what", ""))
        if not what.startswith(OVERRIDE_PREFIX):
            continue
        body = what[len(OVERRIDE_PREFIX):].strip()
        path, _, count = body.rpartition("@")
        try:
            authorised = int(count.strip())
        except ValueError:
            continue
        path = path.strip()
        if authorised > out.get(path, 0):
            out[path] = authorised
    return out


OVERRIDE_PREFIX = "size ratchet override:"


def apply_overrides(findings: list[Finding], overrides: dict[str, int]) -> tuple[list[Finding], list[str]]:
    """Split findings into (still-violating, overridden-notes). An override covers a finding only
    when it authorised AT LEAST the count now being seen."""
    remaining: list[Finding] = []
    notes: list[str] = []
    for f in findings:
        authorised = overrides.get(f.path)
        if authorised is not None and authorised >= f.actual:
            notes.append(f"OVERRIDDEN {f.line()} (logged override authorised {authorised})")
        else:
            remaining.append(f)
    return remaining, notes


def append_warn_log(findings: list[Finding], path: Path | None = None) -> None:
    """Append-only, and ONLY on a real violation. A warn-log that grew on every run regardless of
    violation would be indistinguishable signal from noise -- itself a fail-open control.

    The destination is resolved at CALL time, not bound as a default argument: a default-bound path
    cannot be redirected, which would leave the warn-log's own fail-open (does it grow when it
    shouldn't?) untestable -- and an untestable control is one R15 cannot certify.
    """
    if not findings:
        return
    path = path or WARN_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as fh:
        for f in findings:
            fh.write(json.dumps({"timestamp": stamp, **f.as_dict()}, sort_keys=True) + "\n")


def _print_block(findings: list[Finding], state: str, notes: list[str]) -> None:
    tag = "SIZE-RATCHET WARN" if state == "warn" else "SIZE-RATCHET"
    print(f"\n{'=' * 78}", file=sys.stderr)
    print(f"[{tag}] {len(findings)} violation(s)", file=sys.stderr)
    print(f"{'=' * 78}", file=sys.stderr)
    for f in findings:
        print(f"  {f.line()}", file=sys.stderr)
    for note in notes:
        print(f"  {note}", file=sys.stderr)
    print(
        "\n  Caps apply to NEW files/functions only "
        f"(file {NEW_FILE_LINE_CAP}, function {NEW_FUNCTION_LINE_CAP}); existing files are "
        "grandfathered at their own count.\n"
        "  These are TRIPWIRES, not scores: shrink the real duplication, never obfuscate a clone or "
        "split a file to dodge a count.\n"
        "  Deliberate exception: python3 tools/size_ratchet_override.py --file <p> --lines <n> "
        '--why "..." --reverse "..."',
        file=sys.stderr,
    )
    if state == "warn":
        print(
            f"  rollout_state=warn -- NOT blocking this commit. Logged to {WARN_LOG_PATH.name}.",
            file=sys.stderr,
        )
    print(f"{'=' * 78}\n", file=sys.stderr)


# ------------------------------------------------------------------------------------- freeze
def freeze(project_dir: Path, baseline_path: Path, state: str = "warn") -> dict:
    """Write the baseline artefact from a live census of the INDEX.

    LOWER-ONLY when a baseline already exists: re-freezing may TIGHTEN a ceiling (a file that shrank,
    a clone that was extracted) and may never LOOSEN one. That asymmetry is the ratchet -- an
    automatic re-freeze that absorbed growth would defeat the entire mechanism, so growth requires a
    logged override and is never quietly adopted as the new normal.
    """
    census = census_at(None, project_dir=project_dir)
    files = dict(census.lines)
    ceiling = census.clone_count
    previous = None
    if baseline_path.exists():
        previous = load_baseline(baseline_path)
        for path, count in previous["files"].items():
            if path in files:
                files[path] = min(files[path], count)
            else:
                files[path] = count  # deleted files stay in the snapshot for audit
        ceiling = min(ceiling, int(previous["clone_ceiling"]))

    head = _git("rev-parse", "HEAD", project_dir=project_dir).strip()
    data = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "captured_by_commit": head,
        "scope_roots": list(SCOPE_ROOTS),
        "rollout_state": (previous or {}).get("rollout_state", state),
        "warn_started_at": (previous or {}).get("warn_started_at")
        or datetime.now(timezone.utc).isoformat(),
        "warn_started_at_commit": (previous or {}).get("warn_started_at_commit") or head,
        "clone_ceiling": ceiling,
        "clone_set_count_at_capture": census.clone_set_count,
        "historical_reference_ceiling": RULING_S0_CLONE_COUNT,
        "historical_reference_note": (
            "DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28 s0 counted 223 "
            "instances over 788 modules. It is NOT the live ceiling: re-derived at build time over "
            "this scope the same detector reads a different number, and the DISCOVER doc's own s8 "
            "made 'lands at or very near 223' the condition for trusting it. Carried here so the "
            "delta stays visible rather than being laundered into the frozen figure."
        ),
        "new_file_line_cap": NEW_FILE_LINE_CAP,
        "new_function_line_cap": NEW_FUNCTION_LINE_CAP,
        "totals": {"file_count": len(census.lines), "line_count": sum(census.lines.values())},
        "files": dict(sorted(files.items())),
    }
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


# --------------------------------------------------------------------------------------- main
def run(project_dir: Path, baseline_path: Path, report: bool = False) -> int:
    try:
        touched = staged_paths(project_dir)
        if not touched and not report:
            return 0
        baseline = load_baseline(baseline_path)
        index = census_at(None, project_dir=project_dir)
        head_lines, head_texts = _head_state(project_dir)
        index_texts = _index_texts(project_dir, touched)
        renames = staged_renames(project_dir)
        findings = evaluate(
            baseline, index, head_lines, touched, index_texts, head_texts, renames
        )
    except RatchetUnavailable as exc:
        # An unavailable check is a FAILED check (R15 fail-silent pattern), in BOTH rollout states:
        # the warn rail exists to absorb false positives from the RULES, never to swallow the
        # ratchet being structurally broken.
        print(f"\n[SIZE-RATCHET] CHECK UNAVAILABLE -- refusing: {exc}\n", file=sys.stderr)
        return 1

    state = baseline["rollout_state"]
    if report:
        print(
            f"scope={len(index.lines)} files, {sum(index.lines.values())} lines | "
            f"clones={index.clone_count} instances in {index.clone_set_count} cross-file sets "
            f"(ceiling {baseline['clone_ceiling']}, ruling s0 reference {RULING_S0_CLONE_COUNT}) | "
            f"rollout_state={state} | staged in scope={len(touched)}"
        )

    if not findings:
        return 0

    findings, notes = apply_overrides(findings, active_overrides())
    if not findings:
        for note in notes:
            print(f"[SIZE-RATCHET] {note}", file=sys.stderr)
        return 0

    append_warn_log(findings)
    _print_block(findings, state, notes)
    return 0 if state == "warn" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Size + clone ratchet (SP3).")
    parser.add_argument("--report", action="store_true", help="print the census and all findings")
    parser.add_argument("--freeze", action="store_true", help="(re)write the baseline; lower-only")
    args = parser.parse_args(argv)

    project_dir = Path(__file__).resolve().parent.parent
    if args.freeze:
        data = freeze(project_dir, BASELINE_PATH)
        print(
            f"froze {data['totals']['file_count']} files / {data['totals']['line_count']} lines; "
            f"clone_ceiling={data['clone_ceiling']}; rollout_state={data['rollout_state']} "
            f"-> {BASELINE_PATH}"
        )
        return 0
    return run(project_dir, BASELINE_PATH, report=args.report)


if __name__ == "__main__":
    raise SystemExit(main())
