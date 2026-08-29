# The arms page named a remedy nobody had measured — the arithmetic, filed before the answer

**2026-08-29, delivery seat.** The prediction below was written and committed while the two floor
legs that settle it were still running. That order is the whole point: a prediction filed after
the answer is not a prediction.

## The sentence

`site/data/value_arms.json` published, beside its refusal to state a direction:

> *"What would resolve it is a larger SETTLED BOOK — more renewals actually priced by the arm — and
> not more seeds: re-drawing the dice measures this spread again, it does not shrink it."*

The second half is arithmetic and stands. The first half is a claim about **where the spread comes
from**, and it was published as fact one day after this same page withdrew a different sentence for
asserting more than its evidence carried.

## Why it cannot be read off the artefact as published

`docs/observability/value_cycle_ab_s1_noise_floor_20260829.json` re-draws
`simulation.population_draw.price_elasticity_for_customer` for **2,020–2,074 households** per seed.
`docs/observability/value_cycle_ab_s1_three_arm.json` says the value arm **priced 20 renewals**. So
the £2,577.80 stdev on `selection_gbp` has two possible sources with **opposite remedies**:

| source | shrinks with a bigger settled book? |
|---|---|
| the 20 priced households' own elasticity | yes — as ~1/√n |
| the other ~2,050 households' churn cascade landing in the same net | **no** — not at all |

If the priced side is the small half, the published remedy is wrong.

## The threshold, and it is not a judgement call

The page's own resolution rule (`generate_value_arms_data._resolvable`) is that a contrast must
exceed the spread of the same contrast. Only the priced half shrinks, so the bar converges to the
rest-of-book half alone. With `selection_gbp` = £1,815.79 and an undecomposed variance of
£2,577.80²:

> **A larger settled book resolves this only if more than 50.4% of the variance is priced-side.**

## The price table — printed at real inputs, before the test

`tools/run_value_cycle_ab.remedy_price_table`, at the published floor and funnel:

```
  priced   irreducible   priced decisions   x this   renewals the world
  share    floor (sd)    needed             book     must offer (at 1.46%)
    10%    £   2,446     UNREACHABLE at any book
    20%    £   2,306     UNREACHABLE at any book
    30%    £   2,157     UNREACHABLE at any book
    40%    £   1,997     UNREACHABLE at any book
    50%    £   1,823     UNREACHABLE at any book
    60%    £   1,630          125            6.2x        8,562
    70%    £   1,412           72            3.6x        4,932
    80%    £   1,153           55            2.8x        3,768
    90%    £     815           46            2.3x        3,151
    99%    £     258           41            2.0x        2,809
```

Read the last column against the funnel it came from before using it. Which brings the second,
independent problem with the sentence:

> **This table is superseded — kept because it is the pre-answer record, not because it is right.**
> Its `x this book` column indexed 1/n on the 20 *decisions*, and the table above it says
> "the 20 priced households", which is two errors of the same kind: there are **10** priced
> accounts, not 20, and the elasticity draw is a pure function of `(customer_id, seed)`, so 20
> decisions carry only 10 independent draws. The multiplier survives the correction (it is
> scale-free); the absolute counts do not. **Use the reprinted table at the foot of this file.**

## "A larger settled book" cannot mean a larger DRAWN book

`renewal_funnel.value_arm.accounts_the_arm_priced` is `C1, C1_2, C2 … C9` — **ten accounts, every
one of them the hand-authored static roster, and not one a drawn `SYN-*` household.** The funnel
sums exactly: 662 `product_not_upliftable` (all `tariff_type: None`, i.e. drawn households the world
has no standard-variable product for) + 429 gas + 258 term-0 + 20 priced = 1,369 offered.

So adding drawn households adds renewals to `product_not_upliftable` and households to the churn
cascade — it **enlarges the half of the floor no book size shrinks while adding no priced decisions
at all.** On this world the lever is a *product*, not a *size*. Anyone reading "a larger settled
book" as "run the lifted-budget acquisition" would have been making the instrument worse.

## What was done about it now, before the answer

The remedy clause is no longer a constant. `generate_value_arms_data._what_would_resolve_it` derives
it from `docs/observability/value_cycle_ab_floor_decomposition.json` and has four branches: the
measured-and-true one, the measured-and-false one ("this comparison cannot be resolved at any book
this world can legitimately produce"), the too-close-to-call one, and — the state the live page is
in as this lands — **not measured**, which says so. The old sentence is on the record in
`withdrawn_claim`, in the words it was published in, beside the two others.

## The prediction

The two legs (`--redraw-mode only` and `--redraw-mode except`, seeds 11111/22222/33333, full
window) were launched at 21:46:43 under `systemd-run --user --unit=vcab-floor-legs`. Before they
land, on the record:

1. **The priced side will be the SMALL half** — under 50.4%, so `larger_settled_book_would_resolve_it`
   comes back `false`. The reasoning: the `only` leg moves 20 renewals' prices; the `except` leg
   moves the churn roll of ~2,050 households, and `churn_roster_diff` is already the mechanism by
   which the arms' denominators diverge. Two orders of magnitude more households sit on the side
   that does not shrink.

   > ### ❌ REFUTED, 2026-08-29 23:07Z. I called this the wrong way.
   >
   > The `only` leg landed at 23:07Z: `selection_gbp` stdev **£2,092.29** against the undecomposed
   > **£2,577.80**, so the priced side is **65.9%** of the variance against a threshold of 50.4%.
   > It is the LARGE half, not the small one, and by a clear margin in the direction I did not
   > predict. My reasoning above counted HOUSEHOLDS on each side and inferred variance from
   > population — 2,050 against 20. That inference is what was wrong: the priced households are
   > the only ones whose elasticity reaches a *margin decision*, so each one moves the selection
   > figure by far more than a household that can only move a churn roll. Headcount was the wrong
   > weight and I should have said so before running, because nothing about that argument needed
   > the answer to be visible.
   >
   > This is not yet a licence to publish the remedy — see the decisiveness margin below, which is
   > 0.1550 against a 0.15 bar.
2. **The reconciliation will land inside 0.3–3.0×.** At three seeds each variance carries two
   degrees of freedom; that interval is what the sample size alone produces. Outside it and the
   legs are not two halves of one thing, and the split is withheld rather than published.
3. **`share_is_decisive` will be true** — i.e. the split will not be within 0.15 of the 50.4%
   threshold.

If (1) is wrong, the page gets the remedy back with its price stated, and this note stays here
saying I predicted otherwise. If (2) fails, neither leg is publishable and the finding is about the
legs, not the arm.

**A permitted result, and on this evidence the likely one, is that the arm comparison cannot resolve
at any book this world can legitimately produce.** That is a finding about the instrument. It goes
in the headline, not in a footnote.

> **This paragraph was written expecting prediction (1) to hold, and it did not.** Leaving it to be
> read as agnostic hedging would be the quiet re-read the whole file exists to prevent: it says
> "on this evidence the likely one", and that evidence is now measured and points the other way.
> What survives is the *permission* — it remains a legitimate result — not the expectation.

---

# What the `only` leg returned, and the expectation filed before the second one lands

**2026-08-29, 23:40Z, delivery seat.** The `except` leg is still running (started 23:07Z, the first
took 81 minutes). Everything below is written before it lands, for the same reason as everything
above it.

## (a) The reconciliation number, filed in advance

The two legs partition one call stream, so their variances must sum to the undecomposed one. That
makes the `except` leg's `selection_gbp` stdev a **prediction, not an observation**:

> **sd(except) must come out near £1,505.78** — that is `sqrt(2577.80² − 2092.29²)`.

**The pass band is the preregistration's own 0.3–3.0× on the reconciliation ratio**
`(V_only + V_except) / V_all`, which in this units is sd(except) anywhere in roughly **£930 to
£2,190**. Outside that the two legs are not two halves of one thing, nothing is published from
them, and the finding is about the legs. This number is written down now so it cannot be re-read
after the fact, whichever way it goes.

## (b) The measured share, and why it is not yet a verdict

| quantity | value |
|---|---|
| undecomposed sd (`all` leg) | £2,577.80 |
| priced-side sd (`only` leg) | £2,092.29 |
| rest-of-book sd (`except` leg) | *pending* — expected £1,505.78 |
| contrast (`selection_gbp`) | £1,815.79 |
| **priced share of variance** | **65.9%** |
| threshold above which a bigger book resolves it | 50.4% |
| **margin over the threshold** | **0.1550** |
| `share_is_decisive` bar | 0.15 |

**The decisiveness flag clears by 0.005.** Each stdev is three seeds — two degrees of freedom a
side, a 90% interval spanning roughly a sixth to nine times the truth — and on that instrument a
margin of 0.155 against a bar of 0.15 is a direction, not a resolution. `share_is_decisive` will
return `true`, and it will be the thinnest possible `true`. **That fact belongs beside the number
wherever the number is published**, because a reader who sees only the boolean will read a
resolution that three seeds did not buy.

## (c) The denominator: three counts, one of them a sample size

One leg reports three numbers an order of magnitude apart, and the price table ran a 1/√n argument
through them and then divided again into *"renewals the world must offer"*. They are not
interchangeable and only one is a sample size:

| count | value | what it counts | a sample size? |
|---|---|---|---|
| `accounts_redrawn` | **10** | the households whose elasticity the leg re-rolled | **yes — this one** |
| `priced` | 20 | renewal *decisions* the arm priced (exactly 2.00 per account) | no — two decisions share one draw |
| `elasticity_redrawn` | 90–103 | *calls* to `price_elasticity_for_customer` | no — see below |

`population_draw.price_elasticity_for_customer` is a **pure function of `(customer_id, seed)`** —
five calls at one seed return one value, now asserted in
`test_the_elasticity_draw_is_a_pure_function_so_CALLS_are_not_draws`. So the ~97 calls per seed are
about **9.7 re-reads of the same 10 numbers**. Indexing 1/n on it would claim a sample nearly ten
times the real one.

**The shrinkage indexes accounts.** But the thing that actually gets published is scale-free:

> `needed / n₀` cancels n₀ exactly, so **all three candidate denominators agree the book must grow
> 4.25×** — and disagree wildly on whether that is "43", "86" or "413".

That is why the table below leads with the multiplier and treats the counts as it wearing a unit.
`renewals_the_world_must_offer` is reached from the **decision** count and only from it, because
`priced_share_of_renewals_offered` is 20/1369 — decisions over decisions — and dividing an account
count by it would be a ratio of two different things.

## The price table, reprinted on the named denominator

`tools.run_value_cycle_ab.remedy_price_table`, at the published floor and funnel, `priced_accounts=10`:

```
  priced   irreducible   times this   independent   priced      renewals the world
  share    floor (sd)    book         draws needed  decisions   must offer (at 1.46%)
    10%    £   2,446     UNREACHABLE at any book
    20%    £   2,306     UNREACHABLE at any book
    30%    £   2,157     UNREACHABLE at any book
    40%    £   1,997     UNREACHABLE at any book
    50%    £   1,823     UNREACHABLE at any book
    60%    £   1,630        6.24x          63           125           8,562
    70%    £   1,412        3.57x          36            72           4,932
    80%    £   1,153        2.70x          28            55           3,768
    90%    £     815        2.27x          23            46           3,151
    99%    £     258        2.04x          21            41           2,809
  ------  MEASURED (pending the except leg's reconciliation)  ------
  65.9%   £   1,506*       4.25x          43            86           5,891
```

The `times this book` column is the exact multiplier; the two count columns are it rounded UP into
their own units, so `43 draws` and `86 decisions` are both 4.25× and neither is 43/10 or 86/20 to
two places. Read the multiplier, not the ratio of the roundings.

`*` the irreducible floor at the measured share is the £1,505.78 the `except` leg must confirm.

## What this does and does not settle for the queue behind it

Prediction (1) failing means the arithmetic remedy is **real**: at 65.9% the rest-of-book half
(£1,506) is under the contrast (£1,816), so a book 4.25× this one would resolve the comparison.

**It does not revive the lifted-budget re-run, and the reason is a different measurement.** All ten
priced accounts are the hand-authored static roster; not one is a drawn `SYN-*` household, because
drawn households' renewals all stop at `product_not_upliftable` for want of a standard-variable
product. So acquisition buys churn cascade — the half that never shrinks — and **zero** priced
decisions. The prereg's closing claim, *"the lever is a product, not a size"*, rested on two legs,
and only the one that just failed was about the share. It stands on the funnel leg alone: **4.25× the
priced book is reachable by shipping an SVT product, and not by buying households.** That is a
sharper statement than the one I predicted, and it survives its own refutation.
