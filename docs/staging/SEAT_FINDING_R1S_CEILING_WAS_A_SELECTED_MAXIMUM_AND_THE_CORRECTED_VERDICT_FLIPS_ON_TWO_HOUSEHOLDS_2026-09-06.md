**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R1's ceiling was a selected maximum, and the corrected verdict flips on two households

**Found:** 2026-09-06, delivery seat, claim
`the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`. Repaired in
`tools/r1_inference_ceiling.py` and published on `/harness/`.
Pre-registration: `SEAT_PREREGISTRATION_WHAT_THE_SELECTION_CORRECTED_NULL_DOES_TO_R1S_PUBLISHED_CEILING_2026-09-06.md`
(written before the correction was implemented; graded below, and two of its four predictions are
refuted).

---

## The defect

The pairwise rung scored 45 candidate feature pairs, ranked them `sort(key=lambda r:
-abs(r["held_out"]))`, reported the winner as **the input ceiling**, and graded that winner against
a null drawn **for that pair alone**. That null answers *"could THIS pair have scored this high by
chance"*. The sweep asks *"could the BEST OF 45 have"*, and the maximum of 45 noise draws sits far
out in the tail of any single one of them.

Measured rather than argued, and it is the control that now holds the fix
(`test_the_one_pair_null_accepts_a_book_with_nothing_in_it_and_the_corrected_null_does_not`). Ten
synthetic books in which **every feature and the target are independent noise**:

| null | accepted the winner |
|---|---|
| the one this instrument used (winner vs its own pair's null) | **9 of 10** |
| the corrected one (winner vs the best-of-45 null) | **1 of 10** |

Nine times out of ten, on a book with nothing in it, the published shape called the winner real.

## The fix

One draw of the corrected null shuffles the household → trait assignment across the whole book,
re-scores **every** pair on that shuffled world, and keeps the winner. 200 draws give the
distribution of the quantity actually reported. Two properties make it the same procedure, and both
were live traps:

- the shuffle is **world-wide**, so every candidate in a draw sees the same shuffled world.
  Shuffling each candidate's target independently breaks the correlation between candidates that
  share households, which is what makes the real maximum reach as high as it does.
- the candidate grid is **fixed before any draw**, so eligibility cannot move with the target.

The same correction is applied to the full-coverage single-feature rung, which carries the headline
verdict and is also a maximum (`any(...)` over the full-coverage features). It was `false` before
and is `false` after — as it must be, since a selection correction can only ever be more
conservative.

## The result, and it is not the clean refusal the direction anticipated

Run `run_output_23cbe058b_20260906T141424Z.json`, base seed 20260724:

```
reported ceiling (best of 45 pairs)  : +0.6127   (in-sample +0.1674, n=69)
UNCORRECTED  null floor              : +0.4948   clears: True
CORRECTED    p95 of the best-of-45   : +0.5529   p = 0.0249 (4/200 draws)   clears: True
             margin over the bound   : +0.0598
full-coverage rung (n=213)           : cannot tell, p = 0.8507
```

**It clears.** And the reason this is filed BLOCKING rather than closed is the next table. Four run
outputs, **all drawn from the same population at the same base seed** — they differ only in which
households happened to carry both features of a pair:

| run | n | ceiling | corrected p95 | p | verdict |
|---|---|---|---|---|---|
| `1beec7215_20260904T163914Z` | 71 | +0.5661 | +0.5750 | 0.0746 | **cannot tell** |
| `b01b1dbe3_20260906T083546Z` | 69 | +0.6127 | +0.5617 | 0.0299 | clears |
| `eca0b1341_20260906T102536Z` | 69 | +0.6127 | +0.5529 | 0.0249 | clears |
| `23cbe058b_20260906T141424Z` | 69 | +0.6127 | +0.5529 | 0.0249 | clears |

**The verdict crosses the threshold on a difference of two households in the rung.** The figure
that was actually published as a bound — +0.5661, the one quoted in `site/data/delivery.json` and
in `SEAT_FINDING_R1S_INFERENCE_CEILING_IS_AT_THE_NULL_AND_R2_CANNOT_PAY_UNTIL_R1_LANDS_2026-09-04`
— **does not survive its own selection correction.** The current book's does, by +0.0598, about a
tenth of the figure.

So the honest reading of the whole thing is neither "the ceiling is real" nor "the ceiling is at
the null":

> **This measurement cannot bound the inference programme.** At n=69 only a ceiling above roughly
> +0.55 is distinguishable from a 45-way search of noise at all, and the answer moves across the
> 0.05 line with two households of coverage. A number that flips on two households is not a gate.

That sentence, the p-value, both verdicts and the power bound are now on `/harness/` under **"The
number the inference programme rests on"**, rendered from the committed artefact and held by
`site/test_harness_delivery_record.py` (three tests, mutation-checked: removing the uncorrected
figure or the caveat reds them).

## Grading the pre-registration, beside the result

| | prediction | outcome |
|---|---|---|
| P1 | corrected p95 ≥ 0.5019 (the old artefact's null floor) | **confirmed** — 0.5750 on that book |
| P2 | 15–120 of 200 draws beat the observed; p > 0.05 | **REFUTED** — 14 draws on the 09-04 book (p=0.0746, just outside my range and the right side of the line), 4 on the 09-06 book |
| P3 | the published `ceiling_clears_the_null: true` flips to false | **half** — it flips for the figure that was published, and does not for the current book |
| P4 | the full-coverage rung stays `false` | **confirmed** |

I predicted the correction would kill the number outright. It did not: it killed the *published*
number and left the current one marginally alive. Writing P2 as a numeric range is what made that
readable — a directional prediction would have let me call P2 "broadly right".

## What this does NOT say

It does not say elasticity is learnable. The clearing pair is
`perceived_bill_saving_gbp × portfolio_premium_pct` at n=69, held-out +0.6127 against in-sample
+0.1674 — a fit scoring nearly four times better on households it never saw, which no real fit
does. Under the corrected null that shape is no longer *disqualifying* (the null's own winners show
it too), but it is not evidence of a recoverable trait either. The full-coverage rung, which has
three times the households and is where this book has the power to tell a ceiling from its own
noise, still reads **cannot tell** at p=0.85.

## What would close it

Coverage, not cleverness. Nine of the eleven observables are carried by 100 households or fewer; at
full coverage the pair rung would have 213 households and the p95 bound would fall far enough for a
moderate ceiling to be visible. **The instrument is unchanged as the falsifier** — re-run it on a
book where the pair fields are populated on every household and the answer stops depending on which
two households dropped out.

## Also fixed here, because it was fail-open on the same instrument

`newest_run_output()` picks by mtime, and a linked worktree carries **no gitignored run outputs**.
It selected a tracked stand-in with zero usable rows and the instrument reported `households: 0,
pairs: 0, ceiling +0.0000, clears False` — which reads exactly like *"measured the book, found
nothing"* and is the opposite claim to *"measured nothing"*. It now refuses under
`MIN_HOUSEHOLDS`, names the worktree cause in the refusal, and takes `--run <path>` so the tree
holding the real book can be named.

## Still pointing at the old null, and not touched here

`docs/design/maturity_map.yaml` and
`docs/design/simplifications/A49_the_ceiling_comes_before_the_programme_on_r3_and_r4.yaml` both
describe R1's ceiling as *"held-out per-cell mean against a max/48 null"*. That description is now
wrong in the way this finding is about. Left for a lane that is already editing the map rather than
opened as a second writer to it.
