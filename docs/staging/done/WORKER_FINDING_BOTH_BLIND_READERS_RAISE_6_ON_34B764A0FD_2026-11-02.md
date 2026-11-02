**Severity:** MAJOR · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Both blind readers raise 6 finding(s) on 34b764a0fd (2026-11-02)

*Written by `background/two_reader_review.py`, the automatic lane of the two-reader trial
(director ruling 28 Oct, review 2026-11-11). Nothing here has been checked. Check each pair at
HEAD like any other finding, and record the outcome for the review. Severity is capped at
MAJOR until a check confirms more.*

- **Commit:** `34b764a0fdeb68692dd3ee934455d39289899ad6`, committed 2026-11-02T06:03:41Z.
- **Modules it added:** `company/billing/gas_volume_conversion.py`.
- **Verdicts:** A NEEDS_WORK, B NEEDS_WORK (trust ledger,
  `reading-review-live-2026-11-02:34b764a0fd:arm{A,B}`).

## Raised by both (pairs from the tool-less matcher; undo any that do not name one defect)

1. **A#1 (MAJOR) `company/billing/monthly_bill_assembly.py:840`** When the converted volume disagrees with settlement after an estimated run, the whole difference lands on the current month (month_kwh = converted - sum(used_kwh)); nothing stops it going negative. Input: 3 estimated months with used_kwh 1000 each, a meter advance converting to 2500 kWh, and 500 kWh settled this month give month_kwh = -500, a scale factor of -1 and a negative-usage bill. A meter reading high over a long run is billed as current usage, not through the back-billing-capped catch-up. The test (_VolumeFeed) reads every month, so neither edge is reached.
   **B#1 (BLOCKING) `company/billing/monthly_bill_assembly.py:840`** month_kwh = converted_kwh - sum(settled used_kwh of the pending estimated run) has no lower bound; the rescale at 841-849 then calls _estimated_settlement_records with a ratio <= 0. Input: three estimated months settled at 1000 kWh each, then an actual read converting to 2900 kWh against 200 kWh settled this month -> month_kwh = -100, the bill is rebuilt at -0.5x its settled records. The catch-up still uses settled used_kwh, so the meter-vs-settlement discrepancy is dumped onto one month instead of the run's true-up. The test only covers the all-actual _VolumeFeed (scale=1.1), and the replay never reaches the rescale.
2. **A#2 (MINOR) `company/billing/monthly_bill_assembly.py:841`** The `total_consumption_kwh > 0` guard means a month with 0 settled kWh and a non-zero volume advance bills 0 kWh, ignoring the meter. Untested.
   **B#3 (MINOR) `company/billing/monthly_bill_assembly.py:841`** The guard true_bill['total_consumption_kwh'] > 0 skips the conversion when settlement is 0 kWh but the meter's volume advanced. The bill charges 0 and the kWh register advances only by the pending run, so the printed kWh no longer matches the printed volume advance.
3. **A#3 (MAJOR) `tools/domain_invariant_runner.py:716`** The YAML row's severity (DOMAIN_INVARIANTS.yaml:3137) makes conversion_fields_missing_with_volume_present a flag, but the evaluator records every missing CV/CF/volume/unit as a breach (tally.band with value None). Input: a gas period with read volumes but no calorific_value_mj_per_m3 is BREACHED, not flagged.
   **B#4 (MINOR) `tools/domain_invariant_runner.py:716`** DOMAIN_INVARIANTS.yaml severity says conversion_fields_missing_with_volume_present is a flag; the evaluator sends every missing-field case to tally.band(None), which records a breach. Input: a gas period whose reads carry read_volume but no calorific_value_mj_per_m3 -> BREACHED, not flagged.
4. **A#5 (MINOR) `tools/generate_billing_ledger.py:506`** imperial_meter is printed as `unit == "hcf"`, derived from the read unit leg (c) checks it against, so on any generated book leg (c) cannot fail; the account's gas_meter_imperial record is never what is printed.
   **B#5 (MINOR) `tools/domain_invariant_runner.py:718`** Leg (c) can never fail on real output: the ledger writes imperial_meter = (unit == 'hcf') from the same gas_read_unit (generate_billing_ledger.py:506). Only the hand-built imperial_flag_wrong test case reaches the breach.
5. **A#6 (MINOR) `company/billing/gas_volume_conversion.py:80`** volume_from_kwh treats any unit other than 'm3' as hcf, while metric_volume raises; volume_from_kwh(100, 'kWh') silently returns a volume in hundreds of cubic feet.
   **B#6 (MINOR) `company/billing/gas_volume_conversion.py:80`** volume_from_kwh treats any unit other than 'm3' as hcf: volume_from_kwh(100, 'kWh') returns a value in hcf instead of raising, unlike metric_volume, which raises ValueError.
6. **A#7 (MINOR) `site/explore/test_a_gas_bill_prints_its_volume_cv_and_correction_factor.py:467`** No imperial invoice is rendered, so gasReadRows' hcf branch (the hard-coded '× 2.832' line and the 'hundred cubic feet' unit) is never reached.
   **B#7 (MINOR) `site/explore/index.html:946`** The imperial row prints 'x 2.832' while the conversion uses 2.8317, and the page test has no hcf case, so that leg is unchecked. The test's tolerance 0.05 + 0.0005 * 11.3 has no stated source, and its [\d.]+ regex would misread a comma-formatted kWh.

## Raised by one reader only (not filed under the vote)

- A#4 (MINOR): The row's predicate (e) and numerator compare billed_kwh with the converted volume; the evaluator compares the kWh the two readings span (closing_read_kwh - opening_read_kwh). These differ on every catch-up bill, e.g. the test fixture: consumption 643.6 vs spanned 256.5. The YAML gap note records the tolerance change but not this one.
- B#2 (MAJOR): The prepayment branch records the meter's register_volume but bills settled kWh with no conversion, and the ledger (tools/generate_billing_ledger.py:497-500) prints a volume worked backwards from kWh via volume_from_kwh. The row therefore passes prepayment gas records by construction. 'The bill converts it' holds for credit bills only.

## Done

Checked at origin HEAD ce8694cbb1 on 2 Nov, for the two-reader trial's 11 Nov review. Every verdict
was checked by running the code, and every fix has a test that reds at HEAD (run in a detached HEAD
worktree with only the new test file copied in).

| Pair | Verdict | What was found, what was done |
|---|---|---|
| 1 (A#1 / B#1) | **confirmed** (logic; 0 live) | `month_kwh` had no floor. The scenario reds at HEAD. On the cd4fc5b8d8 replay it never fires: 0 negative bills of 19,651, because the world and the supplier convert at the same stand-in CV. It will fire once G1 lands. Fixed under C5 of the K8 page: a meter below the run's settled use re-prices the run down to the meter, the month bills 0 kWh, and the catch-up credits the difference (test: -2,539 kWh, an overcharge credit of £152.34). |
| 2 (A#2 / B#3) | **confirmed** | A month that settled 0 kWh ignored a meter advance. It is now priced at the rows' tariff (`_estimate_records_at_tariff_rate`). |
| 3 (A#3 / B#4) | **confirmed** | Every missing field went to `band(None)` and became a breach. A volume present without its CV or factor now flags, as the row's severity says. A kWh register, or a flag that disagrees with the unit, still breaches. |
| 4 (A#5 / B#5) | **confirmed** | The ledger printed `imperial_meter = unit == "hcf"`. The bill now carries the account's `gas_meter_imperial` and the ledger prints that. The test goes through `generate_billing_ledger.generate`, and a ledger-only mutation is caught. |
| 5 (A#6 / B#6) | **confirmed** | `volume_from_kwh(100, "kWh")` returned hcf. It now divides through `metric_volume`, which raises. |
| 6 (A#7 / B#7) | **confirmed** | The page printed × 2.832 while the conversion uses 2.8317, and nothing tested the hcf case. The page now prints × 2.8317 (100 × 0.3048³). An hcf case was added at over 1,000 kWh, and the kWh regex now reads the thousands comma; that defect was **confirmed** too. The tolerance is now derived from the printed digits in `_print_tol`. |
| B#2 (one reader) | **confirmed, not fixed** | The prepayment branch charges settled kWh, and the ledger works the volume back from it. The K8 page now says a prepayment charge IS converted, at the meter, at a short-term fixed CV that is later reconciled (R6). The build of C4 is owed; its reconciliation cadence is G6. |
| A#4 (one reader) | **equivalent** (documentation) | The evaluator grades the kWh the reads span, not `billed_kwh`. That is right: after a run, the reads span the month plus the catch-up (§13). The row's gap note now says so. |

Replay (/var/tmp/n11-replay script at the fixed code, cd4fc5b8d8 gas legs): 0 of 19,651 bills moved
in kWh, £, catch-up £ or true-up kWh. The only new key is `gas_meter_imperial`, and there are 0
imperial accounts on this roster (G2). No run was launched.
