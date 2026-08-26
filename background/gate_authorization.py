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
import time
from dataclasses import dataclass
from pathlib import Path

import yaml

from background.finding_severity import classifiable_documents, parse_severity_file
from tools import maturity_map_store as map_store

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
        # BOTH halves, via the store's TEXT rather than its parsed atoms, so this keeps the
        # `safe_load_all` shape-tolerance the walkers below rely on: fixtures here hand in
        # maps that are dicts or multi-document, and a loader that insists on a top-level
        # list turns those into an empty dict -- which reads downstream as `<lane-unknown>`.
        docs = list(yaml.safe_load_all(map_store.map_text(path or MAP_PATH)))
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


# ══════════════════════════════════════════════════════════════════════════════════════════
# OPS11 — A LIVE BLOCKING FINDING REFUSES NEW LEVEL-RAISES IN ITS OWN LANE, AND NOWHERE ELSE
# ══════════════════════════════════════════════════════════════════════════════════════════
#
# WHY (DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12, clause 2, deliverable 3):
# a BLOCKING finding says an instrument IN THIS AREA is untrustworthy. Certifying a new level
# while that instrument is the thing doing the certifying means the new work is certified by
# the lie. The refusal is what makes that structurally impossible rather than merely
# discouraged — the MAKE_IT_STICK rule: a policy that is not a mechanism evaporates.
#
# THE SCOPE IS THE LANE, and that is the whole design. The real-world twin is a calibration
# hold: one bench is out of certification and stops issuing certificates; the rest of the lab
# works on. A repo-wide freeze would be routed around inside a day
# (`feedback_control_that_can_only_fail_wedges`), so the lane bound is not politeness, it is
# what makes the control survivable.
#
# THE TWO RELEASES, both of which are TESTED to actually let the next raise through (R11 — a
# hold whose release does nothing is the defect R11 names):
#   1. REPAIR — the finding's own document gains a checked `**Discharged:**` line, which
#      `finding_severity.parse_severity_file` already reads down to RECORDED. The release is
#      therefore the SAME parse the hold uses; there is no second list that could disagree.
#   2. RECORD AND ACCEPT — a `LIMITATION_ACCEPTED` row in the same ledger, naming the lane,
#      the finding, and why the level move is sound in spite of it. This is clause 2's own
#      second release, made machine-readable.
#
# FAIL-CLOSED, AND WHY THAT IS SAFE HERE — state the reasoning, because a fail-closed control
# with no discharge is exactly how this project has wedged its own publishing before. An
# absent staging root, an unreadable one, a document whose severity cannot be parsed, or an
# atom whose lane cannot be determined all read as UNKNOWN and REFUSE, because an unavailable
# check is a FAILED check (R15 killer pattern 3, fail-silent). That is only safe because
# release 2 ALWAYS exists and needs no repair: any UNKNOWN is itself recordable-and-acceptable
# under a stable identity, so there is no state of the world in which a mover has no legible
# way forward. A fail-closed control whose discharge can also become unavailable is a wedge;
# this one's cannot, because writing a ledger row depends on nothing the check depends on.
#
# AN UNCLASSIFIED DOCUMENT REFUSES EVERY LANE, deliberately. Its severity could be BLOCKING
# and its lane is unknown, so attributing it to no lane would make "mangle the header" the
# cheapest way to clear a hold — the loophole this control exists to close. It is recorded and
# accepted per-document exactly like any other blocker, and the cheaper fix is one header line.

#: The stable identity an UNKNOWN reads under, so it can be recorded-and-accepted like any
#: other blocker. Kept distinct from any real filename (angle brackets are not legal in one).
UNREADABLE_INDEX_FINDING = "<severity-index-unreadable>"

#: The lane an atom is refused under when its own lane cannot be determined.
UNKNOWN_LANE = "<lane-unknown>"


@dataclass(frozen=True)
class LaneBlocker:
    """One live reason a lane refuses new level-raises."""

    lane: str
    finding: str  # the document's basename, or UNREADABLE_INDEX_FINDING
    path: str  # repo-relative path, or a description of the UNKNOWN
    reason: str

    def describe(self) -> str:
        return f"{self.finding} ({self.path}) — {self.reason}"


class LaneBlockedError(RuntimeError):
    """Raised INSTEAD of writing a level record when the atom's lane is held."""

    def __init__(self, atom: str, lane: str, blockers) -> None:
        self.atom = atom
        self.lane = lane
        self.blockers = tuple(blockers)
        super().__init__(refusal_message(atom, lane, self.blockers))


def atom_lanes(map_obj) -> dict:
    """{atom_id: lane} for every atom in a parsed maturity map. Pure. Mirrors
    `atom_loop_stages`' walk, but keys on `id` ONLY: `name` is free prose on these records
    (OPS11's own `name` is a paragraph), and a prose key would silently attribute a lane to
    something that is not an atom."""
    out: dict = {}

    def walk(o):
        if isinstance(o, dict):
            aid = o.get("id")
            if isinstance(aid, str) and "lane" in o:
                out[aid] = o.get("lane")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(map_obj)
    return out


def current_atom_lanes(path: Path | None = None) -> dict:
    """{atom_id: lane} for the live map. {} on any read/parse failure — the caller turns a
    missing lane into an UNKNOWN refusal, so failing to {} here fails CLOSED downstream
    rather than open."""
    try:
        # BOTH halves, via the store's TEXT rather than its parsed atoms, so this keeps the
        # `safe_load_all` shape-tolerance the walkers below rely on: fixtures here hand in
        # maps that are dicts or multi-document, and a loader that insists on a top-level
        # list turns those into an empty dict -- which reads downstream as `<lane-unknown>`.
        docs = list(yaml.safe_load_all(map_store.map_text(path or MAP_PATH)))
        out: dict = {}
        for d in docs:
            out.update(atom_lanes(d))
        return out
    except Exception:
        return {}


def lane_for_atom(atom: str, *, map_path: Path | None = None) -> str | None:
    """The atom's lane, or None when the map cannot answer (absent atom, unreadable map, or a
    lane that is not a string). None means UNKNOWN, never 'no lane to check'."""
    lane = current_atom_lanes(map_path).get(atom)
    return lane if isinstance(lane, str) and lane.strip() else None


def is_valid_limitation_acceptance(entry) -> bool:
    """Is this ledger row a valid RECORD-AND-ACCEPT of one lane blocker?

    Same honesty envelope as every other self-certified row: it says who wrote it and carries
    the evidence. `provenance` is where the acceptance earns its name — 'why this level move
    is sound in spite of that finding' — and an empty one is not an acceptance, it is a
    silence with a filename attached.
    """
    return (
        isinstance(entry, dict)
        and entry.get("action") == "LIMITATION_ACCEPTED"
        and entry.get("authorized_by") == "agent_self_certified"
        and entry.get("channel") == "self"
        and bool(str(entry.get("lane") or "").strip())
        and bool(str(entry.get("finding") or "").strip())
        and bool(str(entry.get("provenance") or "").strip())
    )


def accepted_limitations(ledger: list) -> set:
    """{(lane, finding-basename)} for every valid acceptance in the ledger.

    The finding is normalised to its BASENAME on both sides of the comparison: a document
    moves between `docs/staging/` and `docs/staging/done/` in the ordinary course of the
    machine, and an acceptance that evaporated on an archive move would be a release that
    silently un-releases. Basenames are unique within the staging root, so nothing is
    conflated by the normalisation.
    """
    out = set()
    for e in ledger:
        if is_valid_limitation_acceptance(e):
            out.add((str(e["lane"]).strip(), Path(str(e["finding"]).strip()).name))
    return out


def record_limitation_accepted(lane: str, finding: str, provenance: str, *,
                               ts: float | None = None, path: Path | None = None) -> None:
    """Append a RECORD-AND-ACCEPT row — clause 2's second release, in the ledger where every
    other level-record already lives.

    It accepts ONE (lane, finding) pair on purpose. A blanket 'accept this lane' row would be
    the fail-open shape the refusal exists to prevent: the point of the hold is that somebody
    reads the named finding and says why the move is sound anyway, and a wildcard says it
    about a set nobody enumerated.
    """
    if not isinstance(lane, str) or not lane.strip():
        raise ValueError("record_limitation_accepted requires the lane the acceptance releases.")
    if not isinstance(finding, str) or not finding.strip():
        raise ValueError(
            "record_limitation_accepted requires the finding being accepted (its filename) -- an "
            "acceptance that names no finding accepts nothing anyone can check."
        )
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError(
            "record_limitation_accepted requires non-empty provenance: why the level move is sound "
            "in spite of this finding. That sentence IS the acceptance; without it the row is a "
            "silence with a filename attached."
        )
    _append_envelope({"action": "LIMITATION_ACCEPTED", "lane": lane.strip(),
                      "finding": Path(finding.strip()).name},
                     provenance, "agent_self_certified", "self", ts=ts, path=path)


def lane_blockers(lane: str, *, staging_root: Path | None = None, repo_root: Path | None = None,
                  ledger: list | None = None, ledger_path: Path | None = None) -> list:
    """Live BLOCKING findings holding `lane`, minus those already recorded-and-accepted.

    An absent or unreadable staging root is an UNKNOWN and holds EVERY lane (fail-closed): a
    severity index nobody can read cannot tell you the lane is clear.
    """
    root = Path(staging_root) if staging_root is not None else (PROJECT_DIR / "docs" / "staging")
    rroot = Path(repo_root) if repo_root is not None else PROJECT_DIR
    accepted = accepted_limitations(ledger if ledger is not None else read_ledger(ledger_path))

    def live(blocker: LaneBlocker) -> bool:
        return (blocker.lane, blocker.finding) not in accepted

    if not root.is_dir():
        return [b for b in [LaneBlocker(
            lane, UNREADABLE_INDEX_FINDING, str(root),
            "the severity index (the staging root) is absent or is not a directory, so no lane "
            "can be shown clear -- an unavailable check is a FAILED check (R15)",
        )] if live(b)]

    try:
        documents = classifiable_documents(root)
    except OSError as exc:
        return [b for b in [LaneBlocker(
            lane, UNREADABLE_INDEX_FINDING, str(root),
            f"the severity index could not be listed ({exc.__class__.__name__})",
        )] if live(b)]

    out: list = []
    for doc in documents:
        parsed = parse_severity_file(doc, rroot)
        rel = _repo_relative(doc, rroot)
        if not parsed.is_classified:
            # UNKNOWN: could be BLOCKING, lane undeterminable -> holds every lane. See the
            # header note on why attributing it to no lane would be the loophole.
            out.append(LaneBlocker(lane, doc.name, rel,
                                   f"severity UNCLASSIFIED ({parsed.reason or 'unparseable header'}) "
                                   f"-- an unreadable severity cannot show any lane clear"))
        elif parsed.is_blocking and parsed.lane == lane:
            out.append(LaneBlocker(lane, doc.name, rel,
                                   f"BLOCKING in {parsed.lane}: an instrument, control or published "
                                   f"figure in this lane may be wrong"))
    return [b for b in out if live(b)]


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path(repo_root).resolve()))
    except (ValueError, OSError):
        return str(path)


def refusal_message(atom: str, lane: str, blockers) -> str:
    """The refusal, naming every finding AND its path. Exit criterion 1 of the atom: a refusal
    that does not say which finding blocks it cannot be discharged, so the message is part of
    the mechanism and not decoration."""
    named = "\n".join(f"    - {b.describe()}" for b in blockers)
    first = blockers[0].finding if blockers else "<finding>"
    return (
        f"OPS11: the level-raise on `{atom}` is REFUSED -- lane `{lane}` holds "
        f"{len(list(blockers))} live BLOCKING finding(s), so a new level here would be certified "
        f"by an instrument this lane's own findings say may be wrong:\n"
        f"{named}\n"
        f"  Either release discharges it, and progress in EVERY OTHER LANE is untouched:\n"
        f"    1. REPAIR it, then add a checked discharge line to that document's header block:\n"
        f"         **Discharged:** `tests/x/test_y.py::test_z` -- one line saying why\n"
        f"    2. RECORD AND ACCEPT the limitation:\n"
        f"         python3 -c \"from background.gate_authorization import record_limitation_accepted; "
        f"record_limitation_accepted('{lane}', '{first}', '<why this level move is sound in spite "
        f"of it>')\"\n"
    )


def refuse_level_raise_if_lane_blocked(atom: str, *, lane: str | None = None,
                                       map_path: Path | None = None,
                                       staging_root: Path | None = None,
                                       repo_root: Path | None = None,
                                       ledger_path: Path | None = None) -> None:
    """Raise `LaneBlockedError` when `atom`'s lane is held. Returns None when it is clear.

    An atom whose lane cannot be determined is refused under `UNKNOWN_LANE` rather than waved
    through: 'I could not tell which lane this belongs to' is not evidence that the lane is
    clear, and waving it through would make deleting an atom's lane the cheapest escape.
    """
    resolved = lane or lane_for_atom(atom, map_path=map_path)
    if resolved is None:
        raise LaneBlockedError(atom, UNKNOWN_LANE, [LaneBlocker(
            UNKNOWN_LANE, UNREADABLE_INDEX_FINDING,
            str(map_path or MAP_PATH),
            f"`{atom}` has no readable `lane` in the maturity map, so the lane that would be "
            f"held cannot be determined -- give the atom a lane, or record-and-accept",
        )])
    blockers = lane_blockers(resolved, staging_root=staging_root, repo_root=repo_root,
                             ledger_path=ledger_path)
    if blockers:
        raise LaneBlockedError(atom, resolved, blockers)


def record_level_up_self_certified(atom: str, level: int | None, provenance: str, *, ts: float | None = None,
                                   path: Path | None = None, map_path: Path | None = None,
                                   staging_root: Path | None = None,
                                   repo_root: Path | None = None) -> None:
    """Append a SELF-CERTIFIED level ratification (2026-07-29 ruling item 2). Honestly stamped
    `authorized_by=='agent_self_certified'`, `channel=='self'` — it NEVER masquerades as a console/twin/
    phone act, so the ledger always shows exactly who certified a move. `provenance` is REQUIRED and must
    state the evidence the move rests on (tests green, R15 mutation proof, fetched artifact, etc.) — an
    unattributed/unevidenced self-certification is exactly the self-ratification-without-a-trace defect
    R16 forbids; recording (not director permission) is what makes this valid.

    OPS11 (2026-08-13): this is the FIRST of the two places a level is actually recorded, so the
    lane-scoped BLOCKING refusal fires HERE, before the row is written -- raising `LaneBlockedError`
    rather than appending. Refusing at the writer and again at the commit gate is not belt-and-braces
    for its own sake: a row written before a blocker appeared would satisfy the commit gate's
    recorded-check on a later commit, so only the commit-time half sees the state of the lane AT THE
    MOMENT THE MAP MOVES."""
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError(
            "record_level_up_self_certified requires non-empty provenance (the evidence the move rests "
            "on) -- R16: the ledger is authority, an unevidenced self-certification is not a record."
        )
    if not isinstance(atom, str) or not atom.strip():
        raise ValueError("record_level_up_self_certified requires a non-empty atom id.")
    # The lane refusal runs AFTER the shape checks (so a malformed call still reports the thing
    # wrong with the call) and BEFORE the append (so a refused raise leaves NO row -- a refusal
    # that still recorded would satisfy the commit gate it exists to hold).
    refuse_level_raise_if_lane_blocked(atom, map_path=map_path, staging_root=staging_root,
                                       repo_root=repo_root, ledger_path=path)
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


