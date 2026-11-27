**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `a-won-gas-first-term-is-struck-at-a-quote`

# Pre-registration: S2's cap-hold arm, re-run on the book where a won gas first term is struck at its quote

*Delivery seat, 27 Nov 2026. Filed in the commit that strikes the gas half of the dual-fuel quote, before any
book carries it. Knowledge: `docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §14.
The finding this answers: `docs/staging/SEAT_FINDING_A_WON_GAS_FIRST_TERM_IS_CONTRACTED_ON_A_STRIKE_NOBODY_QUOTED_2026-11-27.md`.*

## The run, and what it is held on

- **Off arm:** the first full-window standing book whose producing commit descends from this landing (default seed,
  not fast). **Arm:** the same commit plus `FIRST_TERM_CAP_HOLD_DELETED = True` and nothing else, as S2 was.
- **HELD ON ITS BOOK.** Nothing runs until that book exists. S2 was graded on `76f894811d`, and its gas
  findings do not carry over to a book where gas is quoted. The pair is read with S2's own
  `/var/tmp/se-s2-caphold/grade_pair.out` method. The void rule is carried over unchanged: if any term-0
  rate outside G1–G3's populations moves by ≥1p/MWh, the off arm is re-run first, before any grade.

## What the probe already established (seed `run_base_seed()`, `/var/tmp/se-gasq/`)

The run has 200 won gas legs. **103** carry a gas quote. **73** belong to default-tariff homes, so they
have no fixed strike. **24** are `cap_constrained`: the company declined the gas fix because it was
over the default (1 in 2020, 14 in 2021, 1 in 2022, 7 in 2023, 1 in 2024). No 2021 or 2022 gas leg is
quoted.

## Predictions (gas legs, term 0, arm vs off, moves of at least 1p/MWh)

| # | population | prediction | range |
|---|---|---|---|
| G1 | the 103 quoted gas legs | **0** move. Each is contracted at its quote, and the company gated that quote under the gas default. | 0–3. Anything above 3 means the company's gate and the hold's cap line (SVT − 4.76%) are not the same line. |
| G2 | the 24 `cap_constrained` legs | **most move.** They are still on the notice-date strike, and that strike is over the default by construction. | 14–24 |
| G3 | the 73 gas legs of default-tariff homes | **some move.** They open on a fixed term nobody quoted (§14 GAP 2), and the hold clamps any of those over the cap. | 5–30 |
| G4 | S2's 47 | **fewer than 47, and not 0.** The 2021–22 legs stay, under G2 and G3. Most of the 2023–25 legs leave. | 20–45 |
| G5 | the campaign | identical between arms: same `acquisition_funnel_log` and same won ids. The hold is downstream of the win. | exact |

**What this decides.** If G1 holds and G2 and G3 do not reach 0, deleting the hold (#2) still bills
the households in G2 and G3 above a price they were never shown. #2 stays off until §14's first two
GAPs are built: what a home is shown when its gas fix is declined, and a default-tariff home's gas
leg. If G1 fails, the gate and the hold disagree on where the cap is, and that is the next item.

**Reverse:** delete this file. It changes nothing on origin.

## Launched (delivery seat, 27 Nov 2026, appended; predictions above unchanged)

The work this claim asked for (`a-won-gas-first-term-is-struck-at-a-quote`) is already done on origin: 637c051d2
landed §14, the gated gas quote and this record. The draw took the disposition, not the work. What was still owed
was queuing the re-run. No book yet descended from 637c051d2 (the newest standing book, `d640bd67e4`, is from
04:28, before it), so both arms run here instead of waiting on the standing publish:

- **Off:** `origin/main` at `5e075efa94` (it descends from 637c051d2 and carries S3's `SETTLEMENT_LOSSES_APPLIED`,
  which is the same in both arms). Job `s2-gasq-off-5e075efa94` writes `/var/tmp/se-s2-gasq/out/run_output_off.json`.
- **Arm:** the same commit plus `/var/tmp/se-s2-gasq/arm.diff` (`FIRST_TERM_CAP_HOLD_DELETED = True`, nothing else).
  Job `s2-gasq-arm-5e075efa94` writes `/var/tmp/se-s2-gasq/out/run_output_arm.json`.
- Both are queued behind `head-green-census` for memory. The grade is continuation
  `s2-gasq-grade-the-cap-hold-arm-on-the-gas-quoted-book`, which is held on the arm's file.
