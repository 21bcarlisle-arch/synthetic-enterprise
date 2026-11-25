**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `the-supplier-estimates-an-unread-month-from-the-accounts-own-history-first`

# Pre-registration: the first book built with `bill_estimate_reads_the_same_period_first` on (25 Nov 2026)

Filed before any book has the flag on. No arm has been run. The box belongs to A4 and the etarms seeds.

## What the switch does, said first

An unread month is billed first from the account's own read advance over the same calendar period one
or two years earlier (`company/billing/unread_month_estimate.same_period_advance`). That advance must
span under 182 days and cover at least half of the shifted period. Within it, the month is shaped by
the class profile. Every other route is unchanged where no such advance is held.
Knowledge: `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` s.5b.

## The comparison

Base: f2c6979d01, with SPAR 0.5 and the annualised advance on, flag off. Arm: the same commit and
world, with only the flag on. Any other change to the book voids the comparison, and the arm is then
graded against a flag-off twin built at the same commit.

## Predictions

1. **E1 (`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`) breaches: 7 → 4, range [3, 7].**
   - Rows 1, 2 and 5 of the finding leave. By hand they are 1.73, 0.94 and 1.68.
   - Rows 3 and 4 stay. They are 3.93 and 3.15, and row 4 is the closest to the band.
   - Row 6 stays, at about 4.0.
   - Row 7 (gas, no earlier year) stays.
   - Up to three new breaches may appear. Candidates are homes whose earlier season was a void or a
     different occupier, and spring-heavy advances shaped into summer, as in row 4.
2. **The book's own coupled electricity gap (`tools.couple_w2_36_d48 --book`): 0.3955 → 0.39, range
   [0.37, 0.405].** The gap only reads runs no actual read closed: final estimated runs and runs open
   at 2025-06. The switch moves those only where they fall in a season the account read before. So
   the effect is small, and it points down.
3. **The (a) cause is not cleared as a class.** At least two of rows 1 to 6 still breach.

## Refuted if

- E1 is above 7, meaning the switch adds more breaches than it removes.
- The gap is above 0.405.
- Either of rows 1 and 2 still breaches. They are the two where the account held the whole season
  within the lookback.

If refuted, the switch stays off, and the finding names the account that refuted it.

## If it holds

Rows 1, 2 and 5 leave the exception's licensed set. The exception is re-based down to the count its
reason still covers, and its reason is amended. The cause becomes "no same-season advance held within
two years", which is true of rows 3, 4 and 6. Turning the switch on is a separate decision, made on
the graded book and recorded beside this file.
