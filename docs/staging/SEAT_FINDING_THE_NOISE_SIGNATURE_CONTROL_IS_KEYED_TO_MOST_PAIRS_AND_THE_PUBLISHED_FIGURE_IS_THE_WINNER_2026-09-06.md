**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The noise-signature control is keyed to most pairs, and the published figure is the winner

**Found:** 2026-09-06, delivery seat, claim
`the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`. Repaired in
`tools/r1_inference_ceiling.py`, `tools/generate_delivery_page.py` and `site/harness/index.html`.
Pre-registration:
`records/SEAT_PREREGISTRATION_THE_SIGNATURE_CONTROL_IS_KEYED_TO_MOST_PAIRS_AND_THE_PUBLISHED_FIGURE_IS_THE_WINNER_2026-09-06.md`
(written before the re-run; all three predictions confirmed, graded below).

This sits **downstream of** the selection correction filed alongside it, which is BLOCKING and
landed at `06fc90189`. That one was about the verdict being wrong. This one is about a control
being green while the tell it is named for sat inside the figure it was written to protect.

---

## The defect

`tools/r1_inference_ceiling.py` carries a control whose name states the property exactly:

```python
"held_out_exceeds_in_sample_on_most_pairs": bool(
    ranked and sum(1 for r in ranked
                   if abs(r["held_out"]) > abs(r["in_sample"])) > len(ranked) / 2),
```

and the module docstring says why it matters — the original defect was spotted by *"held-out +0.5661
against in-sample +0.1724, a fit scoring three times better on households it never saw, which no
real fit does."*

On the real book that control reads **False**. Green. But it asks a question about **most of the 45
pairs**, and the page does not carry most of the 45 pairs. It carries **the winner**:

| | |
|---|---|
| winner held-out | **+0.6127** |
| winner in-sample | **+0.1674** |
| ratio | **3.66×** better on households it never saw |
| `held_out_exceeds_in_sample_on_most_pairs` | **False** (green) |

The exact signature the control is named for was inside the exact number the control exists to
protect, and nothing in the instrument, the feed or the page could see it. **An aggregate is blind
to its own selected extreme** — and `abs(held_out)` is precisely the ranking criterion that finds an
overshoot.

## What this is NOT, and the reason it is LATENT rather than BLOCKING

Inversion is **not** independent evidence that the ceiling is chance. Under the null the winner
overshoots its own fit too, because both worlds rank on `abs(held_out)`. The p-value already
contains the selection. So the verdict does not move and **must not be made to**:
`ceiling_clears_the_null` stays `true`, `p_value` stays `0.0249`. Reaching for `clears` from here
would be keying a control to today's answer, and
`test_the_winner_signature_is_reported_and_never_flips_the_verdict` is the control that refuses it.

What it changes is what a reader can judge. Someone shown *"clears, marginally"* and not this cannot
tell that the winning fit behaves the way no fit behaves.

## The repair

A control keyed to the **instance that gets published**, sitting beside the population one so a
reader sees the pair, plus the sentence that carries it to the page:

- `held_out_exceeds_in_sample_on_the_reported_winner` — **True** on this book
- `reported_winner_held_out_over_in_sample` — **3.66** (`None` when in-sample is zero; an infinite
  ratio is not a number a reader can hold, and a large float would read as measured)
- the caveat in `we_cannot_tell.what_it_does_not_say` gains the sentence, on **both** verdict
  branches
- `/harness/` renders it as its own block, only when the property holds

## Evidence it can fail

Baseline through the identical command: `14 passed`. Poison round first, because *survived* means
two opposite things:

| mutation | result |
|---|---|
| POISON — `_winner_inverts` returns `False` always | **2 failed** (the runner kills) |
| M1 — invert the comparison (`>` → `<`) | **2 failed** |
| M2 — ratio rounds to 1dp | **1 failed** |
| M3 — zero in-sample yields `999.0` rather than `None` | **1 failed** |
| M4 — the caveat sentence never reaches the reader | **1 failed** |
| door — the block never renders | **1 failed** |
| door — the block renders unconditionally | **1 failed** |

The last two are the partition: a panel that always emits the sentence is boilerplate, not evidence.

## The trap inside the door test, caught by its own second leg

The first draft keyed the partition on the phrase `"never saw"`. **Both legs passed** — because the
instrument's `what_it_does_not_say` string already contains that phrase and the panel renders it on
every branch. The discriminator has to be text the block emits **and nothing else on the page
does**; it is now `"does not overturn"`. A discriminator shared with a sibling surface proves the
page contains a string, not that the mechanism ran.

## Pre-registration, graded

1. **Confirmed.** Re-running against the same run output reproduced `0.6127 / 0.1674 / p=0.0249`
   exactly. The instrument is deterministic against a fixed book.
2. **Confirmed.** The winner-level control reads `True` while its sibling reads `False` — they are
   measuring different things and the new one earns its place.
3. **Confirmed.** No verdict field moved.

## What is still open

The published `+0.6127` is a **selected maximum**, so even having cleared, its magnitude is an
upward-biased estimate of the ceiling rather than the ceiling itself. `A49` gates R3 and R4 on this
figure. The page labels it *"what the best of 45 searches recovered"*, which is honest, and the
caveat now says why — but **no unbiased point estimate of the ceiling exists in this instrument**,
and one would need either a held-out selection split or a shrinkage estimator. That is a separate
piece of work and it is not started.
