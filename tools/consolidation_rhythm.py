"""AO6 -- the CONSOLIDATION RHYTHM: an epoch cannot close without a record of the pruning.

Serves `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` §RHYTHM, verbatim: *"Canon already
prunes the harness and advisor memory at epoch boundaries. Extend the same duty to code: every
epoch close includes a consolidation pass -- duplicates found, orphans wired or retired, the
target-design document updated. Organic growth between boundaries; deliberate pruning at them."*

WHY THIS IS CODE AND NOT A LINE IN THE PHASE-CLOSE CHECKLIST
------------------------------------------------------------
The atom's own `origin_note`, written before a line of this existed, is the whole specification:
*"This is the step that decides whether the whole programme decays. MAKE_IT_STICK is directly on
point -- every rule that DECAYED was an exhortation; every rule that HELD was a MECHANISM. An
epoch-close consolidation pass that lives only as prose in a checklist WILL evaporate exactly as
the earlier exhortations did."* So the deliverable is a check that FAILS an epoch close lacking
its consolidation record, and the prose in `.claude/skills/phase-close/SKILL.md` is a pointer at
this module rather than the mechanism itself.

WHAT "EPOCH CLOSE" IS, MEASURABLY
---------------------------------
Epoch E is CLOSED when it holds at least one atom in `docs/design/maturity_map.yaml` and every one
of them has `level_current >= level_target`. That is read from the map, never declared by hand, so
"the epoch closed" is an observation and not an announcement. `--gate` (wired into pre-commit)
compares the STAGED map against HEAD's: a commit that moves an epoch from open to closed without a
committed pass record for that epoch is REFUSED.

THE RATCHET, AND WHY IT IS BOUNDED
-----------------------------------
The tree carries a large pre-existing orphan pile (266 of 842 modules at baseline; AO7's T4 target
reports it as a standing delta). Demanding all of it be dispositioned at the next boundary would
make the first close impossible and the gate would be routed around, which is how gates die. So
the ledger opens with exactly ONE `baseline` record: it stamps that historical pile as declared,
visible debt and forgives it for coverage purposes. Every orphan appearing AFTER the baseline must
carry a disposition in some record before an epoch can close. That is precisely the atom's "organic
growth between boundaries; deliberate pruning at them" -- and `--report` prints the unaccounted set
at any time, so the growth is visible continuously rather than only at a boundary.

A SECOND BASELINE IS THE OBVIOUS ESCAPE, AND IS REFUSED (G8). Without that guard the cheapest move
available to any future turn facing a coverage failure is to re-baseline and forgive itself, which
would leave the mechanism looking green forever while measuring nothing.

THE THREE DISPOSITIONS -- AND WHY `kept` IS ALLOWED TO EXIST
------------------------------------------------------------
    retired  -- the module is gone.        Verified: the path must NOT exist in the tree.
    wired    -- it has a caller now.       Verified: the path must NOT still be an orphan.
    kept     -- deliberately left, with a named reason. NOT verified against the tree.

Only `kept` is unfalsifiable, and it is deliberate. The same director amendment that governs AO2
draws the wall: *"know, then choose -- forced reuse that couples two purposes is the mirror error
of duplication and is equally a defect."* A gate that accepted only `wired`/`retired` would compel
the decision rather than the look, and would push a turn into deleting a module it should have
kept. So `kept` is the recorded, reasoned, attributable choice -- and because the ledger is
append-only, a module kept at successive closes accumulates a visible history. `--report` prints
that repeat count. It is REPORTED, never gated (R12): this measures whether the pass HAPPENED, and
never scores how much was pruned. A consolidation pass that legitimately keeps everything is rc 0.

R15 -- THE THREE KILLER PATTERNS, ANSWERED
-------------------------------------------
TAUTOLOGY   -- the binding coverage rule (G6) does not compare the ledger against itself. It
               compares the ledger against the LIVE orphan set derived by AO1's
               `tools/capability_index.py` from the actual tree. A hand-forged record with an empty
               census therefore buys nothing: only the single baseline grants forgiveness, and
               every other module still shows up in the live scan. Disposition CLAIMS are checked
               the same way -- `retired` is contradicted by the file still being there, `wired` by
               the module still having no caller. The ledger states intent; the tree states fact;
               the two come from different places on purpose.
FAIL-OPEN   -- every scan reports what it scanned. A map yielding zero atoms, or an index yielding
               zero rows, RAISES (`ConsolidationUnavailable`) instead of concluding "nothing wrong":
               "0 unaccounted orphans" and "0 modules scanned" are the same number and opposite
               facts, and this repo has already shipped a control that passed 1557/1557 while the
               field it checked was absent. When there are no closed epochs the coverage rule is
               reported NOT APPLICABLE by name -- never printed as if it had been verified.
FAIL-SILENT -- an unreadable ledger line, an unparseable map, an unavailable capability index and
               an unknown disposition word are all REFUSALS. There is no skip disposition and no
               degrade-to-assume-fine path. Under `--gate`, a record present only in the worktree
               and never staged is likewise refused: the record must be committed to count.

R15 PROOF: `tests/tools/test_consolidation_rhythm.py` -- each guard has a mutation proving it fires
alone, plus the R12 inversion pinned both ways and a vacuity guard.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse AO1's row builder verbatim -- this module must never re-derive the orphan set it checks
# against, or G6 would be measuring the ledger against a second opinion of its own making.
from tools.capability_index import build_rows, orphans  # noqa: E402

MAP_REL = "docs/design/maturity_map.yaml"
LEDGER_REL = "docs/observability/consolidation_ledger.jsonl"

BASELINE = "baseline"
PASS = "pass"
KINDS = (BASELINE, PASS)

RETIRED, WIRED, KEPT = "retired", "wired", "kept"
DISPOSITIONS = (RETIRED, WIRED, KEPT)

# A `kept` reason shorter than this is not a reason. Stated as a measurement convention, the same
# way AO7 states its monolith line count here rather than in the document it measures.
MIN_REASON_CHARS = 12


class ConsolidationUnavailable(Exception):
    """A scan could not run, or ran over nothing. An unavailable check is a FAILED check."""


# --------------------------------------------------------------------------------------------
# The map: what an epoch is, and when it has closed
# --------------------------------------------------------------------------------------------

def atoms_from_map(text: str) -> list[dict]:
    """Every atom in a maturity-map document. Raises rather than returning [] on an empty map."""
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConsolidationUnavailable("maturity map is unparseable: %s" % exc) from exc
    found: list[dict] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            if "id" in node and "level_current" in node:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(doc)
    if not found:
        raise ConsolidationUnavailable(
            "maturity map yielded 0 atoms -- an epoch-close check over an empty map would pass "
            "vacuously, which is the fail-open shape R15 forbids")
    return found


def closed_epochs(atoms: list[dict]) -> set:
    """Epochs where every atom has reached its target.

    `all([])` is True, so the obvious vacuity worry is that an epoch with no atoms reads as closed.
    It cannot happen HERE and the defence is structural rather than a guard: epochs are DERIVED from
    the atoms, so an epoch with no atoms is never a key and is simply absent from the result. An
    added `if members and ...` check was written, found unreachable by its own mutation (nothing
    went red when it was broken), and removed rather than left as a guard that cannot fail. The
    vacuity that IS reachable — a map yielding no atoms at all — is guarded in `atoms_from_map`.
    """
    by_epoch: dict = {}
    for atom in atoms:
        epoch = atom.get("epoch")
        if epoch is None:
            continue
        by_epoch.setdefault(epoch, []).append(atom)
    return {epoch for epoch, members in by_epoch.items()
            if all(int(a.get("level_current", 0)) >= int(a.get("level_target", 0))
                   for a in members)}


# --------------------------------------------------------------------------------------------
# The tree: the live orphan set, derived independently of the ledger
# --------------------------------------------------------------------------------------------

def live_orphan_paths(root: Path | None = None) -> tuple[set, int]:
    """(orphan paths, modules scanned) from AO1's index. Raises if the index scanned nothing."""
    try:
        rows = build_rows(root)
    except Exception as exc:  # the index is a dependency; unavailable is FAILED, never skipped
        raise ConsolidationUnavailable("capability index unavailable: %s" % exc) from exc
    if not rows:
        raise ConsolidationUnavailable(
            "capability index scanned 0 modules -- '0 orphans' and '0 modules scanned' are the "
            "same number and opposite facts")
    return {r["path"] for r in orphans(rows)}, len(rows)


# --------------------------------------------------------------------------------------------
# The ledger
# --------------------------------------------------------------------------------------------

def parse_ledger(text: str) -> list[dict]:
    """Records from JSONL. An unparseable or structurally invalid line RAISES -- never skipped."""
    records: list[dict] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ConsolidationUnavailable(
                "%s line %d is unparseable (%s) -- an unreadable ledger is a FAILED check"
                % (LEDGER_REL, number, exc)) from exc
        if not isinstance(record, dict):
            raise ConsolidationUnavailable("%s line %d is not an object" % (LEDGER_REL, number))
        _validate_record(record, number)
        records.append(record)
    return records


def _validate_record(record: dict, number: int) -> None:
    """Structural validity of one record (G4). Every refusal names the line."""
    where = "%s line %d" % (LEDGER_REL, number)
    kind = record.get("kind")
    if kind not in KINDS:
        raise ConsolidationUnavailable(
            "%s: kind %r is not one of %s" % (where, kind, ", ".join(KINDS)))
    if kind == PASS and record.get("epoch") is None:
        raise ConsolidationUnavailable("%s: a pass record must name the epoch it closes" % where)
    census = record.get("census")
    if not isinstance(census, dict) or not isinstance(census.get("orphan_paths"), list):
        raise ConsolidationUnavailable(
            "%s: census.orphan_paths is missing -- a record with no census claims a pass that "
            "cannot be checked" % where)
    for entry in record.get("dispositions", []):
        _validate_disposition(entry, where)


def _validate_disposition(entry, where: str) -> None:
    if not isinstance(entry, dict):
        raise ConsolidationUnavailable("%s: a disposition must be an object" % where)
    path, verdict = entry.get("path"), entry.get("disposition")
    if not isinstance(path, str) or not path.strip():
        raise ConsolidationUnavailable("%s: a disposition must name a path" % where)
    if verdict not in DISPOSITIONS:
        raise ConsolidationUnavailable(
            "%s: disposition %r for %s is not one of %s (there is no skip disposition)"
            % (where, verdict, path, ", ".join(DISPOSITIONS)))
    if verdict == KEPT:
        reason = entry.get("reason") or ""
        if len(reason.strip()) < MIN_REASON_CHARS:
            raise ConsolidationUnavailable(
                "%s: kept %s without a reason -- 'kept' is the one disposition the tree cannot "
                "contradict, so it carries a named reason or it is not a disposition"
                % (where, path))


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return parse_ledger(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConsolidationUnavailable("%s unreadable: %s" % (LEDGER_REL, exc)) from exc


# --------------------------------------------------------------------------------------------
# The check
# --------------------------------------------------------------------------------------------

def check(records: list[dict], atoms: list[dict], orphan_paths: set,
          root: Path) -> tuple[list[str], dict]:
    """(failures, report). Failures are the named guards; the report is diagnostic (R12)."""
    failures: list[str] = []
    closed = closed_epochs(atoms)
    baselines = [r for r in records if r.get("kind") == BASELINE]

    # G8 -- a second baseline would forgive the pile again, and is the escape from G6.
    if len(baselines) > 1:
        failures.append(
            "G8 second baseline: %d baseline records. The baseline forgives the historical orphan "
            "pile ONCE; a second one lets any future turn re-forgive itself out of a coverage "
            "failure and leaves this check measuring nothing." % len(baselines))

    # G3 -- every closed epoch has a pass record.
    recorded = {r.get("epoch") for r in records if r.get("kind") == PASS}
    for epoch in sorted(closed - recorded, key=str):
        failures.append(
            "G3 epoch %s is CLOSED (every atom at its target) with no consolidation pass recorded "
            "in %s -- the pruning duty at this boundary has no record." % (epoch, LEDGER_REL))

    # G5 -- disposition claims against the tree, which is a different source from the ledger.
    failures.extend(_check_dispositions(records, orphan_paths, root))

    # G6 -- coverage. Binds only at a boundary; reported NOT APPLICABLE otherwise, never as passed.
    forgiven = set()
    for record in baselines:
        forgiven |= set(record["census"]["orphan_paths"])
    dispositioned = {e["path"] for r in records for e in r.get("dispositions", [])}
    unaccounted = sorted(orphan_paths - forgiven - dispositioned)
    if closed and unaccounted:
        failures.append(
            "G6 coverage: %d orphan module(s) appeared after the baseline and carry no disposition "
            "while epoch(s) %s are closed -- e.g. %s"
            % (len(unaccounted), ", ".join(str(e) for e in sorted(closed, key=str)),
               ", ".join(unaccounted[:5])))

    report = {
        "epochs_closed": sorted(closed, key=str),
        "coverage_rule": "applicable" if closed else "NOT APPLICABLE (no epoch is closed)",
        "orphans_live": len(orphan_paths),
        "orphans_forgiven_at_baseline": len(forgiven),
        "orphans_dispositioned": len(dispositioned & orphan_paths),
        "orphans_unaccounted": unaccounted,
        "kept_repeats": _kept_repeats(records),
        "records": len(records),
        "atoms_scanned": len(atoms),
    }
    return failures, report


def _check_dispositions(records: list[dict], orphan_paths: set, root: Path) -> list[str]:
    """G5 -- the tree is asked whether each claim is true. Only `kept` is unfalsifiable, by design."""
    failures = []
    for record in records:
        for entry in record.get("dispositions", []):
            path, verdict = entry["path"], entry["disposition"]
            exists = (root / path).exists()
            if verdict == RETIRED and exists:
                failures.append(
                    "G5 record for epoch %s claims %s RETIRED, but the file is still in the tree."
                    % (record.get("epoch"), path))
            elif verdict == WIRED and exists and path in orphan_paths:
                failures.append(
                    "G5 record for epoch %s claims %s WIRED, but the live index still finds no "
                    "caller and no command for it." % (record.get("epoch"), path))
    return failures


def _kept_repeats(records: list[dict]) -> list[str]:
    """Modules kept at more than one close. Diagnostic only -- a growing pile is visible, not red."""
    seen: dict = {}
    for record in records:
        for entry in record.get("dispositions", []):
            if entry["disposition"] == KEPT:
                seen[entry["path"]] = seen.get(entry["path"], 0) + 1
    return sorted(path for path, count in seen.items() if count > 1)


# --------------------------------------------------------------------------------------------
# Recording a pass
# --------------------------------------------------------------------------------------------

def build_record(kind: str, epoch, orphan_paths: set, scanned: int,
                 dispositions: list[dict], now: str, commit: str) -> dict:
    """A record whose census is MACHINE-TAKEN at record time, never typed."""
    return {
        "kind": kind,
        "epoch": epoch,
        "recorded_at": now,
        "commit": commit,
        "census": {"modules_scanned": scanned, "orphan_paths": sorted(orphan_paths)},
        "dispositions": dispositions,
    }


def _head_commit(root: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def append_record(record: dict, path: Path) -> None:
    _validate_record(record, 0)  # never write what the reader would refuse
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


# --------------------------------------------------------------------------------------------
# The pre-commit gate
# --------------------------------------------------------------------------------------------

def _git_show(root: Path, ref: str) -> str | None:
    """Content of a blob at a ref, or None if it is not there. Read-only plumbing (H24)."""
    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}
    try:
        out = subprocess.run(["git", "-C", str(root), "show", ref],
                             capture_output=True, text=True, timeout=60, env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ConsolidationUnavailable("git show %s failed: %s" % (ref, exc)) from exc
    return out.stdout if out.returncode == 0 else None


def _staged_paths(root: Path) -> set:
    out = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--name-only"],
                         capture_output=True, text=True, timeout=60)
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def gate(root: Path) -> tuple[int, list[str]]:
    """Refuse a commit that CLOSES an epoch with no committed pass record for it."""
    if MAP_REL not in _staged_paths(root):
        return 0, ["consolidation gate: map not staged -- no epoch can close in this commit."]

    staged_map = _git_show(root, ":" + MAP_REL)
    if staged_map is None:
        return 2, ["the map is staged but its blob is unreadable -- refusing rather than allowing "
                   "an unverifiable epoch close (fail-closed)."]
    staged_atoms = atoms_from_map(staged_map)

    head_map = _git_show(root, "HEAD:" + MAP_REL)
    # No map at HEAD: treat every closed epoch as newly closed. Fail-closed direction.
    head_closed = closed_epochs(atoms_from_map(head_map)) if head_map else set()
    newly_closed = closed_epochs(staged_atoms) - head_closed
    if not newly_closed:
        return 0, ["consolidation gate: no epoch closes in this commit."]

    # The record must be COMMITTED, not merely present in the worktree.
    ledger_text = _git_show(root, ":" + LEDGER_REL)
    if ledger_text is None:
        ledger_text = _git_show(root, "HEAD:" + LEDGER_REL) or ""
    recorded = {r.get("epoch") for r in parse_ledger(ledger_text) if r.get("kind") == PASS}
    missing = sorted(newly_closed - recorded, key=str)
    if missing:
        return 2, [
            "COMMIT REFUSED -- this commit closes epoch(s) %s with no committed consolidation pass."
            % ", ".join(str(e) for e in missing),
            "Run the pass, then stage the record:",
            "    python3 tools/consolidation_rhythm.py --record --epoch %s" % missing[0],
        ]
    return 0, ["consolidation gate: epoch(s) %s close WITH a recorded pass."
               % ", ".join(str(e) for e in sorted(newly_closed, key=str))]


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------

def _load_dispositions(spec: str | None) -> list[dict]:
    if not spec:
        return []
    entries = json.loads(Path(spec).read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ConsolidationUnavailable("--dispositions must hold a JSON list")
    return entries


def _do_record(args, root: Path, ledger: Path) -> int:
    paths, scanned = live_orphan_paths(root)
    records = read_ledger(ledger)
    kind = BASELINE if args.baseline else PASS
    if kind == BASELINE and any(r.get("kind") == BASELINE for r in records):
        print("REFUSED: a baseline already exists (G8). The historical pile is forgiven once.")
        return 2
    record = build_record(kind, args.epoch, paths, scanned, _load_dispositions(args.dispositions),
                          datetime.now(timezone.utc).isoformat(timespec="seconds"),
                          _head_commit(root))
    append_record(record, ledger)
    print("recorded %s for epoch %s -- %d orphan(s) in census, %d disposition(s), %d modules scanned"
          % (kind, args.epoch, len(paths), len(record["dispositions"]), scanned))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify every closed epoch has its pass")
    parser.add_argument("--report", action="store_true", help="print the standing census (no gating)")
    parser.add_argument("--gate", action="store_true", help="pre-commit: refuse an unrecorded close")
    parser.add_argument("--record", action="store_true", help="take a census and append a record")
    parser.add_argument("--baseline", action="store_true", help="with --record: the one baseline")
    parser.add_argument("--epoch", help="the epoch a pass record closes")
    parser.add_argument("--dispositions", help="path to a JSON list of disposition objects")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    ledger = root / LEDGER_REL
    if args.epoch is not None and str(args.epoch).lstrip("-").isdigit():
        args.epoch = int(args.epoch)

    try:
        if args.gate:
            code, lines = gate(root)
            print("\n".join(lines), file=sys.stderr if code else sys.stdout)
            return code
        if args.record:
            return _do_record(args, root, ledger)

        atoms = atoms_from_map((root / MAP_REL).read_text(encoding="utf-8"))
        paths, scanned = live_orphan_paths(root)
        failures, report = check(read_ledger(ledger), atoms, paths, root)
        print("CONSOLIDATION RHYTHM -- %d atoms, %d modules scanned, %d record(s)"
              % (report["atoms_scanned"], scanned, report["records"]))
        print("  epochs closed: %s" % (report["epochs_closed"] or "none"))
        print("  coverage rule: %s" % report["coverage_rule"])
        print("  orphans live %d = %d forgiven at baseline + %d dispositioned + %d unaccounted"
              % (report["orphans_live"], report["orphans_forgiven_at_baseline"],
                 report["orphans_dispositioned"], len(report["orphans_unaccounted"])))
        if report["kept_repeats"]:
            print("  kept at more than one close (reported, never gated): %s"
                  % ", ".join(report["kept_repeats"][:10]))
        if args.report and report["orphans_unaccounted"]:
            print("  unaccounted since baseline:")
            for path in report["orphans_unaccounted"]:
                print("    %s" % path)
        for failure in failures:
            print("FAIL " + failure, file=sys.stderr)
        return 2 if failures and not args.report else 0
    except ConsolidationUnavailable as exc:
        print("FAIL consolidation check could not run: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
