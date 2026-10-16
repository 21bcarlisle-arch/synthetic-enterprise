**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`

# Pre-registration: what a ratio screen finds among the world's voids and thefts

**Written before the probe exists or has run.** Finding:
`docs/staging/WORKER_FINDING_W2_36_THEFT_NOW_ARISES_AT_A_PREMISE_AND_AT_THE_IAS_OWN_VOLUME_IT_LOOKS_LIKE_A_VOID_2026-10-16.md`,
which predicted that "voids outnumber thefts among the screen's zero-ratio premises".

## What is being measured

The screen is `company/billing/theft_indicator.classify_anomaly`: registered kWh over EAC, below
a cut. **It has no sourced cut**, so the probe sweeps cuts and fixes none. "A flag" depends on the
**window** the ratio is taken over, and a void and a theft differ most in length, so the two are
measured apart:

- **monthly**: one calendar month, which is what a smart read gives;
- **annual**: one calendar year, which is what an annualised traditional read gives.

The population is one premise per tenure row, 2016-2025, 120 months. A premise's moves are the
world's own (`draw_home_move`), its void the world's own (`void_end`), and its theft the world's
own (`premise_theft_months`). Occupied use is flat at the EAC.

**Named simplification:** flat use means the probe counts flags from voids and thefts only. A
low-use household also flags, and that third source is not priced here. So the probe answers
"of the flags voids and thefts cause, which cause which". It does not answer what share of all
flags are thefts.

Owner-occupier voids are a GAP (`q1_void_months_owner`). Owner premises are printed with no
voids, and the table says so. That is not a finding that owners have none.

## Predictions, by arithmetic, before the run

Per 10,000 premise-years. Thefts give about 1,200 flagged months at any cut (1% of months, ratio 0).

1. **Monthly, ratio below 0.05 (an empty month).** A private-rent void (0.7 months, about 21 days)
   can never empty a whole calendar month, so voids give **0**. A social void (1.15 months, about
   35 days) empties a whole month about 15% of the time, so voids give **about 70**. **Thefts
   outnumber voids by more than 10 to 1 in every tenure.** This refutes the finding's prediction.
2. **Monthly, cut 0.4.** Private voids give about **850**, against 1,200 thefts. Social voids give
   about **550**.
3. **Monthly, cut 0.65.** Private voids give about **1,750**, which is more than thefts. This is the
   only cell where the finding's prediction holds.
4. **Annual, any cut up to 0.9.** Voids give **0**, because the longest void (35 days) takes 9.6% off
   a year. Every annual flag is a theft.
5. **Range ends** (private 0.8 and social 2.0 months). At social 2.0 every void empties at least
   one whole month, so prediction 1 for social rises to about **460 or more**. Thefts still lead.

Grading: each prediction holds if the measured value is within 30% of the figure, or at exactly 0
where 0 is predicted. Grades are written beside each one in this file.

## Grades (same day, after the run)

Run: `python3 -m tools.theft_void_screen_probe --premises 20000 --setting {default,low,high}`,
20,000 premises per tenure, seed 42. Flags per 10,000 premise-years. "Both" means a theft month that
also falls in a void; it is counted apart and is never more than 28.

| Prediction | Measured | Grade |
|---|---|---|
| 1. Empty month (cut 0.05): private voids 0 | 0.2 | **Holds.** The 0.2 is two voids in one month. |
| 1. Empty month: social voids about 70 | 112 | **Misses, by +60%.** My arithmetic counted only months emptied exactly. A 0.05 cut also flags 29 empty days out of 31. |
| 1. Thefts lead by more than 10 to 1 in every tenure | private 1,083 to 0.2; social 1,166 to 112 (10.4 to 1); owner thefts only | **Holds,** though only just for social. |
| 2. Cut 0.4: private voids about 850, social about 550 | 848; 430 | **Holds** (social is −22%). |
| 3. Cut 0.65: private voids about 1,750, above thefts | 1,740, against 1,083 thefts | **Holds.** |
| 4. Annual: no voids at any cut up to 0.9 | 0 up to 0.65. At 0.9: 3.2 private, 1.3 social | **Misses at 0.9.** Two voids can fall in one calendar year: a December void runs on into January, then a new move comes. |
| 5. Social at 2.0 months: empty-month voids 460 or more, thefts still lead | 502, against 1,162 | **Holds.** |

At the high end, the annual cut of 0.9 flags 439 social voids. That is the one annual cell where
voids are not rare. A 61-day void takes 17% off a year.
