"""The direction record — what the delivery seat decided, and the ONLY way that reaches the draw.

Design: `docs/design/THE_DELIVERY_SEAT.md`. Director, 2026-08-25: *"something that wakes on its
own, reads the last stretch ... and decides what actually matters next ... It reads what happened,
judges it against the thesis, sets what the ticks draw from next, and records what it chose and
what it rejected."*

THIS MODULE IS THE READ SIDE AND NOTHING ELSE, and the split is structural rather than tidy.
`background/supervisor.py` imports THIS; it never imports `background/delivery_seat.py`. So the
draw can read direction and has no path to the thing that writes it — the orienting session cannot
reach the draw except through a file on disk that this module validates first.

THE ONE DISTINCTION THE WHOLE DESIGN HANGS OFF. `background/daily_self_note.py` carries a HARD LAW
called SEVERANCE: it may measure the machine and may never touch the draw, because a
self-measurement that feeds the draw is goal-seeking. This module feeds the draw on purpose. That
is not an exception to that law but the other side of a line it never drew:

    The delivery seat may decide WHAT TO WORK ON.
    It may never decide WHAT COUNTS AS SUCCESS.

Priority is a judgement about attention, which is what a delivery seat is for. A target is a
number the work then bends toward, which is R12's entire subject. `validate()` refuses a record
carrying target-shaped content, so that sentence is a control and not a promise.

A WEIGHT, NEVER A GATE. `focus_weights` multiplies the supervisor's existing dial weights. It
never filters, excludes or reorders the candidate list, and it can never return zero. That single
property IS Rule 0 here: a direction record cannot empty the feasible set, so the worst a wrong or
stale direction can do is make the machine slower to reach something, never unable to.

FAIL-SOFT, AND DELIBERATELY THE OPPOSITE OF THE REST OF THIS TREE. Most controls here fail CLOSED
because an unavailable check is a failed check. Direction is not a check — it is advice — and
advice that wedges the draw when it goes missing would be worse than no advice at all. Missing,
unreadable, malformed, or expired all return "no focus", and the draw then behaves byte-for-byte
as it did before this module existed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DIRECTION_DIR = PROJECT_DIR / "docs" / "direction"
DIRECTION_PATH = DIRECTION_DIR / "DIRECTION.yaml"
DECISIONS_PATH = DIRECTION_DIR / "decisions.jsonl"
DELIVERY_FEED = PROJECT_DIR / "site" / "data" / "delivery.json"

#: THE WRITE SCOPE, and the reason "it never becomes a second writer on the tree" is a mechanism
#: rather than an intention. The delivery seat `git add`s exactly these paths and nothing else, so
#: anything the orienting session touched outside them is simply not in its commit.
WRITE_SCOPE = (
    "docs/direction/DIRECTION.yaml",
    "docs/direction/decisions.jsonl",
    "site/data/delivery.json",
)

#: Direction older than this stops biasing the draw. STALE DIRECTION IS WORSE THAN NONE: it steers
#: toward what mattered yesterday with all the confidence of what matters now. Four orientations at
#: the declared three-hour cadence, so a single skipped or failed run never silently disarms it.
FOCUS_MAX_AGE_HOURS = 12.0

#: Weight multipliers by focus rank. Rank 1 is 4x its dial, and everything past the third named
#: item gets `_FOCUS_TAIL_MULTIPLIER`. Chosen to BITE rather than to be gentle: `d7d36b46a`
#: records two soft guards composing into a no-op, an atom with 1,307 unchanged draws weighted
#: exactly like the one promoted that morning. A steer too polite to change a draw is the failure
#: mode of this design, which is why §6 of the design measures whether focus was actually drawn.
FOCUS_RANK_MULTIPLIERS = (4.0, 3.0, 2.0)
_FOCUS_TAIL_MULTIPLIER = 1.5

#: Keys the record may NOT carry, at any depth. This is §2 made mechanical: a direction record
#: naming a number to hit has stopped being direction and become a target, and the next stretch
#: would optimise it. Checked against the KEY, not the prose — a `why` that quotes a measurement
#: ("the belief error is +0.5pp") is exactly what good direction looks like, and forbidding
#: numbers outright would only buy vagueness.
FORBIDDEN_KEYS = frozenset({
    "target", "targets", "goal", "goals", "kpi", "kpis", "quota", "quotas",
    "threshold", "thresholds", "score", "scores", "benchmark", "benchmarks",
    "metric", "metrics",
})

REQUIRED_KEYS = ("version", "oriented_at", "focus", "not_now")


@dataclass(frozen=True)
class Direction:
    """A parsed, VALIDATED direction record. Constructing one is not a claim that its advice is
    good — only that it is a direction record and not something else wearing the filename."""

    oriented_at: datetime
    focus: tuple[dict, ...]
    not_now: tuple[dict, ...]
    wrong: tuple[dict, ...] = ()
    for_the_director: tuple[dict, ...] = ()
    thesis_read: str = ""
    stretch_reviewed: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    def age_hours(self, now: datetime | None = None) -> float:
        now = now or datetime.now(timezone.utc)
        return (now - self.oriented_at).total_seconds() / 3600.0

    def is_live(self, now: datetime | None = None) -> bool:
        return 0.0 <= self.age_hours(now) <= FOCUS_MAX_AGE_HOURS

    def focus_keys(self) -> tuple[str, ...]:
        return tuple(str(item.get("id")) for item in self.focus if item.get("id"))


def _iso(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _forbidden_keys_in(node, seen: set[str] | None = None) -> set[str]:
    """Every forbidden key anywhere in the record, at any depth."""
    seen = set() if seen is None else seen
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str) and key.strip().lower() in FORBIDDEN_KEYS:
                seen.add(key.strip().lower())
            _forbidden_keys_in(value, seen)
    elif isinstance(node, (list, tuple)):
        for item in node:
            _forbidden_keys_in(item, seen)
    return seen


def validate(record) -> list[str]:
    """Every reason this is not a usable direction record, or an empty list.

    RETURNS THE REASONS RATHER THAN A BOOLEAN because the delivery seat pages with them and the
    page prints them: a direction record that was refused and cannot say why is the same
    fail-silent shape this project keeps finding in its own controls.
    """
    problems: list[str] = []
    if not isinstance(record, dict):
        return ["the record is not a mapping"]
    for key in REQUIRED_KEYS:
        if key not in record:
            problems.append(f"missing required key {key!r}")
    if _iso(record.get("oriented_at")) is None:
        problems.append("oriented_at is not an ISO-8601 timestamp")
    focus = record.get("focus")
    if not isinstance(focus, list) or not focus:
        problems.append("focus is empty -- a direction record that names no work is not direction")
    else:
        for i, item in enumerate(focus):
            if not isinstance(item, dict) or not item.get("id") or not item.get("why"):
                problems.append(f"focus[{i}] needs an id and a why")
    not_now = record.get("not_now")
    if not isinstance(not_now, list) or not not_now:
        # THE REJECTIONS ARE THE POINT, and this is the director's own instruction made
        # mechanical: "record the options you considered and why you chose as you did. That
        # record is what I review, and it's what makes it safe for you not to ask." A record
        # listing only what was chosen hides the judgement it was supposed to expose.
        problems.append(
            "not_now is empty -- a direction that rejected nothing recorded no judgement, and "
            "the rejections are what makes it reviewable"
        )
    else:
        for i, item in enumerate(not_now):
            if not isinstance(item, dict) or not item.get("what") or not item.get("why"):
                problems.append(f"not_now[{i}] needs a what and a why")
    forbidden = sorted(_forbidden_keys_in(record))
    if forbidden:
        problems.append(
            "the record carries target-shaped keys {}: direction may say WHAT TO WORK ON and "
            "never WHAT COUNTS AS SUCCESS (R12, and THE_DELIVERY_SEAT.md section 2)".format(
                ", ".join(repr(k) for k in forbidden))
        )
    return problems


def read_direction(path: Path | None = None) -> Direction | None:
    """The current direction, or None. NEVER RAISES -- see the module docstring on fail-soft."""
    path = DIRECTION_PATH if path is None else path
    try:
        import yaml
    except ImportError:
        return None
    try:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        # BREADTH IS THE POINT (see the fail-soft note above): a missing file, a permission
        # error and a YAML syntax error all mean the same thing to the draw -- no advice.
        return None
    if validate(record):
        return None
    stamp = _iso(record.get("oriented_at"))
    if stamp is None:
        return None

    def _rows(key):
        value = record.get(key) or []
        return tuple(r for r in value if isinstance(r, dict)) if isinstance(value, list) else ()

    return Direction(
        oriented_at=stamp,
        focus=_rows("focus"),
        not_now=_rows("not_now"),
        wrong=_rows("wrong"),
        for_the_director=_rows("for_the_director"),
        thesis_read=str(record.get("thesis_read") or ""),
        stretch_reviewed=record.get("stretch_reviewed") or {},
        raw=record,
    )


def current_focus(path: Path | None = None, now: datetime | None = None) -> tuple[str, ...]:
    """The atom ids the current LIVE direction names, in order. `()` when there is no direction,
    it is malformed, or it has expired."""
    direction = read_direction(path)
    if direction is None or not direction.is_live(now):
        return ()
    return direction.focus_keys()


def unreachable_focus(atom_ids, path: Path | None = None,
                      now: datetime | None = None) -> list[dict]:
    """Focus items the DRAW CANNOT REACH, in the seat's own order.

    THE DEFECT THIS NAMES, measured on the seat's very first record (2026-08-25): `focus_weights`
    multiplies the dial weight of an atom the draw was ALREADY considering, so a focus id that is
    not an atom multiplies nothing. Four of five focus items were ids the map had never heard of
    -- `flat-control-credible-average-player`, `publish-path-lands`,
    `expected-cost-collections-term`, `harness-lane-prune` -- and every one of them was work the
    director had to sit through an interactive session to get built.

    So this is the OTHER half of the steer, and `background/delivery_lane.py` is what draws it: an
    item with an atom is reached by the weight bias, and an item without one is reached here.
    Splitting on that keeps the two paths from double-counting the same work.

    ORDER IS PRESERVED because `focus` is ordered and its first entry is what the seat judged
    mattered most. Sorting or filtering it here would quietly overrule the judgement this whole
    mechanism exists to carry.

    An expired or missing record yields NOTHING, exactly as `current_focus` does: stale direction
    stops steering on its own, and it must not start handing out work either.
    """
    direction = read_direction(path)
    if direction is None or not direction.is_live(now):
        return []
    known = set(atom_ids or ())
    return [dict(item) for item in direction.focus
            if item.get("id") and item["id"] not in known]


def focus_multiplier(atom_id: str, focus: tuple[str, ...]) -> float:
    """This atom's weight multiplier under the given focus. ALWAYS >= 1.0 -- an atom the direction
    does not name keeps exactly the weight it had, so direction can only ever ADD attention.

    MUTATION (must fire): return a value below 1.0 for a non-focus atom. That would let a
    direction record make an atom harder to draw, which is a filter wearing a weight's clothes.
    """
    if not atom_id or atom_id not in focus:
        return 1.0
    rank = focus.index(atom_id)
    if rank < len(FOCUS_RANK_MULTIPLIERS):
        return FOCUS_RANK_MULTIPLIERS[rank]
    return _FOCUS_TAIL_MULTIPLIER


def focus_weights(candidates, weights, path: Path | None = None,
                  now: datetime | None = None) -> list[float]:
    """The supervisor's dial weights, biased by the current direction.

    Called with the candidate list ALREADY BUILT, so this function cannot change who is eligible
    -- only how likely each already-eligible atom is. If the two lists disagree in length the
    original weights are returned untouched, because a mismatched bias is a bug and a bug in
    advice must not be able to change a draw.
    """
    original = [float(w) for w in weights]
    try:
        focus = current_focus(path, now)
        if not focus or len(candidates) != len(original):
            return original
        return [w * focus_multiplier(str(a.get("id") or ""), focus)
                for a, w in zip(candidates, original)]
    except Exception:
        return original


def focus_was_drawn(focus: tuple[str, ...], drawn_ids) -> dict:
    """Did the PREVIOUS orientation's focus actually reach the draw?

    THE CONTROL ON THIS WHOLE MECHANISM, and the reason it is recorded every cycle rather than
    assumed. `d7d36b46a` records two soft guards composing into a no-op while an atom sat through
    1,307 unchanged draws: a steer that quietly does nothing looks identical, from the outside, to
    a steer that was taken. So every orientation writes down whether the last one moved anything,
    and a run of `drawn: []` against a non-empty focus is a defect in the steer rather than a
    quiet fact about the week.
    """
    drawn = {str(d) for d in (drawn_ids or [])}
    hit = [f for f in focus if f in drawn]
    return {
        "focus": list(focus),
        "drawn": hit,
        "steered": bool(hit),
        "note": (
            "the previous direction named work the draw then took"
            if hit else
            "the previous direction named work and NONE of it was drawn -- if this repeats, the "
            "steer is a no-op and the weight is not biting"
        ) if focus else "no previous focus to check",
    }


def append_decision(row: dict, path: Path | None = None) -> None:
    """One line on the append-only record. The seat's own writes go through here so the record
    cannot be rewritten -- only added to."""
    path = DECISIONS_PATH if path is None else path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def read_decisions(limit: int = 50, path: Path | None = None) -> list[dict]:
    """The most recent orientations, newest first. Unreadable rows are SKIPPED and counted by the
    caller rather than crashing the page -- a corrupt line must not blank the record."""
    path = DECISIONS_PATH if path is None else path
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    rows = []
    for line in reversed(lines):
        if len(rows) >= limit:
            break
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
