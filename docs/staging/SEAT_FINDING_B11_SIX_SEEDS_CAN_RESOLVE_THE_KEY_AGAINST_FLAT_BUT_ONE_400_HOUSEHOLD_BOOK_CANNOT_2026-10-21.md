**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Claim:** `say-whether-this-book-can-ever-tell-the-key-from-flat` (Lane 0 delivery)

# B11's within-segment test: six seeds can resolve the measured effect; one book cannot, even at 400 households

Measured 2026-10-21, read-only, no code changed. The reading is the same one 27ca9dc7a graded:
`backtest_run_output(run_output_8b6fea024_20261019T033010Z.json, cut, switch_on_default=True,
rescale_over="fit_window")`, field `departure_ranking_within_segment`. The probe is
`/tmp/b11_power_probe.py`, run from the repo root. It reproduces 27ca9dc7a's se to four places.

## What each count counts, before anything is divided

- **Account:** a billing account, meaning a household with its fuels merged (`_billing_account_id`).
  Not a supply point.
- **Graded:** an account supplied at the cut month (December of the cut year). Accounts that joined
  after the cut or left before it are excluded.
- **Departer:** a graded account that left at any time in the held-back window, from the cut to
  2025-06. The window is 54 months at 2020, 30 at 2022 and 18 at 2023. So this is a count per
  window, **not per year**.
- **Stayer:** a graded account still supplied at the end of the book.
- **Same-segment pair:** one departer and one stayer with the same segment label, counted m·n per
  segment. A segment with fewer than 2 departers or fewer than 2 stayers is excluded.

## The table (8b6fea024 book, as published)

| cut | graded | departers | stayers | same-seg pairs | segments excluded | estimate | half-width | se |
|---|---|---|---|---|---|---|---|---|
| 2020 | 184 | 75 | 109 | 4,772 | resi gas (1 dep, 5 stay; 5 pairs) | +0.061 | 0.059 | 0.0300 |
| 2022 | 192 | 42 | 150 | 3,565 | resi gas (0 dep, 5 stay) | +0.035 | 0.073 | 0.0374 |
| 2023 | 201 | 32 | 169 | 3,264 | resi gas (0 dep, 5 stay) | +0.075 | 0.090 | 0.0461 |

Where the variance comes from, by segment. The DeLong term from departers is V10/m, and the term
from stayers is V01/n.

| cut | resi dual: m, n, dep var, stay var | resi electricity: m, n, dep var, stay var |
|---|---|---|
| 2020 | 59, 73, 0.00045, 0.00062 | 15, 31, 0.00111, 0.00160 |
| 2022 | 29, 105, 0.00127, 0.00046 | 13, 40, 0.00493, 0.00150 |
| 2023 | 24, 122, 0.00204, 0.00049 | 8, 42, 0.00670, 0.00152 |

**The departers set the width, not the pairs.** At 2022 and 2023 the departer term is 3–4× the
stayer term. **The item's own unit was the wrong currency, and I am correcting it here:** "how many
pairs" has no single answer. If one book is scaled by k, its pairs grow by k² and its variance falls
only by 1/k. If S independent seeds are pooled, the pairs grow by S and the variance falls by 1/S.
The comparable quantity is the variance, so I state every answer below as a multiple of today's book
or a number of seeds.

## How much book puts the measured effect clear of zero

Multiples of today's book, with the variance taken to scale as 1/k at the same composition:

| cut | effect | point exactly at the 95% bound | 80% power at 95% | 80% power, Bonferroni over 3 cuts |
|---|---|---|---|---|
| 2020 | +0.061 | 0.93× | 1.89× | — |
| 2020 | +0.075 | 0.61× | 1.25× | — |
| 2022 | +0.061 | 1.45× | 2.96× | — |
| 2022 | +0.075 | 0.96× | 1.96× | — |
| 2022 | +0.035 (its own point) | 4.28× | 8.74× | — |
| 2023 | +0.061 | 2.19× | 4.47× | — |
| 2023 | +0.075 | 1.45× | 2.96× | — |

## The 400-household founder book (8927e9345)

The prereg has no departures-a-year figure, so I derived one. Today's 400 supply points are **233
founder households**, and 227 of them appear in the 8b6fea024 book. At the run's seed, 400
households is 689 supply points. The campaign keeps 96.5% of its customer-year room. I assumed that
new founders depart, and carry key information, at today's founder rates. That assumption is
untested.

**Most of the graded book at a late cut is campaign wins, not founders.** By 2023 only 55 founders
are still supplied, and 5 of them depart. Adding founders therefore buys little width where width is
most needed.

| cut | departers (founder / campaign) | projected departers | projected stayers | one-seed se | book multiple | half-width |
|---|---|---|---|---|---|---|
| 2020 | 28 / 47 | 93 | 143 | 0.0265 | 1.28× | 0.052 |
| 2022 | 12 / 30 | 50 | 182 | 0.0343 | 1.19× | 0.067 |
| 2023 | 5 / 27 | 35 | 201 | 0.0439 | 1.10× | 0.086 |

The chance of clearing zero (95%, z), taking the true effect to equal the measured point:

| cut | effect | 1 seed | 6 seeds pooled (z) | 6 seeds, the prereg's rule (mean of 6, t on 5 df): half-width | seeds for 80% power (z) |
|---|---|---|---|---|---|
| 2020 | +0.061 | 0.63 | 1.00 | 0.028 | 1.5 |
| 2020 | +0.075 | 0.81 | 1.00 | 0.028 | 1.0 |
| 2022 | +0.061 | 0.43 | 0.99 | 0.036 | 2.5 (3.3 Bonferroni) |
| 2022 | +0.075 | 0.59 | 1.00 | 0.036 | 1.6 |
| 2022 | +0.035 | — | — | 0.036, so it does **not** clear | 7.5 (10.1 Bonferroni) |
| 2023 | +0.061 | 0.28 | 0.93 | 0.046 | 4.1 (5.4 Bonferroni) |
| 2023 | +0.075 | 0.40 | 0.99 | 0.046 | 2.7 (3.6 Bonferroni) |

On today's 8b6fea024-sized book, six seeds under the t rule give half-widths of 0.032, 0.039 and
0.048. Those also clear +0.061 at every cut.

## What this says, per year

- **2020.** One 400-household seed resolves +0.075 about four times in five, and +0.061 under two
  times in three. Two seeds suffice.
- **2022.** At +0.061 or more, three seeds suffice, and six clear it comfortably. At 2022's own point
  of +0.035, eight to ten seeds are needed, and six do not reach it.
- **2023.** One seed resolves it in only 28–40% of runs. At +0.061, four to six seeds are needed, so
  six is at the edge once Bonferroni is applied.
- **The answer to the item's question is no: the book is not too small to ever tell.** At the
  measured effect size, EP17's six seeds **can** answer, provided each seed's book is at least about
  this size. One book, even at 400 households, cannot: the extra founders add 10–28% to the
  information. So what limits this is the number of independent books, not the key and not the
  founder count.

## What I cannot say, ranked by how much it matters

1. **EP17's analysis book is not this book.** The varied-draws prereg
   (`PREREG_B11_PER_CUSTOMER_AGAINST_FLAT_ON_VARIED_DRAWS_2026-10-16.md`) uses `seed_family`'s
   **40 founders, all_wins** shape. I have not counted its graded departers per cut. If it holds
   materially fewer departers than 32 at 2023, the six seeds fall short at 2023. **GAP.** The next
   read is one run of that shape, counting departers per cut. That needs no comparison and so spends
   no blind seed.
2. **The effect sizes are winner's-curse points.** +0.061 and +0.075 were read off the same book that
   set the width. Per F11, the safe reading is the lower one. On that reading, 2022 at +0.035 is
   beyond six seeds.
3. **Between-seed spread is assumed equal to within-book DeLong se.** The t rule estimates the spread
   from the six seeds. If the world's draws add variance the DeLong term does not see, the
   half-widths above are floors.

## What changes for the director

The `ep17-s-flat-against-per-customer-comparison` row asks for six fresh seeds. This measurement
supports that ask rather than undercutting it. Six seeds is the right order of magnitude for 2020 and
2022 at the measured effect, and marginal for 2023. A bigger founder book is not a substitute. I
have not edited the row. Point 1 is the check that would change this. The next seat to touch the row
should cite this finding beside its evidence.
