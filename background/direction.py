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
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from tools.here_relative_vocabulary import here_relative_phrases  # noqa: E402

DIRECTION_DIR = PROJECT_DIR / "docs" / "direction"
DIRECTION_PATH = DIRECTION_DIR / "DIRECTION.yaml"
DECISIONS_PATH = DIRECTION_DIR / "decisions.jsonl"
#: THE TRIAGE REGISTER for the self-audit list (director, 2026-10-07): every carried `wrong` item
#: gets ONE fate -- fix, fold into a class register, or accept with a reason -- instead of being
#: copied forward on every orientation. Absent means "not triaged yet" and changes nothing.
WRONG_TRIAGE_PATH = DIRECTION_DIR / "wrong_triage.yaml"
DELIVERY_FEED = PROJECT_DIR / "site" / "data" / "delivery.json"

#: THE WRITE SCOPE, and the reason "it never becomes a second writer on the tree" is a mechanism
#: rather than an intention. The delivery seat `git add`s exactly these paths and nothing else, so
#: anything the orienting session touched outside them is simply not in its commit.
WRITE_SCOPE = (
    "docs/direction/DIRECTION.yaml",
    "docs/direction/decisions.jsonl",
    # The seat must be able to obey its own refusal: "carried 7+ days untriaged" names this file
    # as the remedy, and a remedy outside the pathspec would be dropped from the seat's commit.
    "docs/direction/wrong_triage.yaml",
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

#: THE DIRECTION RECORD IS A PUBLISHED SURFACE, and until 2026-09-24 nothing told its author so.
#: `tools/generate_delivery_page.py::what_it_decided` copies `live.focus` VERBATIM into
#: `delivery.json .what_it_decided.focus[]`, and `/harness/` renders each item TWICE: once in
#: `#delivery-decided` (`renderDeliveryDecided`, "Chose") and again in `#delivery-next`
#: (`renderDeliveryNext`, the ordered list). Both regions read `f.what || f.id` and `f.why`.
#:
#: So a sentence the seat writes in a focus item's `what` or `why` has TWO homes, and a pointer
#: that says "here" in it is false from at least one of them. `site/test_a_here_relative_pointer
#: _has_one_home.py` has caught that all along -- but it runs in the site lane, hours after the
#: keystroke, and it named this exact field pair as one sentence away from the parent defect. A
#: sixty-two-hour publish outage whose blocker was a sentence in this file is what it cost to
#: find out that "hours later" is too late for the one surface the seat writes unaided.
#:
#: DERIVED FROM THE PRODUCER, NOT GUESSED, and deliberately narrow. `not_now`, `for_the_director`,
#: `thesis_read` and `wrong` are each rendered in exactly ONE region, so a pointer in them is a
#: claim the page that owns it can check -- and `what_it_got_wrong.entries[].what` writes "the row
#: above" today, truthfully. Refusing those would refuse honest prose and get this rule deleted.
#: RE-DERIVE THIS PAIR whenever `renderDeliveryNext` grows or loses a field: a new second home is
#: a new two-home field, and this list is the only thing that would not notice on its own.
_TWO_HOME_FOCUS_FIELDS = ("what", "why")

#: THE DIRECTOR'S CONCERNS LIST (director, 2026-10-04): *"Escalate with a proposal, and don't
#: wait: concerns about strategy, vision or canon intent. Raise it, propose the change or ask me to
#: investigate, then carry on with everything else. An open question to me sits in a list and never
#: blocks the queue."* `for_the_director` IS that list, and its rows are written by
#: `background/director_concerns.py` or by the orienting session. A row with no proposal is a bare
#: ask, which is the one shape the director has ruled out; a resolved row with no resolution is a
#: question that vanished without an answer anyone can read.
CONCERN_STATUSES = ("open", "answered", "withdrawn")
CONCERN_KINDS = ("strategy", "vision", "canon_intent", "reserved")


def _concern_problems(rows) -> list[str]:
    """Every reason `for_the_director` is not a usable concerns list. `None` and `[]` are both an
    empty list -- the file carried `[]` for its whole life before rows had a shape."""
    if rows is None:
        return []
    if not isinstance(rows, list):
        return ["for_the_director is not a list"]
    problems: list[str] = []
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            problems.append(
                f"for_the_director[{i}] is not a mapping -- a concern needs an id, a what, a "
                "proposal and a status, or it cannot be carried forward or answered")
            continue
        missing = [k for k in ("id", "what", "proposal")
                   if not str(row.get(k) or "").strip()]
        if missing:
            problems.append(
                "for_the_director[{}] has no {} -- {}".format(
                    i, ", ".join(missing),
                    "a concern with no proposal is a bare ask, and the director ruled those out"
                    if missing[-1] == "proposal" else "it cannot be carried forward by id"))
        rid = str(row.get("id") or "").strip()
        if rid and rid in seen:
            problems.append(f"for_the_director[{i}] repeats id {rid!r} -- ids must be unique")
        seen.add(rid)
        status = row.get("status")
        if status not in CONCERN_STATUSES:
            problems.append(f"for_the_director[{i}].status must be one of "
                            f"{', '.join(CONCERN_STATUSES)}, got {status!r}")
        elif status != "open" and not str(row.get("resolution") or "").strip():
            problems.append(f"for_the_director[{i}] is {status} with no resolution -- a closed "
                            "concern must say how it closed")
        kind = row.get("kind")
        if kind is not None and kind not in CONCERN_KINDS:
            problems.append(f"for_the_director[{i}].kind must be one of "
                            f"{', '.join(CONCERN_KINDS)}, got {kind!r}")
    return problems


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


def _two_home_pointers(record) -> list[tuple[str, list[str]]]:
    """`[(field, phrases)]` for every focus field that points somewhere relative to itself.

    ONE VOCABULARY, IMPORTED: `tools/here_relative_vocabulary.py`, the same regex and the same
    landmark exemption the deployed sweep judges the rendered page with. A second copy in
    `background/` would drift, and the drift reads as this refusal passing a sentence the site
    lane then refuses -- the seat corrects the wording it was not refused for and the page stays
    wedged.

    A LANDMARK CLEARS THE SENTENCE, which the vocabulary does and this function does not repeat.
    "directly below this headline" names what the direction is from, so it is true from both homes
    and must be ACCEPTED -- a rule that refuses its own repair gets the repair reverted.
    """
    out: list[tuple[str, list[str]]] = []
    focus = record.get("focus") if isinstance(record, dict) else None
    for i, item in enumerate(focus or []):
        if not isinstance(item, dict):
            continue
        for key in _TWO_HOME_FOCUS_FIELDS:
            value = item.get(key)
            if not isinstance(value, str):
                continue
            phrases = here_relative_phrases(value)
            if phrases:
                out.append((f"focus[{i}].{key}", phrases))
    return out


def _lane_problems(i: int, lane, known: set | None = None) -> list[str]:
    """A focus item's optional `lane` must be a lane on the maturity map.

    It is what `tick_mode.item_is_product` reads FIRST, so a prose-only focus item -- analysis that
    names no atom or path -- can still show it is product work under product-only. Checked the way
    `seat_continuation.hand_off --lane` checks it, and through the same reader: an unreadable map
    leaves the lane unchecked rather than refusing the whole record over it.
    """
    if not isinstance(lane, str) or not lane.strip():
        return [f"focus[{i}].lane must be a maturity-map lane name, got {lane!r}"]
    if known is None:
        from background import seat_continuation
        known = seat_continuation._map_lanes()
    if known and lane not in known:
        return [f"focus[{i}].lane {lane!r} is not a lane on the maturity map "
                f"({', '.join(sorted(known))})"]
    return []


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
        # The map's lanes are read ONCE per record, not once per item: `_retired_ids` reads this
        # record once per retired continuation, and per-item reads made one draw 4,210 parses.
        known = None
        for i, item in enumerate(focus):
            if not isinstance(item, dict) or not item.get("id") or not item.get("why"):
                problems.append(f"focus[{i}] needs an id and a why")
            elif item.get("lane") is not None:
                if known is None:
                    from background import seat_continuation
                    known = seat_continuation._map_lanes()
                problems.extend(_lane_problems(i, item["lane"], known))
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
    wrong = record.get("wrong")
    if wrong is not None and not isinstance(wrong, list):
        problems.append("wrong is not a list")
    else:
        # AN EMPTY SELF-AUDIT ROW IS THE ONE FAILURE THIS SECTION CANNOT SURVIVE, and until
        # 2026-09-03 it was the only section of the record with no clause here at all. `focus` and
        # `not_now` are both checked field by field; `wrong` was accepted in any shape, so five
        # rows of `{}` would have validated, been recorded, been published, and read from outside
        # exactly like five errors honestly declared. The director reported seeing that shape. He
        # had not -- twenty consecutive committed records carry a populated `what` in every row --
        # but nothing in this tree could have told him apart from a human reading the file, which
        # is the same thing as the control not existing. `corrected` is required as a BOOLEAN and
        # not merely present: it is the field that makes the seat correctable, and a missing one
        # reads as "not corrected" while an absent one reads as nothing at all.
        for i, item in enumerate(wrong or []):
            if not isinstance(item, dict) or not str(item.get("what") or "").strip():
                problems.append(
                    f"wrong[{i}] has no what -- an empty self-audit row is indistinguishable "
                    "from an honest one and records nothing"
                )
            elif not isinstance(item.get("corrected"), bool):
                problems.append(
                    f"wrong[{i}] needs corrected: true|false -- an error with no correction "
                    "state cannot be graded next stretch"
                )
    problems.extend(_concern_problems(record.get("for_the_director")))
    forbidden = sorted(_forbidden_keys_in(record))
    if forbidden:
        problems.append(
            "the record carries target-shaped keys {}: direction may say WHAT TO WORK ON and "
            "never WHAT COUNTS AS SUCCESS (R12, and THE_DELIVERY_SEAT.md section 2)".format(
                ", ".join(repr(k) for k in forbidden))
        )
    for field_path, phrases in _two_home_pointers(record):
        problems.append(
            "{} says {} and has TWO homes on /harness/ -- #delivery-decided and #delivery-next "
            "both render it -- so the direction it claims is wrong from at least one of them. "
            "Name the landmark the direction is FROM, which is true from both.".format(
                field_path, ", ".join(repr(p) for p in phrases))
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


def focus_was_drawn(focus: tuple[str, ...], drawn_ids, *, atom_ids=None, window=None) -> dict:
    """Did the PREVIOUS orientation's focus actually reach the draw?

    THE CONTROL ON THIS WHOLE MECHANISM, and the reason it is recorded every cycle rather than
    assumed. `d7d36b46a` records two soft guards composing into a no-op while an atom sat through
    1,307 unchanged draws: a steer that quietly does nothing looks identical, from the outside, to
    a steer that was taken. So every orientation writes down whether the last one moved anything,
    and a run of `drawn: []` against a non-empty focus is a defect in the steer rather than a
    quiet fact about the week.

    AND FOR A YEAR OF CYCLES IT ASKED ONLY HALF THE QUESTION. Focus is two classes reached by two
    different mechanisms -- an ATOM by the dial-weight bias, a LANE 0 slug by `delivery_lane` --
    and the caller passed only the atom tracker, whose key space cannot contain a slug. The
    verdict was a disjunction over a mixed subject, so the class with no channel folded silently
    into the other class's pass: 11 orientations, 2-4 slugs each, `steered: True` every time, a
    slug in `drawn` never. `by_class` is the repair, and it is reported SEPARATELY because that is
    the only shape in which one channel dying is visible while the other still works.

    `atom_ids` is the map's id set. Without it the split cannot be made and `by_class` is absent
    rather than guessed -- an unavailable check reports itself unavailable (R15), it does not
    report a pass.

    `window` IS WHAT `drawn_ids` WAS MEASURED OVER, and this function cannot derive it: the caller
    chooses the horizon and hands over a finished set. It is stated in the verdict because the
    brief carries a SECOND drawn-work reading -- every Lane 0 item drawn in the last day, landed
    or not -- and for four stretches the pair sat side by side with neither saying what it covered
    and one of them named for a population it did not hold. A caller that does not say gets
    "AN UNSTATED WINDOW" on the face of the verdict rather than a blank: an unstated window is a
    finding about the caller, and a verdict that keeps quiet about it will be read as the stretch.
    """
    drawn = {str(d) for d in (drawn_ids or [])}
    hit = [f for f in focus if f in drawn]
    stated = str(window) if window else "AN UNSTATED WINDOW -- the caller did not say"
    out = {
        "focus": list(focus),
        "drawn": hit,
        "window": stated,
        "steered": bool(hit),
        "note": (
            "the previous direction named work the draw then took"
            if hit else
            "the previous direction named work and NONE of it was drawn -- if this repeats, the "
            "steer is a no-op and the weight is not biting"
        ) if focus else "no previous focus to check",
    }
    # ON THE `note` TOO, AND NOT ONLY IN ITS OWN KEY. The note is the sentence that gets quoted,
    # rendered and pasted; a window that lives only in a sibling key travels nowhere with it.
    out["note"] += " (measured over {}; this is the PREVIOUS FOCUS, not every drawn item)".format(
        stated)
    if atom_ids is not None:
        known = {str(a) for a in atom_ids}
        out["by_class"] = {
            cls: {"focus": members, "drawn": [f for f in members if f in drawn],
                  "steered": any(f in drawn for f in members)}
            for cls, members in (("atom", [f for f in focus if f in known]),
                                 ("lane_0", [f for f in focus if f not in known]))
            if members
        }
    return out


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


def wrong_rows(row: dict) -> list[dict]:
    """One recorded orientation's self-audit, as `{what, corrected}`, in BOTH stored shapes.

    THE SHAPE CHANGED ON 2026-09-03 AND THE OLD ROWS ARE NOT MIGRATED. Until then the seat wrote
    `wrong` as a list of bare strings, dropping `corrected` at the first hop out of
    `DIRECTION.yaml`; 69 recorded orientations carry that shape and they are an append-only
    record, so they are read rather than rewritten. A legacy row's correction state is genuinely
    unknown -- not false -- and this returns `None` for it, because "we did not record whether
    this was fixed" and "this was not fixed" are different claims and only one of them is true.
    """
    out: list[dict] = []
    for item in row.get("wrong") or []:
        if isinstance(item, dict):
            what = str(item.get("what") or "").strip()
            corrected = item.get("corrected")
            out.append({"what": what,
                        "corrected": corrected if isinstance(corrected, bool) else None})
        elif isinstance(item, str) and item.strip():
            out.append({"what": item.strip(), "corrected": None})
    return out


# --------------------------------------------------------------------------- #
# The self-audit's triage: count PROBLEMS, not rows, and stop copying them      #
# --------------------------------------------------------------------------- #
#
# Director, 2026-10-07: *"The 'what it got wrong' list reads 987 open, 82 corrected, and that
# number misleads. It counts rows, not problems: each orientation copies every unfixed item
# forward ... Count distinct items, not rows. ... Triage every carried item once ... Then apply
# that as a rule: an item carried unchanged across, say, a week of orientations must be triaged
# rather than copied forward again."*

#: THE CARRY LIMIT, in days -- the director's own figure ("say, a week"), a policy dial and not a
#: measurement. At the three-hour cadence a week is ~56 orientations: long enough that an item
#: still listed has outlived every stretch's chance to fix it, short enough that the list cannot
#: regrow to hundreds of copies before the rule bites. Change it here and nowhere else.
WRONG_CARRY_TRIAGE_DAYS = 7

WRONG_FATES = ("fix", "fold", "accept")

#: The seat's provenance prefix -- "THE MACHINE'S, CARRIED.", "MINE, NEW.", "THE MACHINE'S.",
#: "MINE, NEW, now corrected." (all seen in decisions.jsonl) -- flips from NEW to CARRIED while
#: the problem stays the same, so it is not part of identity. An upper-case lead of two or more
#: letters, an optional short comma tail, then a full stop.
_WRONG_PREFIX = re.compile(r"^\s*[A-Z][A-Z'’ ]+(?:,[^.]{0,40})?\.\s+")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_LABEL_SENTENCE = re.compile(r"^(still open|new|corrected|now corrected)\b[^.]{0,30}\.$", re.I)


def wrong_first_sentence(what: str) -> str:
    """The fallback identity of an untriaged item: its first sentence, provenance prefix stripped,
    case and whitespace folded. A carried item grows a "23:24: unchanged." tail every stretch, so
    its WHOLE text changes each time while its first sentence -- the problem -- does not."""
    text = _WRONG_PREFIX.sub("", str(what or "").strip(), count=1)
    sentences = [s for s in _SENTENCE_END.split(text) if s.strip()] or [""]
    # Older rows lead with a short label sentence ("Still open.", "New.", "My own instruction."),
    # or "Still open, fifth stretch.", which as an identity would merge every row carrying it into
    # one problem. Skip those.
    while len(sentences) > 1 and (len(sentences[0].split()) < 4
                                  or _LABEL_SENTENCE.match(sentences[0])):
        sentences.pop(0)
    return re.sub(r"\s+", " ", sentences[0]).strip().rstrip(".!?").lower()


def read_wrong_triage(path: Path | None = None) -> tuple[list[dict] | None, str]:
    """`(items, "")` for a readable register, `(None, why)` otherwise.

    ABSENT IS NOT AN ERROR: before the register exists everything behaves as it did, and `why`
    says so. UNREADABLE is reported because the callers differ: the panel fails open on it, the
    write-time check refuses on it.
    """
    path = WRONG_TRIAGE_PATH if path is None else path
    if not path.is_file():
        return None, f"no triage register at {path.name}: nothing is triaged, nothing is retired"
    try:
        import yaml
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - every unreadable shape is one answer: unreadable
        return None, f"{path.name} is unreadable ({type(exc).__name__}: {exc})"
    items = doc.get("items") if isinstance(doc, dict) else None
    if not isinstance(items, list):
        return None, f"{path.name} has no `items:` list"
    return [i for i in items if isinstance(i, dict)], ""


def triage_entry_problems(item: dict) -> list[str]:
    """Why one register entry cannot be used. A retirement with no reason is one nobody can
    review, and an entry with no `match` phrase can never claim an item."""
    tid = item.get("id") or "<no id>"
    out = []
    match = item.get("match")
    if not isinstance(match, list) or not [m for m in match if str(m).strip()]:
        out.append(f"triage item {tid!r} has no match phrases, so it can claim no wrong entry")
    fate = item.get("fate")
    if fate not in WRONG_FATES:
        out.append(f"triage item {tid!r} has fate {fate!r}, not one of {'/'.join(WRONG_FATES)}")
    elif fate in ("fold", "accept") and not str(item.get("reason") or "").strip():
        out.append(f"triage item {tid!r} is {fate} with no reason -- a retirement must say why")
    elif fate == "fix" and item.get("status") not in ("open", "already_fixed"):
        out.append(f"triage item {tid!r} is fix with status {item.get('status')!r}, "
                   "not open|already_fixed")
    return out


def triage_is_retired(item: dict) -> bool:
    """Retired = never listed again: folded, accepted, or a fix already made."""
    fate = item.get("fate")
    return fate in ("fold", "accept") or (fate == "fix" and item.get("status") == "already_fixed")


def triage_match(what: str, triage) -> dict | None:
    """The register entry this item belongs to: the first whose `match` phrase occurs in `what`,
    case-insensitively. PHRASES, not the whole text, because the text grows a tail every stretch."""
    low = str(what or "").lower()
    for item in triage or ():
        for phrase in item.get("match") or ():
            phrase = str(phrase).strip().lower()
            if phrase and phrase in low:
                return item
    return None


def wrong_problem_key(what: str, triage) -> str:
    """One problem's identity: `triage:<id>` when the register claims it, else `text:<first
    sentence>`."""
    hit = triage_match(what, triage)
    if hit is not None:
        return f"triage:{hit.get('id')}"
    return "text:" + wrong_first_sentence(what)


def wrong_first_seen(rows, triage) -> dict[str, datetime]:
    """Each problem's earliest appearance over recorded orientations, by `wrong_problem_key`."""
    seen: dict[str, datetime] = {}
    for row in rows or ():
        at = _iso(row.get("at"))
        if at is None:
            continue
        for item in wrong_rows(row):
            key = wrong_problem_key(item["what"], triage)
            if key not in seen or at < seen[key]:
                seen[key] = at
    return seen


#: Director, 2026-10-10: *"Since 7 October about 30% of commits have touched world or supplier
#: code, but the supplier gets only 1-3 a day against the world's 15-17. My priority order is mostly
#: supplier work ... every stretch's focus carries at least two supplier items from the priority
#: order ... World fidelity work continues, but only where it blocks a supplier result."*
FOCUS_SIDES = ("supplier", "world", "other")
SUPPLIER_FOCUS_ITEMS_REQUIRED = 2


def focus_balance_problems(record) -> list[str]:
    """Every reason a NEW record's focus breaks the director's supplier-first balance.

    BINDS THE WRITE, NEVER THE READ, like `wrong_triage_problems`: `read_direction` returning None
    would strip every draw of its focus, so a record already on file -- including every record
    written before this rule -- stays readable, and only the seat's next write is refused.

    Each focus item says which side it serves (`side`: supplier, world or other). At least two are
    `supplier`. A `world` item names in `unblocks` the supplier result it is blocking, because world
    fidelity work is admitted only where it blocks one.
    """
    if not isinstance(record, dict) or not isinstance(record.get("focus"), list):
        return []
    problems: list[str] = []
    supplier = 0
    for i, item in enumerate(record["focus"]):
        if not isinstance(item, dict):
            continue
        side = item.get("side")
        if side not in FOCUS_SIDES:
            problems.append(f"focus[{i}] needs a side ({', '.join(FOCUS_SIDES)}) -- the director "
                            "reads the balance of the focus from it")
            continue
        if side == "supplier":
            supplier += 1
        if side == "world" and not str(item.get("unblocks") or "").strip():
            problems.append(f"focus[{i}] is world work with no `unblocks` -- name the supplier "
                            "result it blocks; world fidelity is admitted only where it blocks one")
    if supplier < SUPPLIER_FOCUS_ITEMS_REQUIRED:
        problems.append(f"focus carries {supplier} supplier item(s); at least "
                        f"{SUPPLIER_FOCUS_ITEMS_REQUIRED} are required from the priority order "
                        "(billing accuracy, forward customer value on held-back history, "
                        "per-customer decisions, levers in merit order)")
    return problems


def wrong_triage_problems(record, *, triage_path: Path | None = None,
                          decisions_path: Path | None = None,
                          now: datetime | None = None) -> list[str]:
    """Every `wrong` entry the triage forbids writing, each as a refusal naming its reason.

    WRITE-TIME ONLY, deliberately not inside `validate`: `read_direction` validates on READ, and a
    record that was legal when written must not lose its focus to a register edited afterwards.

    Two refusals, both meaning "stop copying this forward":
      * the entry matches a RETIRED triage item (fold, accept, fix already_fixed);
      * the entry is still open, matches NO triage item, and its problem first appeared in an
        orientation `WRONG_CARRY_TRIAGE_DAYS` or more before this one.
    An entry marked `corrected: true` is exempt from the second -- closing an item is the opposite
    of carrying it. With NO register file nothing is refused, exactly as before the register.
    """
    path = WRONG_TRIAGE_PATH if triage_path is None else triage_path
    triage, why = read_wrong_triage(path)
    if triage is None:
        return [f"wrong cannot be graded against the triage register: {why}"] \
            if path.is_file() else []
    problems = [p for item in triage for p in triage_entry_problems(item)]
    if problems:
        return problems
    wrong = record.get("wrong") if isinstance(record, dict) else None
    if not isinstance(wrong, list) or not wrong:
        return []
    now = now or _iso(record.get("oriented_at")) or datetime.now(timezone.utc)
    first_seen = None
    for i, entry in enumerate(wrong):
        if not isinstance(entry, dict):
            continue
        what = str(entry.get("what") or "")
        hit = triage_match(what, triage)
        if hit is not None:
            if triage_is_retired(hit):
                fate = hit.get("fate")
                if fate == "fix":
                    fate = f"fix, already_fixed by {hit.get('fixed_by') or 'an unnamed commit'}"
                problems.append(
                    f"wrong[{i}] is the retired triage item {hit.get('id')!r} (fate {fate}): "
                    f"{hit.get('reason') or hit.get('problem') or 'no reason recorded'} -- drop "
                    "it from wrong; docs/direction/wrong_triage.yaml already holds its fate")
            continue
        if entry.get("corrected") is True:
            continue
        if first_seen is None:
            first_seen = wrong_first_seen(read_decisions(limit=10**9, path=decisions_path),
                                          triage)
        since = first_seen.get(wrong_problem_key(what, triage))
        if since is not None and (now - since).total_seconds() >= WRONG_CARRY_TRIAGE_DAYS * 86400:
            problems.append(
                f"wrong[{i}] carried {WRONG_CARRY_TRIAGE_DAYS}+ days untriaged (first listed "
                f"{since.date().isoformat()}: {wrong_first_sentence(what)[:120]!r}): triage it "
                "into docs/direction/wrong_triage.yaml (fix / fold / accept) rather than copy it "
                "forward")
    return problems
