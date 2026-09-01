# [WORKER FINDING] The xfail-strict guarding "2022 is not the worse year" has reversed, and the floor is ruled out

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Found:** 2026-09-01, by running the affected test surface before landing the bill-shock population
bound. Not drawn work; found because it sits in the blast radius of the shock series.

## Class registration

**Shape of `measurements_that_mirror`, deliberately NOT consolidated into it.** That class is lane
`H_harness` and this document is lane `D_billing_metering` — the subject is a billing measurement,
not the harness that runs it. `background.finding_classes` refuses the cross-lane membership fail
closed, and it is right to: archiving this under an `H_harness` class would delete
`D_billing_metering`'s own finding while recording it somewhere its lane cannot see. The shape is
named here so the resemblance is on the record without the consolidation being faked.

## The control did exactly what it was built to do

`tests/tools/test_year_spotlight.py::test_crisis_year_2022_worse_than_2020` is
`@pytest.mark.xfail(strict=True)`, and its own reason text ends:

> *"STRICT so an XPASS alarms: if 2022 ever does become the worse year, the cap modelling or the
> pass-through has changed and this seat wants telling."*

**It is now XPASSing.** This document is the telling.

| | marker's recorded figures (2026-08-27) | live, on `run_output_b9418ce19` |
|---|---:|---:|
| organic shock rate per active account, **2022** | 3.57 | **2.96** |
| organic shock rate per active account, **2020** | 4.72 | **1.68** |
| 2022 ≥ 2020? | **no** — the claim | **yes** — reversed |

Both years fell; **2020 fell much further** (−64%) than 2022 (−17%), and that is what flipped the
comparison. The per-bill denominator the marker calls "the one invariant to book size AND tenure"
has moved the same way: it records 0.366 (2022) against 0.398 (2020), and the live artefacts read
**0.248 against 0.164**. Both years differ from the recorded values by a wide margin, so this is not
2022 rising — **it is the whole book being different.**

## It is not this session's work, and it is not the baseline floor

**Not mine.** The fields the assertion reads — `customers.book_annual[].organic_bill_shock_count`,
`active_elec`, `active_gas` — are **byte-identical** between `HEAD` and the working tree at the time
of the bound commit. Verified by a whole-artefact field diff: the only changed keys were `meta`. The
test is red at clean HEAD.

**Not the floor, and this is the part worth keeping.** The obvious hypothesis was
`BILL_SHOCK_BASELINE_FLOOR_GBP` (`41cdd5b51`), which does remove shock events and did reorder the
year series — the predecessor pre-registration measured 2022 going from 617.2% to 42.2% and becoming
the highest year on `avg_bill_shock_pct`. So I ran the one-variable version across the two run
artefacts that differ only in the floor:

| run | 2022 organic/bill | 2020 organic/bill | 2022 ≥ 2020? |
|---|---:|---:|---|
| `fb6e29e6d` **pre-floor** | 0.252 | 0.170 | **yes** |
| `3df8f7400` **post-floor** | 0.248 | 0.164 | **yes** |
| `b9418ce19` current | 0.248 | 0.164 | **yes** |

**2022 was already the worse year before the floor existed.** The floor moved both years by about
4%, changed no ordering, and is refuted as the cause. My own hypothesis, run and killed.

## What I cannot say

**I cannot yet say what did cause it.** More than one thing has changed since 2026-08-27, and
`docs/reports/` holds no run artefact older than today, so the one-variable comparison that would
settle it cannot be built from what is on disk. Saying "the floor did it" would have been available,
plausible and wrong.

The candidates worth a bisect, in the order I would try them, all of which change the *population*
rather than the shock detector:

1. **C1b's SVT route.** It moved roughly two thirds of the domestic book onto the standard variable
   product. `active_elec + active_gas` — the denominator of the reversed rate — is exactly the sort
   of quantity that moves under it, and 2020's denominator behaviour is what flipped this.
2. **Any change to the acquisition/churn draw** since 2026-08-27, which shifts which accounts are
   active in which year. The marker's own history records this confound biting twice before, and
   both times it was diagnosed as a real population-composition difference rather than a bug.
3. **The catch-up/organic split itself**, since the assertion reads `organic_bill_shock_count` and
   not the raw count.

## Why it is `measurements_that_mirror`

The assertion compares two years of a quantity whose denominator is set by the population draw. It
was already normalised three times for exactly that reason — raw count, then per active account,
then the adjacent bounded test — and it has moved again without the shock detector changing. **A
comparison that keeps needing a new denominator is measuring the draw, not the crisis.**

## What is owed, and what must not be done

1. **Bisect the cause** against runs older than today, which means recovering an artefact from before
   2026-08-27 or re-running the pre-C1b world. Until then the marker's reason text states figures
   that are no longer true and should not be read as current.
2. **Do NOT repair it by asserting `rate_2022 >= rate_2020` live.** That pins today's answer and
   re-creates the change-detector this file has already been burned by twice. The coverage the old
   assertion stood guard over was deliberately rehomed into the adjacent
   `test_bill_shock_is_a_live_bounded_quantity`, which asserts bounds on *every* year — that is the
   property, and it is green.
3. **Do NOT retire the marker to make a commit green.** It is not wedging anything: `tests_for()`
   globs `test_<stem>*.py`, so this file is not selected by any path in the bound commit. It was
   left red on purpose.

## What this finding does not claim

Not that the 2026-08-27 finding was wrong when it was measured — three denominators agreed at the
time and the cap argument behind it is sound. Not that 2022 is now correctly the worse year; that it
reads that way is the observation, not a verdict. The claim is only this: **the relationship the
marker guards has inverted, the floor is not why, and nothing on disk can currently say what is.**
