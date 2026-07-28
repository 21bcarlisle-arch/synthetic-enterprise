"""Batched Inbound-Ratification Path -- BUILD half (b)/(c) of GAP-M2.

PURPOSE (OPS1 standard: state it first). Make the ONE non-autonomous gap-bucket move-direction --
retiring a gap INTO ``deliberate-and-staying`` -- impossible to enact silently, while every
autonomous move flows without friction.

GUARANTEE. An into-``deliberate-and-staying`` move never changes a gap's OPERATIVE bucket (the
disposition the machine draws on) until the director ratifies it; and such requests reach the
director BATCHED (ONE [ACT] escalation), never as N single interrupts, and never via the
interactive window (ESCALATION_IS_NTFY_NEVER_WINDOW -- a window-ask is a silent stall).

WHY. DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28 §2 (the AMENDMENT -- asymmetric ratification on
bucket moves): moving a gap INTO ``deliberate-and-staying`` is a scope claim in the direction where
honest reds quietly vanish, so it RETURNS for director ratification; moving OUT toward ``mint``, or
between the other three buckets, is AUTONOMOUS. Contract:
``docs/design/INBOUND_RATIFICATION_BATCH_PATH_CONTRACT.md`` (DISCOVER half). Buckets defined by
``docs/design/GAP_TRIAGE_AND_RANKING.md`` (GAP2, director-ratified).

WALLS (untouched):
  * No self-ratification (§2 / DIRECTOR_TWIN Law B): this path only ROUTES and HOLDS; the director
    ratifies the into-moves. ``record_ratification`` RECORDS a director act -- the classifier NEVER
    calls it. A mechanism that unblocks itself becomes a rubber stamp.
  * No level self-bump (R16): the BUILD half lands at build-quality with
    ``blocked_on: director_level_up`` for its 0->3 move.
  * R12: the count of batched requests is a diagnostic, never a score/target/headline.

R15 both-ways (tests/background/test_inbound_ratification.py):
  * MUTATION (control FIRES): a held into-move must NOT silently land -- ``operative_bucket`` returns
    the PRIOR bucket, never the proposed ``deliberate-and-staying``. Neuter the hold -> the test reds.
  * PASS-THROUGH (asymmetry is real, not a blanket gate): an out-toward-``mint`` move passes WITHOUT
    escalation.
  * FAIL-SAFE: an ambiguous / unclassifiable move direction is treated as INTO (HELD), never
    autonomous -- silence never retires a red.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from background import action_needed

PROJECT_DIR = Path(__file__).resolve().parent.parent

# The four buckets GAP2 (docs/design/GAP_TRIAGE_AND_RANKING.md §(i)) defines. Canonical spellings.
MINT = "mint"
DELIBERATE = "deliberate-and-staying"
BLOCKED_ON_DIRECTOR = "blocked-on-director"
NOT_WORTH = "not-worth-the-complexity"
BUCKETS = frozenset({MINT, DELIBERATE, BLOCKED_ON_DIRECTOR, NOT_WORTH})

# Append-only ledger of DIRECTOR ratifications of a gap's bucket. One JSON object per line:
# {gap_id, bucket, authorized_by, provenance, ts}. Analogous to gate_authorizations.jsonl -- it is
# the record of prior director ratifications the classifier compares a proposed into-move against
# (contract (T): proposed vs LAST DIRECTOR-RATIFIED bucket, so a re-run cannot launder an unratified
# into-move as "no change").
RATIFICATION_LEDGER_PATH = PROJECT_DIR / "docs" / "observability" / "gap_bucket_ratifications.jsonl"

# The single [ACT] item id the batched escalation registers under -- so a re-ping restates ONE
# concrete batched ask (fire-once-then-daily via action_needed.should_notify), never N singles.
ACT_ITEM_ID = "gap-inbound-ratification-batch"


# --------------------------------------------------------------------------- bucket normalisation
def normalize_bucket(bucket: object) -> str | None:
    """Canonical bucket string, or None if unrecognizable. Accepts underscore/space variants of the
    four GAP2 buckets so a triage producer that emits ``deliberate_and_staying`` reads the same as
    ``deliberate-and-staying``. A non-string, empty, or unknown value -> None (the caller treats an
    unrecognizable proposed bucket as an AMBIGUOUS direction -> HELD, per the fail-safe)."""
    if not isinstance(bucket, str):
        return None
    key = bucket.strip().lower().replace("_", "-").replace(" ", "-")
    return key if key in BUCKETS else None


# --------------------------------------------------------------------------- ratified-bucket ledger
def load_ratifications(path: Path | None = None) -> dict[str, str]:
    """gap_id -> last director-ratified bucket (the LAST valid entry per gap_id wins). Reads the
    append-only ledger.

    FAIL-SAFE TOWARD HOLDING (preserving reds): a missing / unreadable / garbled ledger yields an
    EMPTY map, so NO gap reads as ratified -- an into-``deliberate-and-staying`` move then can never
    be laundered as "already ratified" and is HELD. A single malformed line is skipped, never
    trusted (a forged "ratified deliberate" line is the one thing that could silently retire a red)."""
    p = path or RATIFICATION_LEDGER_PATH
    out: dict[str, str] = {}
    try:
        text = Path(p).read_text(encoding="utf-8")
    except OSError:
        return {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue  # skip a garbled line; never trust it
        if not isinstance(rec, dict):
            continue
        gid = rec.get("gap_id")
        bucket = normalize_bucket(rec.get("bucket"))
        if isinstance(gid, str) and gid and bucket is not None:
            out[gid] = bucket  # later line overrides earlier -> "last ratified"
    return out


def record_ratification(
    gap_id: str,
    bucket: str,
    *,
    authorized_by: str,
    provenance: str,
    path: Path | None = None,
    now: str | None = None,
) -> dict:
    """Append a DIRECTOR ratification of a gap's bucket to the append-only ledger.

    This is the RECORDING primitive invoked ON a director ratification act (same pattern as
    gate_authorizations.jsonl / record_director_ntfy_ruling) -- it records what the director DECIDED;
    it never DECIDES. **The classifier never calls this** (Law B / §2: no self-ratification -- a
    mechanism that ratifies its own into-moves becomes a rubber stamp). On ratification the gap's
    operative bucket flips: a later ``classify_triage_run`` sees it ratified and does NOT re-escalate
    (contract (H)).

    ``authorized_by`` and ``provenance`` are REQUIRED and non-empty -- a ratification with no
    recorded authority is exactly the self-ratification / evaporation defect this guards (R16: the
    ledger is authority; an unattributed line is not)."""
    if not isinstance(authorized_by, str) or not authorized_by.strip():
        raise ValueError(
            "record_ratification requires a non-empty authorized_by -- an unattributed gap-bucket "
            "ratification is the self-ratification defect §2/Law B forbids."
        )
    if not isinstance(provenance, str) or not provenance.strip():
        raise ValueError("record_ratification requires a non-empty provenance (R16: ledger is authority).")
    canon = normalize_bucket(bucket)
    if canon is None:
        raise ValueError(f"record_ratification: unknown bucket {bucket!r} (not one of {sorted(BUCKETS)}).")
    if not isinstance(gap_id, str) or not gap_id.strip():
        raise ValueError("record_ratification requires a non-empty gap_id.")
    entry = {
        "gap_id": gap_id,
        "bucket": canon,
        "authorized_by": authorized_by,
        "provenance": provenance,
        "ts": now or datetime.now(timezone.utc).isoformat(),
    }
    p = path or RATIFICATION_LEDGER_PATH
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


# --------------------------------------------------------------------------- the classifier
def classify_move(proposed_bucket: object, ratified_bucket: object) -> str:
    """``"held"`` or ``"autonomous"`` for a single proposed move.

    HELD iff the move is INTO ``deliberate-and-staying`` AND the gap was NOT already director-ratified
    as ``deliberate-and-staying``. Autonomous otherwise (out-toward-``mint`` and every move among the
    other three buckets pass straight through -- the asymmetry).

    FAIL-SAFE (exit (c), mandatory): an UNRECOGNIZABLE proposed bucket -> the move direction is
    ambiguous -> treated as INTO (HELD), never autonomous. Silence never retires a red."""
    norm = normalize_bucket(proposed_bucket)
    if norm is None:
        return "held"  # FAIL-SAFE: ambiguous/unclassifiable direction -> into (held)
    if norm != DELIBERATE:
        return "autonomous"  # any move NOT into deliberate-and-staying is autonomous (the asymmetry)
    # proposed == deliberate-and-staying: held UNLESS the gap is already director-ratified as such
    # (a re-run of the method must not re-escalate an already-ratified deliberate disposition).
    if normalize_bucket(ratified_bucket) == DELIBERATE:
        return "autonomous"
    return "held"


def operative_bucket(proposed_bucket: object, ratified_bucket: object) -> str:
    """The bucket the machine ACTUALLY draws on after this move -- the HELD guarantee, and the
    control the R15 MUTATION test fires on.

    Autonomous move -> applies as PROPOSED (the normalized proposed bucket). HELD into-move -> stays
    in the PRIOR bucket (the last ratified disposition, or ``mint`` if never ratified) -- the
    into-move is NOT self-enacted. If a held into-move ever returned the proposed
    ``deliberate-and-staying`` here, the honest red would silently vanish; that is the mutation the
    test must catch."""
    if classify_move(proposed_bucket, ratified_bucket) == "autonomous":
        # An autonomous move applies as proposed. (classify_move only returns "autonomous" when the
        # proposed bucket normalizes, so this is never None.)
        return normalize_bucket(proposed_bucket)  # type: ignore[return-value]
    # HELD: the row stays in its prior bucket (last ratified, or mint if never ratified).
    prior = normalize_bucket(ratified_bucket)
    return prior if prior is not None else MINT


def classify_triage_run(
    rows: list[dict],
    ratifications: dict[str, str] | None = None,
    ledger_path: Path | None = None,
) -> dict[str, list[dict]]:
    """Partition a triage run's rows into ``{"held": [...], "autonomous": [...]}``.

    Each row is a dict carrying at least ``gap_id`` and ``proposed_bucket``; a row proposing
    ``deliberate-and-staying`` should also carry the GAP2(iv) evidence (``argument`` and
    ``measured_bound``) the batch needs. ``ratifications`` maps gap_id -> last ratified bucket
    (defaults to ``load_ratifications(ledger_path)``).

    Every HELD row is annotated with ``prior_bucket`` (where the row STAYS -- so the batch and
    ``operative_bucket`` can never disagree). Autonomous rows are returned unchanged."""
    ratifications = load_ratifications(ledger_path) if ratifications is None else ratifications
    held: list[dict] = []
    autonomous: list[dict] = []
    for row in rows:
        gid = row.get("gap_id")
        ratified = ratifications.get(gid) if isinstance(gid, str) else None
        if classify_move(row.get("proposed_bucket"), ratified) == "held":
            annotated = dict(row)
            annotated["prior_bucket"] = ratified if ratified is not None else MINT
            held.append(annotated)
        else:
            autonomous.append(dict(row))
    return {"held": held, "autonomous": autonomous}


# --------------------------------------------------------------------------- batching + escalation
def build_ratification_batch(held_rows: list[dict]) -> dict | None:
    """ONE batched ratification request from the HELD into-moves, or ``None`` when there are none
    (contract (B): a batch with zero into-moves emits NO escalation -- no empty-batch noise).

    Carries, per row: ``gap_id``, ``prior_bucket`` (where the row stays until ratified), the proposed
    ``argument``, and the ``measured_bound`` GAP2(iv) requires. ``count`` is an R12 diagnostic on the
    payload, never a score/target."""
    if not held_rows:
        return None
    return {
        "kind": "inbound-ratification-batch",
        "count": len(held_rows),  # R12: diagnostic only
        "rows": [
            {
                "gap_id": r.get("gap_id"),
                "prior_bucket": r.get("prior_bucket", MINT),
                "proposed_bucket": DELIBERATE,
                "argument": r.get("argument", ""),
                "measured_bound": r.get("measured_bound", ""),
            }
            for r in held_rows
        ],
    }


def format_batch_ask(batch: dict) -> tuple[str, str, str]:
    """(what, how, why) for the single [ACT] item -- restates every held row so a daily re-ping never
    degrades into a vague nag. Kept structured (action_needed's convention)."""
    rows = batch.get("rows", [])
    lines = "; ".join(
        f"{r.get('gap_id')} ({r.get('prior_bucket')}->deliberate-and-staying: "
        f"{r.get('argument') or 'no argument given'}, bound: {r.get('measured_bound') or 'unmeasured'})"
        for r in rows
    )
    what = (
        f"Ratify (or reject) {len(rows)} proposed move(s) INTO deliberate-and-staying -- each retires "
        f"an honest red as a scope choice and is HELD in its prior bucket until you rule: {lines}"
    )
    how = (
        "Reply per row: ratify -> record_ratification(gap_id, 'deliberate-and-staying'); reject -> the "
        "row stays in its prior bucket (already the operative disposition -- nothing to undo)."
    )
    why = (
        "GAP_TRIAGE §2 asymmetry: moving a gap INTO deliberate-and-staying is the one direction where "
        "an honest red quietly vanishes, so it returns for your ratification (never self-enacted). "
        "Batched, not N singles."
    )
    return what, how, why


def escalate_batch(
    batch: dict | None,
    *,
    register_path: Path | None = None,
    send_ntfy_fn=None,
    now: str | None = None,
) -> bool:
    """Route ONE batched ratification request through the existing [ACT] machinery
    (``background.action_needed``) -- NEVER the interactive window (ESCALATION_IS_NTFY_NEVER_WINDOW).
    Fire-once-then-daily via ``should_notify`` / ``mark_sent``, so a re-run this cycle does NOT
    re-page. A ``None`` / empty batch escalates NOTHING and returns False (contract (B)).

    Returns True iff a page was actually sent this call. ``send_ntfy_fn`` is injectable for tests
    (defaults to ``background.ntfy_utils.send_ntfy``); a send is confirmed by a truthy id before the
    send-clock advances (the register-vs-sent discipline action_needed already enforces)."""
    if not batch or not batch.get("rows"):
        return False
    what, how, why = format_batch_ask(batch)
    action_needed.register_item(ACT_ITEM_ID, what, how, why, path=register_path, now=now)
    if not action_needed.should_notify(ACT_ITEM_ID, path=register_path, now=now):
        return False  # already paged this cycle -- silent (fire-once-then-daily)
    if send_ntfy_fn is None:
        from background.ntfy_utils import send_ntfy as send_ntfy_fn  # lazy: keep zero-dep footprint
    sent_id = send_ntfy_fn(action_needed.format_action_needed(ACT_ITEM_ID, what, how, why))
    if sent_id:
        action_needed.mark_sent(ACT_ITEM_ID, path=register_path, now=now)
        return True
    return False  # failed send leaves the item DUE -> next cycle retries (no false "pinged")


def process_triage_run(
    rows: list[dict],
    *,
    ledger_path: Path | None = None,
    register_path: Path | None = None,
    send_ntfy_fn=None,
    now: str | None = None,
) -> dict:
    """The single public entrypoint a triage/GAP3 run calls (so the mechanism is wired, not an orphan
    control -- R11 no-orphan-transition): classify the run's rows, build the batch of held into-moves,
    escalate it via [ACT], and return everything the caller draws on.

    Returns ``{"held", "autonomous", "batch", "escalated", "operative"}`` where ``operative`` maps
    gap_id -> the bucket the machine actually draws on NOW (held into-moves resolve to their prior
    bucket -- the HELD guarantee, computed the same way ``operative_bucket`` does)."""
    ratifications = load_ratifications(ledger_path)
    parts = classify_triage_run(rows, ratifications=ratifications)
    batch = build_ratification_batch(parts["held"])
    escalated = escalate_batch(batch, register_path=register_path, send_ntfy_fn=send_ntfy_fn, now=now)
    operative: dict[str, str] = {}
    for row in rows:
        gid = row.get("gap_id")
        if isinstance(gid, str) and gid:
            operative[gid] = operative_bucket(row.get("proposed_bucket"), ratifications.get(gid))
    return {
        "held": parts["held"],
        "autonomous": parts["autonomous"],
        "batch": batch,
        "escalated": escalated,
        "operative": operative,
    }
