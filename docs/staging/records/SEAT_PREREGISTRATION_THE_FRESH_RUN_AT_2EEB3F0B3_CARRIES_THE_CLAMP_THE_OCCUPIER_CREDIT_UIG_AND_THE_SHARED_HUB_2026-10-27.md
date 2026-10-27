**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION: the fresh default-book run at 2eeb3f0b32 carries the company's cap clamp per payment method, the occupier EBSS credit, Unidentified Gas and the shared smart hub

Filed 2026-10-27, before launch. The predictions below are not edited after the run. The grade is
appended beside them, each marked held or refuted.

## The run

- **Code:** origin/main `2eeb3f0b32`, run from a clean worktree `/var/tmp/se-fresh-run-2eeb3f0b3`. Since
  the 871f674a2 book it carries:
  - c688a5e61 (UIG, world);
  - b67d8c3ee (a dual home's two legs share one smart hub, world);
  - d2be04371 (the occupier EBSS credit, world);
  - 2eeb3f0b3 (the company's cap clamp at the payment method's own column, plus the
    standing-charge penny tolerance, which is a grading change);
  - the two blind register rows (INV_REGISTER_ID_ONE_LABEL and INV_SERIAL_REGISTER_COUNT_STABLE, landed after launch with their evaluators, grading only).
- **Configuration:** the same as the 871f674a2 run. Default book, default `CURRENT_POLICY`, no
  `SE_POPULATION_SEED` override, `report_end=None`. The script is `/var/tmp/fresh-run-scripts/arm.py`,
  unchanged. It pickles to `/var/tmp/fresh-run-out-2eeb3f0b3/`.
- **Grade:** `/var/tmp/fresh-run-scripts/grade.sh`, with its `OUT` pointed at this run's directory,
  run from an origin/main worktree.
- **Attribution limit, stated before the answer.** Four behavioural commits move at once. Two of
  them are world changes that can feed the company's renewal rates through margin (UIG) or reach the
  same households (the hub). A count that moves where no single commit predicts it cannot be
  attributed by this run. The answer to that is "I cannot yet say", followed by the one-variable arm.

## Predictions (reference: the 871f674a2 book, 1,291 accounts; grade e81b1b156)

| Invariant / measure | 871f674a2 | Predicted | Which commit predicts it |
|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | 298 of 5,921 | **0** | the clamp |
| INV_UNIT_RATE_SVT_GAS | 249 of 4,713 | **0** | the clamp |
| INV_STANDING_CHARGE_SVT_ELEC | 735 (0 on re-grade with a penny per period) | **0** | the tolerance, printed pence |
| INV_STANDING_CHARGE_SVT_GAS | 1,502 (0 on re-grade) | **0** | the tolerance |
| INV_READ_MONOTONIC | 0 | **0** | unchanged (8e9fb022d) |
| INV_PPM_NOT_CREDIT_BILLED | 12, all C6 (SME) | **12, all C6; 0 domestic** | nothing touches it |
| INV_PERIODS_CONTIGUOUS | 4 (3 accounts) | **at least 1: persists** | nothing landed addresses it. Traced before launch on 871f674a2: every gap is a bill the company's pre-bill gate HELD (resi electricity at 2,100–4,300 kWh a month) and never re-issued. The months' energy is never billed |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | UNREACHED | **UNREACHED** | no default term prints two registers (finding §3) |
| Every other row CLEAN on 871f674a2 | CLEAN | **CLEAN** | |
| INV_REGISTER_ID_ONE_LABEL (new, blind), breaches (a)+(b) | 39 ids with two labels before 8e9fb022d; 0 after on the 67a893e749 re-run | **0** | 8e9fb022d |
| INV_REGISTER_ID_ONE_LABEL, flags (c): relabel with no term change | not measured | **0** | ids follow the term (finding §3) |
| INV_SERIAL_REGISTER_COUNT_STABLE (new, blind), breaches (b): count change within a period | not measured | **0** | |
| INV_SERIAL_REGISTER_COUNT_STABLE, flags (a): count change with no tariff change | not measured | **0** | the count follows the term (finding §3) |
| Serials whose count changes at a tariff change (pass, reported) | 39 on HEAD's generator | **30–70** | unchanged code path |
| Occupier months carrying an EBSS credit | 0 of 22 | **11 of 22** | d2be04371 (read off the 22 bills' void and occupier shares on 4ae8da9b0f) |
| `total_occupier_debt` | the 871f674a2 figure | **down by at most £737 (11 × £67)** | d2be04371 |

**The occupier rows assume the same 22 occupier bills recur.** The clamp and UIG move company prices,
and so possibly churn and voids. If the occupier set differs, the two rows are graded "not comparable"
and the credit is read off the new set: every occupier month opened on or before the 1st in
Oct 2022 to Mar 2023 carries one credit.

## What c688a5e61 (Unidentified Gas) is predicted to move

From `records/WORKER_PREREG_W2_36_WHAT_THE_UIG_CHARGE_MOVES_ON_THE_NEXT_RUN_2026-10-27.md`, not
re-derived here:
- **P1.** On every settled gas row, `gas_uig_cost_gbp` = `wholesale_cost_gbp` × u/(1+u). Summed,
  it is 1.8–2.1% of gas wholesale cost in each year other than 2022 and 2023, and 2.0–3.0% in
  those two.
- **No suite row moves on UIG alone.** It is a cost, not a rate. P4 of that file says no
  default-tariff rate crosses the cap because of it.
- **Its P2 and P3 cannot be attributed by this run.** The clamp lowers prepayment revenue in the
  same run.

## What b67d8c3ee (the shared smart hub) is predicted to move

- **Each fuel's estimated-bill count is unchanged in expectation.** Each fuel keeps its DESNZ share
  (6.8% electricity, 14.2% gas). So INV_READ_DUTY_ANNUAL, INV_BACK_BILLING_12M and
  INV_SETTLEMENT_ACTUAL_SHARE_ELEC stay FLAGGED-not-BREACHED, as on 871f674a2.
- **What moves is co-occurrence.** Among dual homes, the share with both legs out of smart mode
  goes from about 0.9% to about 7%. The suite has no row that reads it. It is graded here only if
  the run's book exposes each leg's read class, and the grade says which.

## What could refute it, named in advance

- Everything in the clamp's own pre-registration
  (`records/SEAT_PREREGISTRATION_THE_NEXT_FRESH_RUN_HOLDS_A_PREPAYMENT_DEFAULT_TARIFF_AT_ITS_OWN_CAP_THROUGH_THE_COMPANYS_CLAMP_2026-10-27.md`):
  - a household whose method changes inside a cap window;
  - an SVT term that reaches no `decide_renewal`;
  - the writers' response to lower prepayment revenue.
- A standing-charge breach over a penny per period would be a real overcharge, not rounding.
