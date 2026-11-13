**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`
**Knowledge:** home-moves -- `docs/market_research/home_moves.md` s.8.8e (a closing credit set against the other fuel's debt)

# The statement walk does not carry the closing set-off (2026-11-14)

*Found while mapping the repayment-posting area (`docs/design/REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` s.3.2).*

## What was seen

The ledger was rebuilt at origin 83991f5fef over the 6fe7827ab2 run with N29's set-off replay. On it,
`company/billing/statement_export.account_events` closes at a different balance from the page's
`build_account_ledger` on **84 of 1,302 legs**. On earlier books this read 0. Every one of the 84 carries a `set_offs`
entry. The residual on each leg is plus or minus that set-off, and the two legs of each household cancel
(OCC-01e79fcf2d4f +11.50 and OCC-01e79fcf2d4fg −11.50). The ledger s.9.8 built at 282510e8d8 reads the same 84, so
this has been live since N29 put set-offs on the page. Reader: `/var/tmp/rpam/s/stmt.py`.

## Why

N29 posts the set-off on both legs: `tools/generate_billing_ledger.post_refunds_and_set_offs` writes it, and
`tools/generate_payment_ledger_data.build_account_ledger` reads it as entry type `set_off`. `account_events` reads
`refunds` and `desk_write_offs` but not `set_offs`. So the statement is missing the money that moved between the
household's two fuels on the closing day.

## Who reads it

`account_events` is read by `tools/domain_invariant_runner.py`, `tools/bill_validation_comparison.py`,
`company/billing/raw_account_export.py` and `background/post_publish_readers.py`. I have not checked which of their
rows the 84 move. Under F11, a statement row that reads these legs should be taken as wrong until that is checked.

## Recommendation (not built here)

Have `account_events` read `set_offs` the way it reads `refunds`, so both legs' balances move on the set-off's date.
Predicted: the disagreement goes from 84 to 0, and no leg without a set-off moves. The control is a two-leg account
whose credit leg is set off against its debt leg, checked on both legs.

**Reverse.** Delete this file.
