"""GATE-WALL detection control (OPS1, director P0 2026-07-17): a promotion across a gate
(flip loop_stage idle -> build on parked/gated work) is authorized ONLY by a director
gate-opening through the console channel. This DETECTS -- report-only, LOUD -- any BUILD
promotion whose provenance does not trace to a director-console authorization. Hard
prevention comes AFTER this detection is proven live (director's explicit sequencing).

THE PRINCIPLE (director, verbatim spirit): the loop may SELF-SUSTAIN through work already
inside an open gate (draw the next queued task, no nudge -- the self-sustain fix) but may
never SELF-PROMOTE across a gate (flip idle->build on gated work) without the director's
authenticated act. Self-sustaining and self-promoting are DIFFERENT; this wall catches the
second. (Real incident it was built for: the autonomous worker flipped loop_stage idle->build
on OPS1_transport_failure_must_be_loud and OPS1_governance_refusal_mutation_test in its OWN
build commits, with no twin/director authorization -- nothing mechanical prevented it.)

AUTHORIZATION MODEL (director-decided): authorized ONLY by a director gate-opening recorded
with R7 provenance ("acted on the director's authenticated gate-opening"), tracing to a
director act through the CONSOLE channel -- NOT a twin/machine-writable log entry (marking
your own homework), NOT a bare token (spoofable/loseable). The console is the director's
unspoofable channel; this extends the same trust model as .build_executor_enabled. A ledger
entry only counts as authorization if it is action==BUILD_OPEN, authorized_by==director,
channel==console, and carries non-empty provenance.

SCOPE HONESTY (detection-first, per the director): this control robustly catches the ACTUAL
defect -- a promotion with NO valid director-console authorization record. Making the record
itself UNFORGEABLE by the worker (cryptographically tying provenance to the director_input_log
HMAC / a genuine console human-presence stamp so a worker cannot fabricate a channel==console
entry) is the PREVENTION layer, deliberately deferred. Until then a lying entry that self-
declares channel==console is possible; detection makes the honest defect LOUD now, and the
provenance field records the trace for the prevention pass to verify.
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
# Committed baseline: loop_stage per atom at the gate-wall genesis commit. A promotion is any
# atom that was 'idle' at genesis and has since advanced past idle -- that is the moment the
# gate is crossed, and it must trace to a director-console authorization. Atoms already active
# at genesis are grandfathered (the wall governs promotions from genesis forward).
BASELINE_PATH = PROJECT_DIR / "docs" / "observability" / "gate_wall_baseline.json"
# Append-only authorization ledger. Written ONLY via a director-console act (the director, or the
# console orchestrator acting on the director's authenticated console message). One JSON object
# per line: {atom, action:"BUILD_OPEN", ts, authorized_by:"director", channel:"console", provenance}.
LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "gate_authorizations.jsonl"


# ── pure map/loop_stage helpers ───────────────────────────────────────────────────────────
def atom_loop_stages(map_obj) -> dict:
    """{atom_id: loop_stage} for every atom in a parsed maturity map. Pure."""
    out: dict = {}

    def walk(o):
        if isinstance(o, dict):
            aid = o.get("id") or o.get("name")
            if isinstance(aid, str) and "loop_stage" in o:
                out[aid] = o.get("loop_stage")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(map_obj)
    return out


def current_loop_stages(path: Path | None = None) -> dict:
    """{atom_id: loop_stage} for the live map. {} on any read/parse failure (fail-safe: the
    caller treats an unreadable map as 'no promotions detectable' -- the transport-health
    control separately alarms on a broken map, so this does not need to double-alarm)."""
    try:
        docs = yaml.safe_load_all((path or MAP_PATH).read_text())
        out: dict = {}
        for d in docs:
            out.update(atom_loop_stages(d))
        return out
    except Exception:
        return {}


def load_baseline(path: Path | None = None) -> dict:
    """{atom_id: loop_stage} baseline snapshot, or {} if absent/unreadable."""
    try:
        return dict(json.loads((path or BASELINE_PATH).read_text()).get("stages", {}))
    except Exception:
        return {}


# ── the wall: pure predicates (mutation-testable core) ────────────────────────────────────
def promotions_since_baseline(current: dict, baseline: dict) -> list:
    """Atoms that crossed the gate since genesis: 'idle' at baseline, now advanced past idle.
    Pure. Only atoms PRESENT in the baseline are considered (new atoms are a separate concern,
    noted for the prevention pass) so a fresh legit atom does not false-positive here."""
    out = []
    for atom, base_stage in baseline.items():
        if base_stage == "idle":
            cur = current.get(atom)
            if cur is not None and cur != "idle":
                out.append({"atom": atom, "from": base_stage, "to": cur})
    return out


def _is_valid_authorization(entry) -> bool:
    """A ledger entry counts as authorization ONLY if it is a director-console BUILD_OPEN with
    provenance. A twin/machine self-write tagged anything other than console, or missing
    provenance, does NOT authorize -- 'not marking your own homework'."""
    return (
        isinstance(entry, dict)
        and entry.get("action") == "BUILD_OPEN"
        and entry.get("authorized_by") == "director"
        and entry.get("channel") == "console"
        and bool(str(entry.get("provenance") or "").strip())
    )


def authorized_atoms(ledger: list) -> set:
    """Set of atoms with at least one VALID director-console BUILD_OPEN authorization."""
    return {e["atom"] for e in ledger if _is_valid_authorization(e) and e.get("atom")}


def unauthorized_promotions(promotions: list, ledger: list) -> list:
    """THE predicate: promotions (idle->advanced) with NO valid director-console authorization.
    Pure -> mutation-testable. A promotion with a matching valid ledger entry is authorized
    (quiet); one with none, or only an invalid (non-console / no-provenance) entry, is LOUD."""
    ok = authorized_atoms(ledger)
    return [p for p in promotions if p["atom"] not in ok]


# ── ledger read/write ─────────────────────────────────────────────────────────────────────
def read_ledger(path: Path | None = None) -> list:
    """All ledger entries (one JSON object per line). [] if absent/unreadable. Never raises."""
    p = path or LEDGER_PATH
    out: list = []
    try:
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        return []
    return out


def record_gate_opening(atoms, provenance: str, *, ts: float | None = None,
                        path: Path | None = None) -> None:
    """Append a director-console BUILD_OPEN authorization for one or more atoms. CONSOLE-PATH
    ONLY: call this when acting on the director's authenticated console gate-opening, and pass
    a provenance string that traces to that console act (the director_input_log 'window' entry
    / the console directive). The autonomous worker (doorbell channel) must never call this --
    that is the prevention layer; detection makes an unauthorized flip LOUD regardless."""
    if isinstance(atoms, str):
        atoms = [atoms]
    p = path or LEDGER_PATH
    stamp = ts if ts is not None else time.time()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            for atom in atoms:
                f.write(json.dumps({
                    "atom": atom, "action": "BUILD_OPEN", "ts": stamp,
                    "authorized_by": "director", "channel": "console",
                    "provenance": provenance,
                }) + "\n")
    except Exception:
        pass


# ── live evaluation (report-only) ─────────────────────────────────────────────────────────
def evaluate_gate_wall(*, map_path: Path | None = None, baseline_path: Path | None = None,
                       ledger_path: Path | None = None) -> dict:
    """REPORT ONLY. Classify the gate wall from the live map vs baseline vs ledger.
      GATE_CLEAN     every promotion since genesis is director-console-authorized  (no alarm)
      GATE_VIOLATION >=1 idle->build promotion with no director-console authorization (ALARM)
    Never raises."""
    current = current_loop_stages(map_path)
    baseline = load_baseline(baseline_path)
    ledger = read_ledger(ledger_path)
    proms = promotions_since_baseline(current, baseline)
    unauth = unauthorized_promotions(proms, ledger)
    if unauth:
        names = ", ".join(u["atom"] for u in unauth[:6])
        return {"status": "GATE_VIOLATION", "alarm": True,
                "detail": f"{len(unauth)} BUILD promotion(s) with no director-console authorization: {names}",
                "unauthorized": unauth}
    return {"status": "GATE_CLEAN", "alarm": False,
            "detail": f"all {len(proms)} promotion(s) since genesis are director-authorized",
            "unauthorized": []}


if __name__ == "__main__":
    import sys
    r = evaluate_gate_wall()
    print(json.dumps(r, indent=2))
    sys.exit(1 if r["alarm"] else 0)
