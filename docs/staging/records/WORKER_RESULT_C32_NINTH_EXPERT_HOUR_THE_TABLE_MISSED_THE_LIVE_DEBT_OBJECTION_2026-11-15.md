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
