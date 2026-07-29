"""NEVER ASK WITHOUT RECOMMENDING — the outbound half of the 2026-07-29 ruling.

PURPOSE. The director, 2026-07-29 (`docs/staging/done/from_rich_20260729_182313.md`,
verbatim): *"You asked three questions and recommended nothing. Two of them weren't
mine to answer ... From now: never ask without recommending, and default to acting
on your own recommendation and telling me what you did. 'Here's what I'm doing
unless you object' — not 'which would you like?' Only real money, real people,
safety controls, and public claims in the company's name need me first.
Forgiveness, not permission."*

WHY A MECHANISM AND NOT A LINE OF PROSE. MAKE_IT_STICK (2026-07-12) is explicit:
every rule that DECAYED here was an exhortation, every rule that HELD was a
mechanism. "Ask better" is an exhortation. This module is the mechanism, and it
sits on the ONE channel the director actually reads — NTFY. A bare ask cannot
reach his phone, because the send raises before it is posted.

WHAT IT GUARANTEES.
  1. A message that ASKS the director for a decision and offers NO recommendation
     never leaves the machine.
  2. The carve-out is exactly the ruling's own list — and it is not re-enumerated
     here. `one_way_door.classify_action` is already this project's single source
     of truth for "does this need him first?", so the reserved categories stay in
     ONE place (DON'T ACCRETE). Ask bare about real money / real people / safety
     controls / public claims: allowed, that is what he reserved.
  3. FAIL-LOUD, NEVER FAIL-SILENT (R15). A blocked message RAISES. It is never
     dropped, swallowed or silently rewritten — a lost alert would be a worse
     defect than the one being fixed.

WHY BLOCKING IS SAFE HERE. Measured before wiring, not assumed: there are 6
`send_ntfy` call sites in `background/` + `tools/`, and NONE contains a question
mark in its message. The blast radius of the blocking form is empirically zero on
today's callers; it constrains only NEW asks, which is the point.

DELIBERATELY OVER-INCLUSIVE. `_looks_like_an_ask` treats any question mark as an
ask. That is the same doctrine `one_way_door`'s keyword lists use: a false positive
costs one rephrase (add the recommendation, or drop the question mark), a false
negative defeats the whole guard. Asking rhetorically and recommending nothing is
the exact habit being removed.
"""
from __future__ import annotations

import re

from background.one_way_door import classify_action


class RecommendationRequired(RuntimeError):
    """Raised when an outbound message asks without recommending.

    Deliberately an exception and not a silently-dropped send: the caller learns
    immediately, at the call site, with the fix in the message text.
    """


# An ask is a question mark, or one of the stock ways of requesting a decision
# without punctuating it as a question ("let me know which", "please advise").
_QUESTION_MARK = re.compile(r"\?")
_DECISION_REQUEST = re.compile(
    r"\b("
    r"which would you (like|prefer)"
    r"|let me know"
    r"|please advise"
    r"|your call"
    r"|awaiting (your|a) (decision|steer|answer|ruling)"
    r"|shall i\b"
    r"|should i\b"
    r"|do you want"
    r"|would you like"
    r"|confirm whether"
    r"|thoughts\b"
    r")",
    re.IGNORECASE,
)

# A recommendation is a stated intention to act, or an explicit recommendation.
# "Here's what I'm doing unless you object" — the director's own phrasing — and
# its ordinary variants.
_RECOMMENDATION = re.compile(
    r"\b("
    r"recommend(ing|ation)?\b"
    r"|unless you object"
    r"|unless told otherwise"
    r"|unless you say otherwise"
    r"|here'?s what i'?m doing"
    r"|i'?m (doing|going to|proceeding|acting)"
    r"|i will\b"
    r"|i'?ve decided"
    r"|my recommendation"
    r"|proceeding with"
    r"|default(ing)? to\b"
    r"|propos(e|ing|al)\b"
    r"|plan:"
    r"|decision:"
    r"|plan is to"
    r")",
    re.IGNORECASE,
)


def _looks_like_an_ask(message: str) -> bool:
    return bool(_QUESTION_MARK.search(message) or _DECISION_REQUEST.search(message))


def _carries_a_recommendation(message: str) -> bool:
    return bool(_RECOMMENDATION.search(message))


def _is_director_reserved(message: str) -> bool:
    """Is this an ask the director actually reserved to himself?

    Delegated wholesale to `one_way_door.classify_action` so the reserved list
    lives in exactly one place. A classification error must not silence the
    guard's own failure, so an exception here resolves to "reserved" (permit the
    ask): the cost of permitting one extra question is a message the director can
    ignore, whereas the cost of raising here is a crash on the alert path.
    """
    try:
        return classify_action(message, uncertain=True).is_one_way_door
    except Exception:
        return True


def check_message(message: str) -> None:
    """Raise `RecommendationRequired` if `message` asks without recommending.

    Returns None (permits the send) when the message does not ask, when it asks
    AND recommends, or when the ask falls in a director-reserved category.
    """
    if not isinstance(message, str) or not message.strip():
        return
    if not _looks_like_an_ask(message):
        return
    if _carries_a_recommendation(message):
        return
    if _is_director_reserved(message):
        return
    raise RecommendationRequired(
        "This message ASKS the director for a decision and RECOMMENDS nothing "
        "(director ruling, 2026-07-29: 'never ask without recommending ... "
        "\"Here's what I'm doing unless you object\" — not \"which would you "
        "like?\"'). Decide it yourself on the evidence you have, state what you "
        "are doing and why, and send that instead. Only real money, real people, "
        "safety controls and public claims in the company's name may be asked "
        "bare. Blocked message was: {!r}".format(message[:300])
    )
