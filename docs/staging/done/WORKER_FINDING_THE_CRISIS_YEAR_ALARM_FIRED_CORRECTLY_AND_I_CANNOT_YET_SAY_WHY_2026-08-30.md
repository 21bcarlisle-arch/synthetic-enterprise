**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The crisis-year alarm fired exactly as it was armed to, and I cannot yet say why — but it is not what the alarm guessed

**Found:** 2026-08-30, in the HEAD red census. `tests/tools/test_year_spotlight.py::
test_crisis_year_2022_worse_than_2020` is `XPASS(strict)`.

**This is not a stale xfail and must not be flipped to a pass.** It is a control doing precisely
the job it was armed for, three days after it was armed, and the honest output is a measurement
plus "I cannot yet say".

## The control's own words

```
STRICT so an XPASS alarms: if 2022 ever does become the worse year, the cap modelling or
the pass-through has changed and this seat wants telling.
```

Told. 2022 is now the worse year on both denominators the original finding used.

## The measurement, against the figures the xfail's own reason records

`WORKER_FINDING_THE_2022_CRISIS_IS_NOT_VISIBLE_IN_DOMESTIC_BILL_SHOCK_2026-08-27.md` recorded
three independent denominators, all agreeing that 2020 was the worse year. Two of them are
recomputable from `site/data/dashboard.json` today:

| denominator | 2022 then | 2020 then | 2022 now | 2020 now |
|---|---|---|---|---|
| organic shocks per active account | 3.57 | 4.72 | **4.35** | **3.90** |
| organic shocks per active *electricity* account | 6.56 | 8.57 | **6.32** | **5.41** |

**2022 barely moved. 2020 collapsed.** On the electricity denominator 2022 went 6.56 → 6.32, a
4% drift; 2020 went 8.57 → 5.41, a 37% fall. The ordering flipped because the comparison year
changed, not because the crisis year did.

So the alarm's stated hypothesis — *"the cap modelling or the pass-through has changed"* — is
**not supported**. A pass-through change would move 2022, the year with the wholesale spike behind
it. Something moved 2020.

## And the series shape says the comparison itself may be the wrong instrument

Organic shocks per active electricity account, whole record:

| 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| 2.58 | 3.87 | 4.41 | 4.81 | 5.41 | 6.00 | 6.32 | 5.83 | 6.49 | 3.00 |

That is a **ramp**, not a spike. It rises almost monotonically from 2016 to 2022, dips, and rises
again to a 2024 value (6.49) HIGHER than the crisis year. 2025 at 3.00 is a partial year.

A test that asks "is 2022 greater than 2020" on a series with a decade-long upward drift is
answering a question about the drift, not about the crisis. **It will pass for the wrong reason
whenever the drift is steep enough, and its passing today may be exactly that.** The 2024 value
exceeding 2022 is the clearest evidence: no crisis story explains 2024 being the worst year in the
record.

## Why I am not attributing it

More than one thing changed between 2026-08-27 and today, and the standing rule is that a result
which moves while two variables moved cannot be attributed. Between those dates the tree took the
competitor-reference landing (2026-08-28), the arms work, and the ordinary run-to-run book
evolution. I have not established which, and guessing would be worse than the gap.

**What is owed is a one-variable run**, and the prediction goes on the record now, before it:

> The 2020 fall is a BOOK-COMPOSITION effect, not a shock-physics one. Prediction: holding the
> roster fixed at its 2026-08-27 composition and re-running reproduces 2020 ≈ 8.57 and leaves
> 2022 ≈ 6.5, i.e. the original ordering. If it does not — if 2020 stays near 5.4 on the old
> roster — then something in the shock computation itself moved and this becomes a much more
> serious finding about a published series.

Filed as a prediction so that whichever way it lands, it was written before the answer.

## What must not happen to this test

Three wrong repairs, named so they are not attempted:

1. **Flipping the xfail to a plain pass.** It would record that 2022 became the worse year and
   silently accept an unexplained cause. The strictness is the whole value.
2. **Deleting the xfail marker and asserting the new ordering.** Same defect, tidier.
3. **Adding a third normalisation until the old ordering returns.** The original finding says in
   as many words why it did not do this — *"R12 is why the metric was not normalised a fourth
   time until it passed"* — and that restraint is the best thing about it.

**Leave it red.** A control that is correctly red is not a problem to be cleared; it is the
project working. It should go green when the one-variable run explains the move, or its subject
should be replaced by one that asks about the crisis rather than about a two-year comparison on a
drifting series.

## A separate thing the same table exposed, not chased here

`worst_shock_pct` alternates between roughly 1,240 and 3,800 across the decade — bill shocks of
1,200% to 3,800%. Whatever those are, they are not domestic bill shocks, and a metric named
"worst shock percent" carrying a 3,799 in 2016 is either a different unit or an absurdity the
`domain_invariants` class check should own. Not investigated: it is not this finding's subject
and it is not the census's. Recorded so the next reader of that column has been warned.
