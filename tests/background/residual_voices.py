"""The residual disposition has TWO VOICES, and `evidence == ""` was both of them at once.

WHY THIS IS SHARED AND NOT COPIED. `_nothing_answered` was given a reason per branch on 2026-09-18
(commit `2984864c7`) because the residual is the one disposition reached by every route that failed
to conclude, so it is the one place where "the tree said no" and "the tree was never asked" arrived
wearing the same clothes. That repair left EIGHT legs across FOUR suites asserting the silence it
abolished — `assert ...["evidence"] == ""` — and every one of them went red while the code got more
honest, which is the backwards direction CLAUDE.md names. Four files re-keyed to the same property by
four private copies of this predicate is how the next widening drifts in three of them and nobody
notices; the point of the repair was that ONE function decides which voice it used.

WHAT EACH VOICE MEANS TO A READER, because that is the whole distinction and it is not cosmetic:

  * `looked_and_found_nothing` — git WAS asked, on paths this row actually named, over this row's
    own window, and answered nothing. This is the only residual that means **workable, draw it
    again**.
  * `could_not_ask` — the query could not be built or the asking broke. A louder disposition may be
    TRUE and was lost, so a reader who acts on "nothing landed" here may redo work that exists.

They want opposite actions, which is what made conflating them expensive rather than untidy.

THESE ARE STRICTLY STRONGER THAN THE `== ""` THEY REPLACE, and that is the test of whether this is a
repair or a widening to green: the empty string was satisfied by BOTH voices, so it could not express
the distinction at all. A suite that asserted it graded nothing once the residual learned to speak.

KEYED TO THE PROPERTY, NEVER TO THE SENTENCE. The discriminator is which QUESTION the residual
answers, not today's wording: `CANNOT ANSWER` is the declared prefix every unanswerable branch
carries, and the asked/none pair is what the answered branch carries. A reworded sentence that kept
both properties keeps these green; one that collapsed the voices reds them, which is the direction
that matters.
"""
from __future__ import annotations

from background import delivery_lane as dl

#: The declared prefix `_nothing_answered` puts on every branch that could not ask. Named once here
#: rather than spelled in each caller, so the four suites cannot drift apart on the spelling.
CANNOT_ANSWER = "CANNOT ANSWER"


def looked_and_found_nothing(verdict: dict) -> bool:
    """The residual that ASKED and got nothing — the one reading meaning 'workable, draw again'."""
    evidence = verdict.get("evidence", "")
    return (verdict.get("disposition") == dl.NOT_DONE
            and CANNOT_ANSWER not in evidence
            and "asked git" in evidence and "none." in evidence)


def could_not_ask(verdict: dict) -> bool:
    """The residual that could NOT ask — a louder disposition may be true and was lost."""
    return (verdict.get("disposition") == dl.NOT_DONE
            and CANNOT_ANSWER in verdict.get("evidence", ""))
