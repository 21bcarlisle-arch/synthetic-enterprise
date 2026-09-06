**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R1's gating verdict is a step function of coverage, and the page published a hedge in its place

**Found:** 2026-09-06, delivery seat, claim
`the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`. Measured by
`tools/r1_inference_ceiling.py --stability`, published on `/harness/`.
Pre-registration: `SEAT_PREREGISTRATION_WHETHER_R1S_CORRECTED_VERDICT_IS_STABLE_ACROSS_DRAWS_OF_THE_SAME_BOOK_2026-09-06.md`
(written before the sweep existed; graded below, and it refuted me twice).

---

## The defect

The selection correction landed at `f53c90b85` and is sound. What it left behind is a **published
hedge standing in for evidence we already owned.**

`site/data/delivery.json` carried: *"a figure that clears by a tenth of itself **will move** with
the next draw of the book"* — a prediction. The record already held the observation that it **had**
moved, to the other side of alpha, on a run two days earlier. That fact was the entire reason
`SEAT_FINDING_R1S_CEILING_WAS_A_SELECTED_MAXIMUM...` stayed BLOCKING, and it lived only in a staged
finding. A49 gates R3 and R4 on this figure. Nothing a reader of the page could see said the gate
changes side depending on which file the instrument opened.

## The fix, and it is a measurement rather than a sentence

`verdict_across_runs` re-runs the **whole instrument** — the 45-way sweep and its own 200-draw
selection-corrected null — on each of the K most recent run outputs, and reports whether the verdict
survives. 32 draws take 40 seconds, so this is cheap enough to be a standing rung rather than a
one-off.

## The result, and it is sharper than the hand table it replaces

| n in rung | n in book | runs | ceiling | p | verdict |
|---|---|---|---|---|---|
| 71 | 214 | 13 | +0.5661 | 0.0746 | **cannot tell** |
| 69 | 213 | 19 | +0.6127 | 0.0249 – 0.0299 | **clears** |

**There is no scatter inside either group.** This is not noise around the threshold that more draws
would settle — it is a step, and it fell once, between the 09-05 06:39 and 09-05 08:26 run outputs.
19 of 32 recent draws of the same population publish "clears" and 13 publish "we cannot tell".

**Which of two things moved it cannot be attributed, and is not claimed.** The rung lost two
households and the book lost one, together, perfectly confounded across this window. The earlier
finding's headline — *"flips on two households"* — is the rung's share of a change the whole book
also underwent. Stating it alone would be attributing a move when more than one thing changed.
What survives needs no attribution: **the published answer is decided by about half a percent of
the book, and that is not a quantity a programme can be gated on.**

The instrument now says so on `/harness/`, on all three states — moved, held, and *never measured*
— held by `test_whether_the_gating_figure_SURVIVES_A_REDRAW_reaches_the_reader` (three poison
rounds: deleting the block, rendering unmeasured as stable, and emitting the sentence
unconditionally all red it).

## Grading the pre-registration, beside the result

| | prediction | outcome |
|---|---|---|
| P1 | the verdict is NOT unanimous across the recent series | **REFUTED at K=8, confirmed at K=32** — see below |
| P2 | restricted to 09-06 runs, unanimous `clears` | **confirmed** — 8 of 8 |
| P3 | ≤4 distinct `n` and ≤5 distinct ceilings across K=8 | **confirmed, and far tighter than I predicted** — exactly 2 of each across K=32 |
| P4 | full-coverage rung reads `cannot tell` on every run, n=213 | **confirmed** — and n=214 on the older regime, which I did not anticipate and which is the confound above |
| P5 | `n` in [65,75]; 4–8 of 8 clearing | **confirmed** — 69/71, 8 of 8 at K=8 |

**P1 is the one worth keeping.** My pre-registration said "the K most recent run outputs" and
**never fixed K** — and the answer depends on it. At K=8 the series is unanimous and I would have
published "the verdict is stable". At K=32 it is a 19/13 split. I found this by running K=8 first,
getting a refutation, and widening the window *because I knew the 09-04 run existed and disagreed* —
which is choosing the window after seeing the answer, and is the same defect class as grading a
selected maximum against a single comparison. **That is why `coverage_regimes` is the published
statistic and the ratio is not.** The grouping does not move with K; the counts do. A free parameter
I left open in a document written specifically to close free parameters is the finding inside the
finding.

P4's second half was a genuine surprise: I predicted n=213 on every run and asserted the population
was constant. It was not — `same_population` reads **False**, and the trait spread is perfectly
confounded with the regime. My pre-registration committed me to reporting that if seen, which is the
only reason it is in the caveat rather than lost.

## What this does NOT say

It does not say the ceiling is chance, and it does not say the ceiling is real. It says the
instrument cannot hold either claim steady across consecutive states of one book. The full-coverage
rung (n=213/214, the one with the power) reads `cannot tell` on **every one of the 32 draws**, at
p=0.85 — unanimous in the direction of refusal.

Nor is this a bootstrap. These are consecutive states of one population at one base seed, not
independent books, so the spread here **understates** what a re-drawn book would show.

## What would close it

Unchanged, and now measured rather than argued: **coverage.** Nine of eleven observables are carried
by ≤100 households. At full coverage the pair rung would carry 213 rather than 69, the p95 bound
would fall, and the verdict would stop being a function of which household dropped out. The
instrument is the falsifier and needs no further correction — `--stability` is now the check that
says whether the answer has stopped moving.

**Why this stays BLOCKING:** A49 was minted on the premise that R1's ceiling could gate R3 and R4.
It cannot, and now both the atom and the page say so. The premise is what needs repair, not the
measurement.

---

## CORRECTION — 2026-09-06, later the same day. "Coverage" is not established as the variable.

Left above unedited, because a wrong cause kept beside its refutation is the only evidence the
grouping was chosen before its answer was known.

This finding's whole claim is that the verdict is **a step function of coverage**, grouping runs by
`households_in_rung` (69 vs 71) and `households_in_book` (213 vs 214). **Those are supply-point
counts, not household counts.** A run output's `customer_id` is a supply point, and a household's
gas leg is registered under its electricity point's id plus `GAS_LEG_ID_SUFFIX`
(`simulation/household.py:485`) — `C1` and `C1g` are one property. On `run_output_f53c90b85` I
count **264 supply points belonging to 177 households: 87 legs.** Worse, the target those legs were
graded against is fabricated — `price_elasticity_for_customer` is a hash of the id and answers for
any string at all (`NOT_A_REAL_ID` → 1.4223), so `C1g` was graded at 0.5255 while the world had
given household `C1` a 1.6043.

So the two runs I grouped as "n=69" and "n=71" differ by two *supply points*, which need not be two
households, and both rungs carry rows whose target belongs to nobody. **The step-function grouping
may well survive re-keying — it is a clean partition and I would not be surprised if it holds — but
nothing here establishes that it does, and this finding published it as established.** That is the
same defect this project keeps paying for: the cause was inferred from the split rather than the
split following from a definition. `does_the_verdict_survive_a_redraw` is on `/harness/` asserting
it right now.

**What is NOT withdrawn:** that the verdict moves at all between consecutive run outputs of one
population at one seed, and that a number which moves like that cannot gate a programme. That
observation does not depend on what the grouping variable turns out to be, and it is the reason
this stays BLOCKING.

**Who is repairing what.** The keying defect was found by another lane, which holds the whole R1
publication chain dirty in the shared tree and is fixing it; I verified their claim independently
before relying on it and touched none of those files. This seat fixed the **class** instead — the
ground-truth draw now refuses a supply-point leg and names the household that should have been
asked for (`simulation/population_draw.price_elasticity_for_customer`), so the next instrument to
key on the wrong id is refused rather than answered. Full account, with the census and the
pre-registration that predicted the world would come out clean, in
`SEAT_FINDING_R1S_CEILING_WAS_A_SELECTED_MAXIMUM_AND_THE_CORRECTED_VERDICT_FLIPS_ON_TWO_HOUSEHOLDS_2026-09-06.md`.

**The re-run that settles it** is the one this finding already names — `--stability` over the same
window — but it must be run *after* the re-keying lands, and its household counts read as household
counts for the first time. Until then the coverage cause on the page is a hypothesis wearing a
measurement's clothes.
