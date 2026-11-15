# C32's ninth Expert Hour, over the whole enforcement table: the table missed a live action, the debt objection

**Fate (2026-11-15):** RESULT. **C32 stays at level 2.** The ninth pass failed on items 12, 1, 6 and 3.

**Next:** a debt-objection row (SLC 14), knowledge first. The company decides an objection live in
every run (`company/interfaces/transfer_objection.py:33`, called from `simulation/run_phase2b.py`),
and no protection is read for it. It is the cell nobody had listed.

## What landed

- **The table.** `ENFORCEMENT_TABLE` in `company/billing/winter_moratorium.py` sets 6 actions
  against 13 protection grounds. It is published, with clause and file:line for each cell, in the
  PSR commons §5. No cell is absent.
- **The cells that were absent:**
  - **Consent offer:** 27A (no self-disconnection watch), the supplier's own holds, and 27.8 (held
    only by the ladder's order).
  - **Disconnection:** 27.9 (PPM first), 27.8 and Breathing Space.
  - **Warrant, remote switch and agency hand-off:** every cell, because no gate existed.
- **One gate.** `may_take(action, case)`. The desk's Consent offer is asked through it. Live, every
  withheld offer now names two grounds: no S&RP finding, and no 27A watch.
- **Controls** (`tests/company/billing/test_the_enforcement_table.py`):
  - one control engages each ground alone and checks that exactly the covered cells refuse;
  - the permit leg comes first;
  - support is never refused;
  - the page table and the code's table agree, cell by cell;
  - no company or saas function takes an action without `may_take`.
- **Mutations, all red:** 11 mutations run in-process. Each of the 9 checks was made never to
  refuse; one made the arrangement check refuse everything; one marked support as barred by a hold.
  The bypass check, run with the gate call removed, also goes red.

## The pass

- **Blindness.** A fresh agent, 0 tool uses, the same persona. The audit reports the blindfold
  intact on all 20 rows.
- **The reviewer's first doubt:** "The safety claim costs nothing, because no action ever reaches
  it."
- **Grades:** in commons §5, "The ninth blind pass".

| Item | Grade |
|---|---|
| 12 | Fails: the debt objection is live and has no row. |
| 1 | Fails: the gate is never tested in operation. |
| 6 | Fails: 28B's preconditions are one flag. |
| 3 | Fails, in the protective direction: nothing is dated. |
| 16 | Fixed in this tick. |
| 10, 4 | Pass. |
| 2 | Partly passes. |

**The order of what is owed:**
1. the debt-objection row (knowledge first);
2. dating 28B and 27A;
3. splitting 28B's flag into four dated records before any route uses it;
4. the S&RP assessment and a run caller for the self-disconnection detector, which close item 1
   (collections atom and C10).

## Steps 2 and 3, landed (2026-11-15, delivery seat)

- **Step 2, the census.** `DEBT_STEP_CENSUS` in `company/billing/winter_moratorium.py` places every
  name under which the company acts on a domestic debt. That means every stage of the domestic
  desk, every call through its world door, the objection door and the objection register's write.
  The control derives the same set from the code, and a name added or dropped on either side reds
  it. The bypass control's action names are read from the census too.
- **The diff against the table:**
  - **recovery through the meter** had no row. It now has one, unrouted:
    `SEAT_FINDING_A_METER_KEEPS_RECOVERING_DEBT_THROUGH_A_MORATORIUM_WITH_NO_DOOR_TO_STOP_IT_2026-11-15.md`;
  - **dunning contact** has no row by design: its one Breathing Space implementation is the
    selector's `MORATORIUM_HOLD`;
  - **the rest** are outcomes, records or relief.
- **Step 3, the dating.** 28B is four dated `ProtectionRecord`s: the Debt Trigger, 10 contact
  attempts, the Site Welfare Visit and the do-not-install check, which lives in the PSR module.
  27A's watch is a dated record. 27A is dated from 15 Dec 2020 and 28B from 8 Nov 2023. Before
  those dates the gate still refuses, as the supplier's own policy, and says so. One control over
  the partition takes the permit leg and fails each record alone; 9 of 9 mutations went red.
  Commons §5: "The census" and "28B and 27A, dated".
- **Still owed before a tenth pass:** item 1, the S&RP assessment and a run caller for the
  self-disconnection detector (collections atom and C10).
