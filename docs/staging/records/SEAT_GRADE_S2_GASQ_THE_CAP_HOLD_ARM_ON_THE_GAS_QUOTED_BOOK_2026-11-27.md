**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `s2-gasq-grade-the-cap-hold-arm-on-the-gas-quoted-book`

# S2 re-graded on the gas-quoted book: the cap-hold arm against its off arm at 5e075efa94

*Delivery seat, 27 Nov 2026. This grades G1–G5 of
`SEAT_PREREG_S2_RERUN_WITH_THE_GAS_FIRST_TERM_AT_ITS_QUOTE_2026-11-27.md`.*

- **Off arm:** `/var/tmp/se-s2-gasq/out/run_output_off.json`, producing commit `5e075efa94`.
- **Arm:** `/var/tmp/se-s2-gasq/out/run_output_arm.json`, producing commit `853aae3ba9`. `git diff
  5e075efa94 853aae3ba9` is one file and one line: `FIRST_TERM_CAP_HOLD_DELETED = True`.
- Both ran the full window at the default seed, not in fast mode, on the same world digest
  (`cdba75ebb9197b33`).
- **The method is S2's:** term-0 `unit_rate_gbp_per_mwh` from `account_state_log`, arm minus off, with a
  move counted at |Δ| ≥ 1p/MWh.
- **The populations** were re-derived at `5e075efa94` by `/var/tmp/se-s2-gasq-grade/classify.py`
  (that is probe2's split). They match the pre-registration exactly: **103 quoted, 24
  `cap_constrained`, 73 default-tariff homes**.
- **Where the pair is read:** `/var/tmp/se-s2-gasq-grade/{diff_arms,grade,quote_vs_billed}.out`.
- Nothing flips on origin.

## The void rule fired, so this grade is conditional

**11 term-0 rates outside G1–G3 move by ≥1p/MWh.** Each has a mechanism the switch owns:

| legs | move | what it is |
|---|---|---|
| S2's four PROS-2021 electricity legs (0212, 0385, 0396, 0399) | +£1.89 to +£13.33 | Exactly the legs S2's P2′ named |
| SYN-2021-001 electricity, SYN-2021-001g gas, SYN-2025-001g gas | +£6.06 to +£7.50 | Synthetic legs held at the cap, outside the campaign |
| Four June-2023 electricity legs | +1.5 to +1.6p | Portfolio-premium feedback |

The rule is not waived. The off re-run is longjob `s2-gasq-off-rerun-5e075efa94` at `5e075efa94` in
`/var/tmp/se-s2-gasq/wt-rerun`. It writes `/var/tmp/se-s2-gasq/out-rerun/run_output_off_rerun.json`.
`/var/tmp/se-s2-gasq-grade/check_rerun.py` was filed before the re-run ends.

**Prediction: DETERMINISTIC.** The re-run's `account_state_log`, `acquisition_funnel_log`, `bills` and
headline totals will be identical to the off arm's. S2's own re-run read the same way at
`76f894811d`. A DIFFERS verdict voids every row below.

## The grade

| # | prediction | measured | verdict |
|---|---|---|---|
| G1 | 103 quoted gas legs: **0** move (range 0–3) | **28 move by ≥1p/MWh, all in 2024.** 24 of them fall by 1.0–1.8p: portfolio-premium feedback, the same thing as S2's ±1p gas moves. **4 rise, by +12.5p to +45p** (PROS-2024-0247g, 0249g, 0253g, 0256g, Sept 2024). In the off arm all four sit at exactly the cap line, 52.190 = SVT 54.8 × 0.9524. In the arm they sit at quote × 1.0106. | **MISSED.** Even counting only the 4 real moves, 4 is above the range of 3. |
| G2 | 24 `cap_constrained` legs: most move (range 14–24) | **18 move by ≥1p/MWh.** 15 rise: 14 in 2021 and 1 in 2022, from +£1.02 to +£80.12/MWh, up to **2.92× the SVT** (PROS-2021-0399g, 38.76 → 118.88). 3 fall by about 1.5p (feedback). 6 stay put: 2023–24 legs whose notice-date strike sits under the cap line. | **HELD** (18, or 15 counting rises only) |
| G3 | 73 default-tariff homes' gas legs: some move (range 5–30) | **22 move** (71 are in the log). 20 rise: 2019 1, 2021 6, 2022 6, 2023 3, 2024 1, 2025 3. The largest are **+£110/MWh** (PROS-2022-0327g and 0332g, 98.29 → 208.5, 1.41× SVT) and +£46 (PROS-2022-0178). 2 fall by 1–2p. | **HELD** |
| G4 | S2's 47: fewer than 47 and not 0 (range 20–45). The 2021–22 legs stay; most 2023–25 legs leave. | **37 of S2's 47 still move.** All 24 of the 2021–22 legs stay. **10 leave**: 9 are now G1 legs at their quote (8 from 2025, PROS-2024-0345g) and 1 is PROS-2023-0025g. Of S2's 21 legs from 2023–25, **11 stay**. 4 of those are the G1 −1.8p feedback. 7 are real: 5 G3 legs (2023-0010g, 2023-0377g, 2024-0353g, 2025-0013g/0051g/0062g) and SYN-2025-001g. | Count **HELD**. "Most 2023–25 leave" **MISSED narrowly**: 10 of 21 leave. |
| G5 | Campaign identical, exact | `acquisition_funnel_log` identical. Won PROS base ids are the same 254. Wins are 443 = 443. No `account_state_log` row differs before 2019-02-07 (PROS-2019-0024g, a G3 leg). | **HELD exactly** |

**Book against book, arm minus off:**

| | arm − off |
|---|---|
| net | +£7,477 |
| revenue | +£7,754 |
| EV | +£14,627 |

That is more than S2's +£6,293 net. The 2023–25 quoted legs left the moving set, but the 2021–22
G2 and G3 legs did not. On the re-derived book they now carry more customer-years. **It is all
transfer (M2):** households billed above the default, on a fixed term at a price they were never
shown.

## What G1's miss says

The pre-registration said: "Anything above 3 means the company's gate and the hold's cap line are not
the same line." **That is what was measured, and the cause is one step earlier than either line.**

**None of the 103 quoted gas legs is billed at its quote.** In the off arm, term-0 rate ÷ quote runs from
**1.0019 to 1.0283** (median 1.018, and 0 within 1p of the quote). The arm reads 1.0022–1.0283.

The cause is in `run_phase2b.py`. `contracted_first_term` sets the unit rate to the quote. Then the
company's renewal chain (`decide_renewal`, `simulation/run_phase2b.py:3974`) re-prices term 0 on
top of it. The gate tested the quote against the gas default. The hold tests the re-priced rate
against SVT − 4.76%. For four Sept-2024 legs the quote was under the line and the re-priced rate
was over it.

S2's electricity reading shows the same thing (arm/quote ≈ 1.004). So it is not a gas-only defect.
It is filed as `docs/staging/SEAT_FINDING_A_QUOTED_FIRST_TERM_IS_REPRICED_ABOVE_ITS_QUOTE_BY_THE_RENEWAL_CHAIN_2026-11-27.md`.

## What this decides

The pre-registration's decision rule binds both ways:

- **G2 and G3 do not reach 0.** Deleting the hold still bills **35** gas first terms above a
  price they were never shown (15 G2 rises and 20 G3 rises), up to 2.9× the default. **#2
  (`FIRST_TERM_CAP_HOLD_DELETED`) stays off.** It waits until §14's first two GAPs are built: what a
  home is shown when its gas fix is declined, and a default-tariff home's gas leg.
- **G1 failed,** so the next item is the line disagreement. In fact it is the re-pricing beneath it:
  a quoted first term must bill at the quote (SLC 23 / 22C, §13). Until that holds, no quoted leg can
  be called "contracted at its quote", in either fuel.
- **B8 does not flip on this pair.** What would flip it is a transfer, not value created.

**Reverse:** delete this file and the finding. The re-run writes only under `/var/tmp/se-s2-gasq/`.

**Graded:** G1 MISSED (28 ≥1p: 4 real, at the cap line, plus 24 feedback) · G2 HELD (18 of 24) · G3 HELD
(22 of 73) · G4 count HELD (37 of 47), "most 2023–25 leave" MISSED narrowly (10 of 21) · G5 HELD
exactly · all of it conditional on `check_rerun.py` reading DETERMINISTIC.
