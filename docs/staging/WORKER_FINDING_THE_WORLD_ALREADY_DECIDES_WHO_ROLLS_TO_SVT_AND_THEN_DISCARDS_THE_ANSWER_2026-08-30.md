**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The world already decides who rolls onto SVT at every renewal, and then puts them on a fixed term anyway

**Found:** 2026-08-30, designing C1b's assignment half. It changes that work from *"invent a rule
for who is on SVT"* — which would have needed a curriculum value and a director act — to *"stop
discarding a decision the world already makes"*, which needs neither.

## The decision already exists, is per-household, and is anchored

`simulation/renewal_engagement.rolls_active_renewal` is called at every electricity renewal
(`run_phase2b.py:1487`) and returns, in its own docstring's words:

> True if this renewal is an 'active' choice, **False if a passive SVT roll**.

It is not a coin flip per renewal. The caller threads the household's persistent engagement
archetype, so *"a household's active/passive/disengaged trait is persistent across its whole
tenure"*, and the population shares are externally anchored — Ofgem RMI, 45/35/20, already wired.
The module's own constant carries the anchor too:

```
PASSIVE_RENEWAL_RATE = 0.35   # ~65% of domestic/SME customers roll to SVT by inaction at term end
                              # SVT inertia data: Ofgem Consumer Engagement Surveys 2018-2019;
                              # CMA 2016 investigation
```

**So the world computes, for every household at every renewal, whether it rolled onto SVT — and
then builds it another fixed-term contract regardless.** The answer survives as far as
`event["is_active_renewal"]`, where it is recorded as an observable and used to pick a churn cap,
and no further. `build_renewal_schedule` never sees it.

That is the whole of the assignment gap: not a missing rule, a discarded answer.

## What it means for C1b, and it is smaller than the roadmap assumed

`docs/design/CHOICE_AND_CHANNEL_ROADMAP.md` C1 says the SVT product must be *"generated from
behaviour"* by three routes: never engaged, lapsed off a fixed deal without acting, or a home move
onto the incumbent. Measured against the tree:

| route | mechanism | status |
|---|---|---|
| lapsed off a fixed deal without acting | `rolls_active_renewal` returning False | **exists, anchored, per-household, discarded** |
| never engaged | the same engagement archetype at the account's first renewal | exists, same call |
| home move onto the incumbent | — | absent; C6 |

Two of the three routes are one function call that already runs. The third is C6 and is already
named as C1's stated simplification, with its recorded consequence — the generated SVT share comes
out LOW against the published one, which errs toward leaving more of the book priceable than
reality would.

**And no curriculum value is created**, which is the part that matters for R13. The split is not
chosen: it falls out of `PASSIVE_RENEWAL_RATE` and the engagement archetype, both already in the
world and both already anchored. The published year-by-year fixed/SVT share stays what the
determination said it must be — a CHECK on the output, never an input.

## The constraint this creates, which is the reason to write it down before building

`71242c941` fitted `simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR` against the CURRENT book —
a book in which every account holds annual fixed terms and every account faces a renewal decision.
C1b changes that composition: on the published shares, roughly two thirds of the domestic book
would have no renewal decision at all, and would instead carry the SVT inertia hazard landed in
`3bf3345de`.

**So C1b invalidates the fit that just landed.** The anchor's own note says what to do — *"a year
flagged OUT OF BAND means the anchor has gone stale against a world that moved under it —
re-capture and re-fit, never widen the band"* — and the re-fit is therefore part of C1b rather
than a follow-up someone discovers when a year goes red.

Sequence, so that no step moves two things at once:

1. Assignment lands with the anchor UNCHANGED. The departure series moves, and it moves for one
   reason. Measure it and record the size.
2. Re-capture the factor table and re-fit the anchor against the new composition.
3. Only then read the reason mix, which now has a fourth cause in it.

Doing 1 and 2 in one commit would leave the level change and the composition change
inseparable — the exact thing `1596019fc` held the C2 wiring back to avoid, and the reason that
restraint was right.

## What is owed

Thread `is_active_renewal` from the renewal decision into the schedule the NEXT term is built
from, so a passive roll produces an SVT segment run (`simulation/svt_product.build_svt_schedule`,
landed in `067a00dfd`) instead of another fixed term. The hazard that lets those households leave
again is landed. The interlock test
`tests/simulation/test_svt_product.py::test_no_account_is_on_the_svt_product_yet` is what says the
assignment has not happened yet, and it must be REPLACED by a split-in-range check rather than
deleted — that replacement is the deliverable that proves C1 done.
