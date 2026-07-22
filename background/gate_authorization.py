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

# PHONE-NATIVE AUTHORITY WIRING (director console ratification 2026-07-22,
# PHONE_NATIVE_AUTHORITY_CHANNEL_PROPOSAL_2026-07-22.md). This import is THE authorization-trust
# change the proposal held for a single console act: gate_authorization.py now ALSO accepts a
# director_ntfy (HMAC-signed) or advisor_ruling entry for ROUTINE actions, in addition to the
# console channel. The two systems compose ADDITIVELY -- console validity is unchanged; the phone
# channels only ADD acceptance for the default-deny ROUTINE_ACTIONS allowlist. Reserved actions
# (safety/authz-trust/Tier-1/one-way-door) stay console-only, enforced by dac's allowlist.
from background import director_authority_channels as dac

PROJECT_DIR = Path(__file__).resolve().parent.parent

# The advisor-bridge git identity (CLAUDE.md: "21bcarlisle-arch is a legitimate identity -- Rich's
# advisor using his GitHub token via the staging bridge"). The advisor_ruling channel requires the
# carrying commit to be authored by this identity. NOTE (honest limitation, flagged to the director):
# advisor commits are NOT GPG-signed and share the director's email, so this keys on the author NAME
# only -- a defence-in-depth layer on top of R7 (committed git state) + the [DIRECTOR-RULING] marker,
# NOT a cryptographic guarantee. The autonomous worker could set an author name, so the advisor_ruling
# channel is weaker than director_ntfy (whose HMAC key is out-of-tree and worker-unreadable). The
# strong channel is director_ntfy; advisor_ruling is the advisor's convenience path.
ADVISOR_BRIDGE_AUTHOR_NAME = "21bcarlisle-arch"
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
    """A ledger entry counts as BUILD_OPEN authorization if it is a director-console BUILD_OPEN with
    provenance, OR (since the 2026-07-22 phone ratification) a phone-native director_ntfy/advisor_ruling
    BUILD_OPEN (BUILD_OPEN is on the ROUTINE_ACTIONS allowlist). A twin/machine self-write tagged
    anything other than these, or missing provenance, does NOT authorize -- 'not marking your own
    homework'; and the worker cannot mint a director_ntfy entry (HMAC key is out-of-tree)."""
    return _valid_director_act(entry, "BUILD_OPEN")


def authorized_atoms(ledger: list) -> set:
    """Set of atoms with at least one VALID director-console BUILD_OPEN authorization."""
    return {e["atom"] for e in ledger if _is_valid_authorization(e) and e.get("atom")}


def _is_valid_hold(entry) -> bool:
    """A HELD_PENDING_VERIFICATION record: the director has SEEN this specific promotion and
    deliberately parked it RED pending live verification (NOT authorized -- it stays uncleared).
    Same director-console provenance requirement as an authorization. A hold does NOT wave the
    atom through; it distinguishes a director-acknowledged known-red from an unacknowledged
    violation, so the deadman does not hourly-re-page a state the director already parked (R5).
    Accepts a console hold OR (since 2026-07-22) a phone-native HELD (on the ROUTINE allowlist)."""
    return _valid_director_act(entry, "HELD_PENDING_VERIFICATION")


def held_atoms(ledger: list) -> set:
    """Atoms the director has explicitly HELD red pending verification (acknowledged, NOT cleared)."""
    return {e["atom"] for e in ledger if _is_valid_hold(e) and e.get("atom")}


# ── SCOPE-MODEL record types (SELF_GOVERNANCE_SCOPE_MODEL.md §3, sub-step 3) ────────────────
# The scope model generalises the single-atom gate-wall to a declared REGION. It ADDS record types
# to THIS ledger (it does NOT build a parallel one). Every new record type validates through the
# SAME four checks as an authorization — action + authorized_by==director + channel==console +
# non-empty provenance — so the autonomous worker (the doorbell channel) can never legitimately
# mint one, exactly as it can never mint a BUILD_OPEN. (Detection is honest+loud now; forge-proofing
# the console trace cryptographically is the deferred prevention layer, sub-step 7.)
SCOPE_ACTIONS = ("FRONT_OPEN", "GATE_CLEAR", "FRONT_CLOSE", "LEVEL_UP_PROPOSED")


def _valid_console_act(entry, action: str) -> bool:
    """The four-check console-validity predicate for an arbitrary record `action`. Same trust model
    as _is_valid_authorization (which is the BUILD_OPEN-specialised form) — a non-console / no-
    provenance / non-director entry is NOT a director act, whatever it self-declares as its action.
    PURE console predicate — the phone channels are added by `_valid_director_act`, never here."""
    return (
        isinstance(entry, dict)
        and entry.get("action") == action
        and entry.get("authorized_by") == "director"
        and entry.get("channel") == "console"
        and bool(str(entry.get("provenance") or "").strip())
    )


def _advisor_commit_is_bridge_authored(commit, *, runner=None) -> bool:
    """Git-authorship check for the advisor_ruling channel: is `commit` authored by the advisor
    bridge identity? FAIL-CLOSED — a missing commit, a git error, an unknown commit, or a
    non-bridge author all return False (an unverifiable authorship is a FAILED check, R15). `runner`
    is injectable for tests. See ADVISOR_BRIDGE_AUTHOR_NAME for this check's honest limitation."""
    c = str(commit or "").strip()
    if not c:
        return False
    run = runner or (lambda args: subprocess.run(
        ["git", *args], cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=15))
    try:
        r = run(["log", "-1", "--format=%an", c])
        if getattr(r, "returncode", 1) != 0:
            return False
        return (r.stdout or "").strip() == ADVISOR_BRIDGE_AUTHOR_NAME
    except Exception:
        return False


def _valid_phone_authority(entry, action: str, *, runner=None) -> bool:
    """Does this entry carry valid ROUTINE director authority for EXACTLY `action` via a phone-native
    channel? Two channels, action-matched so a signature for one routine action can never satisfy a
    predicate for another (the REPURPOSE guard, preserved at the gate boundary too):
      - director_ntfy: dac.is_valid_director_ntfy (HMAC-signed, key out-of-tree, bound to action:atom).
      - advisor_ruling: dac.is_valid_advisor_ruling (marker + structural provenance) AND the carrying
        commit is bridge-authored (`_advisor_commit_is_bridge_authored`) — the git check the proposal
        adds at the wiring layer (impure, so it lives here, not in the pure dac validator).
    FAIL-CLOSED throughout; `entry.action == action` required on both branches."""
    if not (isinstance(entry, dict) and entry.get("action") == action):
        return False
    if dac.is_valid_director_ntfy(entry):
        return True
    if dac.is_valid_advisor_ruling(entry):
        return _advisor_commit_is_bridge_authored(entry.get("commit"), runner=runner)
    return False


def _valid_director_act(entry, action: str, *, runner=None) -> bool:
    """Console OR phone-native routine authority for `action` — the umbrella every routine `is_valid_*`
    predicate routes through since the 2026-07-22 ratification. Console validity is unchanged; the
    phone channels only ADD acceptance, and only for the default-deny ROUTINE_ACTIONS allowlist that
    dac enforces (a reserved/safety/authz-trust action fails on the phone branch even with a perfect
    signature). Additive by construction — a console entry still passes via `_valid_console_act`."""
    return _valid_console_act(entry, action) or _valid_phone_authority(entry, action, runner=runner)


def is_valid_front_open(entry) -> bool:
    """A FRONT_OPEN opens a declared front: authorizes continuous BUILD of every in-region, non-
    gated atom (present and future) until a FRONT_CLOSE. Requires a non-empty `front` id + the four
    console checks. The scaling win: ONE act authorizes a REGION."""
    return _valid_director_act(entry, "FRONT_OPEN") and bool(str(entry.get("front") or "").strip())


def is_valid_front_close(entry) -> bool:
    """A FRONT_CLOSE re-freezes a front's region to DISCOVER/FRAME (R11: every open has a tested
    close whose effect is real). Requires a non-empty `front` id + the four console checks."""
    return _valid_director_act(entry, "FRONT_CLOSE") and bool(str(entry.get("front") or "").strip())


def is_valid_gate_clear(entry) -> bool:
    """A GATE_CLEAR waves ONE specific atom through ONE specific gate (narrower than opening a
    front). Requires a non-empty `atom` + the four console checks. `gate` is optional (absent =>
    clears any gate for that atom, like a per-atom BUILD_OPEN)."""
    return _valid_director_act(entry, "GATE_CLEAR") and bool(str(entry.get("atom") or "").strip())


# The DIRECTOR_TWIN standing approver may ratify ROUTINE levels only (director console
# 2026-07-21: "run its live L1/L2 proof ... so routine levels stop queuing on me -- L3 stays
# mine"). This is the STRUCTURAL boundary: a twin authority NEVER clears L3+, even if a twin
# entry forges level>=3 (is_valid_twin_level_up caps it). L3+ is the director's "this is real"
# ruling and needs a genuine director-console LEVEL_UP_PROPOSED.
TWIN_LEVEL_CAP = 2


def is_valid_twin_level_up(entry) -> bool:
    """A DIRECTOR_TWIN routine level ratification. Valid ONLY for an explicit integer level in
    [1, TWIN_LEVEL_CAP] — a twin entry at L3+ is INVALID (the R15 refusal point in the validator:
    the twin cannot ratify a director-reserved level even by forging the entry). Honestly stamped
    authorized_by==director_twin, channel==twin (it does NOT masquerade as a director-console act),
    with non-empty provenance carrying the twin's canon-based verdict."""
    if not (isinstance(entry, dict)
            and entry.get("action") == "LEVEL_UP_TWIN"
            and entry.get("authorized_by") == "director_twin"
            and entry.get("channel") == "twin"
            and bool(str(entry.get("atom") or "").strip())
            and bool(str(entry.get("provenance") or "").strip())):
        return False
    lvl = entry.get("level")
    return isinstance(lvl, int) and 1 <= lvl <= TWIN_LEVEL_CAP


def is_valid_level_up(entry) -> bool:
    """Does this ledger entry authorize an atom's level_current move? Two valid authorities:
      1. A DIRECTOR-CONSOLE LEVEL_UP_PROPOSED (any level, incl. L3+) — the director+advisor act.
      2. A DIRECTOR_TWIN LEVEL_UP_TWIN (routine L1/L2 ONLY, per is_valid_twin_level_up) — the
         standing approver so routine levels stop queuing on the director; L3+ stays director-reserved.

    Requires a non-empty `atom`. For the console act an optional integer `level` bounds the
    authorization to a specific target (absent => any increase). A worker-forged entry self-declaring
    channel==console is the known residual (sub-step 7 prevention); a twin entry is honestly stamped
    and structurally capped at L2 so it can never over-reach into the director's L3+ reservation."""
    if is_valid_twin_level_up(entry):
        return True
    if not (_valid_director_act(entry, "LEVEL_UP_PROPOSED") and bool(str(entry.get("atom") or "").strip())):
        return False
    lvl = entry.get("level")
    return lvl is None or isinstance(lvl, int)


def record_front_open(front: str, provenance: str, *, ts: float | None = None,
                      path: Path | None = None) -> None:
    """Append a director-console FRONT_OPEN. CONSOLE-PATH ONLY (same contract as
    record_gate_opening): call it acting on the director's authenticated console act. The autonomous
    worker must never call this — that is the prevention layer; detection makes a forged/absent
    authorization LOUD regardless."""
    _append_record({"front": front, "action": "FRONT_OPEN"}, provenance, ts=ts, path=path)


def record_front_close(front: str, provenance: str, *, ts: float | None = None,
                       path: Path | None = None) -> None:
    """Append a director-console FRONT_CLOSE (re-freezes the region). Console-path only."""
    _append_record({"front": front, "action": "FRONT_CLOSE"}, provenance, ts=ts, path=path)


def record_gate_clear(atom: str, gate: str | None, provenance: str, *, ts: float | None = None,
                      path: Path | None = None) -> None:
    """Append a director-console GATE_CLEAR for one atom (optionally one named gate). Console-path only."""
    rec = {"atom": atom, "action": "GATE_CLEAR"}
    if gate is not None:
        rec["gate"] = gate
    _append_record(rec, provenance, ts=ts, path=path)


def record_level_up(atom: str, level: int | None, provenance: str, *, ts: float | None = None,
                    path: Path | None = None) -> None:
    """Append a director-console LEVEL_UP_PROPOSED authorizing an atom's level move (optionally to a
    specific `level`). Console-path only — the worker proposes with evidence, the director+advisor
    move the cell, and only THAT act writes this."""
    rec = {"atom": atom, "action": "LEVEL_UP_PROPOSED"}
    if level is not None:
        rec["level"] = level
    _append_record(rec, provenance, ts=ts, path=path)


def record_twin_level_up(atom: str, level: int, provenance: str, *, ts: float | None = None,
                         path: Path | None = None) -> None:
    """Append a DIRECTOR_TWIN routine level ratification (L1/L2 ONLY). Honestly stamped
    authorized_by==director_twin, channel==twin — it does NOT masquerade as a director-console act.
    Raises on a non-integer or director-reserved (>=3) level: the twin ratifies routine levels only,
    and the write path itself refuses to record a level the twin has no authority over (belt to the
    is_valid_twin_level_up braces). Called by the orchestrator ONLY on a twin APPROVE verdict
    (director_twin.ratify_routine_level); the twin process itself stays a voice, not a hand."""
    if not isinstance(level, int):
        raise ValueError("twin level ratification requires an explicit integer level")
    if not (1 <= level <= TWIN_LEVEL_CAP):
        raise ValueError(
            f"the DIRECTOR_TWIN may ratify routine L1-L{TWIN_LEVEL_CAP} only; L{level} is "
            "director-reserved (canon) and needs a genuine director-console LEVEL_UP_PROPOSED")
    _append_twin_record({"atom": atom, "action": "LEVEL_UP_TWIN", "level": level},
                        provenance, ts=ts, path=path)


def _append_record(fields: dict, provenance: str, *, ts: float | None = None,
                   path: Path | None = None) -> None:
    """Append ONE console record (arbitrary extra `fields` + the fixed director-console envelope).
    Same writer discipline as _append_ledger; never raises."""
    _append_envelope(fields, provenance, "director", "console", ts=ts, path=path)


def _append_twin_record(fields: dict, provenance: str, *, ts: float | None = None,
                        path: Path | None = None) -> None:
    """Append ONE twin record with the HONEST director_twin/twin envelope (never the console one)."""
    _append_envelope(fields, provenance, "director_twin", "twin", ts=ts, path=path)


def record_director_ntfy_ruling(signed_payload: str, *, provenance: str | None = None,
                                max_age_seconds: int | None = None, ts: float | None = None,
                                path: Path | None = None) -> dict | None:
    """THE ONLY path that mints a director_ntfy authority ledger entry. Called by ntfy_responder on
    an inbound message. FAIL-CLOSED: verifies `signed_payload` HMAC-signs a fresh, bound
    `RULING:<action>:<atom>` for a ROUTINE action, and writes NOTHING otherwise (unverifiable,
    stale, reserved-action, or malformed → returns None, no ledger write). The autonomous worker
    cannot mint one because it cannot read SE_WAKE_HMAC_KEY to produce a valid signature (the
    out-of-tree-key TAUTOLOGY guard). Returns the written entry, or None.

    Belt-and-braces: the assembled entry is re-validated through dac.is_valid_director_ntfy before
    the write, so the ledgered record is exactly one the read-side predicates will accept — no path
    writes an entry that would later be judged invalid."""
    max_age = dac.NTFY_MAX_AGE_SECONDS if max_age_seconds is None else max_age_seconds
    if not isinstance(signed_payload, str) or not signed_payload.strip():
        return None
    try:
        from background.ntfy_utils import verify_wake_message
    except Exception:
        return None  # ntfy_utils unavailable (no send topic) -> mint nothing (fail-closed)
    verified = verify_wake_message(signed_payload, max_age_seconds=max_age)
    if verified is None or not verified.startswith("RULING:"):
        return None  # no key / bad signature / stale / not a ruling → mint nothing
    parts = verified.split(":", 2)   # ["RULING", action, atom]
    if len(parts) != 3:
        return None
    _, action, atom = parts[0], parts[1].strip(), parts[2].strip()
    stamp = ts if ts is not None else time.time()
    entry = {
        "atom": atom, "action": action, "ts": stamp,
        "authorized_by": "director", "channel": dac.DIRECTOR_NTFY,
        "provenance": provenance or f"director_ntfy HMAC-verified ruling '{verified}'",
        "signed_payload": signed_payload,
    }
    # Only write what the read-side predicate will accept (routine action, bound, fresh).
    if not dac.is_valid_director_ntfy(entry, max_age_seconds=max_age):
        return None
    p = path or LEDGER_PATH
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        return None
    return entry


def _append_envelope(fields: dict, provenance: str, authorized_by: str, channel: str, *,
                     ts: float | None = None, path: Path | None = None) -> None:
    """Append ONE record with the given authority envelope. Never raises."""
    p = path or LEDGER_PATH
    stamp = ts if ts is not None else time.time()
    rec = dict(fields)
    rec.update({"ts": stamp, "authorized_by": authorized_by, "channel": channel,
                "provenance": provenance})
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


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
    _append_ledger(atoms, "BUILD_OPEN", provenance, ts=ts, path=path)


def record_hold(atoms, provenance: str, *, ts: float | None = None,
                path: Path | None = None) -> None:
    """Append a director-console HELD_PENDING_VERIFICATION record: the director has SEEN this
    promotion and deliberately parks it RED pending live verification (NOT an authorization).
    Console-path only, same as record_gate_opening. The atom stays uncleared in the wall; the
    hold only suppresses hourly re-paging of a state the director already acknowledged."""
    _append_ledger(atoms, "HELD_PENDING_VERIFICATION", provenance, ts=ts, path=path)


def _append_ledger(atoms, action: str, provenance: str, *, ts: float | None = None,
                   path: Path | None = None) -> None:
    if isinstance(atoms, str):
        atoms = [atoms]
    p = path or LEDGER_PATH
    stamp = ts if ts is not None else time.time()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            for atom in atoms:
                f.write(json.dumps({
                    "atom": atom, "action": action, "ts": stamp,
                    "authorized_by": "director", "channel": "console",
                    "provenance": provenance,
                }) + "\n")
    except Exception:
        pass


# ── live evaluation (report-only) ─────────────────────────────────────────────────────────
def evaluate_gate_wall(*, map_path: Path | None = None, baseline_path: Path | None = None,
                       ledger_path: Path | None = None) -> dict:
    """REPORT ONLY. Classify the gate wall from the live map vs baseline vs ledger.
      GATE_CLEAN     every promotion since genesis is director-console-authorized   (no alarm)
      GATE_HELD      the only un-authorized promotions are director-ACKNOWLEDGED holds (no alarm,
                     but NOT cleared -- still red, pending live verification)
      GATE_VIOLATION >=1 promotion with NEITHER authorization NOR an acknowledged hold  (ALARM)
    Never raises."""
    current = current_loop_stages(map_path)
    baseline = load_baseline(baseline_path)
    ledger = read_ledger(ledger_path)
    proms = promotions_since_baseline(current, baseline)
    authz = authorized_atoms(ledger)
    held = held_atoms(ledger)
    unauth = [p for p in proms if p["atom"] not in authz and p["atom"] not in held]
    held_proms = [p for p in proms if p["atom"] not in authz and p["atom"] in held]
    if unauth:
        names = ", ".join(u["atom"] for u in unauth[:6])
        return {"status": "GATE_VIOLATION", "alarm": True,
                "detail": f"{len(unauth)} BUILD promotion(s) with NO director-console authorization "
                          f"and NO acknowledged hold: {names}",
                "unauthorized": unauth, "held": held_proms}
    if held_proms:
        names = ", ".join(h["atom"] for h in held_proms[:6])
        return {"status": "GATE_HELD", "alarm": False,
                "detail": f"{len(held_proms)} promotion(s) HELD red pending director verification "
                          f"(acknowledged, not cleared): {names}",
                "unauthorized": [], "held": held_proms}
    return {"status": "GATE_CLEAN", "alarm": False,
            "detail": f"all {len(proms)} promotion(s) since genesis are director-authorized",
            "unauthorized": [], "held": []}


if __name__ == "__main__":
    import sys
    r = evaluate_gate_wall()
    print(json.dumps(r, indent=2))
    sys.exit(1 if r["alarm"] else 0)
