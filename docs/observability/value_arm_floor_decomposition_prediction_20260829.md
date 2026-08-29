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
