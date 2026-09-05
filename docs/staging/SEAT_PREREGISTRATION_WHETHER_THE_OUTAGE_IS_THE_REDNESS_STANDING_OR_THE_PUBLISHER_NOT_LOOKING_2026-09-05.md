**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: is the outage the redness STANDING, or the publisher NOT LOOKING?

**Filed:** 2026-09-05, delivery seat, closing the fifth turn on the Lane 0 direction *"split the
RED TEST bucket by failing node id"*. **Written before the decomposition below was computed once.**
The two quantities it needs (`span_s`, `outage_s`) have been printed by
`tools/commit_refusal_attribution.py` for four turns; their *difference* has never been taken, and
is not taken in this document.

## Why this question and not the one that was handed on

The split's finding closes by naming *"whether the cost is the retry-into-a-standing-red behaviour
rather than the redness itself"*. As phrased that is not answerable, and saying so is the first
half of this pre-registration: **retrying more often cannot shorten a standing red.** While a red
stands the publisher cannot land however often it tries, so the retry rhythm can only ever add a
tail — bounded by one inter-attempt gap — to an outage the redness already owns. A question whose
answer is fixed by construction is not a measurement.

The decomposable question underneath it is:

> Of an episode's outage, how much is time the red **demonstrably stood**, and how much is time
> the publisher **had not yet looked again**?

## The definitions, stated before the split rather than inferred from it

For one bounded cost-definition episode:

- **span** = last refused attempt − first refused attempt. Every minute of it is bracketed by two
  observed refusals, so it is a **lower bound on how long the redness stood**.
- **trailing gap** = outage − span = the landing attempt − the last refused attempt. This is one
  inter-attempt gap by construction. The red may have cleared at any instant inside it, so it is an
  **upper bound on time lost to the retry rhythm** and never an estimate of it.

Neither is the quantity itself. They bracket it from opposite sides, and the whole answer is which
bracket is wide.

## THE TRAP, named now so the answer cannot be manufactured by it

**A single-cycle episode has span 0 by construction**, so its outage is 100% trailing gap. Folding
those in would return "the retry rhythm is the whole cost" as an arithmetic identity of the episode
definition, not as an observation about the publisher. The measurement therefore reports
single-cycle and multi-cycle episodes **separately and never pooled**, and the headline is the
multi-cycle set. The single-cycle count is reported because it is real cost — but it is cost the
rhythm owns by definition, and it must be labelled as such.

## Predictions, and what would refute them

1. **The redness dominates.** Over multi-cycle bounded episodes, total trailing gap will be
   **under 25%** of total outage. Refuted at >50%, where the rhythm is the story and the cadence is
   a real lever.
2. **The tail is one cycle, not a queue.** Median trailing gap will be within a factor of two of
   the median inter-attempt gap (~3300s ≈ 0.9h). A median several multiples of that would mean the
   episode boundaries are not what this module believes they are.
3. **The single-cycle set is a minority of outage.** Under 25% of all bounded outage. If it is the
   majority, the honest headline is that most cost is one missed cycle each time — a different
   finding with a different remedy from anything measured on this direction so far.

Written in this order deliberately: 1 and 3 can both be false, and if they are, the retry rhythm
is the finding and the four preceding turns were looking at the wrong half.

## Analytic controls — what a wrong instrument, not a wrong world, would show

- **Trailing gap ≥ 0 for every bounded episode.** A negative value means `outage_s` and `span_s`
  are measured from different anchors, and the whole decomposition is void.
- **Trailing gap ≤ the maximum observed inter-attempt gap (19,454s).** It is *one* gap by
  construction. Any episode exceeding it means a landing was missed and the episode was closed on
  the wrong cycle.
- **span + trailing gap = outage, exactly, per episode.** Not asserted as a tautology of the
  arithmetic but as a check that both are read from the same episode record — the index-alignment
  defect this module has already had once, in `subjects` against `cause_sequence`.
- **Censored episodes stay excluded**, as everywhere else on this direction: an open wedge has no
  terminating landing, so it has no trailing gap at all, and it is the episode most likely to be
  the longest.

## What no outcome of this licenses

A cadence change. Prediction 1 being *refuted* would establish that the tail is large, not that
shortening it is free: the inter-attempt gap is also what bounds how hard the publisher hammers a
tree several lanes are writing to. The action on a refutation is a further question about that
cost, not a dial move — and this document does not pre-authorise one.
