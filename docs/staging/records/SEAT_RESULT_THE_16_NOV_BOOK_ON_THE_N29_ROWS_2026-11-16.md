**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Result: the 16 Nov book on the N29 rows, graded against the 12 Nov pre-registration (2026-11-16)

Grades `SEAT_PREREG_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-12.md` and its two 14 Nov amendments.

**The book.** `docs/reports/run_output_8a300fa561_20261116T031305Z.json`, `producing_commit` 8a300fa561 (resolved
03:13 GMT). The publisher graded it at 06:48 (`docs/reports/domain_invariants.json`, 1,306 accounts) and paused
the publish on five other rows, none of them N29.

**Does the prediction apply?** Yes. `simulation/arrears_engine.py` (last 69866925bd) and
`simulation/credit_refund_events.py` (last ceeefa5960) are the same at 8a300fa561, at the publisher's HEAD
6ffe49a398 and at origin/main.

| | predicted (as amended 14 Nov) | read | verdict |
|---|---|---|---|
| P1 `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` | 0 breached (S6b moves SYN-2016-139 inside reg 6D); cross-arm legs read 0, with PROS-2021-0117 off the book | **0 of 1,679** (76 flagged). PROS-2019-0318, SYN-2016-047, SYN-2016-142g and SYN-2016-139 are on the book and read 0. PROS-2021-0117 is not on it | **held** |
| P2 blind row `INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT` | 30 ± 3 | **23 of 132** | **refuted, low** |
| P3 refunds with a set-off | 40 ± 5 | **43 of 187 refund-log rows, GBP 1,469.38** (159 refunds, GBP 18,433.99) | **held** |

## What the miss says, and what it cannot

P3's census matches the e17ebc596 arm of the 13 Nov fabric A/B to the penny (43 set-offs, GBP 1,469.38; 159
refunds, GBP 18,433.99). So the world's refunds and set-offs did not move between that arm and this book. The
blind row compares each refund with the credit **printed on the page** for the other leg (the runner's own
registry: "reads two fuel legs' printed pages"). So the fall from 31 to 23 is on the page side, or in which
households are graded (130 → 132).

**I cannot yet say which commit moved it.** 159 commits lie between e17ebc596 and 8a300fa561. One candidate
contradicts this file's 14 Nov amendment. That amendment said the statement walk (84a44b51c3) "cannot move" P1–P3,
because `--ledger` output is byte-identical. That holds only for the raw export. The blind row also reads the page,
and 84a44b51c3 changed what the page prints for the 84 set-off legs. **Prediction, filed before any test:** a
one-variable page rebuild of this run at 84a44b51c3^ against 84a44b51c3 moves the blind row by most of the 8. If it
moves by 2 or fewer, the cause lies elsewhere in the window.

*(Graded 16 Nov: it moves by **0**, every page byte-identical. 84a44b51c3 changed the statement, not the customer page the blind row reads, so the sentence above saying it changed what the page prints was wrong. The leading candidate is now ceeefa5960. See `SEAT_RESULT_THE_STATEMENT_WALK_DOES_NOT_MOVE_THE_N29_BLIND_ROW_2026-11-16.md`.)*

## What changed

- `DOMAIN_INVARIANT_EXCEPTIONS.yaml`: the N29 blind row's ceiling went from 60 to **23**, the count the book reads
  (the exception's own `retired_by` asked for this). `recheck_by` moved to 26 Nov. What retires it now is the
  per-household trace of the two-walk residue.
- The SYN-2016-139 exception (max 1) is **retired**. Its condition, the cash-day money-in graded 0 on a fresh run,
  is met. Its finding moved to `docs/staging/done/` with a Done section. If it breaches again, the gate refuses.
- Re-gated on the published results with the edited register, the unexcepted list is unchanged: the same five
  non-N29 rows.

**Reverse.** Revert the commit. The 60 and the SYN-2016-139 exception come back.
