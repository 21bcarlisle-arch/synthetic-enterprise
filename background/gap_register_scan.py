"""GAP1 BUILD half (b/c/d) -- the INDEPENDENT gap-register reader.

Serves `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` via the DISCOVER contract
`docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md`. The acceptance the ruling turns on:
*a saturation/rest claim is impossible while any published register holds an open, un-triaged item.*

This module emits the OPEN residue across the eight published gap registers, reading PRIMARY state
directly. `supervisor.py` wires `gap_register_open()` as a detector level in
`authorized_set_enumeration()` (Y => drawable => rest illegitimate), so the whole-set rest proof
includes the published registers -- they were the backlog and nothing read them as work.

Reader-contract invariants (from the contract, each enforced below):
  1. INDEPENDENT READ (LAW-C). Imports NOTHING from `supervisor.py`; reads disk exactly as
     `background/primary_state_scan.py` does. A reader that restated the tick's own belief could not
     falsify a saturation claim (R15 tautology, forbidden).
  2. FAIL-SAFE TOWARD WORK. A parse/read error on any register yields an `unreadable` OPEN row (the
     Rule-0 direction -- ambiguity forbids rest), NEVER a silent empty. Mirrors `_safe()`.
  3. R12. The residue COUNT is a diagnostic on the enumeration line only -- never a score/target.
     This module emits the residue; it never scores it.
  4. DIAGNOSTIC, NOT CLOSURE. A row in the residue means *drawable* ("a saturation claim is
     illegitimate while this is open"). The deliberate-vs-mint call is GAP2, director-ratified --
     never made here.

Two OPEN rules the GAP3 live-register pass proved would FAIL-OPEN, corrected here per the contract:
  - Register 1 keys on a TEXT HEURISTIC (not the non-existent `measured_bound` field): an entry is
    OPEN when it is neither a dated progress-log line NOR carries an inline measured bound.
  - Register 6 keys on `state` across ALL prefixes (not `audit:*`): OPEN when state is `open` or
    `adjudicated-real`. The 15 real findings live under coldwalk/harden_sweep/expert_hour/... .

FIXTURE ISOLATION: every register function takes an injectable path so tests pin their own files
(a new draw signal must never read live disk in a test -- feedback_new_draw_rung_needs_fixture_isolation).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(__file__).resolve().parent.parent
DESIGN_DIR = PROJECT_DIR / "docs" / "design"
OBS_DIR = PROJECT_DIR / "docs" / "observability"

MATURITY_MAP_PATH = DESIGN_DIR / "maturity_map.yaml"
FIDELITY_LEDGER_PATH = OBS_DIR / "fidelity_evidence_ledger.json"
SANITY_LEDGER_PATH = OBS_DIR / "sanity_adjudication_ledger.json"
BOARD_SPEC_GLOB_DIR = DESIGN_DIR
MODEL_ON_A_PAGE_PATH = DESIGN_DIR / "THE_MODEL_ON_A_PAGE.md"
PROPOSALS_DIR = DESIGN_DIR / "proposals"
CARBON_LEDGER_PATH = PROJECT_DIR / "company" / "carbon" / "carbon_ledger.py"

# A row that stands for "a register could not be read". Its PRESENCE is the fail-safe: an unreadable
# register is a *reason the residue may be non-empty*, never a silent empty (invariant 2).
def _unreadable(register: str, detail: str) -> dict[str, str]:
    return {"register": register, "id": f"unreadable:{register}", "reason": f"read-error: {detail}"}


# --------------------------------------------------------------------------- register 1
# Deliberate-simplifications register: maturity_map.yaml per-atom `simplifications:` lists. Plain
# free-text strings (no structured `measured_bound` field exists). OPEN when the entry is NEITHER a
# dated progress-log line NOR carries an inline measured bound.
_DATED_LOG_RE = re.compile(r"^\s*\d{4}-\d{2}-\d{2}\s+[A-Z]")  # ISO date + uppercase log verb
# An inline measured bound: any numeric/interval/percent/plus-minus/comparison token stating HOW
# WRONG the simplification is. Deliberate simplifications argue their bound inline (staying); a bare
# unmeasured, non-log simplification is OPEN.
_MEASURED_BOUND_RE = re.compile(
    r"[<>±]|\d+\s*%|[+-]?\d+(?:\.\d+)?\s*(?:x|×|bps|pp|kwh|mwh|gwh|£|gbp|days?|hours?|hh|£/|p/)"
    r"|\b\d+(?:\.\d+)?\s*(?:to|-|–|—)\s*\d+(?:\.\d+)?\b"
    r"|\+/-|\bwithin\s+\d|\berror\b.*\d|\bgap\b.*\d",
    re.IGNORECASE,
)


def _iter_simplifications(node: Any):
    """Yield every free-text simplification string from a parsed maturity_map (recursive)."""
    if isinstance(node, dict):
        s = node.get("simplifications")
        if isinstance(s, list):
            for e in s:
                if isinstance(e, str):
                    yield node.get("id", node.get("atom", "?")), e
        for v in node.values():
            yield from _iter_simplifications(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_simplifications(v)


def _entry_is_open(entry: str) -> bool:
    """A simplification entry is OPEN (drawable) when it is NEITHER a dated progress-log line NOR
    carries an inline measured bound. FAIL-SAFE toward OPEN on an entry we cannot classify."""
    if _DATED_LOG_RE.match(entry):
        return False  # a FRAME/HARDEN progress-log line, not a live simplification
    if _MEASURED_BOUND_RE.search(entry):
        return False  # argued with a measured bound -> deliberate-and-staying (pending GAP2)
    return True  # bare, unmeasured, non-log simplification -> OPEN


def register1_simplifications(path: Path | None = None) -> list[dict[str, str]]:
    p = path or MATURITY_MAP_PATH
    try:
        import yaml  # local import: the reader must not hard-fail if PyYAML is unavailable

        data = yaml.safe_load(Path(p).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 -- any parse/read failure is fail-safe toward work
        return [_unreadable("simplifications", str(exc)[:120])]
    out: list[dict[str, str]] = []
    for atom_id, entry in _iter_simplifications(data):
        if _entry_is_open(entry):
            out.append({"register": "simplifications", "id": f"{atom_id}", "reason": entry[:140]})
    return out


# --------------------------------------------------------------------------- register 2
# Fidelity-evidence ledger: a per_cell_lift cell is OPEN when at commercial_weight > 0 the model is
# at/below its own naive baseline (lift <= 0 OR err_model >= err_naive).
def _finite(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def register2_fidelity(path: Path | None = None) -> list[dict[str, str]]:
    p = path or FIDELITY_LEDGER_PATH
    try:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [_unreadable("fidelity", str(exc)[:120])]
    if not isinstance(data, dict):
        return [_unreadable("fidelity", "ledger is not a dict")]
    out: list[dict[str, str]] = []
    for row_id, row in data.items():
        cells = row.get("per_cell_lift") if isinstance(row, dict) else None
        if not isinstance(cells, list):
            continue
        for cell in cells:
            if not isinstance(cell, dict):
                out.append(_unreadable("fidelity", f"{row_id}: non-dict cell"))
                continue
            cw = _finite(cell.get("commercial_weight"))
            if cw is None:
                # cannot tell if commercially weighted -> fail-safe toward OPEN
                out.append({"register": "fidelity", "id": f"{row_id}:{cell.get('cell','?')}",
                            "reason": "commercial_weight non-finite (fail-safe OPEN)"})
                continue
            if cw <= 0:
                continue
            lift = _finite(cell.get("lift"))
            err_model = _finite(cell.get("err_model"))
            err_naive = _finite(cell.get("err_naive"))
            below_naive = (
                lift is None  # non-finite lift at weight>0 -> fail-safe OPEN
                or lift <= 0
                or (err_model is not None and err_naive is not None and err_model >= err_naive)
                or (err_model is None or err_naive is None)  # missing error terms at weight>0 -> OPEN
            )
            if below_naive:
                out.append({"register": "fidelity", "id": f"{row_id}:{cell.get('cell','?')}",
                            "reason": f"lift={cell.get('lift')} err_model={cell.get('err_model')} "
                                      f"err_naive={cell.get('err_naive')} regime={cell.get('regime')}"})
    return out


# --------------------------------------------------------------------------- register 6
# Standing sanity findings: sanity_adjudication_ledger.json, key `<prefix>:<finding>`, value has a
# `state` field. OPEN when state is `open` or `adjudicated-real`, across ALL prefixes (NOT audit:*).
_RESIDUE_STATES = {"open", "adjudicated-real"}


def register6_sanity(path: Path | None = None) -> list[dict[str, str]]:
    p = path or SANITY_LEDGER_PATH
    try:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [_unreadable("sanity", str(exc)[:120])]
    if not isinstance(data, dict):
        return [_unreadable("sanity", "ledger is not a dict")]
    out: list[dict[str, str]] = []
    for key, row in data.items():
        state = row.get("state") if isinstance(row, dict) else None
        if state is None:
            out.append(_unreadable("sanity", f"{key}: no state field"))
            continue
        if str(state).strip().lower() in _RESIDUE_STATES:
            out.append({"register": "sanity", "id": str(key), "reason": f"state={state}"})
    return out


# --------------------------------------------------------------------------- registers 3, 4
# Board-spec reconciliations + disqualification battery. Heuristic md scan; FAIL-SAFE toward drawable
# (an unreadable doc yields an `unreadable` row). Register 3: rows marked PARTIAL or ABSENT. Register
# 4: battery items whose status is not `met`.
_BOARD_SPEC_RE = re.compile(r"BOARD_SPEC_00\d_RECONCILIATION\.md$|WHOLESALE_TRADING_BOARD_RECONCILIATION.*\.md$")
_PARTIAL_ABSENT_RE = re.compile(r"\b(PARTIAL|ABSENT)\b")
_BATTERY_HEAD_RE = re.compile(r"disqualification battery", re.IGNORECASE)
_MET_RE = re.compile(r"\b(met|✓|resolved|closed)\b", re.IGNORECASE)


def _board_spec_files(dir_path: Path | None = None) -> list[Path]:
    d = dir_path or BOARD_SPEC_GLOB_DIR
    try:
        return sorted(p for p in Path(d).glob("*RECONCILIATION*.md") if _BOARD_SPEC_RE.search(p.name))
    except OSError:
        return []


def register3_board_reconciliations(dir_path: Path | None = None) -> list[dict[str, str]]:
    files = _board_spec_files(dir_path)
    out: list[dict[str, str]] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            out.append(_unreadable("board_recon", f"{f.name}: {exc}"))
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("|") and _PARTIAL_ABSENT_RE.search(line):
                out.append({"register": "board_recon", "id": f"{f.name}:L{i}", "reason": line.strip()[:140]})
    return out


def register4_disqualification_battery(dir_path: Path | None = None) -> list[dict[str, str]]:
    files = _board_spec_files(dir_path)
    out: list[dict[str, str]] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            out.append(_unreadable("battery", f"{f.name}: {exc}"))
            continue
        in_battery = False
        for i, line in enumerate(text.splitlines(), 1):
            if line.startswith("#"):
                in_battery = bool(_BATTERY_HEAD_RE.search(line))
                continue
            if not in_battery:
                continue
            if line.lstrip().startswith(("|", "-", "*")) and line.strip("|-* \t"):
                if not _MET_RE.search(line):
                    out.append({"register": "battery", "id": f"{f.name}:L{i}", "reason": line.strip()[:140]})
    return out


# --------------------------------------------------------------------------- register 5
# Claim-status placeholders (designed-but-not-working). Seed: the carbon ledger (E5_carbon_three_ledger,
# idle level 0->3). A placeholder marker still present is an OPEN row (R11: claim != pixel).
_CLAIM_STATUS_RE = re.compile(r"claim_status|PLACEHOLDER|not[_\s-]wired|NotImplemented", re.IGNORECASE)


def register5_claim_placeholders(carbon_path: Path | None = None) -> list[dict[str, str]]:
    # The contract SEEDS the residue with E5_carbon_three_ledger (map atom idle, level_current 0->3):
    # an idle-level-0 atom whose surface claims a capability that is not yet wired to a live consumer
    # is a placeholder by definition (R11: claim != pixel). It stays an OPEN row until that atom reaches
    # build-quality -- the BUILD pass enumerates the rest. So seed it UNCONDITIONALLY, and additionally
    # note any explicit placeholder marker found in the seed file.
    p = carbon_path or CARBON_LEDGER_PATH
    reason = "seed: carbon three-ledger placeholder (map atom E5 idle, level_current 0->3; claim != pixel)"
    try:
        if Path(p).exists() and _CLAIM_STATUS_RE.search(Path(p).read_text(encoding="utf-8")):
            reason = "carbon_ledger.py carries an explicit placeholder/claim_status marker (R11)"
    except OSError:
        pass  # cannot read the seed file -> still seed the known-idle atom (fail-safe toward work)
    return [{"register": "claim_placeholder", "id": "E5_carbon_three_ledger", "reason": reason}]


# --------------------------------------------------------------------------- registers 7, 8
# Model-on-a-page Timeframe 2 (best-effort) + registered follow-ons. Heuristic; FAIL-SAFE toward
# drawable. These are the contract's "enumerate the rest on the BUILD pass" registers -- documented
# best-effort scanners, never a silent empty on a read error.
def register7_model_timeframe2(path: Path | None = None) -> list[dict[str, str]]:
    p = path or MODEL_ON_A_PAGE_PATH
    try:
        if not Path(p).exists():
            return [_unreadable("model_tf2", "THE_MODEL_ON_A_PAGE.md absent")]
        text = Path(p).read_text(encoding="utf-8")
    except OSError as exc:
        return [_unreadable("model_tf2", str(exc)[:120])]
    out: list[dict[str, str]] = []
    in_tf2 = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            in_tf2 = "timeframe 2" in line.lower() or "timeframe-2" in line.lower()
            continue
        if not in_tf2:
            continue
        stripped = line.strip()
        if stripped.startswith(("-", "*")) and stripped.strip("-* \t"):
            # a Timeframe-2 capability line not marked LIVE/backed is OPEN (best-effort)
            if not re.search(r"\b(LIVE|backed|shipped|done|✓)\b", line, re.IGNORECASE):
                out.append({"register": "model_tf2", "id": f"L{i}", "reason": stripped[:140]})
    return out


def register8_followons(dir_path: Path | None = None) -> list[dict[str, str]]:
    d = dir_path or PROPOSALS_DIR
    try:
        files = sorted(Path(d).glob("PROPOSE_*FOLLOWON*"))
    except OSError as exc:
        return [_unreadable("followons", str(exc)[:120])]
    out: list[dict[str, str]] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except OSError as exc:
            out.append(_unreadable("followons", f"{f.name}: {exc}"))
            continue
        for i, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            # a ranked follow-on row (numbered/bulleted) neither minted nor explicitly retired
            if re.match(r"^\s*(\d+[.)]|[-*])\s+\S", line) and not re.search(
                r"\b(minted|retired|done|superseded|MINTED|✓)\b", line
            ):
                out.append({"register": "followons", "id": f"{f.name}:L{i}", "reason": stripped[:140]})
    return out


# --------------------------------------------------------------------------- aggregate
_REGISTERS = {
    "simplifications": register1_simplifications,
    "fidelity": register2_fidelity,
    "sanity": register6_sanity,
    "board_recon": register3_board_reconciliations,
    "battery": register4_disqualification_battery,
    "claim_placeholder": register5_claim_placeholders,
    "model_tf2": register7_model_timeframe2,
    "followons": register8_followons,
}


def open_residue(paths: dict[str, Path] | None = None) -> dict[str, list[dict[str, str]]]:
    """The OPEN residue across all eight registers, {register_name: [open_row, ...]}. Every register
    fails safe toward work (an unreadable register yields an `unreadable` row, never a silent empty).
    Paths (for fixture isolation): {register_name: Path} overrides a register's primary-state path.

    R12: this is a DIAGNOSTIC. It emits the residue; it NEVER scores or ranks it. The
    deliberate-vs-mint call is GAP2, director-ratified -- never made here (invariant 4)."""
    paths = paths or {}
    out: dict[str, list[dict[str, str]]] = {}
    for name, fn in _REGISTERS.items():
        try:
            out[name] = fn(paths.get(name)) if name in paths else fn()
        except Exception as exc:  # noqa: BLE001 -- a register bug must fail SAFE toward work, never crash the draw
            out[name] = [_unreadable(name, f"scanner-exception: {exc}")]
    return out


def gap_register_open(paths: dict[str, Path] | None = None) -> bool:
    """True iff any published gap register holds an OPEN row (=> drawable => rest illegitimate). The
    detector `supervisor.authorized_set_enumeration()` wires this as the `gap_register` level."""
    residue = open_residue(paths)
    return any(rows for rows in residue.values())


def open_residue_counts(paths: dict[str, Path] | None = None) -> dict[str, int]:
    """Per-register open-row counts, for the enumeration/diagnostic line only (R12: never a score)."""
    return {name: len(rows) for name, rows in open_residue(paths).items()}
