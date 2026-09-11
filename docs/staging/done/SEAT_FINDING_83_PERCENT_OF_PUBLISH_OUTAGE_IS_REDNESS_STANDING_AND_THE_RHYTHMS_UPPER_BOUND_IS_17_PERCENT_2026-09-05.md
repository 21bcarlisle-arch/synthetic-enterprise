**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# 83% of publish outage is redness STANDING; the retry rhythm's UPPER bound is 17%

**Measured:** 2026-09-05, delivery seat, against the shared tree's live
`docs/observability/sim-runner-log.md` (233,053 lines; 446 publish cycles in the observable
window). The committed copy in a clean worktree is truncated at 2026-07-17 and the module refuses
it with exit 2, so this figure is re-derived by running
`tools/commit_refusal_attribution.py --log` against the shared tree's copy.

**The pre-registration is
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_OUTAGE_IS_THE_REDNESS_STANDING_OR_THE_PUBLISHER_NOT_LOOKING_2026-09-05.md`
(filed as 986499b1f).** It was read in full before the difference was taken, and its three
predictions and four analytic controls are graded below as written. This document does not restate
its definitions; it answers them.

## The answer

**The redness is the wide bracket. The rhythm is not the story.**

| Multi-cycle bounded episodes — **the headline** | | |
|---|---:|---:|
| episodes | 26 | |
| total outage | 228.7h | |
| **span** — redness demonstrably stood, LOWER bound | **189.5h** | **82.9%** |
| **trailing gap** — retry rhythm, UPPER bound | **39.2h** | **17.1%** |
| median trailing gap | 1.2h | |
| max trailing gap | 8.1h | |

| Single-cycle episodes — **reported apart, never pooled** | | |
|---|---:|---:|
| episodes | 12 | |
| total outage | 10.9h | |
| span | 0.0h | 0% *by construction* |
| trailing gap | 10.9h | 100% *by construction* |
| share of ALL 239.6h of bounded outage | | **4.6%** |

The single-cycle 100% is an arithmetic identity of the episode definition, not an observation about
the publisher. It is here because the cost is real, and it is labelled because pooling it into the
headline would have manufactured the opposite conclusion — which is why the pre-registration named
that trap before the number existed.

## The three predictions, graded as written

1. **"The redness dominates" — trailing gap under 25% of multi-cycle outage. HELD at 17.1%.**
   Refutation was set at >50%; the observed value is a third of that.
2. **"The tail is one cycle, not a queue" — median trailing gap within a factor of two of the
   median inter-attempt gap. HELD.** Median trailing gap 4,290s against a median inter-attempt gap
   of 3,240s: a ratio of **1.32**. The document guessed the gap at "~3300s ≈ 0.9h" and it is
   3,240s, so the episode boundaries are what the module believes they are.
3. **"The single-cycle set is a minority of outage" — under 25% of all bounded outage. HELD at
   4.6%.**

All three held, so nothing here refutes the four turns that preceded it. **1 and 3 were written so
that both could be false**, and the reading in which the retry rhythm is the finding is the one the
evidence declines.

**And 17.1% is generous to the rhythm, not to this conclusion.** A trailing gap is time the
publisher had not looked again — which includes intervals where the publisher was not attempting at
all. The log contains inter-attempt gaps of 40.0h (2026-08-15 17:48 → 2026-08-17 09:46) and 28.4h
(2026-08-20 18:34 → 2026-08-21 22:55) against a 0.9h median, and the two widest trailing gaps in
the set (8.1h and 5.4h) are of that kind rather than of the cadence. So the cost attributable to
the *cadence* is materially below 17.1%, and 17.1% is the number to quote precisely because it is
the bound that cannot be argued down.

## What this decides

The direction asked which bracket is wide, because that decides whether a future mechanism
addresses the redness or the cadence. **It is the redness.** A mechanism that made the publisher
retry faster would be competing for at most 17.1% of multi-cycle outage, and a mechanism that
shortens or prevents standing reds is competing for 82.9%.

**This licenses no cadence change and the pre-registration pre-refused one.** Prediction 1 held, so
the case for touching the inter-attempt gap is weaker than it was before the measurement, not
stronger — and the gap is also what bounds how hard the publisher hammers a tree several lanes are
writing to.

## The controls, and the one that was wrong

Three of the four pre-registered controls pass on all 38 bounded episodes. The fourth does not
work, in either of its two readings, and saying so is the second finding here.

- **Trailing gap ≥ 0 on every bounded episode.** PASS, 38 of 38.
- **span + trailing gap = outage from the same episode record.** PASS, 38 of 38 — and not as a
  tautology of the differencing: the gap is re-derived from the episode's own `last_at` and
  `recovery_at`, so an outage and a span anchored at different starts disagree here instead of
  cancelling.
- **Censored episodes excluded.** PASS. The open wedge has no terminating landing and so has no
  trailing gap at all.
- **"Trailing gap ≤ the maximum observed inter-attempt gap (19,454s)" — THIS CONTROL CANNOT WORK.**
  Against the 19,454s the document quoted, it is keyed to yesterday's answer: two episodes exceed
  it (2026-08-24 06:02 at 19,500s; 2026-08-28 03:38 at 29,280s) and the reason is that the log has
  since grown a 40.0h gap, so the control reddens when the publisher merely stalls longer — exactly
  backwards. Against a bound **derived** from the log it cannot fail at all, because a trailing gap
  *is* one of the inter-attempt gaps the maximum is taken over. Keyed to the answer it is fragile;
  keyed to the property it is arithmetic.

  **What it was reaching for is an adjacency claim, not a duration claim.** Its stated fear was
  that "a landing was missed and the episode was closed on the wrong cycle". That is now checked
  directly: an episode holds every non-landing cycle, so its recovery must be the *immediately
  next* cycle. PASS, 38 of 38 — and the field is shown reachable both ways over one partition (a
  strict-definition episode broken by `behind_origin` has a non-adjacent recovery), so it is an
  observation rather than a constant wearing a check's clothes. The duration comparison is kept as
  a corrupt-record canary and is explicitly labelled in the module as not being evidence about the
  publisher.

## One definitional divergence the pre-registration did not anticipate

It defines the trailing gap as "the landing attempt − the last **refused** attempt". Under the cost
definition an episode ends on the last attempt that did not **land**, which can be a
`behind_origin` cycle that refused nothing. **Three of the 38 bounded episodes end that way**, and
for them the two phrasings name different quantities — on 2026-08-31 15:00 they differ by an order
of magnitude (1,560s from the last attempt against 18,540s from the last refusal).

The figures above use the last **attempt**, which is what `outage − span` means and what the span
definition already assumes. Both readings are carried per episode and the divergence is counted, so
no reader has to infer which one a number came from. This is the *average unit rate* shape caught
before it published: one word in a definition, two populations, and a figure that would have been
quoted under the other one's words.

## Where the derivation lives

`tools/commit_refusal_attribution.py::trailing_gap_report`, printed by the module's own `main` as
the `=== DECOMPOSITION ===` section, so the figure is re-derivable rather than quoted. Ten controls
in `tests/tools/test_commit_refusal_attribution.py`, each mutation-proven to fire: the single-cycle
partition, the anchor re-derivation, the derived-not-hardcoded bound, the negative flag, the
adjacency check, the two-definition divergence, the empty-side `None` median, censoring, and the
pinned tautology.
