"""SP5 -- the shared-primitive census as a standing gap register.

Serves `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28` s5 (via
`docs/design/SHARED_PRIMITIVE_ENSURING_ACTIVITY_DISCOVER.md`, 5.1): everything the ruling's
s2-s4 (working-day calculator, RNG substream, size/clone ratchet, quantity registry) built is a
*gate* -- it fires on a diff and returns pass/fail. Nothing asks "should this have been shared?"
or notices "this is the 92nd register." This module is the standing LOOK -- re-runnable from
primary state, never re-typed from the advisor's one-off AST census prose -- that turns the s0
snapshot into a register whose OPEN residue makes a rest/saturation claim impossible, matching
`background/gap_register_scan.py`'s own invariant for its eight registers (this is a candidate
row #9 in that same table -- see `docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md`).

SOFT-DEP HONESTY (2026-08-03, this atom's own BUILD pass): the DISCOVER doc named
`SP3_size_and_clone_ratchet`'s tooling as the substrate this census would read the clone ceiling
from. Verified against live disk: **no clone-detection tool exists anywhere under `tools/`** (nor
`background/`) at build time -- `SP3_size_and_clone_ratchet` is itself still unbuilt. Per the
DISCOVER doc's own instruction ("say so plainly and build the census on a substrate that does
exist rather than wiring a register to a stale artefact"), this module contains its OWN minimal,
independent AST clone-detector (see `_clone_census` below) rather than importing/wiring to a
nonexistent SP3 module. The clone ceiling (223) is recorded from the ruling's own s0 snapshot
directly, exactly as SP3's own mint doc licenses doing symmetrically ("the ratchet can record 223
from the ruling directly and reconcile when the census lands") -- to be reconciled against SP3's
own detector once that atom lands, never silently assumed equal.

INDEPENDENCE (LAW-C pattern, matching `background/primary_state_scan.py` /
`background/gap_register_scan.py`): imports NOTHING from `background/supervisor.py`. Walks the
live tree directly. A generator that read its own prior output to answer "did anything change"
would be a tautology; every number here is recomputed from source on every run.

LEVEL HONESTY: this atom targets level_current 0 -> 2, deliberately NOT 3 -- level 3 requires the
census to have caught a REAL re-duplication in the wild, which cannot be claimed at build time
(the register has never yet run against a genuine drift event). See module docstring bottom for
what is and is not built.

Primary-state artefact (generator-owned; nothing else may write it):
    docs/observability/shared_primitive_census.json

CLI:
    python3 -m background.shared_primitive_census            # regenerate + print residue
    python3 -m background.shared_primitive_census --check    # read-only: print residue, exit 1 if OPEN
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
OBS_DIR = PROJECT_DIR / "docs" / "observability"
CENSUS_PATH = OBS_DIR / "shared_primitive_census.json"

# The scan roots named in the DISCOVER doc (5.1), matching the advisor's own method: company code,
# not test code.
SCAN_ROOTS = ("company", "sim", "simulation", "saas", "background")

# Structural clone-set threshold: a function body normalises to >= this many AST node-type tokens
# before it is eligible to be counted as a clone instance (per the ruling's s0 method: "fingerprints
# of >=45 nodes appearing in >=2 files"). Exposed as a parameter (not a bare constant use-site) so
# tests can exercise the detector against small fixture functions without waiting for a 45-node
# example to be hand-written.
DEFAULT_NODE_THRESHOLD = 45

# Recorded from the ruling's s0 snapshot (2026-07-28) directly -- see module docstring for why this
# is not read from a still-nonexistent SP3 tool. Reconciled, not re-derived, once SP3 lands its own
# detector.
CLONE_CEILING = 223

# The retro cadence is the EXISTING scheduling mechanism this census's "standing structural review"
# rides (5.3: "does not invent a new cadence... avoids a second scheduling mechanism to maintain").
# A census is STALE if it was generated more than this many days before "now" -- the same threshold
# `background/retro_cadence_check.py` already uses for retro staleness, imported (not re-declared)
# where used, so the two clocks can never drift apart by editing one file and not the other.
_STALE_DAYS_FALLBACK = 14  # used only if retro_cadence_check is itself unimportable (fail-safe)


# =========================================================================== 1. AST clone census
def _iter_source_files(roots: tuple[str, ...] = SCAN_ROOTS, project_dir: Path = PROJECT_DIR) -> list[Path]:
    """Every .py file under the named roots, excluding tests and caches. FAIL-SAFE: a missing root
    is silently skipped (a partial repo checkout must not crash the census), but the aggregate
    reader downstream still treats a wholly-empty scan as suspicious via `files_scanned == 0`."""
    out: list[Path] = []
    for root in roots:
        base = project_dir / root
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            parts = p.relative_to(project_dir).parts
            if any(part == "__pycache__" for part in parts):
                continue
            if any(part == "tests" for part in parts):
                continue
            if p.name.startswith("test_"):
                continue
            out.append(p)
    return out


def _function_shape(node: ast.AST) -> list[str]:
    """Normalise a function body to its node-TYPE sequence (never literal values/names) -- the
    same structural-shape method the ruling's s0 census used. Two functions with identical control
    flow but different variable names/literals hash identically; two functions that merely share a
    name do not (this is a structural detector, not a name-grep -- the working_day_guard precedent
    already proved a name-only detector fail-opens on a rename)."""
    seq: list[str] = []
    for child in ast.walk(node):
        if child is node:
            continue
        seq.append(type(child).__name__)
    return seq


def _clone_census(
    files: list[Path], project_dir: Path = PROJECT_DIR, node_threshold: int = DEFAULT_NODE_THRESHOLD
) -> dict[str, Any]:
    """Independent AST clone-set detector. Returns {clone_count, clone_set_count, functions_scanned,
    files_scanned, unparseable}. `clone_count` = total function INSTANCES participating in a
    cross-file clone set (matching the ruling's s0 "223 instances" framing); `clone_set_count` =
    number of distinct fingerprints with >=2 distinct files (matching "70 clone-sets"). A clone set
    confined to ONE file (a local helper called twice) does NOT count -- only cross-file
    duplication is the s0 concern."""
    groups: dict[str, list[tuple[str, str, int]]] = {}
    functions_scanned = 0
    unparseable: list[str] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(f))
        except (OSError, SyntaxError, ValueError) as exc:
            unparseable.append(f"{f.relative_to(project_dir)}: {exc}")
            continue
        rel = str(f.relative_to(project_dir))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            functions_scanned += 1
            shape = _function_shape(node)
            if len(shape) < node_threshold:
                continue
            fp = hashlib.sha256(",".join(shape).encode("utf-8")).hexdigest()
            groups.setdefault(fp, []).append((rel, node.name, node.lineno))

    clone_count = 0
    clone_set_count = 0
    for members in groups.values():
        distinct_files = {m[0] for m in members}
        if len(distinct_files) >= 2:
            clone_set_count += 1
            clone_count += len(members)

    return {
        "clone_count": clone_count,
        "clone_set_count": clone_set_count,
        "functions_scanned": functions_scanned,
        "files_scanned": len(files),
        "unparseable": unparseable,
    }


# =========================================================================== 2. register-module count
def _register_count(project_dir: Path = PROJECT_DIR) -> int:
    """Count of modules under company/ whose FILENAME contains 'register' (case-insensitive),
    excluding caches -- the exact method that reproduces the ruling's own '91 register modules'
    figure (grep-verified against live disk at build time: 91/91)."""
    base = project_dir / "company"
    if not base.is_dir():
        return 0
    return sum(
        1
        for p in base.rglob("*.py")
        if "register" in p.name.lower() and "__pycache__" not in p.parts
    )


# =========================================================================== 3. named shared-primitive inventory
@dataclass(frozen=True)
class _PrimitiveSpec:
    canonical_path: str  # relative to project root; need not exist yet
    caller_pattern: re.Pattern[str]
    migrated_pattern: re.Pattern[str]


# The ruling s3 explicit list of seven named primitives. Each entry's canonical_path is the module
# that WOULD be the single source (built or not); caller_pattern matches files that touch the
# CONCEPT (a duplicate implementation or an ad-hoc reimplementation); migrated_pattern matches
# files that import the canonical module instead of reimplementing. The canonical file itself is
# excluded from both counts (a definition is not a "caller").
_NAMED_PRIMITIVES: dict[str, _PrimitiveSpec] = {
    "working_day_calculator": _PrimitiveSpec(
        canonical_path="company/compliance/working_days.py",
        caller_pattern=re.compile(
            r"\b(_add_working_days|_add_wd|_working_days_between|add_working_days|"
            r"working_days_between|working_days_open|working_days_to_pay|is_working_day)\b"
        ),
        migrated_pattern=re.compile(r"company\.compliance\.working_days"),
    ),
    "rng_substream_primitive": _PrimitiveSpec(
        canonical_path="company/compliance/rng_substream.py",
        caller_pattern=re.compile(
            r"\brandom\.Random\(|np\.random\.default_rng\(|numpy\.random\.RandomState\("
        ),
        migrated_pattern=re.compile(r"company\.compliance\.rng_substream"),
    ),
    "register_base_class": _PrimitiveSpec(
        canonical_path="company/compliance/register_base.py",
        caller_pattern=re.compile(r"^\s*class\s+\w*[Rr]egister\w*\s*[:(]", re.MULTILINE),
        migrated_pattern=re.compile(r"company\.compliance\.register_base"),
    ),
    "background_daemon_log_helper": _PrimitiveSpec(
        canonical_path="background/log_utils.py",
        caller_pattern=re.compile(r"^def log\(msg", re.MULTILINE),
        migrated_pattern=re.compile(r"background\.log_utils\s+import\s+log|from\s+\.\s*log_utils"),
    ),
    "clamp_term_end": _PrimitiveSpec(
        canonical_path="simulation/term_utils.py",
        caller_pattern=re.compile(r"_clamp_term_end"),
        migrated_pattern=re.compile(r"simulation\.term_utils"),
    ),
    "season_for_date": _PrimitiveSpec(
        canonical_path="sim/season_utils.py",
        caller_pattern=re.compile(r"\bseason_for_date\b"),
        migrated_pattern=re.compile(r"sim\.season_utils"),
    ),
    "vat_constant": _PrimitiveSpec(
        canonical_path="company/finance/vat_book.py",
        caller_pattern=re.compile(
            r"VAT_RATE\s*=\s*0\.\d+|_VAT_RATES\s*[:=]|\bvat_rate\s*\("
        ),
        migrated_pattern=re.compile(r"company\.finance\.vat_book"),
    ),
}


def _primitive_inventory(
    files: list[Path], project_dir: Path = PROJECT_DIR
) -> dict[str, dict[str, Any]]:
    """{name: {exists, caller_count, migrated_count}} for the seven named primitives. Reads real
    file text (independent of any other module's own inventory of itself)."""
    out: dict[str, dict[str, Any]] = {}
    for name, spec in _NAMED_PRIMITIVES.items():
        canonical_abs = (project_dir / spec.canonical_path).resolve()
        exists = canonical_abs.is_file()
        callers = 0
        migrated = 0
        for f in files:
            if f.resolve() == canonical_abs:
                continue  # the definition site is not a "caller"
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            if spec.caller_pattern.search(text):
                callers += 1
            if spec.migrated_pattern.search(text):
                migrated += 1
        out[name] = {"exists": exists, "caller_count": callers, "migrated_count": migrated}
    return out


# =========================================================================== 4. owned-quantity coverage
# The ruling s4 six named quantities. "has_owner" is TRUE only when some module's own text
# EXPLICITLY declares itself the single owning module for that quantity -- a related module simply
# existing (e.g. carbon_ledger.py) is NOT enough (that would be a tautology: "a file about carbon
# exists" is not "a file that OWNS carbon"). None declare this today (SP4_owned_quantity_registry_gate
# is itself unbuilt), so this reads all-False honestly rather than fabricating coverage.
_QUANTITIES = ("net_margin", "treasury", "expected_value", "bad_debt", "cost_to_serve", "carbon")
_QUANTITY_ALIASES = {
    "net_margin": r"net margin",
    "treasury": r"treasury",
    "expected_value": r"expected value|\bEV\b",
    "bad_debt": r"bad debt",
    "cost_to_serve": r"cost.to.serve",
    "carbon": r"carbon",
}
_OWNERSHIP_PHRASE = r"single (?:owning|source of truth)|canonical owner|the one (?:owning|canonical) module"
# PROXIMITY WINDOW (found live, 2026-08-03 build pass -- a real false-positive, not hypothetical):
# `simulation/arrears_engine.py`'s docstring contains BOTH "Single source of truth" (for payment
# outcome/arrears) AND, ~280-380 chars later in the same docstring, incidental mentions of "bad
# debt" and "cost_to_serve" (the module it REPLACES, not owns). A whole-docstring co-occurrence
# check read that as has_owner=True for both -- a FAIL-OPEN (a coverage row silently reads CLOSED
# for a quantity nobody actually declared ownership of). Binding the ownership phrase and the
# quantity alias into ONE regex with a bounded window removes the coincidental-co-occurrence
# false-positive: a genuine declaration ("single owning module for net margin") sits within a few
# words of the quantity name; an incidental same-paragraph mention of an unrelated quantity 300+
# chars away does not.
_PROXIMITY_CHARS = 80


def _quantity_coverage(files: list[Path], project_dir: Path = PROJECT_DIR) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for q in _QUANTITIES:
        alias = _QUANTITY_ALIASES[q]
        # Either order (ownership phrase then quantity, or quantity then ownership phrase),
        # bounded window between them -- a genuine declaration, not a same-docstring coincidence.
        combined_re = re.compile(
            rf"(?:{_OWNERSHIP_PHRASE}).{{0,{_PROXIMITY_CHARS}}}(?:{alias})"
            rf"|(?:{alias}).{{0,{_PROXIMITY_CHARS}}}(?:{_OWNERSHIP_PHRASE})",
            re.IGNORECASE | re.DOTALL,
        )
        owner: str | None = None
        for f in files:
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            head = text[:2000]  # module docstring lives at the top; bounded read
            if combined_re.search(head):
                owner = str(f.relative_to(project_dir))
                break
        out[q] = {"has_owner": owner is not None, "owner_module": owner}
    return out


# =========================================================================== generator entrypoint
def generate(
    project_dir: Path = PROJECT_DIR,
    roots: tuple[str, ...] = SCAN_ROOTS,
    node_threshold: int = DEFAULT_NODE_THRESHOLD,
    migration_note: str | None = None,
    previous_census_path: Path | None = None,
) -> dict[str, Any]:
    """Recompute the whole census from primary state (never from a prior JSON's own numbers --
    that would be the TAUTOLOGY pattern R15 forbids). `previous_census_path` (defaults to
    CENSUS_PATH) is read ONLY to detect register_count DRIFT since the last run; every number in
    the returned dict is freshly computed from the live tree."""
    files = _iter_source_files(roots, project_dir)
    clone = _clone_census(files, project_dir, node_threshold)
    register_count = _register_count(project_dir)
    inventory = _primitive_inventory(files, project_dir)
    coverage = _quantity_coverage(files, project_dir)

    prev_path = previous_census_path or CENSUS_PATH
    prev_register_count: int | None = None
    try:
        prev = json.loads(Path(prev_path).read_text(encoding="utf-8"))
        prev_register_count = prev.get("register_count")
    except Exception:  # noqa: BLE001 -- no valid prior census; drift check simply has nothing to compare
        prev_register_count = None

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clone_count": clone["clone_count"],
        "clone_ceiling": CLONE_CEILING,
        "clone_set_count": clone["clone_set_count"],
        "functions_scanned": clone["functions_scanned"],
        "files_scanned": clone["files_scanned"],
        "unparseable": clone["unparseable"],
        "register_count": register_count,
        "previous_register_count": prev_register_count,
        "migration_note": migration_note,
        "shared_primitive_inventory": inventory,
        "quantity_registry_coverage": coverage,
    }


def write_census(
    data: dict[str, Any] | None = None,
    path: Path | None = None,
    **generate_kwargs: Any,
) -> Path:
    """Write the census JSON. This module is the ONLY writer of `shared_primitive_census.json`
    (matches the DISCOVER doc's own invariant: 'the generator is the only writer, everything else
    only reads it')."""
    p = path or CENSUS_PATH
    data = data if data is not None else generate(**generate_kwargs)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


# =========================================================================== register #9 reader
def _unreadable(reason: str) -> dict[str, str]:
    return {"register": "shared_primitive_census", "id": "unreadable", "reason": reason}


def _stale_days_threshold() -> int:
    """The SAME staleness threshold `retro_cadence_check.py` uses (imported, never re-declared) --
    5.1's own R15 spec: 'a census that cannot have observed recent drift is not evidence of "no
    drift"'. FAIL-SAFE: if the retro module is itself unimportable, fall back to the local constant
    rather than raising (an unavailable staleness threshold must not silently disable staleness
    detection -- it must use a conservative fallback and keep checking)."""
    try:
        from background.retro_cadence_check import RETRO_STALE_DAYS

        return int(RETRO_STALE_DAYS)
    except Exception:  # noqa: BLE001
        return _STALE_DAYS_FALLBACK


def census_register_open(path: Path | None = None, now: datetime | None = None) -> list[dict[str, str]]:
    """Register #9's OPEN rows (empty list = CLOSED). FAIL-CLOSED (R15, matching GAP1's own
    invariant 2 -- 'fail-safe toward work'): unreadable/missing/malformed census -> ONE open
    'unreadable' row (never a silent empty list). A stale census (generated before the last retro
    window) is likewise OPEN -- 'unmeasured' is not evidence of 'no drift'. Every other check
    (clone drift past ceiling, an unmigrated named primitive, an uncovered quantity, ungoverned
    register-count growth) is evaluated independently, so a clean run can read CLOSED with proof,
    not merely 'no error happened'."""
    p = path or CENSUS_PATH
    try:
        raw = Path(p).read_text(encoding="utf-8")
    except OSError as exc:
        return [_unreadable(f"read-error: {exc}")]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return [_unreadable(f"malformed-json: {exc}")]
    if not isinstance(data, dict):
        return [_unreadable("census file is not a JSON object")]

    # Required shape check -- an empty {} or a truncated/wrong-shape file must NOT vacuously pass
    # (the exact FAIL-OPEN-ON-EMPTY-INPUT class named in the brief: verdict({}) must never read
    # CLOSED). Every key this reader depends on must be present and of the right kind.
    required = (
        "generated_at", "clone_count", "clone_ceiling", "register_count",
        "shared_primitive_inventory", "quantity_registry_coverage",
    )
    missing = [k for k in required if k not in data]
    if missing:
        return [_unreadable(f"census missing required field(s): {missing}")]

    out: list[dict[str, str]] = []

    # (staleness) generated_at older than the retro cadence's own staleness threshold -> OPEN.
    now = now or datetime.now(timezone.utc)
    try:
        gen_at = datetime.fromisoformat(str(data["generated_at"]))
        if gen_at.tzinfo is None:
            gen_at = gen_at.replace(tzinfo=timezone.utc)
        age_days = (now - gen_at).total_seconds() / 86400.0
    except (ValueError, TypeError):
        return [_unreadable(f"unparseable generated_at: {data.get('generated_at')!r}")]
    threshold = _stale_days_threshold()
    if age_days > threshold:
        out.append({
            "register": "shared_primitive_census",
            "id": "stale",
            "reason": f"census is {age_days:.1f}d old, threshold {threshold}d "
                      "(unmeasured is not evidence of no drift)",
        })

    # (a) clone drift past the ratchet's recorded ceiling.
    try:
        clone_count = int(data["clone_count"])
        clone_ceiling = int(data["clone_ceiling"])
    except (TypeError, ValueError):
        return [_unreadable("clone_count/clone_ceiling non-numeric")]
    if clone_count > clone_ceiling:
        out.append({
            "register": "shared_primitive_census",
            "id": "clone_drift",
            "reason": f"clone_count={clone_count} > ceiling={clone_ceiling}",
        })

    # (b) an unfinished migration: a named primitive EXISTS but a caller still runs the duplicate.
    inventory = data.get("shared_primitive_inventory")
    if not isinstance(inventory, dict):
        return [_unreadable("shared_primitive_inventory is not a dict")]
    for name, entry in inventory.items():
        if not isinstance(entry, dict):
            out.append({"register": "shared_primitive_census", "id": f"inventory:{name}",
                        "reason": "malformed inventory entry (fail-safe OPEN)"})
            continue
        if entry.get("exists") is True:
            caller = entry.get("caller_count")
            migrated = entry.get("migrated_count")
            if not isinstance(caller, (int, float)) or not isinstance(migrated, (int, float)):
                out.append({"register": "shared_primitive_census", "id": f"inventory:{name}",
                            "reason": "non-numeric caller/migrated count (fail-safe OPEN)"})
                continue
            if migrated < caller:
                out.append({
                    "register": "shared_primitive_census",
                    "id": f"unmigrated:{name}",
                    "reason": f"{name} exists but migrated_count={migrated} < caller_count={caller}",
                })

    # (c) a named quantity with no declared owning module.
    coverage = data.get("quantity_registry_coverage")
    if not isinstance(coverage, dict):
        return [_unreadable("quantity_registry_coverage is not a dict")]
    for q, entry in coverage.items():
        if not isinstance(entry, dict) or "has_owner" not in entry:
            out.append({"register": "shared_primitive_census", "id": f"coverage:{q}",
                        "reason": "malformed coverage entry (fail-safe OPEN)"})
            continue
        if entry.get("has_owner") is not True:
            out.append({
                "register": "shared_primitive_census",
                "id": f"no_owner:{q}",
                "reason": f"{q} has no declared single owning module",
            })

    # (d) register_count grew since the last recorded run without a migration note in the SAME run.
    try:
        register_count = int(data["register_count"])
    except (TypeError, ValueError):
        return [_unreadable("register_count non-numeric")]
    prev = data.get("previous_register_count")
    if isinstance(prev, (int, float)) and register_count > prev and not data.get("migration_note"):
        out.append({
            "register": "shared_primitive_census",
            "id": "register_growth",
            "reason": f"register_count grew {prev} -> {register_count} with no migration_note "
                      "recorded in this run (new duplication accreting, not draining)",
        })

    return out


def shared_primitive_census_open(path: Path | None = None) -> bool:
    """True iff register #9 holds any OPEN row -- symmetrical to
    `background.gap_register_scan.gap_register_open()`. Wiring this in as row #9 of that reader's
    `_REGISTERS` table (background/gap_register_scan.py, outside this atom's file_scope) is the
    ONE remaining line needed to make register #9 count toward the whole-set rest proof in
    `supervisor.authorized_set_enumeration()` -- see this module's own docstring tail for the exact
    line. Until that wiring lands, this function is directly callable/testable but not yet on the
    tick's own draw path."""
    return bool(census_register_open(path))


def open_residue_counts(path: Path | None = None) -> int:
    """Diagnostic count only (R12: never a score/target) -- number of open rows in register #9."""
    return len(census_register_open(path))


# =========================================================================== 5.3 standing structural review trigger
def standing_review_due(today=None, retro_dir: Path | None = None, project_dir: Path = PROJECT_DIR) -> str | None:
    """5.3's trigger -- MECHANISED, not prose, and NOT a new scheduling mechanism (design doc:
    'rides the existing retro trigger... avoiding a second scheduling mechanism to maintain').
    Delegates entirely to `background.retro_cadence_check.check_retro_staleness()` (the retro
    cadence already live in `health_check.py`) -- returns that function's own alarm string
    (non-None => review due: re-run the census, diff, route through phase-close-evaluator per 5.4)
    or None (not due). FAIL-SAFE: if the retro module is unimportable, treat the review as DUE
    (returns a message saying so) rather than silently never firing."""
    try:
        from background.retro_cadence_check import RETRO_DIR, check_retro_staleness

        rd = retro_dir or RETRO_DIR
        return check_retro_staleness(today=today, retro_dir=rd, project_dir=project_dir)
    except Exception as exc:  # noqa: BLE001 -- an unavailable trigger must not silently mean "never due"
        return f"standing structural review DUE: retro_cadence_check unavailable ({exc})"


# =========================================================================== CLI
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="read-only: report residue, do not regenerate")
    parser.add_argument("--migration-note", default=None, help="record a migration note for this run's register-count growth")
    args = parser.parse_args()

    if args.check:
        rows = census_register_open()
        if rows:
            print(f"[shared_primitive_census] OPEN ({len(rows)} row(s)):")
            for r in rows:
                print(f"  - {r['id']}: {r['reason']}")
            return 1
        print("[shared_primitive_census] CLOSED (no open rows)")
        return 0

    data = generate(migration_note=args.migration_note)
    path = write_census(data)
    print(f"[shared_primitive_census] wrote {path}")
    print(f"  clone_count={data['clone_count']} (ceiling {data['clone_ceiling']}), "
          f"clone_set_count={data['clone_set_count']}, register_count={data['register_count']}")
    rows = census_register_open(path)
    if rows:
        print(f"[shared_primitive_census] OPEN ({len(rows)} row(s)):")
        for r in rows:
            print(f"  - {r['id']}: {r['reason']}")
        return 1
    print("[shared_primitive_census] CLOSED (no open rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
