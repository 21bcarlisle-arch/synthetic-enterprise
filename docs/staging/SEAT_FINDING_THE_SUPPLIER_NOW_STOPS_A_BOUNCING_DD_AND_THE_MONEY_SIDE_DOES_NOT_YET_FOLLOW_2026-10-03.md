# The supplier now stops a bouncing DD, and the world's money side does not yet follow

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `build-the-supplier-dd-stopping-rule` (Lane 0). **PB8 L0 -> L1.**

## What landed
*Built by a scheduled worker (pid 2590080, about 12:38) that died before landing it. The executor
seat re-drew the item at 16:41, found the holder gone and the shared-tree copies on the same base as
origin/main, re-ran the controls (48 green; `<`→`<=` and cancel→`False` each red 2/21), and landed
them unchanged with the map row and the level record.*

- `company/billing/dd_collections_desk.py`: `record_collection_outcome` cancels the mandate
  (`cancel_mandate`, `as_of` = the return's date) after `DD_STOP_THRESHOLD_CONSECUTIVE_RETURNS`
  consecutive returns, and says so (returns True). `instruct_collection` refuses a cancelled
  mandate. `pays_by_direct_debit(cid)` is the new query. `cancel_mandate` now has a production
  caller in the collections path. Before this, its only caller was the portal.
- `simulation/dd_collection_book.py`: once the desk has stopped a customer's DD, their later bills
  go onto no rails at all, and no new mandate is opened for them.
- Controls (`tests/company/billing/test_dd_collections_desk.py` §11): N returns leaves DD; N-1 does
  not; a success between returns resets the run; a partition control over a 40-household rails
  book reaches both cancelled and active. The mutations `<`→`<=`, cancel→`False`, and dropping the
  cancelled refusal each turn it red.
- The three ground-truth replay tests in `tests/simulation/test_dd_collection_book.py`: the first
  now asserts a PREFIX (the register is ground truth up to the stopping return, then empty). The
  two RNG-sync tests hold the stop off, because their subject is a full year of draws.

## N, and the question put to the director
British Gas is the only supplier found that publishes a count: "If your payment fails for a second
time, we'll have to cancel your Direct Debit and send you a bill instead"
(https://www.britishgas.co.uk/help/struggling-to-pay/what-happens-if-i-dont-pay.html). **Their 2
counts presentations of ONE collection**, the original plus a re-presentation about 14 days later.
OVO publishes only "retries every 7-10 days". This world does not re-present, so 2 consecutive
returned monthly collections is the closest reading. If a world "failure" is net of
re-presentation (the C1 gap), it would be 1. NTFY `G1hjgUfv3nsL` (delivered 2026-10-03) put the
question with a recommendation: keep 2, and send the customer to pay-on-receipt.

## What is NOT done (PB8's L2)
The stop reaches **the DD register only** (the DD-rails business surface). Two readers still use
the fixed-for-life `simulation.household_segments.payment_channel_for_customer` draw:
- `simulation/arrears_engine.py` `payment_method`, so a stopped customer's later bills are still
  drawn with DD outcomes and DD provision buckets;
- `SimInterface.get_payment_method`, so the company's engagement ledger still reads them as DD.

Making the channel follow the mandate needs the desk's stop date available inside the run's bill
loop (`run_phase2b`), not in the post-hoc rails pass. That is a sequencing change across the
seam, and it will move published bad-debt figures. It is the next build on this row. The household-
authored route stays parked on the published-rate gap.
