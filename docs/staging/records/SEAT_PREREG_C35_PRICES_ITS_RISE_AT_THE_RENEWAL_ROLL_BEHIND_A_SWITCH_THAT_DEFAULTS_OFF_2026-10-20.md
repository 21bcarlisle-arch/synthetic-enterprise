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

## Graded 2026-10-20 ~16:40 BST (the predictions above are unchanged)

**The runs.** The caller was rebuilt from `/var/tmp/se-c35`'s C35 hunks onto `c61d8b608`, item 1's
landing, and run twice at the default seed over the window to 2019-12-31:
- C34 on, rise off: `/var/tmp/se-c35-onarm-out/build_c34.json`;
- C34 on, rise on: `/var/tmp/se-c35-onarm-out/build_c35.json`.

Both used `run_arm.py` in that directory, with the same kept keys as the retention-guard grade
(`/var/tmp/se-ret-margin/run_both.py`), plus every output key's length. Grader:
`/var/tmp/se-c35-onarm-out/grade.py`. The landed caller is the same hunks on origin's later trunk
(`8e0a30ae5`). That trunk adds `ee995aadc`, the holdout's expected-value decision, which sits behind
`retention_runs_holdout`, off on both arms, so it should not move either run. That was not re-run.

| | prediction | result | verdict |
|---|---|---|---|
| O1 | off arm byte-equal to parent | **not run.** By construction, every hand-off sits inside `_renewal_advice is not None`, and the refusal raises only with the rise on. Not measured. | UNGRADED |
| O2 | C34-only arm byte-equal to parent | **not run as written.** The one parent C34 arm is the full-window `/var/tmp/se-ret-margin/on_arm.json`. Over its rows starting before 2020, 519 of 525 match; 6 late-2019 rows differ by GBP 0.0001 in margin. The window end differs, so this does not isolate C35. The desk's own control (`test_carrying_the_terms_leaves_a_c34_only_arms_rows_unchanged`) holds. | UNGRADED |
| R1 | on = C34-only in every key but the renewal log | every kept key equal, and every key's length equal | CONFIRMED (over the kept keys) |
| R2 | same 525 rows, order, account, start, legs, margin, hazard, effect; advised stay advised with no rise; pre-2019 refusals keep the no-default reason | all hold. C34 advised 0 rows in this window. All 381 pre-2019 rows are refused with `retention rise: no published default…` | CONFIRMED (the advised leg is vacuous: 0 rows) |
| R3 | of 2019 rows C34 refused: ≥60% risen at (GBP 2, 0.3 pt); ≥50% at (2, 0.1); ≥40% at (3, 0.3) | 34/48 = 70.8%; 38/48 = 79.2%; 37/48 = 77.1%. 109 of 144 risen overall | CONFIRMED |
| R4 | every rise in (0, headroom] and GBP 1.50–4.50; two-leg headroom > one-leg at the median | all 109 in (0, headroom], range GBP 2.00–3.47; median headroom two-leg 15.47 (n 26) vs one-leg 8.00 (n 22) | CONFIRMED |

**Unpredicted.** The smaller hazard cut (0.1 pt) is admitted more often than the larger (0.3 pt)
at the same GBP 2 give-up: 38/48 against 34/48. The prereg had the larger cut needing the smaller
rise. The refusal reasons show the opposite. At 0.1 pt, all 10 refusals name the headroom, with
the rise needed at GBP 2.01–2.13. At 0.3 pt, 11 name the headroom, at GBP 2.02–2.36. The other 3
are refused because the rise takes more (GBP 97–100) than the household keeps from the advice:
the kept-benefit test the pre-build print found at margins of 15 or more. So the deeper cut needs
a larger rise, not a smaller one. One reading: a household kept longer pays the advice's give-up
for more months. The rule's arithmetic was not traced here to confirm it. *A first draft of this
paragraph said every 2019 refusal named the headroom. The tally above corrected it before landing.*

**What this licenses.** The caller is on origin behind its switch, off on every standing policy.
Switching it on is a decision, not a fidelity fix. In 2019 it prices a rise for three quarters of
the renewals C34 refuses, at GBP 2–3.5 a month, within the room under the default. It decides
nothing before 2019, because no default was published, and the rows say so. These are records:
no rise is billed, and the book is unmoved (R1).
