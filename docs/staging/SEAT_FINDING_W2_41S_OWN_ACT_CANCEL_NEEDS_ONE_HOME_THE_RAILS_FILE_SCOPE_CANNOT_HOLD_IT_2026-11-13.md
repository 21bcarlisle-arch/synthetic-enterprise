**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_41_a_household_cancels_its_mandate_as_its_own_act`

# W2_41's own-act cancel needs one home, and the rails file_scope cannot hold it (2026-11-13)

**Found by** the delivery worker on 13 Nov, about 23:30 GMT. It was drawn to build W2_41 (lane 1), after the
final-bill item it held turned out to be spent: its landings ceed1aa38 and ceeefa596 were both on origin, through
99c8e05dd and f16b29a31b. No fork was dispatched, for the reason below.

## What it is

`simulation/bacs_rails.py::draw_payer_cancellation` exists, refuses on its GAP (`PAYER_CANCELLATION_PROBABILITY =
None`, `docs/market_research/bad_debt_provisioning.md` §4a), and **no run code calls it**. The only cancel the world
draws today is DD4b's shock response. It is decided once, on the per-household `SHOCK_RECORD_KEY` record
(`simulation/dd_shock_response.py`), and read through `bill_effect` by both sides:

- the money side: `simulation/arrears_engine.py` ~1069 (`shock.cancelled` moves the bill to pay-on-receipt) and
  ~1089 (`shock.cancel_return` returns the collection unpaid);
- the rails: `simulation/dd_collection_book.py` ~610 (`instruction_cancelled=` gives ARUDD 1) and ~633 (ADDACS 1
  the next working day).

## Why the atom's file_scope cannot fix it

The map row scopes W2_41 to `simulation/bacs_rails.py` plus its test. A cancel the household makes on its own,
noticed before the next collection, changes whether that collection is presented. If only the rails drew it, the DD
book would stop a collection that `arrears_engine` still resolves through `payment_outcome` or the triad. That gives
two homes for one fact, the shape the one-payment-truth work removed.

## Proposed shape (reversible, world-only, decided blind to company results)

1. Draw an unprompted cancel month once per household, on the same record as DD4b's response (or a sibling key read
   by the same `bill_effect`). The draw is `draw_payer_cancellation`, with its probability supplied by the caller,
   from a toggle that defaults to 0 or None. The rate is a GAP, so no number ships, and nothing published moves.
2. `bill_effect` exposes it as `cancelled` from the month after the act. The ADDACS 1 day is the act day plus one
   working day. The next collection is never presented, and that bill is payable on receipt on both sides.
3. One control over the whole partition, with the toggle at 1.0 on a small book: assert that both the own-act route
   (ADDACS 1 with no failed collection before it) AND DD4b's overtaking route (ARUDD 1 then ADDACS 1) occur. Then
   assert that the money side and the rails agree, bill by bill, on which collections were presented.
4. Re-scope the map row's `file_scope` to `dd_shock_response.py`, `arrears_engine.py`, `dd_collection_book.py`
   and `bacs_rails.py`. This file does not edit the map: `docs/design/maturity_map.yaml` carries another lane's
   unlanded hunks in the shared tree.

**What L2 means here.** The rate is a GAP, so L2 is the mechanism working end to end at a stated test probability,
on one home, with that control. It is not a shipped rate.

The build stays on W2_41 itself, re-scoped as above; this finding mints no new atom.
