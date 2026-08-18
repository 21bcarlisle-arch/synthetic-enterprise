#!/usr/bin/env python3
"""When a Knowledge page is due for review — one rule, read by the page and by the control.

THE REQUIREMENT (brief §4, Knowledge): "Every page carries a last-reviewed date, and flips to
a visible 'review due' state past a threshold. **Staleness must be visible on the page, not
discovered by a reader.**"

THE THRESHOLD IS PER TOPIC, NOT GLOBAL. Ofgem resets the price cap quarterly, so a year-old
cap page is not stale, it is wrong; the merit order is structural economics and does not move
from year to year. A single global threshold would either nag about the second or stay silent
about the first. The classes and their day counts are DATA, in
`site/data/knowledge_wholesale.json` under `review_policy`, so changing the policy is an edit
to the record rather than to code.

FAIL-CLOSED, AND THIS IS THE PROPERTY THAT MATTERS (R15 killer pattern 2, FAIL-OPEN):

    a page with NO recorded review is DUE, never fresh.

Seven of the eight topics have never been reviewed. If "no date" read as "fine", the control
would be decorative on the day it shipped, and the section would look maintained precisely
because nobody had ever maintained it. An unparseable date, an unknown rate class and a
missing policy all resolve the same way — DUE — because every one of them means nobody can
say when this was last checked.

Deliberately NOT here: any notion of a page being "good". This answers one question — when
was this last checked against the world, and is that long enough ago to warn a reader.
"""
from __future__ import annotations

from datetime import date, datetime

DUE = "due"
FRESH = "fresh"
NEVER = "never"

#: Used only when the record carries no policy at all. The tightest class, because guessing
#: generously is how a fail-open gets introduced by accident.
_FALLBACK_DAYS = 92


def _parse(value) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value.strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def threshold_days(rate_of_change, policy: dict | None) -> int:
    """Days this class may go unchecked. An unknown class gets the tightest threshold."""
    table = (policy or {}).get("threshold_days") or {}
    value = table.get(rate_of_change)
    return value if isinstance(value, int) and value > 0 else _FALLBACK_DAYS


def review_state(topic: dict, policy: dict | None = None, today: date | None = None) -> dict:
    """The review state of one topic: `never`, `due`, or `fresh`, with the numbers behind it.

    `today` is injectable so the control can drive the boundary rather than wait for it.
    """
    today = today or date.today()
    reviewed = (topic or {}).get("reviewed") or {}
    last = _parse(reviewed.get("last_verified"))
    days_allowed = threshold_days((topic or {}).get("rate_of_change"), policy)

    if last is None:
        # WRITTEN is not REVIEWED, and the difference is the whole point. A page can be
        # written today from what its author already knew and still never have been checked
        # against the published source. Saying "never reviewed" on a page finished this
        # morning looks like a bug unless the page also says when it was written -- so both
        # are carried, and only the CHECK moves the state.
        written = reviewed.get("written")
        return {
            "state": NEVER, "last_verified": None, "written": written,
            "days_allowed": days_allowed, "age_days": None, "overdue_by": None,
            "label": "Never checked against the source",
            "detail": (
                (f"Written {written}. " if written else "")
                + "Nobody has recorded checking it against the published source since."
            ),
        }

    age = (today - last).days
    overdue = age - days_allowed
    if overdue > 0:
        return {
            "state": DUE, "last_verified": reviewed.get("last_verified"),
            "days_allowed": days_allowed, "age_days": age, "overdue_by": overdue,
            "label": "Review due",
            "detail": (f"Last checked {age} days ago; this subject is meant to be re-checked "
                       f"every {days_allowed} days."),
        }
    return {
        "state": FRESH, "last_verified": reviewed.get("last_verified"),
        "days_allowed": days_allowed, "age_days": age, "overdue_by": None,
        "label": f"Reviewed {reviewed.get('last_verified')}",
        "detail": (f"Checked {age} days ago against a {days_allowed}-day threshold."
                   + (f" Source: {reviewed['source']}." if reviewed.get("source") else "")),
    }


def states_for(feed: dict, today: date | None = None) -> dict[str, dict]:
    policy = (feed or {}).get("review_policy")
    return {t["id"]: review_state(t, policy, today) for t in (feed or {}).get("topics") or []}
