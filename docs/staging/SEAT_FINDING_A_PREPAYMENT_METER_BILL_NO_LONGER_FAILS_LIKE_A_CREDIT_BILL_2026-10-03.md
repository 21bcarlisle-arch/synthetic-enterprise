# A prepayment meter's bill no longer fails like a credit bill

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `W2_payment_channel_dd_consistency_invariant` · **Claim:** `a-prepayment-meter-bill-cannot-fail-like-a-credit-bill` (Lane 0 delivery)

Fixed in the same commit. Class absurdity in the world: a meter that is paid before use could
"fail" a bill and have it written off. It contaminated the prepayment per-method cell.
**Claim:** `a-prepayment-meter-bill-cannot-fail-like-a-credit-bill` (handed off by
`SEAT_FINDING_WHAT_THE_PER_METHOD_BAD_DEBT_FIGURE_COUNTS_AND_WHAT_THE_WORLD_PRODUCES_BY_METHOD_2026-10-03.md` §6.2).

## 1. Pre-registration (written before either reading below)

Harness: `/tmp/permethod_probe.py` (the source finding's probe), seed 42, over one frozen copy of
`run_output_latest.json`. BEFORE = origin/main `6f84ea996` unmodified; AFTER = the same tree with
the fix.

1. AFTER, prepayment shows **0 failed bills and £0 written off**, by construction.
2. **Every DD and standard-credit row is identical to the penny**, BEFORE and AFTER. Each bill
   draws its own `bill_substream`, and `supplier_dd_stops` reads only DD households. If any non-PPM
   row moves, a stream I have not read is shared, and this is a world change wider than PPM.
3. The total resi write-off falls by exactly the BEFORE prepayment write-off.

## 2. What a PPM customer's debt is (published evidence, `docs/market_research/company_debt_management.md` §3)

A prepayment meter is paid before use, so there is no bill to miss. A PPM household's real debt
has three sources: standing charge that accrues while it is self-disconnected and is recovered at
the next vend (63% of PPM customers self-disconnect at least once a year), emergency or friendly
credit it does not repay, and credit-account debt recovered through the meter (41% of electricity
repayment plans use PPM). Ofgem's cap allows 0.6% of the PPM cap for PPM debt cost. **No published
source sizes the £ left unrecovered on a meter at exit**, and the world draws no self-disconnection.

**Decision:** `payment_outcome` returns `("success", 0)` for `prepayment`, the vend having paid. The
residual PPM debt is a **named gap in code** (the comment on `arrears_engine.PREPAYMENT_METHOD`),
not a number. The world's PPM write-off is now zero, which **understates** the published 0.6%. That is
the honest direction: before this, 1.71% came from a mechanism that does not exist.

## 3. Results (one process per side, same frozen input)

| group | bills | failed BEFORE → AFTER | write-off £ BEFORE → AFTER |
|---|---|---|---|
| prepayment (drawn = paying) | 907 | 4.63% → **0.00%** | 1,605 → **0** |
| paying DD | 5,334 | 4.78% → 4.78% | 4,280 → 4,280 |
| paying standard credit | 1,743 | 11.99% → 11.99% | 12,039 → 12,039 |
| drawn DD / drawn SC | 6,124 / 953 | unchanged | 15,534 / 785, unchanged |

| | predicted | measured |
|---|---|---|
| 1. PPM 0 failed, £0 | 0 / £0 | **HELD** |
| 2. every DD/SC row identical | identical | **HELD**, to the penny |
| 3. resi write-off falls by exactly £1,605 | −£1,605 | **HELD** (follows from 1 and 2) |

Control: `tests/simulation/test_arrears_engine.py::test_a_prepayment_bill_cannot_fail_or_be_late_because_the_meter_is_paid_before_use`.
It has a control arm: standard credit on the same draws must fail and be late, so a guard that zeroed
every resi failure reds it. Mutation (branch disabled): **RED**. Restored: green.

## 4. Not done, and where it lives

1. **The live triad has the same absurdity by a different route.**
   `payment_behaviour_source.generate_payment_event` maps every non-corporate method, prepayment
   included, to the `direct_debit` core, so the triad can still emit a failed PPM event. That module is
   inside the concurrent claim `one-payment-method-home-in-the-world`, which is unifying the two
   method draws. When it lands, pass the real method to `payment_outcome` there and this fix will
   cover the triad too. Left to that claim, not duplicated here.
2. **The PPM debt mechanism itself** (self-disconnection, accrued standing charge, meter debt
   recovery) needs a published £ size before it is built. Knowledge-map row "Bad debt rates by
   payment method" now says so.
3. Knowledge-map row "PPM and collections" still says "PPM not modeled in sim — all customers
   implicitly on DD". That is stale, because 20 of 175 supply points are drawn prepayment. Corrected
   in the same commit.
