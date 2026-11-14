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

## Done (2026-11-14, delivery worker)

**The premise was half stale, and the build is smaller than proposed.** Steps 1 and 2 already existed:
PB8's own-reasons cancel (`simulation/payment_method_dynamics.py`, 12 Oct, shipped at 0) writes to the
same mandate book as DD4b, read through the same `bill_effect`. What was wrong was the route. It was
found out only through that month's collection coming back ARUDD 1, so the ADDACS-first route never
happened.

- `own_reasons_cancellation` now draws its act day inside the billed month through
  `bacs_rails.draw_payer_cancellation`, with the caller supplying the probability. It reuses the
  draw's own uniform (u/p), so no stream moves. The record carries `act_date` and
  `addacs_available`.
- In the act month, `bill_effect` returns `cancelled` together with the ADDACS day, so the triad,
  the arrears engine and the rails all bill it on receipt and present nothing. DD4b rows carry no
  ADDACS day and still overtake their collection (ARUDD 1).
- `dd_collection_book` tells the desk ADDACS 1 on that day. It does so ahead of the channel
  switch, because under one payment truth the triad has already moved that month off DD.
- The control (`test_both_routes_occur_and_...`) covers the whole partition: both routes on one
  book, and the rails and the money side agreeing household by household on what was presented.
  Mutating either leg reds it.
- Knowledge: `dd_failure_basis_and_live_arrears_provision_rates.md` s.4a, with a correction beside
  the earlier "still open" claim. Map row: L2, with the file_scope re-scoped.

**Incident, recorded beside the work.** While editing the shared tree's map in place, I wrote
`open(p, 'w').write(edit(open(p).read()))`. Python opens (and truncates) the file before it reads
it, so the edit read an empty file, raised, and left `docs/design/maturity_map.yaml` at 0 bytes.
The index still held HEAD. The 04:05 reconcile record (e263f56cd9) had found the tree copy
byte-equal to origin's 98ba0292e, so the tree held no unique bytes then. I restored the tree from
origin/main (ebe786128a, a superset of that), plus this row. **What cannot be shown:** any in-place
map edit another lane made between 05:01 and 05:11 and had not landed. If a lane finds a map hunk of
its own missing, that is the cause. Reverse: none needed. Origin holds every landed byte.
