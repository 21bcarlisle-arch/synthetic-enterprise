# Sanity triage 2026-07-11 -- adjudication ledger + verdicts

**Ordered:** 2026-07-10 15:15 (lost overnight in the supervisor stall), re-ordered
2026-07-11 04:43 via NTFY (from_rich_20260711_044314.md, from_rich_20260711_044335.md).
Director's own framing: "did it catch true C6-class defects or cry wolf?"

## The 3 persistent findings

`background/sanity_daemon.py`'s internal-audit (Qwen skeptic) stream re-alerted via
NTFY on almost every single 30-min cycle for 21h+ (confirmed: 70 "NTFY sent" log
lines against ~70 cycles in `docs/observability/sanity-daemon-log.md`). Root cause:
`_audit_signature()` already normalises findings to one of 3 known categories
(`gas-kwh-unit`, `vat-mismatch`, `high-consumption`) specifically to stop a fresh
random customer/date sample looking "new" -- but because only 2 bills are sampled
per cycle, a DIFFERENT subset of those same 3 known categories gets drawn each
time, and the signature (a set of category strings) still changes cycle to cycle,
so the fix only partly worked. This is the actual "still alarming every 30min"
Rich flagged, separate from the (already-silent since 2026-07-09 13:44) population-
sanity stream.

## Verdicts (each NTFY'd individually as landed)

### 1. `gas-kwh-unit` -- ADJUDICATED FALSE POSITIVE

Qwen's note pattern: "Gas consumption is reported in kWh, which is typically used
for electricity, not gas, indicating a possible unit error." This is real, standard
UK domestic gas billing practice, not a defect: gas consumption is legally/
conventionally always converted from the meter's raw volume (m³) to kWh via the
calorific value before it reaches a bill -- every real UK gas bill states
consumption in kWh, never m³ alone. Qwen has no domain grounding for this and
pattern-matches "kWh + gas" as suspicious. No fix needed; category suppressed.

### 2. `vat-mismatch` -- ADJUDICATED FALSE POSITIVE (confirmed by exact arithmetic)

Qwen's note pattern (verbatim from the log): "The VAT amount of GBP 8.12 does not
align with the expected 20% VAT rate on the total charges." Verified against the
real bill (`docs/reports/run_output_latest.json`, customer C2, period 2022-07-31):

```
commodity_amount_gbp   126.60005770089286
non_commodity_amount   27.43226639423077
standing_charge_gbp      8.370000000000001
-----------------------------------------
net-of-VAT total       162.40232409512363
vat_gbp (reported)       8.120116204756183
162.40232409512363 * 0.05 = 8.120116204756...  <- EXACT match
```

The bill correctly charges the UK domestic reduced VAT rate (5%, VAT Act 1994
Group 1 -- domestic fuel and power), not the 20% standard rate Qwen assumed.
Confirmed real, not assumed: this is the same false-positive CLAUDE.md 2a already
documented once ("a live run flagged a bill's correct VAT... as implausible").
No fix needed; category suppressed.

### 3. `high-consumption` -- SPLIT VERDICT (real defect found, not a rubber stamp)

Two instance classes checked directly against real bill data:

- **I&C-scale instances** (e.g. C_IC3, 324,336 kWh in April 2021, segment `I&C`,
  ~3.9 GWh/year) -- FALSE POSITIVE. Real, plausible I&C consumption; same class
  CLAUDE.md 2a already documented (a real 3GWh/yr I&C customer flagged as
  "implausible").
- **Resi "large but plausible" instances** (e.g. C8, 376.665 kWh in August 2018,
  segment `resi`, ~12.15 kWh/day) -- FALSE POSITIVE. Within the real range of
  UK high-usage/all-electric households; `bill_shock_likely_seasonal: true` on
  this bill confirms the system's own mechanism already recognises it as
  ordinary seasonal variation, not an anomaly.

**But a REAL defect was found while checking a third instance**, C1_2 -- flagged
by BOTH streams on the exact same underlying data point:
- Qwen (audit stream): "The consumption of 128.68 kWh over a single day... is
  extremely high for a typical UK residential customer."
- `population_sanity.py`'s `check_consumption_distribution()`: "C1_2 (electricity,
  resi) annual consumption 129 kWh in 2020 is implausible against the TDCV-derived
  envelope" -- implausibly LOW.

Checked C1_2's real bill history: their very first-ever bill covers a 2-day stub
period (2020-12-30 to 2020-12-31, 128.68 kWh), followed by full monthly bills from
2021-01 onward (January: 1622.325 kWh, i.e. ~52.3 kWh/day) -- a normal, if
electric-heated, winter household. The 2-day stub's own rate (~64.3 kWh/day) is
close to that same customer's own January rate once correctly read as a partial
period, not a full year.

**Root cause confirmed: `check_consumption_distribution()` sums a customer's
bills per CALENDAR YEAR and compares the total against a fixed full-year envelope
(500-15,000 kWh/year) regardless of how many actual days of billing history that
year contains.** A customer whose only billing history in a given calendar year is
a short partial-period (a genuine, common real-world case: joining or leaving
mid-year) will ALWAYS look implausibly low against a full-year bound, no matter how
normal their true per-day rate is. This is a real check-level defect, not a
customer-bill defect -- adjudicated-real, R10 class fix applied (see below), not
suppressed as a false positive (suppressing the SYMPTOM here would have hidden a
genuine gap in the check's own logic).

## R10 class fix

`company/compliance/population_sanity.py::check_consumption_distribution()` now
tracks total `days_in_period` covered per (customer, year) and skips the annual-
envelope comparison entirely when that coverage is below
`_MIN_DAYS_COVERAGE_FOR_ANNUAL_CHECK` (60 days) -- insufficient real billing
history to make a meaningful full-year plausibility judgement, matching the
existing precedent in `YearlyRangeInvariant.check()` ("no valid anchor... check()
always passes rather than extrapolating"). This is a class fix, not an instance
fix: it protects every future partial-year joiner/leaver, not just C1_2.

## Remaining genuinely open (NOT part of this ask, registered separately)

The population-sanity stream's OTHER two findings -- C1g (gas, resi) unit rate
42.6 GBP/MWh in 2019 vs a plausible band of [10.4, 39.0] (marginal, ~9% over);
C4 (electricity, resi) unit rate 320.5 GBP/MWh in 2024 vs [84.0, 315.0] (marginal,
~1.7% over) -- belong to a DIFFERENT check category (`unit_rate_vs_cap_band`), not
one of the 3 named in this ask (gas-in-kWh / VAT / high-consumption). Both are
full-year customers (not partial-period artefacts) with only marginal band
breaches against a band that already carries generous ±40%/+50% tolerance --
plausibly real tariff/consumption-mix variance the band doesn't perfectly capture,
not confirmed defects. Left `open` in the ledger rather than force-adjudicated
either way under time pressure; registered as backlog for a closer look.
