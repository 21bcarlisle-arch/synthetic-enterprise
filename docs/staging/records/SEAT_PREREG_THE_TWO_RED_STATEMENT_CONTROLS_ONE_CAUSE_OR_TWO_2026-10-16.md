**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `D46_the_validator_holds_against_the_varied_population` · **Claim:** `the-two-red-statement-controls-get-a-cause`

# Pre-registration: the two red statement controls, one cause or two

*Delivery seat, 2026-10-16, written BEFORE the controls were run on origin `bdd6d1657`. Nothing below
has been measured yet; the result is appended underneath, with the wrong predictions kept.*

**Subject.** `test_the_statement_shows_how_each_bill_reached_its_number.py` against the committed
`docs/state/billing_ledger.json` (written by publish `ed3dadd9d`, run `2248e3baf`):
(i) the event walk's close disagrees with the ledger's `balance_gbp` on some accounts;
(ii) 2 catch-up bills charge VAT on neither base.

**The two candidate lists.**
- H — the 11 held-estimate catch-up bills, on PROS-2017-0336 (8), PROS-2017-0117, PROS-2024-0065,
  PROS-2025-0106 (`SEAT_PREREG_A_HELD_ESTIMATE_IS_KNOWN_AT_ASSEMBLY_2026-10-15.md`).
- W — the 48 accounts on which the ledger and the P&L disagreed on write-offs before `9f09d9c87`
  (recomputed from the pre-fix control on the published run, since the finding names only 8).

**Predictions.**
- **Q1 (walk).** At least 80% of the accounts whose walk disagrees are in W, and none is
  explained by H alone. Mechanism guessed: the 2248e3baf ledger's `balance_gbp` moves on a
  write-off or repayment event that the statement walk does not book (or books with the other sign).
  PROS-2016-0207g and PROS-2022-0327 being in the disagreement set, and 0207g in W, is the basis.
- **Q2 (VAT).** The 2 "neither" bills are NOT among H's 11 (probability I give it: 60%). If they are
  not, I expect them to be catch-ups whose `catchup_written_off_gbp` is non-zero (the cap writes
  part of the correction off, so the adjustment printed is not the gross delta the VAT rule assumes).
- **Q3 (count).** One cause per control, so two causes in total, neither of them the held estimate.

**What would refute.** Q1 refuted if fewer than 80% of disagreeing accounts are in W. Q2 refuted if
either "neither" bill is one of H's 11. Q3 refuted if one mechanism explains both.

---

## Result (measured 2026-10-16 03:20 BST, origin `bdd6d1657`, committed ledger: 989 accounts)

**Two causes. Neither is the held estimate, and neither is the write-off.**

**Walk: 12 accounts, every one explained to the penny by `part_paid_gbp` on a failed payment.**
`tools/generate_billing_ledger.py` counts a failed payment's `part_paid_gbp` in `total_paid_gbp`
(and so in `balance_gbp`). `statement_export.account_events` moved every failed payment by 0.00.
The 12 accounts are exactly the 12 on the book that carry a part-paid failure; each gap equals it.

| account | walk | ledger | gap = part paid |
|---|---|---|---|
| PROS-2016-0207g | −10.10 | −3.17 | 6.93 |
| PROS-2022-0327 | −430.02 | −389.17 | 40.85 |
| PROS-2022-0327g | −125.70 | −117.72 | 7.98 |
| PROS-2024-0110 | −9.16 | −7.29 | 1.87 |
| SYN-2016-202 | −1.81 | −1.35 | 0.46 |
| SYN-2016-221 | 134.69 | 141.20 | 6.51 |
| SYN-2016-310 | −37.46 | −35.66 | 1.80 |
| SYN-2016-361 | −34.25 | −33.29 | 0.96 |
| SYN-2016-408 | −76.87 | −70.01 | 6.86 |
| SYN-2016-475 | −70.62 | −58.65 | 11.97 |
| SYN-2016-527 | −80.30 | −58.83 | 21.47 |
| SYN-2016-593 | −68.04 | −65.13 | 2.91 |

None of them is a held-estimate account. Earlier ledgers had no `part_paid_gbp` (it arrived with
`9a7449b4b`, the mover's exit model), which is why the walk agreed on 175 and 251 accounts before.

**VAT: the 2 "neither" bills are C5 invoices 110 and 113** (SME, electricity, June and September
2016). They charge 5% on the NET base. They average 31.0 and 30.8 kWh/day, under electricity's
published de minimis of 33 kWh/day (VAT Notice 701/19 §5.2), so 5% is the law. C5's 115 catch-up,
at 64.8 kWh/day, charges 20%. The biller is right. The control was wrong: it read `SME` as
"always 20%".

**Grading.**
- **Q1 — REFUTED on mechanism.** The cause is part payment, not write-off. Membership in W was not
  graded: the W finding names only 8 of its 48 accounts, and two of those (PROS-2016-0207g,
  PROS-2022-0327) are in the 12. With the mechanism exact on all 12, recounting W would not change
  the answer, so I did not spend the run.
- **Q2 — HELD.** Neither bill is one of H's 11. The guessed mechanism (a non-zero
  `catchup_written_off_gbp`) was WRONG: both write off 0.00. It is the VAT rate, not the base.
- **Q3 — HELD on count, two causes, neither the held estimate.** Nothing to hand to
  `grade-the-held-estimate-fix-on-the-81c12-arms`.

**Fixed.** `account_events` moves a failed payment by its `part_paid_gbp`. The VAT control takes
each bill's rate from `tools.independent_bill_validator.statutory_vat_rate` (the published law, read
independently of the biller). Both controls are green on the committed ledger. The mutation that
walks a failed payment as 0.00 again reds the new synthetic leg and the real-book walk.

**Why nobody saw them** (the third part of the item, handed on): the head-green census already
runs all three tests — it is unscoped — and they were green at its last completed run (2026-10-12).
It has not completed since the 10-13 publish: DEFERRED by `resource_headroom` on 10-13 and 10-14
(long jobs holding the memory budget), and timed out at 17,400 s on 10-15. The publish's own
post-publish remainder run is also skipped (`.remainder_annotation.json`: 4 of 4 attempts timed
out). So after a publish, no route runs the tests that read what it published.
