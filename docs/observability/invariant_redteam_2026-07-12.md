# Adversarial red-team: domain-invariants library vs pre-bill validation gate

**Date:** 2026-07-12
**Scope:** `company/compliance/domain_invariants.py` (the anchored invariants library) and
`company/billing/pre_bill_validation.py` (the Tier-1 pre-bill gate that consumes it).
**Method:** read both files in full, then constructed concrete adversarial bill/scenario dicts
and called the actual `check_*()` / `validate_bill()` functions from a live Python REPL against
this repo's real code (no mocking) to confirm each finding. Every finding below is labelled
**CONFIRMED** (executed against real code, transcript included) or **PLAUSIBLE** (reasoned,
not executed) per this project's R9 evidence discipline. This is a read-only review — no
repo file was modified as part of this exercise.

---

## Finding 1 — Most of the invariants library is never wired into any check (CONFIRMED)

`ALL_INVARIANTS` lists 28 invariants. Grepping the whole codebase for actual `.check(...)` call
sites (not just definitions) shows only **9 of 28** are ever consumed by any `check_*()`
predicate anywhere:

| Wired (9) | Consumer |
|---|---|
| `VAT_RESIDENTIAL`, `VAT_SME` | `check_vat` → **pre-bill gate** |
| `RESI_CONSUMPTION_ENVELOPE_ELEC/GAS` (annual) | `check_resi_consumption_plausible` → `population_sanity.py` only (population-level, not pre-bill) |
| `RESI_CONSUMPTION_ENVELOPE_ELEC/GAS_MONTHLY` | `check_resi_bill_consumption_plausible` → **pre-bill gate** |
| `UNIT_RATE_ELEC/GAS_RESI_BY_YEAR` | `check_unit_rate_plausible` → `population_sanity.py` only |
| `BACK_BILLING_CAP_RESPECTED` | `check_back_billing_cap_respected` → **pre-bill gate** |

**Never consumed by any `check_*()` call, anywhere, in the whole codebase (19 of 28):**
`STANDING_CHARGE_ELEC_RESI/SME`, `STANDING_CHARGE_GAS_RESI/SME` (all 4), `NON_COMMODITY_ELEC_RESI/SME`,
`NON_COMMODITY_GAS_RESI/SME`, `NON_COMMODITY_SHARE_OF_BILL` (all 5), `TDCV_ELEC_LOW/MEDIUM/HIGH`,
`TDCV_GAS_LOW/MEDIUM/HIGH` (all 6), `NET_MARGIN_PCT_OF_REVENUE`, `GROSS_MARGIN_PCT_OF_REVENUE`,
`BAD_DEBT_RATE_SME` — and `BAD_DEBT_RATE_RESI` is only ever read as a bare `.low` constant
(`crisis_bad_debt_validator.py`), never through its own `.check()` predicate.

Practical consequence, confirmed by actually calling `validate_bill()`:

```
bill = resi electricity, 300 kWh in Jan-2024, correct 5% VAT arithmetic,
       standing_charge_gbp = 15.50 (= 50p/day; band says 25-35p/day),
       non_commodity_amount_gbp = 5000.00 (= 16,667 GBP/MWh; band says 50-65 GBP/MWh)
validate_bill(bill) -> ValidationOutcome.PASS, reasons=[]
```

A non-commodity cost more than **250x** the anchored plausible band, and a standing charge
43% above its band, both pass the Tier-1 "100% of bills, zero tolerance, continuous, not
sampled" gate silently. The `pre_bill_validation.py` module docstring's claim ("Checks every
bill against the Tier-1 obligations... using the anchored predicates") is materially overstated
— only VAT, monthly resi-consumption, and back-billing are actually enforced pre-issue; standing
charge, non-commodity cost, TDCV bands, and margin/bad-debt are either population-level/sampled
(a different tier) or entirely inert.

---

## Finding 2 — Non-resi (SME/I&C) bills get zero consumption-plausibility check of any kind (CONFIRMED)

In `validate_bill()`, the entire consumption check is gated: `if segment == "resi": ...`. There
is no equivalent check for any other segment — and no SME-specific consumption invariant exists
in the library at all to plug in even if the gate were extended.

```
bill = segment="sme", total_consumption_kwh = -500.0 (negative), correct 20% VAT arithmetic
validate_bill(bill) -> PASS, reasons=[]

bill = segment="sme", total_consumption_kwh = 500,000.0 (a plausible units-error, e.g. kWh
       entered as Wh), correct 20% VAT arithmetic
validate_bill(bill) -> PASS, reasons=[]
```

Both a negative and a 500,000 kWh/month SME bill sail through the Tier-1 gate. Combined with
Finding 1 (no non-commodity/standing-charge check either), an SME bill is effectively checked
for only one thing pre-issue: whether its VAT rate arithmetically matches its own self-declared
segment (see Finding 5).

---

## Finding 3 — Back-billing write-off is checked for existence, never for magnitude (CONFIRMED)

`check_back_billing_cap_respected()` only verifies `catchup_written_off_gbp > 0` and that the
ledger balances (`adjustment + written_off == raw_delta`, ±£0.01). It never computes what
*should* have been written off (the portion of the catch-up period before the 365-day
protected-start boundary) and compares magnitudes.

```
bill = catchup_applied=True, catchup_direction="undercharge",
       catchup_period_start="2019-01-01", period_end="2024-01-31"  (~5 years, way past cap),
       catchup_raw_delta_gbp=5000.00,
       catchup_written_off_gbp=0.01,      # token 1p "write-off"
       catchup_adjustment_gbp=4999.99     # customer charged essentially the full amount
check_back_billing_cap_respected(bill) -> True   # "cap respected"
```

A customer can be charged 99.998% of a five-year-old, cap-breaching undercharge with a
one-penny symbolic write-off, and the SLC 21BA gate reports full compliance. This is arguably
the most consequential finding: it defeats the entire purpose of the check the
`ADVISOR_STEER_BACKBILLING_GATE.md` steer asked for, using a value that technically satisfies
the letter of the code (`written_off > 0`) while completely failing its intent.

---

## Finding 4 — Malformed/missing `catchup_direction` or `catchup_period_start` silently passes (CONFIRMED)

The function early-returns `True` (compliant) whenever:
- `bill.get("catchup_direction") != "undercharge"` — a case-sensitive, exact-string match, so a
  typo/case variant like `"Undercharge"` is treated identically to "not an undercharge at all"
  and passes.
- `catchup_direction` is missing entirely (`None`).
- `catchup_period_start` or `period_end` is missing.

```
Same 5-year, £5,000, zero-write-off breach as Finding 3, but varying one field at a time:

catchup_direction = "Undercharge" (capital U)      -> check returns True  (should be False)
catchup_direction absent (key deleted)             -> check returns True  (should be False)
catchup_period_start absent (key deleted)          -> check returns True  (should be False)

Control -- catchup_direction = "undercharge" exactly, all fields present, same facts
                                                    -> check returns False (correctly HELD)
```

The control confirms the check's core logic is otherwise sound — the gap is specifically in
trusting well-formedness of `catchup_direction`/`catchup_period_start` rather than validating
or defaulting them defensively. A real upstream bug (a typo in whatever code sets
`catchup_direction`, or a code path that forgets to populate `catchup_period_start`) would
silently disable the entire back-billing Tier-1 control for every affected bill, with no error
raised anywhere.

---

## Finding 5 — Segment is self-declared and never independently cross-checked (CONFIRMED)

`check_vat` and `check_resi_bill_consumption_plausible` both key off `bill["segment"]` as
ground truth. Neither the invariants library nor the pre-bill gate has any independent signal
(meter profile class, tariff code, MPAN/MPRN classification) to catch a bill whose declared
segment is simply wrong. This is the R10 "C6 SME-as-Household" defect class, but recurring at a
consumption scale too small to trip the wide (500-15,000 kWh/yr, or 15-2100 kWh/~30days) resi
envelope:

```
bill = segment="resi" (actually a small SME premises, e.g. a corner shop),
       total_consumption_kwh=320 (plausible for either resi or a small SME),
       VAT arithmetic = 5% (internally consistent with the DECLARED, wrong, segment)
validate_bill(bill) -> PASS, reasons=[]
```

Both checks pass simultaneously because both are self-consistent with whatever segment string
sits on the bill — the gate can only ever catch a segment mislabel when the OTHER declared
facts (consumption, in this design) are inconsistent with the true segment, never when they
happen to also fit. Real underpaid VAT (15 percentage points, ongoing every billing cycle) is
undetectable by this library as currently wired.

---

## Finding 6 — Per-bill monthly envelope has no cross-bill/annual visibility (CONFIRMED)

The Tier-1 gate only ever validates one bill in isolation via the monthly-scaled envelope
(`RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY`, 15-2100 kWh/~30days). The separate annual envelope
(`RESI_CONSUMPTION_ENVELOPE_ELEC`, 500-15,000 kWh/yr) that WOULD catch a sustained implausible
rate is never called from `validate_bill()` — it only runs later, as a population-level check
in `population_sanity.py`, and only for a customer-year with ≥60 days of accumulated billing
history.

```
bill = segment="resi", electricity, 31-day period, 2000.0 kWh
validate_bill(bill) -> PASS, reasons=[]              # well inside the monthly band (high ~2131 kWh for 31 days)

If this rate recurred monthly: annual-equivalent = 2000 * 365/31 = 23,548 kWh/yr
check_resi_consumption_plausible("electricity", 23548.4) -> False   # fails the annual band by ~57%
```

A sequence of consecutive bills each individually just under the per-bill ceiling would all
issue through the zero-tolerance Tier-1 gate before the population-level annual check (running
on a different cadence, with its own 60-day minimum-coverage carve-out) has a chance to flag the
class — a timing/coverage gap relative to the gate's own "zero tolerance, continuous, not
sampled" stated principle.

---

## Finding 7 — Unit-rate-by-year's asymmetric margin lets a near-crisis rate pass for a calm year (CONFIRMED, lower severity — documented tradeoff)

`YearlyRangeInvariant`'s upside margin is deliberately wide (`high_margin=0.5`, i.e. +150% of
anchor) per its own docstring, to avoid false positives on legitimate fixed-term pricing. But
this also means:

```
Year 2020 (real cap anchor: 157 GBP/MWh, a calm pre-crisis year)
plausible_range(2020) -> (62.8, 235.5)
check_unit_rate_plausible("electricity", 2020, 234.0) -> True
```

234 GBP/MWh is ~49% above the real 2020 cap and sits within a few pounds of the actual 2021
crisis-onset rate (183) and not far off 2022's peak (305) — yet it registers as "plausible" for
a genuinely calm year. This is a real, confirmed exploitable gap in year-precision, but it is
also the check's own documented, deliberate design tradeoff ("still catches gross
implausibilities... not year-on-year precision") and it is not even wired into the pre-bill
gate today (population-sanity only), so it's ranked lowest of the confirmed findings.

---

## Finding 8 — `jurisdiction` field is pure decoration, never enforced (CONFIRMED via exhaustive grep)

Every invariant dataclass (`RateInvariant`, `RangeInvariant`, `YearlyRangeInvariant`,
`StructuralInvariant`) carries a `jurisdiction: str = "UK"` field, added per
`ADVISOR_STEER_BACKBILLING_GATE.md` item 2 specifically so a future non-UK invariant wouldn't
silently inherit the UK default. `grep -rn "\.jurisdiction\b" --include="*.py"` across
`company/`, `saas/`, `simulation/`, `tools/` returns **zero matches** outside the dataclass
definitions themselves. No `check_*()` function, no consumer, reads or asserts `.jurisdiction`
against anything. It is schema-only, not an active control — today this is harmless (no
non-UK invariant or bill exists yet), but the field currently provides no actual protection: a
mis-tagged or genuinely non-UK bill would not be caught by "jurisdiction" at all, only by
whatever numeric coincidence its rates/bands happen to share with UK law. Worth closing before
any Epoch/portability work (the project's own stated multi-market destination) adds a second
jurisdiction's invariants.

---

## Minor / non-exploitable note

`check_vat()`'s second condition (`abs(actual_rate - expected) <= invariant.tolerance`) is
logically redundant with `invariant.check(actual_rate)` — by construction `invariant.value ==
expected` on both branches, so the two conditions are always equal. Not exploitable, just dead
logic; noted for completeness, not ranked as a finding.

---

## Ranked severity (most severe first)

1. **Finding 3** — back-billing write-off checked for existence only, not magnitude: a 1p
   token write-off validates a £5,000, 5-year-old undercharge as "cap respected." Defeats the
   explicit intent of the SLC 21BA control with a trivially satisfiable letter-of-the-code
   condition.
2. **Finding 1** — 19 of 28 invariants (all standing-charge, all non-commodity-cost, all TDCV,
   both margin invariants) are never invoked by any check function anywhere — the Tier-1 gate
   cannot catch absurd standing charges (confirmed: 50p/day vs 25-35p band) or non-commodity
   costs (confirmed: 16,667 GBP/MWh vs 50-65 band) at all, contradicting the gate's own
   "100%... zero tolerance" docstring claim.
2 (tie). **Finding 4** — malformed/missing `catchup_direction`/`catchup_period_start` silently
   passes a real, severe back-billing breach; a single upstream typo or missing-field bug
   disables the whole SLC 21BA control with no error raised.
4. **Finding 2** — non-resi (SME/I&C) bills get zero consumption-plausibility check of any
   kind; negative consumption and a 1,666x units-error both pass silently.
5. **Finding 5** — segment is self-declared and never independently cross-checked; a small SME
   mislabeled "resi" underpays VAT by 15 points every cycle, undetected, because both wired
   checks are self-consistent with the (wrong) declared segment.
6. **Finding 6** — the per-bill monthly envelope has no cross-bill/annual visibility; several
   consecutive bills each individually near the per-bill ceiling all issue before the
   population-level annual check (different cadence, 60-day minimum coverage) can flag the
   implausible sustained rate.
7. **Finding 7** — unit-rate-by-year's wide asymmetric upside margin lets a near-crisis rate
   pass as "plausible" for a calm year (documented tradeoff, and not wired into the pre-bill
   gate today — lowest severity of the confirmed findings).
8. **Finding 8** — `jurisdiction` field is schema-only, never read by any consumer; no active
   protection today (no multi-jurisdiction bills exist yet), but should be wired before any
   portability/second-market work per the project's own stated constraints.
