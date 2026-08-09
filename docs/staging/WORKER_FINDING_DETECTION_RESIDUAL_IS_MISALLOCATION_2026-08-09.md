# WORKER FINDING — the payment DETECTION headline does not count what it says it counts

**Date:** 2026-08-09 · **Found by:** worker tick building atom `D10_detection_headline_is_single_channel`
**Advances:** D8_ambiguous_remittance_misdating
**Status:** RECORDED, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — the machine is not blocked).
**R12:** nothing was tuned. The detection gap is byte-for-byte what it was. What changed is the sentence describing it.

## The claim that was published

Every surface this instrument feeds — `tools/couple_w2_11_d5.py`'s `det.note`, the live ledger note in
`background/live_payment_triad.py`, `coupled_gap_ledger.json`, and the Proof door that reads it — described the
W2_11↔D5 detection gap as:

> "fraction of true payment failures the company **never observes** through the seam — the no-remittance blind spot"

## What is actually true (observed, not inferred — R9)

Asking the company's **own** `expected_collection_misses` organ at each invoice's `due + grace` date, rather than
only at the single `as_of` the scorer happens to ask on:

| seed | detection gap | true failures | never detected by **either** channel |
|------|---------------|---------------|--------------------------------------|
| 7    | 0.0725        | 138           | **0** |
| 11   | 0.1515        | 132           | **0** |
| 23   | 0.0811        | 148           | **0** |

Nothing goes unobserved. The misses the headline counts are cases the company **detected on time and then
un-detected**. Mechanism, inspected case by case:

```
seed 7, H27S7C000024, prepayment
  p0 FAILED, p1 success, p2 success
  flagged at due+5 : ['H27S7C000024::0']   <- correct, on time
  open at as_of    : ['H27S7C000024::2']   <- the failed invoice went quiet; a PAID one took its place
```

A later period's ambiguous non-DD payment carries no invoice reference (`correlation_id` does not match any
`invoice_ref`), so `AccountLedger.allocate`'s oldest-first fallback puts it on the **failed** invoice. Clayton's
Case — the mechanism `D8_ambiguous_remittance_misdating` was minted for, showing up in a dimension nobody had
looked for it in.

The no-remittance blind spot is **real** (a failed non-DD payment emits no rail event at all). It is simply not
what this residual is made of.

## Why it matters beyond the wording

D7 measured the wrongful-**dunning** exposure (truly-current invoices believed in arrears). This is its twin in
the other direction: a real arrears case **disappears from the company's arrears view entirely**, so it is never
pursued. For a real supplier that is un-recovered debt and a mis-stated provision, not a cosmetic error.

## What was done about it this tick

- Corrected at every site that repeated it: `det.note`, the live ledger note, the module `notes` (new key
  `detection_residual_is_misallocation_not_blindness`), and the H27 simplification register.
- Pinned by `test_detection_residual_is_misallocation_not_a_never_observed_blind_spot`, which **fires** if any
  true failure ever does escape both channels — so the corrected sentence cannot rot the way the old one did.
- Recorded as evidence on `D8_ambiguous_remittance_misdating` (level unchanged at 0 — this is evidence for that
  build, not the build).

## What was NOT done, and why

The detection dimension's own definition (`flagged_set` = believed-unresolved **at `as_of`**) was left exactly as
it was. Changing it would move a published number, and the honest reading is that the number is fine — the
sentence next to it was wrong. Whether the dimension *should* be an ever-detected set rather than a believed-at-
`as_of` set is a real design question and belongs to whoever takes `H27_payment_belief_gap` to L3, with the
Expert-Hour pass that entails.

## Second, smaller correction carried in the same tick

The 2026-08-08 HARDEN pass recorded that DD detection latency "cannot be honestly measured in this scenario
because the adapter emits `value_date == due_date` with no ARUDD lag". That was the **wrong field**, not a
missing capability: `WallResponse.observed_at` — the bank-feed report date, carried onto
`DDFailureObservation.observed_at` — is already lagged `0..ARUDD_NOTIFICATION_LAG_DAYS` by the seam. Measured DD
lags are `{0, 1, 2}` days. The measurement was available all along. Retracted in the register.
