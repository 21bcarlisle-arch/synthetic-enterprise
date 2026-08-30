**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The world's departure LEVEL has never been checked against a published switching rate — and it is the anchor C2's calibration was missing

**Found:** 2026-08-30, after C2's P0 calibration came back non-identifying and was correctly
refused (`54b9dfa72`). That commit found the P0 target was contaminated — the composed form lets
the price multiplier scale the bill-shock term, and the company is cheaper than the market
reference in 74.4% of renewals. **This is the other half of the same problem, and it is the larger
half: the target was not merely contaminated, it was never anchored to anything outside this
repository.**

**No published figure is known to be wrong.** This is about what the world's churn level IS, not
about a number on the site.

## What the world does

Departures per household-year, from the live run. Stated with what each number counts, because
the wrong denominator is the standing trap here:

* a departure is a **household-level** decision, rolled once per year and keyed to the electricity
  leg — confirmed, all 44 departures in the run carry `commodity: "electricity"`;
* `active_elec` is one account per household with power. `active_elec + active_gas` double-counts
  dual-fuel households and is the WRONG denominator for this numerator.

| year | departures | active elec | per household-year |
|---|---|---|---|
| 2017 | 1 | 81 | 1.2% |
| 2018 | 7 | 88 | 8.0% |
| 2019 | 6 | 94 | 6.4% |
| 2020 | 2 | 101 | 2.0% |
| 2021 | 3 | 108 | 2.8% |
| 2022 | 6 | 110 | 5.5% |
| 2023 | 1 | 117 | 0.9% |
| 2024 | 4 | 131 | 3.1% |

**2017–2024 mean: 3.6% of households leave per year.** (2016 has 3 renewals and 2025 is a partial
year; both excluded rather than averaged in.)

## What the published record says, on every denominator it will bear

The knowledge page `how-households-choose` already records that published switching counts are
**not one series** — some count electricity meter-point transfers, some gas, some changes of
supplier across both fuels — and refuses to publish a year series for exactly that reason. So the
comparison is done on every plausible reading rather than on a chosen one:

| source | numerator | denominator | rate |
|---|---|---|---|
| ElectraLink 2024 | 3.21m changes of supplier | ~51m domestic fuel accounts (28m elec + 23m gas) | **6.3%** |
| ElectraLink 2024 | 3.21m changes of supplier | ~28m domestic electricity meter points | **11.5%** |
| DESNZ 2019–20 | ~6M switches | ~28M accounts (its own pair) | **~21.4%** |

## The comparison, taken against the reading least favourable to the finding

**2024, our 3.1% against the most conservative published reading of the same year, 6.3%: a factor
of 2.0.**

**2019–20, our 4.2% against DESNZ's own matched numerator/denominator pair, 21.4%: a factor of
5.1.**

2024 is the fair test — it is the year the published record is at a post-crisis low and Ofgem
describes switching as still "below pre-crisis levels", so it is where our world has the best
chance of agreeing. It is still half the published rate on the most generous denominator
available, and a fifth of it on the one the source itself used.

**Our world is somewhere between two and five times too sticky.**

## Why this matters more than it looks, and why it is C2's blocker

C2's pre-registration put P0 first: calibrate so the population-mean churn matches today's, making
the level a control and the decomposition the only variable. That was the right shape and the
wrong target. Matching today's mean would have **locked a departure rate 2–5× below the published
record into the new mechanism**, and done it invisibly, because P0 would have reported a clean
±0.0000% match.

`54b9dfa72` refused the calibration on identifiability — every `a_shock` from 0.87 down hits P0
exactly while the reason mix runs 99.9% to 56.6%. That refusal was right, and this finding says
the calibration would have been unsafe even had it identified: **you cannot fit a decomposition to
a level nobody has checked.**

## What is owed, and it is a better job than the one C2 was blocked on

**Anchor the departure LEVEL externally before fitting the decomposition.** The published rate is a
per-year switching rate over a stated population, and the world can be held to it directly — a
target the tree does not generate, which is the whole point.

Two things have to be got right and both are the standing traps in this area:

1. **The denominator must be declared per comparison.** Our numerator is household-level
   departures; the published numerators vary by fuel. The table above is the shape any future
   comparison should take — every reading, not a chosen one.
2. **A supplier's churn is not the market's switching rate for free.** If 21% of accounts switch
   in a year and switching were uniform, ~21% of any supplier's book leaves. Switching is not
   uniform — engaged customers switch repeatedly and the disengaged never do — so the market rate
   is an upper bound on a book of average engagement and the gap between them is itself a
   modelling question, not a discrepancy to close by tuning. **The world already models
   engagement** (Ofgem RMI 45/35/20, wired), so it can be asked to reproduce both the aggregate
   rate and its concentration, which is a stronger check than either alone.

## R13, stated because this one runs toward us

Raising the world's departure rate to meet the published record makes the company's book **harder
to hold**: more departures, more revenue lost, more of the book to re-win. It is unambiguously
unflattering, which under the director's refinement of 2026-08-30 puts the correction on the
delivery seat's side of the line — *"if a curriculum-adjacent change is a correction rather than a
choice, and the honest version makes our position worse or leaves it unchanged, make it and tell
me."*

**But the SIZE of the move is a curriculum value and it is his.** How sticky a book this company
faces is a difficulty setting; "match the published rate exactly" is one defensible answer and
"land inside the published range, at the sticky end, because a supplier's book is less engaged
than the market" is another. Not chosen here. The measurement is the deliverable; the target is a
decision, and this is precisely the class he asked to see rather than have waved through.

## The falsifier this is owed

None yet, deliberately. A control asserting "the departure rate equals 3.6%" would pin today's
answer and go red when the world became more honest — the exact shape repaired this morning in
`test_as_of_r1_sees_r1_estimate_not_final`. The control worth writing is that **the world's
departure rate sits inside the published range on a declared denominator**, and it cannot be
written until the range and the denominator are settled, which is the work above.
