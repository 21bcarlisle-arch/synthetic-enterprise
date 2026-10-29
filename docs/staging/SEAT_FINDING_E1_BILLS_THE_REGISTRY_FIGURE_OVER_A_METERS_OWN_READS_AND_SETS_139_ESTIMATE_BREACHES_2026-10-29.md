**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# E1 bills the registry figure over a meter's own reads, and sets 139 estimate breaches (2026-10-29)

**Source:** the grade of `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` on the fresh 209c3350ab book, which
carries E1 (1bdd86b849). Pre-registration with T1/T2 and the results:
`docs/staging/records/SEAT_PREREGISTRATION_ONE_FRESH_RUN_AT_0B2879EF7D_GRADES_THE_SIX_FIXES_IN_CODE_2026-10-29.md`.
It is BLOCKING because the correctness stretch's exit needs zero unexplained breaches. These 191 are
excepted on a cause, and the cause rests on a GAP our own knowledge page names. A cause that rests on
a GAP is not yet an explanation.

## What was measured

Every estimated bill graded on both books (24,887 in common) was compared with
`/var/tmp/est-probe-scripts/est2.py`, which records each bill's estimate and the row's band:

- 1,451 estimates moved between 37abacdf42 and 209c3350ab. **All 1,451 are in E1's registry branch**: the
  company's reads span under 182 days (gas: 273) from the change-of-supply read to the latest actual.
  No estimate outside the branch moved.
- 139 breaches are new. Each is the same bill under the same band with only its estimate moved.
- 23 breaches are gone, all in the branch.
- That leaves 269 breaches: 191 in the branch (52 carried over, 139 new) and 78 outside it, carried
  over unchanged. The 78 are the older open cause, the estimator's reference window against the
  row's.

Example: C6 electricity. Its actual reads are Apr 2016 (2,077 kWh) and Jul 2016 (1,129 kWh), a span of
122 days from the change-of-supply read. Each estimate from Aug to Nov 2016 is now the registry figure
shaped, 3,131 to 4,342 kWh a month. Before E1 it was 1,402 to 1,944. Nov 2016's estimate is 144.7 kWh/day
against a band of 40.6 to 75.5 drawn from its own reads. Within one account the ratio to the old
estimate is constant (SYN-2016-538g: 1.47 on all 15 bills), which is what a registry level held in
place would leave.

A correction: the first classifier put 47 of the new breaches outside the branch. It measured from the
first actual read to the bill's start. E1 measures from the change-of-supply read to the latest actual
read. Re-classed under E1's own definition, all 139 are in the branch.

## The conflict

E1 (`docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §7) bills the
registry EAC/AQ until the reads span an advance. It cites the BSC rule that "an EAC is used where two such
meter readings [at least 6 months apart] are not available". That is a **settlement** rule. The same
page's §5 records as established that the registry figure "ranks second, behind the supplier's own
metered history, under SLC 27.15". Its §7 GAP says that whether a supplier's **billing** estimate holds
the registry figure for six months, or blends it with early reads, is not published.

So 191 breaches of a row written blind from the knowledge pages turn on a GAP, and the established half
of the evidence (SLC 27.15's ordering) leans against E1. E1 was right about its own target: a single
short first month (138 kWh) should not set a year of estimates, and it took
`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` from 13 to 6. But it fixed that by discarding reads that
span four months, not only the one-read case.

## What would settle it, in order

1. The practitioner side (K4). Published sources stop at the GAP. A supplier's billing practice in the
   first six months is the kind of thing too obvious to the trade to be written down. Read BSCP504's EAC
   weighting of a new advance against the prior EAC first, because the page says it was not read.
2. **Recommendation, if nothing better arrives:** blend. Weight the company's own advance against the
   registry figure by the span it covers, so that one short month moves the estimate little and four
   months move it a lot. That is BSCP504's own shape for the settlement EAC. It keeps E1's gain on the
   one-read runs and stops a 122-day span being ignored. It needs a knowledge-page amendment (K8) before
   any build, and a fresh run to grade.
3. Until then the exception carries the 191 as this class, at a ceiling of 269.
