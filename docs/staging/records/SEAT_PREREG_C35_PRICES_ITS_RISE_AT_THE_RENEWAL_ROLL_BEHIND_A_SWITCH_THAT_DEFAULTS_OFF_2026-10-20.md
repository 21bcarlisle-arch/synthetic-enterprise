# Pre-registration: C35 gets an engine caller at the renewal roll, behind the rise switch that defaults off

**Written 2026-10-20 ~08:10 BST, before the engine build and before any run.** Claim
`c35-gets-an-engine-caller-behind-a-switch-that-defaults-off` (Lane 0, seat direction). The desk's
half is drafted. `simulation/run_phase2b.py` is untouched. No run of this code has been made. The
only number read is the headroom input, from the 19 Oct published book (below). No decision was
read. Item 1 is NOT yet on origin as this is written: its first landing was refused by its gate at
~08:20 BST. The build waits for it, as the direction says.

## What is being built, said first

- **The precondition holds.** Item 1 (`one-contribution-margin-for-every-renewal-decision`, the run's
  one contribution helper) is on origin before the build. C35's margin is the margin C34's desk
  already holds, through that helper. Nothing else is used, so there is no fifth implementation.
- **The desk** (`company/crm/renewal_advice_desk.py`) carries each leg's `RenewalTerms`: the offer
  ex VAT, `published_default_rate_ex_vat` for its fuel on the start, and the company EAC / 1000.
  The roll leg and the riding (gas) leg each carry their own. Merged per household,
  `HouseholdRenewalTerms` sums the headroom. `decide` already prices the rise when the policy names
  it. With the rise on, rows gain `headroom_gbp_per_month` and `retention_rise_gbp_per_month`.
  With it off, rows are unchanged to the byte.
- **The run** hands the terms at both `observe_roll` and `observe_riding_leg`, through one
  `_renewal_terms`. It refuses a policy with the rise on and `next_best_action_decides_at_renewal`
  off, and names the reason.
- **The switch is the existing `next_best_action_shares_by_retention_rise`, not a new field.** The
  direction asked for "a DecisionPolicy switch, default False on every standing policy and declared
  in FIELD_CONSUMPTION". This field already is that switch: it is False on every standing policy
  and declared `run_argument`. Its only consumer was `decide`, and `decide` had no engine route to
  it. A second field for the same decision would make one combination of the two meaningless. So
  this gives the existing switch its caller and states the choice here.

## The input, measured before predicting

Headroom of fixed terms under `published_default_rate_ex_vat`, (default − offer) × company EAC / 12,
over `account_state_log` of `run_output_ad8afadc5_20261019T132751Z.json` (GBP/month per leg):

| year | elec n, median, share ≥ 2 | gas n, median, share ≥ 2 |
|---|---|---|
| 2019 | 65, 8.36, 0.88 | 51, 9.02, 0.86 |
| 2020 | 73, 8.94, 1.00 | 50, 9.11, 0.98 |
| 2021 | 37, 1.91, 0.49 | 20, 0.00, 0.05 |
| 2022 | 7, 2.08, 0.57 | 10, 0.00, 0.00 |
| 2023 | 28, 8.38, 0.79 | 26, 7.33, 0.58 |
| 2024 | 48, 3.69, 0.69 | 41, 6.76, 0.85 |
| 2025 | 16, 2.27, 0.81 | 12, 0.00, 0.33 |

Before 2019 the default is None for both fuels. The rise the rule needs, printed over the real range
(margin −4 to 30 GBP/month, belief 0.1–0.3, offer 0–15% under a 2019 default, 3.1 MWh), runs
GBP 2.00–3.73. It is refused where the headroom is 0. At margins of 15 or more, (GBP 2, 0.1 pt) and
(GBP 3, 0.3 pt) are also refused, because the price's own effect on staying, or the household's
kept benefit, fails.

## Predictions

**O1, off arm.** At a fixed seed, over the short window to 2017-06-30, with `CURRENT_POLICY`, a
run at the build equals a run at its parent (item 1's landing), byte for byte (`cmp` on the
run-output JSON). Nothing on the off path is new.

**O2, the C34-only arm.** At a fixed seed, over the window to 2019-12-31, with
`next_best_action_decides_at_renewal` on and the rise off, a run at the build equals a run at its
parent (`cmp`). Carrying the terms changes no row.

**On arm (C34 on, rise on, window to 2019-12-31, build), against O2's build arm:**
- **R1. Records only.** On equals C34-only in every top-level key apart from
  `next_best_action_renewal_log`.
- **R2. Nothing C34 decided changes.** The same rows, in the same order, with the same account,
  start, legs, margin and hazard. Every row C34 advised is advised again, with no rise. Every row
  dated before 2019 that C34 refused is still refused, and carries
  `retention rise: no published default for this fuel on the renewal date…`.
- **R3. The rise is reachable in 2019.** Among 2019 rows that C34 refused:
  - at least 60% are advised with a rise under (GBP 2, 0.3 pt);
  - at least 50% under (GBP 2, 0.1 pt);
  - at least 40% under (GBP 3, 0.3 pt).
  The basis: a median headroom of GBP 8–9/month per leg, against a rise of about GBP 2–3.3.
- **R4. Every rise lies in (0, headroom]** and between GBP 1.50 and 4.50 a month. Two-leg
  households' headroom exceeds one-leg households' at the median.

## What would refute the design, not just a number

- **R3 under 30% under (GBP 2, 0.3 pt).** Either the headroom is not what the input reading says
  (the offer the desk is handed is not the one measured), or the contribution runs far below
  −GBP 4. Both are findings about the inputs, not a licence to change the floors.
- **Any O1 or O2 byte difference.** It refutes the build.

## How it will be graded

O1, O2 and R1–R4 are graded in the landing commit, below this line, with the predictions unchanged.
