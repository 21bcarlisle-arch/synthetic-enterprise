# PRE-REGISTRATION — the noise signature is checked on most pairs, published on the winner

**Filed:** 2026-09-06, delivery seat, BEFORE the measurement below is run.
**Subject:** `tools/r1_inference_ceiling.py`, control `held_out_exceeds_in_sample_on_most_pairs`.
**Claim it belongs to:** `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.

## What I already know, so it is not what I am registering

The selection correction landed at `06fc90189` and is on `origin/main`. The published panel carries
the corrected bound: observed `+0.6127`, p95 of the selected-maximum null `+0.5529`, `p=0.0249`,
verdict *clears, marginally*. That part is done and I am not re-opening it.

## The thing I noticed, which is not the same defect

The module's own docstring names the tell that exposed the original defect:

> held-out +0.5661 against in-sample +0.1724, a fit scoring three times better on households it
> never saw, which no real fit does.

A control exists for it — `held_out_exceeds_in_sample_on_most_pairs` — and it reads **False**
(green) on this book. But it is keyed to *most pairs*, and the number the page publishes is not most
pairs. It is the **winner**: `+0.6127` held-out against `+0.1674` in-sample, **3.66× better out of
sample than in it**. The exact signature the control is named for is present in the exact figure the
control was written to protect, and the control is green.

This is the shape the house calls *keying a control to the population when the claim is about the
instance*. The aggregate can be healthy while the selected extreme is not — and selection on
`abs(held_out)` is precisely the search that finds an overshoot.

## What I am NOT claiming, registered so I cannot quietly upgrade it later

Inversion is **not** independent evidence that the ceiling is chance. Under the null the winner
overshoots its own fit too, because the winner is chosen for a large held-out score in both worlds.
The p-value already contains the selection. So:

- I will **not** flip the verdict on this. Flipping would be keying a control to today's answer.
- I will surface it, on the page, beside the figure — a reader who gets `clears, marginally` and
  not this cannot judge the number.

## Predictions, written before running

1. Re-running the instrument against the SAME run output
   (`run_output_23cbe058b_20260906T141424Z.json`, read from the shared tree via `--run`) reproduces
   `best_pair.held_out = 0.6127`, `in_sample = 0.1674`, `p = 0.0249`. **If it does not, the
   instrument is not deterministic against a fixed book and that is a bigger finding than this
   one, and it takes priority.**
2. The new winner-level control reads **True** (signature present) on this book while its sibling
   reads **False**. If both read the same, the two controls are not measuring different things and
   the new one is not worth having.
3. No verdict field changes value: `ceiling_clears_the_null` stays `true`, `p_value` stays `0.0249`.

*Corrections go beside this file, not over it.*
