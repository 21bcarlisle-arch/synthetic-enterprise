**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_payment_channel_dd_consistency_invariant`
**Evidence:** `tests/tools/test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py::test_an_invoice_is_outstanding_by_what_its_case_still_owes_not_by_its_face`

# A part-credited open bill read "overdue" at its full face; the invoice now carries what it still owes

**2026-09-28.** Follows `SEAT_FINDING_AN_ACCOUNT_CREDIT_DOES_NOT_NET_AGAINST_THAT_ACCOUNTS_ARREARS_2026-09-28.md`
(`ba1b6c259`). That commit netted credit into the arrears case and the household balance, but not
into the invoice record. The premise was therefore live at HEAD, not spent.

**What "outstanding on this invoice" means.** It is what the customer still owes on this bill once
payments and account credit on the same contract (SLC 27.16) are netted. It is not the face. It is
zero on a paid, credited, settled-by-credit or written-off (at book date) bill. On an open failed or
disputed bill it is the case's `arrears_gbp`, the same figure the household balance nets.

**The label.** `overdue` stays: the bill is past due and money is still owed on it. The defect was
never the word. It was that the only amount the record offered was `total_amount_gbp`, the face.

**Change.** `tools/generate_billing_ledger.py` writes `outstanding_gbp` on every invoice, taken from
the same `amount` its case uses. It also writes `credit_applied_gbp` on every bill that has a case,
and it zeroes `outstanding_gbp` when the bill is relabelled `written_off`.
`tools/generate_invoice_data.py` carries both through to the portal feed. A record that predates the
field gets `None`; it is never given the face as a guess.

**Measured** on the worktree's `docs/reports/run_output_latest.json` (dated 2026-09-09, not the
2026-09-28 run the item counted 10 on): **33** open part-credited bills, with GBP 933.10 of credit
netted across them. On every one the invoice's `outstanding_gbp` now equals its case's
`arrears_gbp`. The 33 and the 10 come from different runs and are not compared.

**Control.** The test checks every invoice in the real book: `outstanding_gbp` must equal its case's
`arrears_gbp`, zero when written off or when there is no case. It first asserts that at least one
open part-credited bill exists, so the rare branch cannot pass vacuously. Mutation-proven twice:
setting outstanding to the face → red, and dropping the written-off zeroing → red.

**Not done:** no page renders a per-bill "Outstanding" sum today. `site/explore` does not read
`status`, and `generate_shadow_html` prints `payment_status` without an amount. So no rendered value
moves yet. The fact now has one home for whichever surface reads it next.
