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
import re
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



# ── PERMISSION SURFACE: DELETED 2026-08-03 ────────────────────────────────────────────────
# Removed here (director console, finishing DIRECTOR_RULING_RIP_OUT_PERMISSION_MACHINERY items
# 1-3 and NTFY_IS_THE_DIRECTOR): `_is_valid_authorization` / `authorized_atoms` (per-atom
# BUILD_OPEN), `_is_valid_hold` / `held_atoms`, the SCOPE_ACTIONS record family
# (FRONT_OPEN / FRONT_CLOSE / GATE_CLEAR) with `is_valid_front_open` / `is_valid_front_close` /
# `is_valid_gate_clear`, and the authority-channel predicates underneath them --
# `_valid_console_act`, `_advisor_commit_is_bridge_authored`, `_valid_phone_authority`,
# `_valid_director_act`.
#
# Every one of them answered the same question: HAS THE DIRECTOR PERMITTED THIS? That question no
# longer exists inside the simulation. Their last consumers went with `background/fronts.yaml` and
# `background/fronts_reconciler.py`; deleting the callers while leaving these would have left the
# convention one import away from regrowing.
#
# WHAT SURVIVES IN THIS MODULE, and why: the LEDGER ITSELF and the level RECORD. R16's real
# requirement was that a level move be ledger-backed -- an auditable trace of what moved and on
# what evidence -- never that a human authorise it. That is the "record" in propose / record / act,
# so `record_level_up_self_certified` + `is_valid_level_up` stay, and `tools/level_promotion_gate.py`
# still refuses an UNRECORDED level move at commit time. It refuses unrecorded, never unpermitted.


def is_valid_self_certified_level_up(entry) -> bool:
    """A SELF-CERTIFIED level ratification: the agent records its own level move with evidence, no
    director/twin act required. Requires a non-empty `atom` and non-empty `provenance` (the evidence),
    honestly stamped `authorized_by=='agent_self_certified'`, `channel=='self'`. An optional integer
    `level` bounds the certification to a specific target exactly like the console form."""
    return (
        isinstance(entry, dict)
        and entry.get("action") == "LEVEL_UP_SELF_CERTIFIED"
        and entry.get("authorized_by") == "agent_self_certified"
        and entry.get("channel") == "self"
        and bool(str(entry.get("atom") or "").strip())
        and bool(str(entry.get("provenance") or "").strip())
    )


def is_valid_level_up(entry) -> bool:
    """Is this ledger entry a valid RECORD of an atom's level_current move?

    ONE authority remains (2026-08-03, director console, finishing the 2026-07-29 ruling): a
    SELF-CERTIFIED `LEVEL_UP_SELF_CERTIFIED` entry -- honestly stamped, carrying the evidence the
    move rests on. The two director-permission authorities that used to sit above it are gone:
    the DIRECTOR-CONSOLE `LEVEL_UP_PROPOSED` act and the DIRECTOR_TWIN routine ratification (which
    existed only to stop routine levels queuing on a human, a queue that no longer exists).

    "Propose, record, act": this predicate is the RECORD half and nothing else. It asks whether the
    move left an auditable trace, never whether anyone permitted it. `tools/level_promotion_gate.py`
    refuses an UNRECORDED level increase at commit time on exactly this basis.

    A legacy console/twin entry already in the ledger is still readable history; it simply is not a
    separate authority any more, so this returns False for it and the mover self-certifies instead.
    """
    return is_valid_self_certified_level_up(entry)


def record_level_up_self_certified(atom: str, level: int | None, provenance: str, *, ts: float | None = None,
                                   path: Path | None = None) -> None:
    """Append a SELF-CERTIFIED level ratification (2026-07-29 ruling item 2). Honestly stamped
    `authorized_by=='agent_self_certified'`, `channel=='self'` — it NEVER masquerades as a console/twin/
    phone act, so the ledger always shows exactly who certified a move. `provenance` is REQUIRED and must
    state the evidence the move rests on (tests green, R15 mutation proof, fetched artifact, etc.) — an
    unattributed/unevidenced self-certification is exactly the self-ratification-without-a-trace defect
    R16 forbids; recording (not director permission) is what makes this valid."""
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError(
            "record_level_up_self_certified requires non-empty provenance (the evidence the move rests "
            "on) -- R16: the ledger is authority, an unevidenced self-certification is not a record."
        )
    if not isinstance(atom, str) or not atom.strip():
        raise ValueError("record_level_up_self_certified requires a non-empty atom id.")
    fields = {"atom": atom, "action": "LEVEL_UP_SELF_CERTIFIED"}
    if level is not None:
        fields["level"] = level
    _append_envelope(fields, provenance, "agent_self_certified", "self", ts=ts, path=path)


def record_level_correction_self_certified(atom: str, level: int, provenance: str, *,
                                           ts: float | None = None, path: Path | None = None) -> None:
    """Append a SELF-CERTIFIED level CORRECTION — a level_current move DOWN, recorded with the
    evidence that stopped reproducing.

    WHY THIS EXISTS, and it is not symmetry-for-its-own-sake. Until this landed the ledger could
    only record a level going UP, so the one direction that carries bad news had no auditable
    trace at all. R16's requirement is that a level MOVE leave a record of what moved and on what
    evidence; a demotion is a move, and it is the move a reader most needs to find later. The
    un-knowing case is the one this codebase has already been bitten by — a population change can
    retire an artefact that a sibling atom's promotion rested on, and the tell is precisely that
    the sibling's cited evidence no longer reproduces
    (`docs/staging/done/WORKER_FINDING_EVER_FLAGGED_IS_BLIND_TO_UN_KNOWING_2026-08-09.md`). With
    no record path, the only honest options were to leave a known-stale level standing or to edit
    it silently. Both are worse than a row saying what was un-known and why.

    IT IS DELIBERATELY NOT AN AUTHORITY. `is_valid_level_up` returns False for these rows, so a
    correction can never be used to satisfy `tools/level_promotion_gate.py` — recording a
    demotion cannot smuggle a promotion past the commit gate. Going back UP later requires its own
    `LEVEL_UP_SELF_CERTIFIED` with fresh evidence, exactly as the first move did.
    """
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError(
            "record_level_correction_self_certified requires non-empty provenance (the evidence "
            "that stopped reproducing) -- an unevidenced demotion is not a record either."
        )
    if not isinstance(atom, str) or not atom.strip():
        raise ValueError("record_level_correction_self_certified requires a non-empty atom id.")
    if not isinstance(level, int) or isinstance(level, bool):
        raise ValueError("record_level_correction_self_certified requires the new integer level.")
    _append_envelope({"atom": atom, "action": "LEVEL_CORRECTION_SELF_CERTIFIED", "level": level},
                     provenance, "agent_self_certified", "self", ts=ts, path=path)




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


