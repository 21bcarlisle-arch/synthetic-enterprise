# The company's ledger is paid by one payment-method draw and the seam tells it another

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `W2_payment_channel_dd_consistency_invariant` · **Claim:** `the-company-default-belief-is-measured-against-its-own-ledger` (Lane 0 delivery)

**2026-10-03.** Found while measuring the company's default belief against its own ledger.

## What is true

A household's payment method has two homes in the world, and both are live in every run:

| reader | draw | what it decides |
|---|---|---|
| `background/live_payment_triad.LivePaymentTriad._method_for` | `simulation.payment_behaviour_source.generate_payment_method` (DD / standing order / card / prepayment) | the payment events that cross the seam into the company's ledger: which bills fail, which are paid late |
| `SimInterface.get_payment_method` → `simulation.household_segments.payment_channel_for_customer` | a separate stream, `paychannel_{household}_electricity` | the method the company is told it holds, which the renewal price now reads to choose its provision row (`e0370bf94`), and which the engagement antecedent and the world's own `arrears_engine.payment_method` read |

Measured over 300 ids (`PROS-2016-0000`..`0299`, electricity), mapping standing order and card to
standard credit as the seam does: **153 agree, 147 disagree.** Among the disagreements, 28 households
the ledger bills as direct debit are reported to the company as prepayment, and 23 the ledger bills as
prepayment are reported as direct debit. The two draws are independent, and with a 72% DD share each,
51% agreement is about what chance gives.

## Why it matters now and did not before

`docs/staging/done/SEAT_FINDING_THE_ENGAGEMENT_ANTECEDENT_R1_NEEDS_IS_DESTROYED_BY_A_COLLAPSED_PAYMENT_BUCKET_2026-09-05.md`
measured the same disagreement (41% on DD/non-DD) and called it "NOT a live inconsistency today,
precisely because one of the two never runs". **That premise was already false.** The triad has
called `generate_payment_method` since `3bfd4e98c` (2026-07-18). That finding's search covered
`simulation/`, `company/` and `saas/`, and the caller is in `background/`.

Since `e0370bf94` (2026-10-03) the renewal price reads the ledger's unpaid bills and provisions them on
the row for the seam's method. So about half the book is priced on a provision row for a method that
is not the one that produced the debt. Any per-method default rate the company learns from its own
book (`company/pricing/default_belief.py`) is blurred in the same way, because its cells are keyed by
the method the company was told.

## The fix, not done here

Do what the 09-05 finding asked: one definition. Move `payment_channel_for_customer` onto
`generate_payment_method`'s draw, or the reverse. Either way the triad and the seam then read the same
fact. It is a world change. It moves households between buckets and it will move published bad-debt
figures, so it is fidelity work, done deliberately and measured. It is not a refactor. A control that
asserts the triad's method equals `SimInterface.get_payment_method` for every account in a run is the
one leg that catches the class. Not built here, because building it would mean writing the fix.

## Which draw the world follows, established before changing anything (2026-10-03, Lane 0 `one-payment-method-home-in-the-world`)

Every world reader except the triad already follows `payment_channel_for_customer`:

- **The world's churn response.** `household_segments.active_renewal_probability_for_customer`
  scales the engagement base by `engagement_multiplier_for_channel(payment_channel_for_customer(cid))`.
- **`arrears_engine.payment_method`.** For a resi customer with an id it returns
  `payment_channel_for_customer(customer_id, fuel).value`. Over the live resi book (178 supply
  points, `live_population()` + `successor_supply_points()`, each on its own fuel) it agrees with the
  seam on **178 of 178**.
- So do `final_bill_outcome`, `experienced_bill_shock`, the run's NF payment channel and the seam
  itself.

**The triad was the only reader of the second stream.** On the same live book it agreed with the
seam on **112 of 178**. It also asked every supply point as electricity, so a gas leg read the
electricity anchor on its own id. That covers both the `g`-suffixed legs and the 16 gas-only
households, whose ids carry no suffix.

## The fix, done

`payment_channel_for_customer` is the one draw. `generate_payment_method` now takes the channel
from it and only refines standard credit into standing order or card, using its existing sub-split
stream keyed on the household's electricity leg. `SEAM_CHANNEL_FOR_METHOD` maps the four-way method
onto the seam's three values. The triad is handed the supply point's fuel by the run
(`record_period(..., fuel=commodity)`).

- Live book: triad = seam on **178 of 178**. Marginals over 4,000 ids: electricity DD 72.3%, gas
  DD 75.8%.
- Control: `tests/background/test_the_ledger_pays_by_the_method_the_seam_reports.py`. It first
  checks that all three channels and a gas-only household are present, then requires the ledger's
  method to equal the seam's for every resi supply point. Restoring the independent stream reds it
  (69/178). Dropping the fuel in the triad reds it (21/178, all of them gas legs).
- **World change, recorded as fidelity.** It was decided from the disagreement, blind to results.
  The seam, arrears and churn side is byte-identical. What moves is the payment events in the
  company's ledger: which bills fail, which are late, and which are paid by prepayment. The world
  identity gains a third part, `payment_methods`, because neither the departure digest nor the
  homes digest can see a payment method. Over its probe (400 ids × 2 fuels) the digest goes
  **`8a105ad7c9346758` → `86560148d7db82b7`**, and 384 of the 800 (id, fuel) pairs change the
  channel the ledger is paid by. Departure `cf823b185f8ca51c` and homes `35f8efe8ff02f245` are
  unchanged.
- Expect published bad-debt and arrears figures from the triad's ledger to move on the next run. Any
  per-method figure learned from the ledger before this commit was keyed by a method that had not
  produced the debt.

### What the change moved, and what it deliberately did not

- `tests/background/test_live_payment_triad.py::test_q3_EVERY_PUBLISHED_FIGURE_IS_UNCHANGED_BY_THE_NEW_LEGS`
  pinned five gaps at pass 43's values. Under the old draw it still reproduces them exactly. Under
  the unified draw: detection 0.1182 → 0.0909, latency 2.135 → 1.908, belief 0.1471 → 0.1176,
  population-mix 0.2667 → 0.2133, ageing 0.2470 → 0.2210. These are re-pinned, and the docstring
  names the world change.
- **The H27 harness (`tools/couple_w2_11_d5.py`) keeps its book, and that is owed work, not a
  second home.** Its `H27S…` ids are a synthetic calibration sample. No run bills them, and nothing
  asks the seam about them, so they cannot disagree with it. Re-drawing them through the unified
  draw moved 36 of the registers that file measures, each of which was argued from that sample, and
  re-measuring 36 registers in one turn would be re-pinning blind. The harness now draws through a
  named `_calibration_book_method`, which reads the world's DD and prepayment anchors and is
  byte-identical to its old sample. **Owed:** re-draw the H27 book through
  `generate_payment_method` and re-measure its registers in one deliberate pass. The 36 tests that
  red when you do it are the list of what to re-measure.

### Landed by a later invocation of the same claim (2026-10-03 evening)

The fix above was built in the shared tree and never landed. This invocation carried it into an
isolated worktree and landed it. One part had to be re-done. Origin had replaced the run's
per-record `record_period` call with a monthly bill (`_post_month_bill`, `6e9025e9b`), so the fuel
is now carried on the held month (`"fuel": commodity`) and passed from there. Re-measured here:
restoring the independent stream reds the control at **71/178** (the 69 above used the fuel-specific
DD share; this mutation used 0.72 flat). A fuel-blind triad reds it at **21/178**.

**One leg the control does not guard.** The control calls `LivePaymentTriad._method_for(cid, fuel)`
directly. If the run stopped passing `fuel=held["fuel"]`, every gas leg would be paid by its
electricity anchor and the control would stay green. Closing that needs the run's own ledger
compared with the seam, which means a run. Recorded here rather than covered with a grep for the
keyword.
