#!/usr/bin/env python3
"""MODEL TIERING — match the frontier model to the DRAWN WORK, not to the process (2026-08-12).

THE DEFECT THIS CLOSES. `worker_tick.py` spawns exactly one `claude -p` per tick and pinned it to
`claude-opus-5` with a module constant. The model was therefore a property of the TRANSPORT, not of
the work: a tick that re-runs a measurement tool and commits the row cost the same per token as a
tick that diagnoses a wedged publish gate. MODEL_SELECTION_POLICY.md (2026-07-12) already said the
right thing — "model choice is a per-ROLE decision, not a per-session preference" — and then said
"encode the assignment in the harness config... a model policy that depends on memory is a model
policy with an expiry date". It was never encoded for the tick. This module is that encoding.

THE RULE, AND WHY IT IS SHAPED THIS WAY (director, 2026-08-12):

    "Diagnosis, science, level moves and wall decisions stay Opus... If quality drops on
     anything, revert that class and say so — I'd rather spend the tokens than get shallower
     work."

That is an asymmetric loss function, and the code is built around it. A wrongly-cheap draw costs a
shallow turn on work that compounds — the expensive error. A wrongly-expensive draw costs tokens —
the cheap error. So:

  * OPUS IS THE DEFAULT AND THE FALLBACK. Sonnet is reachable only by an explicit, enumerated,
    currently-enabled pilot class.
  * ANY reserved marker anywhere in the doorbell forces Opus, even if pilot markers are also
    present. The tick spawns ONE process for a doorbell that may combine several drawn items
    (`primary; ALSO -- refill`), so the tier must be the MAXIMUM over everything drawn, never a
    majority vote and never the first match.
  * AN UNRECOGNISED DOORBELL IS OPUS. A new draw rung added next month is unclassified here, and
    unclassified must cost tokens rather than quality. `test_an_unknown_doorbell_is_opus` is the
    R15 proof that this direction is the one that holds.

WHAT IS *NOT* IN THE PILOT, DELIBERATELY. The RULE-0 HARDEN floor ("re-verify its exit tests,
mutation-re-test a control, red-team its invariants") looks mechanical and is not: red-teaming an
invariant is findings-quality work, the exact thing the director said he would rather pay for. It
stays Opus. Recorded here so the next reader knows it was considered and declined, not missed.

THE PILOT IS DATA, NOT CODE. Which classes are live, and for how long, is declared in
`docs/observability/model_tier_pilot.yaml` — readable, committed, revertible per class without a
code change, per the IaC rule ("NO behaviour-determining state lives outside the readable repo").
Deleting that file, or setting every class `enabled: false`, restores the pre-pilot behaviour
exactly: everything on Opus.

REUSE: background/model_tier.py
CLASS: CUSTOM
INDEX: searched "model tier", "model selection", "doorbell classify", "draw classification" --
       every query came back empty except this module's own row. Nothing in the tree routes a
       model: `worker_tick`, `worker_seat`, `director_twin`, `naive_organ` and `build_executor`
       each hold their own hard-coded constant, and MODEL_SELECTION_POLICY.md is a doc with no
       code behind it. The nearest thing to a doorbell CLASSIFIER is `supervisor.py`'s rung
       ladder, which PRODUCES the reason strings this reads -- so this module stands on that
       vocabulary rather than restating it, and
       `test_every_reserved_and_pilot_marker_is_actually_emitted_by_supervisor` pins the two
       together so the borrowed strings cannot drift apart silently. Deliberately NOT put in
       supervisor.py: the draw decides WHAT to work on, and letting it also decide what it costs
       would put a budget concern inside the rung ladder Rule 0 governs.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
PILOT_CONFIG = PROJECT_DIR / "docs" / "observability" / "model_tier_pilot.yaml"
TIER_LOG = PROJECT_DIR / "docs" / "observability" / "model_tier_log.jsonl"

OPUS = "claude-opus-5"
SONNET = "claude-sonnet-5"

# ── RESERVED: any of these anywhere in the doorbell forces OPUS ──────────────
#
# Each marker is a literal substring of a reason string that `supervisor.py` actually emits; they
# were read off the draw rungs on 2026-08-12, not invented. `test_every_reserved_marker_is_emitted_
# by_supervisor` pins them to the source so a rung reworded upstream fails here loudly instead of
# silently falling through to "unclassified" (which is Opus anyway — but silently, and a silent
# right answer stops being right the moment the fallback is ever loosened).
RESERVED: tuple[tuple[str, str, str], ...] = (
    # ── DIAGNOSIS (director-reserved) ────────────────────────────────────────
    ("PUBLISH-GATE WEDGE self-refill", "diagnosis",
     "a wedged publish gate is root-cause work under time pressure; R4 diagnosis discipline"),
    ("OPERATIONAL-LAYER PERSISTENT-RED self-refill", "diagnosis",
     "a daemon-lifecycle red that survived paging is the overnight-stall class"),
    # ── LEVEL MOVES (director-reserved) ──────────────────────────────────────
    # Every BUILD-lane draw carries `level N->M` and ends in a self-certified promotion, so the
    # BUILD lane IS the level-move lane. Both message shapes are matched: the byte-for-byte
    # single-atom string that other callers parse, and the three-lane assembly.
    ("self-refill from maturity map (dial-weighted)", "level_move",
     "a BUILD atom draw ends in a level move recorded to gate_authorizations.jsonl"),
    ("LANE 1 BUILD", "level_move", "the BUILD lane of a three-lane draw"),
    ("RULE 0 self-refill", "level_move",
     "the HARDEN floor red-teams invariants and mutation-re-tests controls — findings-quality "
     "work, excluded from the pilot deliberately (see module docstring)"),
    # ── SCIENCE (director-reserved) ──────────────────────────────────────────
    ("DECLARED-DEFECT self-refill", "science",
     "a declared fidelity defect is simulation science; closing it moves what the model claims"),
    ("LANE 3 DISCOVER/FRAME", "science", "DISCOVER/FRAME is judgment work per MODEL_SELECTION_POLICY"),
    ("FORWARD-DISCOVERY self-refill", "science", "forward discovery is open-ended research"),
    ("PROPOSE-HALF self-refill", "science", "writing a build proposal is architectural design"),
    ("RUNG 7 PLANNER self-refill", "science",
     "minting atoms from ratified goals decides what the company builds next"),
    # ── WALL DECISIONS (director-reserved) ───────────────────────────────────
    # Matched on content rather than on a rung: a wall crossing can ride in on ANY lane, and the
    # epistemic wall is the one control CLAUDE.md classes as a WALL rather than a dial.
    ("epistemic wall", "wall", "an epistemic-wall decision is a wall, never a dial"),
    ("wall_crossing", "wall", "wall-crossing paydown"),
    ("KNIFE", "wall", "the KNIFE passes cut wall crossings"),
    # ── JUDGMENT (not in the director's four, but Opus by standing policy) ───
    ("urgent from_rich queued", "director_input",
     "the director's own words; NTFY IS THE DIRECTOR — never handled by the cheaper tier"),
    ("[DIRECTOR-RULING]", "director_input", "a ruling is director authority"),
    ("[STEER]", "director_input", "a steer is director authority"),
    ("agenda open", "agenda",
     "an open agenda is mid-phase state whose next step is unknown to this classifier"),
    ("OPEN-CAMPAIGN self-refill", "campaign",
     "campaign surfaces land Expert-Hour-reviewed against scored rubric rows — judgment"),
)

# ── PILOT: reachable by Sonnet, when enabled and when nothing reserved fires ──
PILOT: tuple[tuple[str, str, str], ...] = (
    ("STALE-GAP-ROW self-refill", "stale_gap_row",
     "re-run a named tool against unchanged inputs, commit the row, show it reading CURRENT — the "
     "acceptance test is mechanical and stated in the doorbell itself"),
    ("LANE 2 SITE", "site_surface",
     "site/** surface build to a settled design, disjoint from sim/company by construction, "
     "pixel-verified against R11 — MODEL_SELECTION_POLICY already files this as volume work"),
)

# Staged-doc prefixes that carry NO judgment: a receipt of work already done, whose disposition is
# to archive it to docs/staging/done/. Everything NOT on this list (a WORKER_FINDING to disposition,
# an ADVISOR_ doc, a CLASS_ doc, a PLANNER_MINTED block) is judgment and forces Opus.
RECEIPT_PREFIXES = ("WORKER_REPORT_", "WORKER_RECEIPT_", "run_complete_", "run_pending_")
_STAGING_MARKER = "unprocessed staging -- "


@dataclass
class TierDecision:
    """The tier choice plus everything needed to audit it afterwards."""
    model: str
    tier: str                                  # "opus" | "sonnet"
    classes: list[str] = field(default_factory=list)
    reserved_hits: list[str] = field(default_factory=list)
    pilot_hits: list[str] = field(default_factory=list)
    why: str = ""
    reason_sha: str = ""

    @property
    def is_pilot(self) -> bool:
        return self.tier == "sonnet"


def _load_enabled_classes(config: Path | None = None, *, today: str | None = None) -> set[str]:
    """The pilot classes currently switched on.

    FAIL-CLOSED TOWARD OPUS at every step: a missing, unreadable or malformed config, an absent or
    unparseable `ends` date, or a date past `ends` all yield the empty set — which routes everything
    to Opus. An error in the pilot's own configuration must never be able to make work cheaper.

    THE WINDOW IS ENFORCED, NOT PROMISED. "Run them there for a defined period" is only a defined
    period if something ends it; a pilot that quietly becomes permanent because nobody remembered to
    stop it is the decay class this repo audits CLAUDE.md for. Past `ends`, every class is off and
    the tick is back on Opus with no edit, no deploy, and nobody needing to notice.
    """
    import time
    path = PILOT_CONFIG if config is None else config
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(data, dict):
            return set()
        ends = str(data.get("ends") or "")
        now = today or time.strftime("%Y-%m-%d")
        if len(ends) != 10 or now > ends:      # ISO dates compare correctly as strings
            return set()
        classes = data.get("classes") or {}
        if not isinstance(classes, dict):
            return set()
        return {name for name, cfg in classes.items()
                if isinstance(cfg, dict) and cfg.get("enabled") is True}
    except Exception:
        return set()


def _staging_is_receipts_only(reason: str) -> bool | None:
    """Judge the `unprocessed staging -- a.md, b.md, ...` segment of a doorbell.

    Returns True if every staged item is a receipt (archive-only), False if any needs judgment, and
    None if there is no staging segment to judge. Parsed rather than substring-matched because the
    segment is a LIST: 'contains a receipt' says nothing, only 'contains nothing but receipts' does.
    """
    if _STAGING_MARKER not in reason:
        return None
    segment = reason.split(_STAGING_MARKER, 1)[1]
    # The staging list runs to the end of `primary`. Two things can be appended after it, both by
    # `find_work`: '; ALSO -- <refill>' when a refill was also drawn, and
    # '; <name>.md: MINT one atom per named deliverable...' when a [DIRECTOR-RULING]/[STEER] is among
    # the staged docs (`ruling_mint_instruction`). Cut at whichever comes FIRST — cutting at the
    # first match in a fixed order would leave the other one's prose inside the list.
    cuts = [segment.index(t) for t in ("; ALSO -- ", ": MINT one atom") if t in segment]
    if cuts:
        segment = segment[:min(cuts)]
        # ': MINT one atom' cuts mid-item, leaving a partial trailing name; drop it.
        segment = segment.rsplit(";", 1)[0] if ";" in segment else segment
    names = [n.strip() for n in segment.split(",") if n.strip()]
    if not names:
        return False  # a staging marker with no parseable list: fail toward judgment
    return all(Path(n).name.startswith(RECEIPT_PREFIXES) for n in names)


def classify(reason: str, *, config: Path | None = None, today: str | None = None) -> TierDecision:
    """Choose the model for one drawn doorbell.

    The order below IS the safety property, and it is deliberately not the order that reads most
    naturally: reserved markers are collected FIRST and across the WHOLE string, before any pilot
    marker is considered, so no arrangement of the doorbell can let a pilot class win a draw that
    also contains reserved work.
    """
    text = reason or ""
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16] if text else ""

    reserved_hits = [marker for marker, _cls, _why in RESERVED if marker in text]
    reserved_classes = sorted({cls for marker, cls, _ in RESERVED if marker in text})

    # The staging segment is a reserved hit only when it holds something needing judgment.
    receipts_only = _staging_is_receipts_only(text)
    if receipts_only is False:
        reserved_hits.append(_STAGING_MARKER.strip())
        reserved_classes = sorted(set(reserved_classes) | {"finding_disposition"})

    if reserved_hits:
        return TierDecision(
            model=OPUS, tier="opus", classes=reserved_classes,
            reserved_hits=reserved_hits, reason_sha=sha,
            why="reserved work in the draw: " + ", ".join(reserved_classes),
        )

    enabled = _load_enabled_classes(config, today=today)
    pilot_hits = [marker for marker, _cls, _why in PILOT if marker in text]
    pilot_classes = sorted({cls for marker, cls, _ in PILOT if marker in text})
    if receipts_only is True:
        pilot_hits.append(_STAGING_MARKER.strip())
        pilot_classes = sorted(set(pilot_classes) | {"receipt_archival"})

    if not pilot_classes:
        return TierDecision(
            model=OPUS, tier="opus", classes=["unclassified"], reason_sha=sha,
            why="no marker matched — an unrecognised doorbell costs tokens, never quality",
        )

    disabled = [c for c in pilot_classes if c not in enabled]
    if disabled:
        return TierDecision(
            model=OPUS, tier="opus", classes=pilot_classes, pilot_hits=pilot_hits, reason_sha=sha,
            why="pilot class(es) not enabled in model_tier_pilot.yaml: " + ", ".join(disabled),
        )

    return TierDecision(
        model=SONNET, tier="sonnet", classes=pilot_classes, pilot_hits=pilot_hits, reason_sha=sha,
        why="every drawn item is an enabled pilot class: " + ", ".join(pilot_classes),
    )


def log_decision(decision: TierDecision, reason: str, *, outcome: str = "SPAWNED",
                 path: Path | None = None, now: float | None = None) -> None:
    """Append one auditable line per tick decision. Never raises — measurement must not be able to
    wedge the tick (an unavailable check is a failed check, but an unavailable LOG is not a reason
    to stop working). `reason_head` is truncated: the doorbell can be 8k of staged filenames."""
    import json
    import time
    target = TIER_LOG if path is None else path
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": now if now is not None else time.time(),
            "model": decision.model,
            "tier": decision.tier,
            "classes": decision.classes,
            "reserved_hits": decision.reserved_hits,
            "pilot_hits": decision.pilot_hits,
            "why": decision.why,
            "reason_sha": decision.reason_sha,
            "reason_head": (reason or "")[:400],
            "outcome": outcome,
        }
        with target.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception:
        pass


if __name__ == "__main__":  # pragma: no cover - operator convenience
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/model_tier.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("model_tier")
    import sys
    d = classify(sys.stdin.read() if len(sys.argv) < 2 else " ".join(sys.argv[1:]))
    print(f"{d.tier}\t{d.model}\t{','.join(d.classes)}\t{d.why}")
