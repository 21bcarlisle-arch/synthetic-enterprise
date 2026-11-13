# Weekly balance review for the week from Mon 16 Nov 2026

*Delivery seat, Fri 13 Nov. This is the first review under the director's ruling of 11 Nov
(`docs/staging/advisor/done/DIRECTOR_RULING_END_THE_FEATURE_FREEZE_A_THIRD_TO_FEATURES_AND_A_WEEKLY_BALANCE_REVIEW_2026-11-11.md`,
point 4). It is a proposal. If he has not answered by the Mon 16 Nov 03:00 GMT reset, it stands,
and he can change it at any time.*

## 1. First feature item: the value test redesign, with its predictions filed before any run

The director's steer of 13 Nov names this the first item of the feature third. It is the thesis
test: per-customer decisions against an efficient flat supplier. The amended design is
`docs/design/THE_VALUE_TEST_REDESIGN.md` (§3a, rules 2–5, §5, §6). In short:

- **Where it stands today, per household per year.** On the 8 Oct run (272 households, 1,831
  household-years, 2016–2025):
  - The belief cannot yet tell who leaves. Its AUC is 0.52, against 0.50 for a coin, with an
    interval of 0.41 to 0.65. It expects 64% of households to stay; 87% do.
  - The per-customer arm earns **about £3 more per household-year** than a £2/MWh flat rule.
    Across households that is 0.6 standard errors from zero.
  - A later unpublished run on 780 households reads the same way: AUC 0.55, and +£1.12 per
    household-year.
  - **Honest answer: no evidence yet that per-customer value works, and none that it does not.**
- **The redesign.**
  - One world, one tree, one book.
  - The baseline is the efficient-supplier margin: about £44 per household-year from Oct 2023,
    and 1.9% of revenue before that. It replaces £2/MWh.
  - A paired standard-variable arm (left at the cap, against placed on a better tariff).
  - The write-off rule is settled at an 86% final-account loss (84–88%, Centrica grade P),
    replacing about 95% today.
  - Scored on money, time and carbon apart.
- **Predictions filed now** (§5, P1–P10). The belief's skill comes first:
  - AUC between 0.45 and 0.60, with an interval that includes 0.50.
  - Calibration error between −0.27 and −0.10.
  - Then the money: **between −£3 and +£3 per household-year** against the efficient flat
    supplier, interval including zero.
- **Size.** To tell £3 per household-year from zero takes about **4,900 households** if the
  spread between households is real heterogeneity. It takes about **410 households at 12 draws
  each** if it is the luck of each household's rolls. One run on this machine holds about 1,200.
  - The first step (a 12-draw family, about 9 machine-hours, about 1 point) measures which of the
    two holds. P6 predicts roll noise is at least half.
  - If it is not, this machine cannot settle a £3 effect in one run, and that comes back to him as
    a finding with its remedy and its cost.
- **Cost.** About **16 points (11–24) and about 82 machine-hours** for the whole redesign. Next
  week takes steps 1–4, about 8 points. The sized run probably reads in the week of 23 Nov.
- **No arm has been run for this.**

## 2. What the feature share actually was this week, and why

**Measured, not recalled.** The figures are landed sessions since the Mon 9 Nov reset, priced in
dollars from the session logs and classed by the paths each session's commits touched
(`tools.work_cost_estimate.classify`). 174 landed sessions, $459:

| Class (by path) | Sessions | Share of landed spend |
|---|---|---|
| Records and staging (`record`) | 46 | 22% |
| Grading runs (`docs/staging/records/`) | 34 | 20% |
| Harness (`background/`, `tools/`, `tests/`) | 35 | 16% |
| Supplier code (`company/`, `saas/`) | 17 | 14% |
| World code (`sim/`, `simulation/`) | 18 | 11% |
| Knowledge | 15 | 11% |
| Site pages | 9 | 6% |

**The path class is not the purpose.** I read the 35 world and supplier sessions' commits one by
one:

- **34 are correctness fixes, or the grading of them.** They cover the close refund, the level-DD cure and dunning, the
  Bacs-day direct debit, repayment dating, the closing dual-fuel netting (N29), the dual-fuel meter
  reading day (N30) and the SME catch-up VAT lines.
- **One is a world fidelity feature**: ElecLink and Viking in the historic interconnector mix,
  $2.3.

So **the feature share this week was about 0.5% of landed spend, against the third the ruling set.**

**Why.** These are the causes I can name. I have not measured how much each one contributed.

1. **Correctness had first claim while a book was refused.** The site did not publish a
   gate-passing book until 11 Nov 20:31 (the 6fe7827ab2 book). The ruling keeps that first claim,
   and it was the right call while the publish was at stake.
2. **The usage trim.** The 11 Nov 18:10 reading paused W3_3 until the reset. The seat's focus
   also held W2_18 and W2_19 in `not_now`.
3. **The share lives in the wrong place.** `feature_share: 0.33` acts on the BUILD draw. Lane 0
   (the seat's own focus) draws ahead of it, and this week the seat's focus was correctness. A
   third of a draw that rarely ran is close to nothing. This is the cause I rate most likely. It
   has not been measured.

**Correction.** The 11 Nov ruling's "Done" said that 0.33 "is what gives the BUILD draw" this
week's 30% to features. That described the mechanism, not the outcome. The outcome was 0.5%.

## 3. The split proposed for the week from Mon 16 Nov

| Share | % | What it is for |
|---|---|---|
| Correctness and backlog | 42 | First claim whenever a book is refused. The live money findings in the staging root, with the serious classes first. Grading runs count here. |
| **Supplier features** | **18** | **The value test redesign, steps 1, 3 and 4 (§1)**, then the standard-variable arm's knowledge page |
| **World features** | **15** | The write-off rule (value test step 2), then the forward weather and price steer (11 Nov), then W3_3 once the reset lifts its pause |
| Knowledge | 15 | K8 pages ahead of each build above: `debt_and_collections.md` P5, the pre-2019 efficient margin, tariffs and the default tariff |
| Harness | 10 | Only what keeps the machine running and learning |

- **The feature third is held at 33%** (18 + 15).
- **The trim comes from harness first.** This week, harness, records and staging took 38% of
  landed spend. Records are mostly the machine writing to itself.
- **Holding it is a mechanism change, not a number.** The third has to sit where the draw
  actually happens. So the value test steps go onto the seat's lane-0 focus for the week. They will
  not be left to the 0.33 BUILD share, which this week showed lane 0 can starve.
- `feature_share` stays at 0.33.

**The measures the ruling names, as far as this review could read them:**

- **Serious classes per cold read**: one each on the eleventh and twelfth reads (N29, N30). That
  is converging.
- **The site** published on 11 Nov.
- **Usage**: 62% at Fri 06:00, burning about 0.50 points an hour. That ends the week at about
  96–97%, so there is no weekend excess (advisor reading, 13 Nov).
- **Not measured in this review**: the learning loop's hit rates and the week's regression count.
  They are owed by the Friday step of `background/weekly_rhythm.py`. That step has not been filed
  this week; the rhythm's state still shows Monday's step open. I state that rather than fill the
  slot.

**The accelerate list proposed for the week** (from Saturday, only when more than the roughly
10-point reserve is unspent):

1. Value test step 1, the 12-draw family. About 1 point and 9 machine-hours, and it decides the
   book.
2. The `debt_and_collections.md` P5 amendment for the write-off rule. About 0.6 points.
3. A second gate-passing book on the current tree. Grading-run class.

It is written into `priority_order.yaml` `accelerate:` at the reset if he has not changed it. It is
not written there before.
