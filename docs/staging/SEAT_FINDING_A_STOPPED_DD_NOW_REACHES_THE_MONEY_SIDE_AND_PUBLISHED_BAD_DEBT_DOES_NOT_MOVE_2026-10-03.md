# A stopped DD now reaches the world's money side, and published bad debt does not move

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `pb8-l2-the-paying-channel-follows-the-stopped-mandate` (Lane 0). Follows
`SEAT_FINDING_THE_SUPPLIER_NOW_STOPS_A_BOUNCING_DD_AND_THE_MONEY_SIDE_DOES_NOT_YET_FOLLOW_2026-10-03.md`.

## Pre-registration (written 2026-10-03, before anything was run)

**What the item expected.** "That change will move [published bad-debt figures]." The expected
direction was up: a stopped customer moves from DD to pay-on-receipt.

**What reading the code says instead.** For a resi bill, `arrears_engine.payment_outcome` does not
branch on method. DD and standard credit draw the same `_DD_FAILURE_PROB` and `_ON_TIME_PROB` from the
same `bill_substream`. Method reaches the draw by two routes only:
- `_tone_for_bill`, which treats direct debit and standard credit identically;
- `_fuel_poor_for_bill`, which picks the household's fuel-poverty rate BY CHANNEL.

Fuel poverty is a household's circumstance. It does not change because the supplier cancelled the
household's mandate. So the change keeps the fuel-poverty flag on the household's drawn channel (its
trait), and only the PAYING method follows the stop. Re-drawing the flag on the new channel would
flip some households into fuel poverty on the day their DD stopped, with the same uniform draw and a
different rate. That would be an artefact, not fidelity.

**Predictions** (latest run output, `docs/reports/run_output_latest.json`, seed 42):
1. `emergent_bad_debt_lines(...)["total"]` is **byte-identical** before and after. Every resolved
   bill's `outcome` and `days_late` are identical. If either moves, my reading of `payment_outcome`
   is wrong.
2. What moves is the `method` on resolved rows and write-offs. Every bill after a stopping return
   reads `standard_credit`, not `direct_debit`. The ledger's opening arrears stage on those bills
   becomes "Standard credit payment not received", not `DD_FAILED`.
3. Size: the number of stopped customers is small but not zero. A stop needs 2 consecutive failed
   resi draws, with `_DD_FAILURE_PROB` of a few percent a month in the ordinary stress band and more
   in the stressed bands. My guess is **1 to 15 stopped supply points** over the decade, and **tens to
   a few hundred** bills changing method. This is a guess written down so it can be refuted.

**What this means for the item's WHY.** If prediction 1 holds, the per-customer arm does not lose
because the money side thinks a stopped customer is on DD. The world's resi payment outcome is
method-blind, so it cannot lose there. The fidelity gap that matters is upstream: **a household's
payment behaviour does not depend on how it pays.** That is a separate, sourced question (Ofgem
arrears by payment method), and it is not answered here.

## Results

Measured in one process on `docs/reports/run_output_latest.json` (13:00 run, 8,134 issued bills),
using the change itself and the same change with the stops emptied (`/tmp/pb8l2_probe.py`):

| | predicted | measured |
|---|---|---|
| 1. bad-debt total | byte-identical | **HELD.** £17,924.02 both sides, `total` dict equal; 0 of 8,134 outcomes or `days_late` moved |
| 2. what moves | `method` on later bills | **HELD.** 790 bills go `direct_debit` → `standard_credit` (650 paid, 140 failed); 25 of them are written-off cases |
| 3. stopped supply points | 1 to 15 | **REFUTED, 22.** 11 `PROS-` (6 of them gas legs) and 11 `SYN-` |
| 3. bills changing method | tens to a few hundred | **REFUTED, 790.** Early stops (2016-2018) have most of the decade still to bill |

The 790 moved bills fail at 18% (140/790). The book fails at a few percent. A stop selects the
stressed households, which is what it exists to do.

## What landed

- `simulation/dd_collection_book.py`: `supplier_dd_stops(bills, behavioral, seed)` runs the same
  rails loop and returns `{customer_id: period_end of the last bill presented by DD}`. That comes
  from the desk's own `record_collection_outcome` returning True, so the world reads the notice the
  household gets and not the rule. `build_dd_collection_book` is unchanged in behaviour.
- `simulation/arrears_engine.py`: `paying_method(...)` is the one rule. A DD household's bill after
  its stop is `standard_credit` (pay on receipt). `_resolve_bills` uses it for the paying channel and
  keeps `_fuel_poor_for_bill` on the drawn channel.
- `tools/generate_billing_ledger.py`: the same rule, over the same issued bills. A stopped
  household's later failures now open as "Standard credit payment not received", not `DD_FAILED`.
  That was the `W2_payment_channel_dd_consistency_invariant` absurdity, reached by a new door: a
  returned DD with no mandate.
- Controls: `tests/simulation/test_a_stopped_dd_is_paid_on_receipt_by_the_money_side.py`. The
  partition comes first: over a real 40-household stressed book, some DD households are stopped and
  some are not. Then the bill-by-bill rule, outcomes unmoved, fuel poverty on the trait, and the
  ledger. Mutations: stop ignored (3 red), `>`→`>=` (2 red), fuel poverty on the paying channel
  (1 red), ledger on `payment_method` (1 red). `stops.get(cid, period_end)` stays green, and that is
  an equivalence: the book skips a stopped household, so it can be stopped only once.

## What is NOT done, and the reason it is a separate piece

1. **The seam, `SimInterface.get_payment_method`**, which the renewal price and the engagement
   antecedent read in-loop. A stop is decided on DD outcomes, and those need
   `per_customer_behavioral`'s stress. `run_phase2b` builds that only at run end
   (`_build_behavioral_trajectories`, after the customer loop). So the stop does not exist yet at
   the moment the seam is asked. Getting it there is the sequencing change, and it is not done.
2. **`background/live_payment_triad`**, which feeds the company's ledger in-loop. It draws its own
   outcomes, so even with the stop it would not see the returns that made it. Another lane is
   landing "the ledger pays by the method the seam reports" (`/tmp/pm_land`, 2026-10-03). Once the
   seam follows the stop, the triad follows it with no further change.
3. **`dd_balance_book`, `credit_refund_events`, `tools/dd_opening_arms`** still read
   `payment_method`. They are business-surface readers, and none of them reaches a published figure.
4. The rails book in `run_phase4c_on_phase2b` is built over unfiltered `bills`, while the engine
   reads `issued_bills(bills)`. A held bill is presented on the rails and not in the money side.
   This was here before this change. It could make the two disagree on a stop if a held bill sits
   in a failure run.

**The finding the item did not expect.** The item's WHY was "credit is where the per-customer arm
loses, and the money side still believes the customer is on DD". Prediction 1 held, so that is not
where it loses. **The world's resi payment outcome does not depend on payment method at all**, apart
from fuel poverty. If standard-credit households default more than DD households (Ofgem publishes
arrears by payment method), the world cannot show it. Taking a stopped household off DD then cannot
cost anything, and the per-method default belief (`company/pricing/default_belief.py`) is learning
cells that the world made identical by construction. That needs a knowledge-first source before any
number moves. It is handed on as the next piece.
