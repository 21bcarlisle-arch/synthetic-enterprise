"""Self-Governance Scope Model — reconcile the DECLARED scope (fronts.yaml + the console ledger)
against the ACTUAL map state (loop_stage + level_current deltas vs baselines). REPORT ONLY.

docs/design/SELF_GOVERNANCE_SCOPE_MODEL.md (§2 reconcile, §4 composition, §5 anti-failure, §10
addendum: the LEVEL gate + loop_stage-respect). Sub-steps 2 (predicates + classifier), 4 (wired
report / transition-only alarm), 5 (draw-filter helper).

WHAT THIS GENERALISES (it does NOT fork a parallel mechanism):
  background/gate_authorization.py caught ONE thing — a loop_stage idle->build promotion of ONE
  named atom with no director-console BUILD_OPEN. This lifts that to a declared REGION ("fronts")
  minus declared boundaries ("gates"), and adds two gate classes the single-atom wall never had:
    * the LEVEL gate (§10.1): any level_current increase vs the committed baseline with no
      director+advisor LEVEL_UP_PROPOSED is a LEVEL_SELF_PROMOTION — the agent proposes, never
      moves a cell (MATURITY_MAP.md §0).
    * loop_stage-respect / stage-advance (§10.2): advancing an atom's canonical stage (idle->build)
      is the reserved BUILD-open gate; a DISCOVER-stage (loop_stage: idle) atom is DISCOVER/FRAME-
      only, never BUILD.
  It REUSES gate_authorization's promotions_since_baseline / authorized_atoms / _is_valid_* and
  one_way_door.classify_action verbatim — the wrappers wrap, they do not replace.

INDEPENDENCE (R15 anti-tautology): the thing CHECKED (the map — loop_stage/level_current, written
by the loop) and the AUTHORITY it is checked against (the console ledger — valid entries written
only by the console orchestrator on a director act) have DIFFERENT WRITERS. A loop that promotes
an atom cannot also mint the console entry that authorizes it (that is the prevention layer). A
forged entry self-declaring channel==console is the known residual (sub-step 7); detection is
honest and LOUD now.

NO WRITE PATH TO THE MAP by construction (like process_reconciler.py — reaping/writing by inference
caused the blackout). This module detects and reports; it never "fixes".
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from background import gate_authorization as _gw
from background import one_way_door as _owd

PROJECT_DIR = Path(__file__).resolve().parent.parent
FRONTS_PATH = PROJECT_DIR / "background" / "fronts.yaml"
MAP_PATH = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"

# The LEVEL baseline (§10.1): level_current per atom AT this committed genesis ref. Any live increase
# past it with no LEVEL_UP_PROPOSED is a LEVEL_SELF_PROMOTION. A committed git ref (not a JSON file in
# docs/observability) so the baseline is IaC that lives in-scope and cannot be silently rewritten by a
# working-tree edit — the loop would have to rewrite git history to move it. Pinned to the scope-model
# genesis commit; advancing it is a deliberate, reviewed act (a level baseline re-snapshot).
LEVEL_BASELINE_REF = "2e95ffacc754de9bbbf2739ac8905d3cf993e73c"

# Draw-filter enforcement flag (sub-step 5) — DARK by default (the .build_executor_enabled precedent).
# ABSENT => the supervisor BUILD draw is byte-for-byte UNCHANGED (detection alone; prevention off).
# Only a future director act creates this, AFTER the fronts are opened (sub-step 6). This is what
# keeps sub-step 5 DORMANT/safe on the live loop: the mechanism is built and tested while inert.
FRONTS_ENFORCEMENT_FLAG = PROJECT_DIR / "docs" / "observability" / ".fronts_enforcement_enabled"

# Only these three statuses PAGE (real-alarms, §2 table). Everything else is informational/quiet.
ALARM_STATUSES = {"DRAW_OFF_FRONT", "GATE_CROSSED", "LEVEL_SELF_PROMOTION"}

VALID_FRONT_STATES = {"open", "held"}


class FrontsError(ValueError):
    """fronts.yaml violates its schema — fail LOUD, never trust a malformed scope declaration."""


# ── declaration: load + validate (sub-step 1 loader) ───────────────────────────────────────
def load_fronts(path: Path | None = None) -> dict:
    """Parse + validate fronts.yaml. Returns {"fronts": [...], "gates": [...]}. Raises FrontsError
    on a schema violation — crucially, a front `state: open` with `opened_by: null` FAILS (an open
    front with no console trace is drift, not authorization)."""
    data = yaml.safe_load((path or FRONTS_PATH).read_text())
    fronts = (data or {}).get("fronts") or []
    gates = (data or {}).get("gates") or []
    _validate_fronts(fronts)
    return {"fronts": fronts, "gates": gates}


def _validate_fronts(fronts: list) -> None:
    if not fronts:
        raise FrontsError("fronts.yaml declares no fronts — refusing empty scope declaration")
    seen: set = set()
    for i, f in enumerate(fronts):
        where = f"fronts[{i}] ({f.get('id') if isinstance(f, dict) else '?'})"
        if not isinstance(f, dict):
            raise FrontsError(f"{where}: front must be a mapping")
        fid = str(f.get("id") or "").strip()
        if not fid:
            raise FrontsError(f"{where}: missing 'id'")
        if fid in seen:
            raise FrontsError(f"{where}: duplicate front id {fid!r}")
        seen.add(fid)
        state = f.get("state")
        if state not in VALID_FRONT_STATES:
            raise FrontsError(f"{where}: state {state!r} not in {sorted(VALID_FRONT_STATES)}")
        if not isinstance(f.get("epoch_ceiling"), int):
            raise FrontsError(f"{where}: 'epoch_ceiling' must be an int")
        if state == "open":
            if not str(f.get("opened_by") or "").strip():
                raise FrontsError(
                    f"{where}: state 'open' requires a non-null 'opened_by' referencing the ledger "
                    "FRONT_OPEN console act — an open front with no console trace is drift, not "
                    "authorization")
        else:  # held: mirror process_manifest's reason+flip discipline (a state without its reason
               # is archaeology; IaC).
            for req in ("reason", "flip"):
                if not str(f.get(req) or "").strip():
                    raise FrontsError(f"{where}: state 'held' requires a non-empty {req!r}")


def _gate_index(gates: list) -> dict:
    """Index the gated atom-sets / path-list out of the gates declaration (pure)."""
    idx = {"schema_atoms": set(), "schema_paths": [], "values_atoms": set()}
    for g in gates or []:
        if not isinstance(g, dict):
            continue
        if g.get("id") == "schema_sim_structure":
            idx["schema_atoms"] = set(g.get("gated_atoms") or [])
            idx["schema_paths"] = list(g.get("gated_paths") or [])
        elif g.get("id") == "values_decisions":
            idx["values_atoms"] = set(g.get("gated_atoms") or [])
    return idx


# ── map reads (live loop_stage + level_current) ────────────────────────────────────────────
def _walk_atoms(map_obj) -> list:
    out: list = []

    def walk(o):
        if isinstance(o, dict):
            if o.get("id") and ("loop_stage" in o or "level_current" in o):
                out.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(map_obj)
    return out


def load_map_atoms(path: Path | None = None) -> list:
    """Every atom dict in the live map. [] on any read/parse failure (fail-safe read)."""
    try:
        return _walk_atoms(yaml.safe_load((path or MAP_PATH).read_text()))
    except Exception:
        return []


def _levels_from_map_obj(map_obj) -> dict:
    return {a["id"]: a.get("level_current") for a in _walk_atoms(map_obj)}


def current_levels(path: Path | None = None) -> dict:
    try:
        return _levels_from_map_obj(yaml.safe_load((path or MAP_PATH).read_text()))
    except Exception:
        return {}


def level_baseline(ref: str | None = None) -> dict | None:
    """{atom: level_current} at the committed LEVEL_BASELINE_REF, read from the git object (not the
    working tree — so a working-tree edit cannot move the baseline). None if git/ref is unreadable:
    an UNAVAILABLE baseline is surfaced by evaluate() as a degraded state, NOT silently treated as
    'no promotions' (R15: an unavailable check is a failed check, not a pass)."""
    ref = ref or LEVEL_BASELINE_REF
    try:
        r = subprocess.run(["git", "show", f"{ref}:docs/design/maturity_map.yaml"],
                           cwd=str(PROJECT_DIR), capture_output=True, text=True)
        if getattr(r, "returncode", 1) != 0:
            return None
        return _levels_from_map_obj(yaml.safe_load(r.stdout))
    except Exception:
        return None


# ── membership + gate predicates (pure, mutation-testable core) ─────────────────────────────
def atom_in_region(atom: dict, front: dict) -> bool:
    """Is `atom` a member of `front`'s declared region? A total, pure function of the map's own
    coordinates (lane / id / file_scope) — no runtime discretion widens it (F-1 bounded)."""
    if not isinstance(atom, dict) or not isinstance(front, dict):
        return False
    if atom.get("lane") in (front.get("lanes") or []):
        return True
    if atom.get("id") in (front.get("include_atoms") or []):
        return True
    for p in front.get("include_paths") or []:
        for fs in atom.get("file_scope") or []:
            if str(fs) == p or str(fs).startswith(p):
                return True
    return False


def _front_for(atom: dict, fronts: list) -> dict | None:
    """The (single) front whose region contains this atom, or None. Fronts are disjoint by
    construction (SIM_ACTORS lanes W1/W2; SUPPLIER lanes D/B/E/C/F + site/) so first-match is total."""
    for f in fronts:
        if atom_in_region(atom, f):
            return f
    return None


def crosses_static_gate(atom: dict, epoch_ceiling, gate_index: dict, action_desc: str = "") -> str | None:
    """The NON-delta gate classes (do not need a baseline): returns the gate id, or None.
      one_way_doors    — action matches a one_way_door.classify_action category (reused verbatim).
      epoch_boundary   — atom.epoch > the applicable front epoch_ceiling.
      values_decisions — atom.id in the reserved-values gated set.
      schema_sim_structure — atom.id in the gated-atom set, OR atom.file_scope touches a gated path.
    Order: door > epoch > values > schema (most-reserved first). The LEVEL gate and the stage-advance
    (BUILD-open) gate are DELTA gates, decided in classify_atom from the baselines."""
    aid = atom.get("id")
    if action_desc:
        v = _owd.classify_action(action_desc)
        if v.is_one_way_door:
            return "one_way_doors"
    ep = atom.get("epoch")
    if isinstance(ep, int) and isinstance(epoch_ceiling, int) and ep > epoch_ceiling:
        return "epoch_boundary"
    if aid in gate_index.get("values_atoms", set()):
        return "values_decisions"
    if aid in gate_index.get("schema_atoms", set()):
        return "schema_sim_structure"
    for fs in atom.get("file_scope") or []:
        for gp in gate_index.get("schema_paths", []):
            if str(fs) == gp or str(fs).startswith(gp):
                return "schema_sim_structure"
    return None


def _level_cleared(atom_id: str, to_level, ledger: list) -> bool:
    """Is a level move to `to_level` authorized by a valid director-console LEVEL_UP_PROPOSED for
    this atom? An entry with a `level` bounds the clearance to that target; without one, it clears
    any increase for the atom. A forged (non-console / no-provenance) entry does NOT clear (M4-class)."""
    for e in ledger:
        if not _gw.is_valid_level_up(e) or e.get("atom") != atom_id:
            continue
        lvl = e.get("level")
        if lvl is None or (isinstance(to_level, int) and isinstance(lvl, int) and to_level <= lvl):
            return True
    return False


def _gate_cleared(atom_id: str, gate: str, ledger: list) -> bool:
    """Is a gate crossing for this atom authorized by a director-console act? A valid GATE_CLEAR
    (naming this gate, or gate-less) OR a per-atom BUILD_OPEN clears it (§4.2 step 1/3). Forged
    entries do not clear (they fail the four console checks)."""
    if atom_id in _gw.authorized_atoms(ledger):  # per-atom BUILD_OPEN (backward compatible)
        return True
    for e in ledger:
        if _gw.is_valid_gate_clear(e) and e.get("atom") == atom_id:
            g = e.get("gate")
            if g is None or g == gate:
                return True
    return False


def open_front_ids(fronts: list, ledger: list) -> set:
    """Fronts that are OPEN: declared state==open in fronts.yaml AND covered by a valid director-
    console FRONT_OPEN in the ledger that is NOT superseded by a later valid FRONT_CLOSE (R11). The
    yaml AND the ledger must agree — the declaration alone cannot open a front (independence)."""
    last: dict = {}  # front id -> (ts, action) of the latest valid open/close console act
    for e in ledger:
        if _gw.is_valid_front_open(e) or _gw.is_valid_front_close(e):
            fid = e.get("front")
            ts = e.get("ts") or 0
            if fid and (fid not in last or ts >= last[fid][0]):
                last[fid] = (ts, e.get("action"))
    ledger_open = {fid for fid, (ts, act) in last.items() if act == "FRONT_OPEN"}
    return {f.get("id") for f in fronts
            if f.get("state") == "open" and f.get("id") in ledger_open}


# ── the classifier (§2 status table, generalising unauthorized_promotions) ──────────────────
def classify_atom(atom: dict, *, from_stage, to_stage, from_level, to_level, fronts: list,
                  open_ids: set, gate_index: dict, ledger: list, action_desc: str = "") -> dict:
    """Classify ONE atom's promotion (vs its stage+level baselines) into the §2 status table.
    ALARM statuses (page): DRAW_OFF_FRONT, GATE_CROSSED, LEVEL_SELF_PROMOTION.
    Quiet statuses: ON_FRONT (authorized), FRONT_HELD (frozen, not promoted), GATE_HELD (at a gate,
    not promoted), QUIET (no change). Gate check is FIRST (G-1: a front never dissolves a gate)."""
    aid = atom.get("id")
    front = _front_for(atom, fronts)
    fid = front.get("id") if front else None
    ceiling = front.get("epoch_ceiling") if front else None
    front_open = bool(fid and fid in open_ids)

    stage_advanced = (from_stage == "idle" and to_stage not in (None, "idle"))
    level_bumped = (isinstance(from_level, int) and isinstance(to_level, int) and to_level > from_level)

    def R(status, detail):
        return {"atom": aid, "status": status, "alarm": status in ALARM_STATUSES,
                "front": fid, "detail": detail}

    # ── LEVEL gate (§10.1) — distinct class, checked first; the agent never moves a cell itself ──
    if level_bumped and not _level_cleared(aid, to_level, ledger):
        return R("LEVEL_SELF_PROMOTION",
                 f"level_current {from_level}->{to_level} with no director+advisor LEVEL_UP_PROPOSED "
                 f"(agent proposes, never moves the cell — MATURITY_MAP.md §0)")

    # ── static gates (one-way / epoch / values / schema) — a gate beats a front (G-1) ──
    static_gate = crosses_static_gate(atom, ceiling, gate_index, action_desc)
    if static_gate is not None:
        if stage_advanced or level_bumped:
            if _gate_cleared(aid, static_gate, ledger):
                return R("ON_FRONT", f"gate {static_gate!r} crossed with a clearing console act")
            return R("GATE_CROSSED", f"crosses gate {static_gate!r} with no clearing console act")
        return R("GATE_HELD", f"at gate {static_gate!r}, correctly held (not promoted)")

    # ── stage advance (idle->build == the reserved BUILD-open / stage gate, §10.2) ──
    if stage_advanced:
        if front_open:
            return R("ON_FRONT", f"in OPEN front {fid}, non-gated BUILD")
        if aid in _gw.authorized_atoms(ledger):
            return R("ON_FRONT", "per-atom BUILD_OPEN (backward compatible)")
        if fid is not None:  # member of a HELD front but it ADVANCED — crossed the BUILD-open gate (M7)
            return R("GATE_CROSSED",
                     f"stage idle->{to_stage} in HELD front {fid} with no console act (self-advance)")
        return R("DRAW_OFF_FRONT",
                 f"stage idle->{to_stage} in NO open front, no BUILD_OPEN (drew off-front)")

    # ── a level bump that WAS authorized, no stage advance -> quiet ──
    if level_bumped:
        return R("ON_FRONT", f"level {from_level}->{to_level} authorized by LEVEL_UP_PROPOSED")

    # ── not promoted ──
    if fid is not None and not front_open:
        return R("FRONT_HELD", f"member of HELD front {fid}, correctly BUILD-frozen (DISCOVER/FRAME ok)")
    return R("QUIET", "no promotion since baseline")


# ── reconcile: the DECLARATION vs ACTUAL map state (report-only) ────────────────────────────
def reconcile(*, atoms: list | None = None, fronts_decl: dict | None = None, ledger: list | None = None,
              stage_baseline: dict | None = None, level_baseline_map: dict | None = None,
              action_descs: dict | None = None) -> list:
    """Per-atom classification of the live map vs the declaration + ledger + baselines. REPORT ONLY.
    Every argument is injectable for tests; production reads live. `level_baseline_map` None => the
    level gate is skipped for this call (evaluate() surfaces the unavailable-baseline condition)."""
    atoms = atoms if atoms is not None else load_map_atoms()
    decl = fronts_decl if fronts_decl is not None else load_fronts()
    fronts = decl["fronts"]
    gate_index = _gate_index(decl["gates"])
    ledger = ledger if ledger is not None else _gw.read_ledger()
    stage_baseline = stage_baseline if stage_baseline is not None else _gw.load_baseline()
    level_baseline_map = level_baseline_map or {}
    action_descs = action_descs or {}

    open_ids = open_front_ids(fronts, ledger)
    results = []
    for atom in atoms:
        aid = atom.get("id")
        results.append(classify_atom(
            atom,
            from_stage=stage_baseline.get(aid),
            to_stage=atom.get("loop_stage"),
            from_level=level_baseline_map.get(aid),
            to_level=atom.get("level_current"),
            fronts=fronts, open_ids=open_ids, gate_index=gate_index, ledger=ledger,
            action_desc=action_descs.get(aid, ""),
        ))
    return results


def drift_alarms(results: list) -> list:
    return [r for r in results if r["alarm"]]


def drift_signature(results: list) -> list:
    """Stable order-independent signature of the CURRENT alarm set — the thing whose CHANGE is the
    transition worth paging (R5). Clean == []."""
    return sorted(f"{r['status']}:{r['atom']}" for r in drift_alarms(results))


def evaluate() -> dict:
    """Live REPORT-ONLY evaluation against the current map + fronts.yaml + ledger + baselines.
    Never raises. `level_baseline_available` False => the LEVEL gate could not run (degraded, not a
    false clean)."""
    lvl = level_baseline()
    results = reconcile(level_baseline_map=lvl if lvl is not None else {})
    alarms = drift_alarms(results)
    return {
        "status": "SCOPE_VIOLATION" if alarms else "SCOPE_CLEAN",
        "alarm": bool(alarms),
        "alarms": alarms,
        "signature": drift_signature(results),
        "level_baseline_available": lvl is not None,
        "results": results,
    }


# ── report entrypoint (sub-step 4): transition-only typed real-alarms (R5) ───────────────────
def format_report(ev: dict) -> str:
    if not ev["alarms"]:
        base = f"[SCOPE] clean — every promotion traces to the declared open fronts / console ledger."
        if not ev.get("level_baseline_available", True):
            base += " NOTE: level baseline UNAVAILABLE (git) — LEVEL gate degraded this run."
        return base
    lines = [f"[SCOPE] self-governance DRIFT — {len(ev['alarms'])} promotion(s) off the declared scope:"]
    for r in sorted(ev["alarms"], key=lambda r: (r["status"], r["atom"])):
        lines.append(f"    ✗ {r['atom']}: {r['status']} — {r['detail']}")
    return "\n".join(lines)


def page_decision(sig_prev: list, sig_now: list) -> tuple:
    """PURE transition decision (R5): given the previous and current alarm signatures, returns
    (should_page, tag, is_clear). Unchanged -> no page (suppress). Appeared/changed -> rotating_light.
    Cleared back to clean (was drifting, now empty) -> white_check_mark."""
    if sig_now == sig_prev:
        return (False, None, False)
    if sig_now:
        return (True, "rotating_light", False)
    return (True, "white_check_mark", True)   # cleared


def run(notify_fn=None) -> dict:
    """Run one live evaluation and PAGE only on an alarm-set transition (R5), typed real_alarm,
    hourly re-escalate while unchanged-but-still-drifting — behind the shared notify contract
    (background.notify.notify, which owns the transition-dedup + re_escalate_after). REPORT ONLY
    (no map writes). `notify_fn` injectable for tests so a test never actually sends an NTFY.
    Returns {paged, status, signature, ...}."""
    from background import notify as _n
    ev = evaluate()
    sig = ev["signature"]
    key = "scope_governance"
    state = ";".join(sig) if sig else "clean"
    try:
        prev = _n._read_transitions().get(key)
        prev_state = prev.get("state") if isinstance(prev, dict) else None
    except Exception:
        prev_state = None
    # No page on a clean state that was already clean / never drifted (R5: no false clean heartbeat).
    # A CLEARED page fires only when we were actually drifting (prev_state is a real signature).
    if not sig and prev_state in (None, "clean"):
        return {"paged": False, "status": ev["status"], "signature": sig, "detail": "clean; no transition"}
    fn = notify_fn or _n.notify
    result = fn(message=format_report(ev), kind="real_alarm", transition_key=key, state=state,
                re_escalate_after=3600.0,
                headers={"Tags": "rotating_light" if sig else "white_check_mark",
                         "X-Priority": "high" if sig else "default"})
    paged = not (isinstance(result, str) and result.startswith("suppressed"))
    return {"paged": paged, "status": ev["status"], "signature": sig, "notify_result": result}


# ── draw-filter helper (sub-step 5): prevention, read-side — DARK by default ─────────────────
def fronts_enforcement_enabled(path: Path | None = None) -> bool:
    """True iff the enforcement flag file is present (fail-closed on error). ABSENT (the default,
    and the state through sub-steps 1–5) => the supervisor BUILD draw is UNCHANGED. This is what
    keeps the draw filter dormant/safe on the live loop until the director opens the fronts."""
    try:
        return (path or FRONTS_ENFORCEMENT_FLAG).is_file()
    except Exception:
        return False


def is_build_authorized(atom: dict, *, fronts_decl: dict | None = None, ledger: list | None = None,
                        action_desc: str = "") -> bool:
    """PURE §4.2 composition: may the loop BUILD (stage-advance) this atom now? gate check FIRST,
    then open-front membership, then a per-atom BUILD_OPEN (backward compatible). Does NOT consider
    the LEVEL gate (building code doesn't move a cell; the level move is a separate proposal)."""
    decl = fronts_decl if fronts_decl is not None else load_fronts()
    fronts = decl["fronts"]
    gate_index = _gate_index(decl["gates"])
    ledger = ledger if ledger is not None else _gw.read_ledger()
    open_ids = open_front_ids(fronts, ledger)
    aid = atom.get("id")
    front = _front_for(atom, fronts)
    ceiling = front.get("epoch_ceiling") if front else None
    gate = crosses_static_gate(atom, ceiling, gate_index, action_desc)
    if gate is not None:
        return _gate_cleared(aid, gate, ledger)
    if front and front.get("id") in open_ids:
        return True
    return aid in _gw.authorized_atoms(ledger)


def filter_build_candidates(candidates: list, *, fronts_decl: dict | None = None,
                            ledger: list | None = None) -> list:
    """Intersect a BUILD candidate list with authorized_build (§4.2). The supervisor calls this ONLY
    when fronts_enforcement_enabled(); DISCOVER/FRAME/SITE lanes are separate functions, untouched."""
    decl = fronts_decl if fronts_decl is not None else load_fronts()
    ledger = ledger if ledger is not None else _gw.read_ledger()
    return [a for a in candidates if is_build_authorized(a, fronts_decl=decl, ledger=ledger)]


if __name__ == "__main__":
    import json
    import sys
    ev = evaluate()
    print(format_report(ev))
    print(json.dumps({"status": ev["status"], "signature": ev["signature"],
                      "level_baseline_available": ev["level_baseline_available"]}, indent=2))
    sys.exit(1 if ev["alarm"] else 0)
