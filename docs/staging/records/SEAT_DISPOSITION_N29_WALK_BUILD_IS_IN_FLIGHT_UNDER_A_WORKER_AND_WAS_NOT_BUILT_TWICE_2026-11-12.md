**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `home-moves` -- docs/market_research/home_moves.md s.8.8e, the set-off this build carries

# The N29 walk build is in flight under a worker, and was not built twice (2026-11-12)

*Delivery seat, LANE 0 draw `n29-set-off-netted-in-the-debt-legs-walk`, executor worktree.*

At draw time (about 04:45 BST) the same WORK text was already being carried by a live worker tick.
That worker is `claude -p` pid 3122181, about 1h41m old, in worktree `/var/tmp/se-n29-walk`, on base `39744630a1`.

- The build is done in that worktree. It changes 14 files, adds the test
  `tests/simulation/test_a_closing_dual_fuel_household_is_set_off_before_it_is_refunded.py`, and
  adds its own PREREG and RESULT records (`SEAT_*_THE_SET_OFF_NETTED_IN_THE_DEBT_LEGS_WALK_ON_6FE7827AB2`).
- Its first gate (`/var/tmp/n29/walk_land.log`, 04:09) refused on 4 reds: the seam-currency test,
  `test_main_produces_credit_refund_log`, and two legs of the ledger-vs-P&L real-book test.
  Its drafted message (`/var/tmp/n29/msgbba0`, 04:28) addresses each of those. At draw it was
  re-running `tests/simulation/test_run_phase4c_on_phase2b.py` (pid 4077876).
- Building it again from `/var/tmp/n29/build.patch` would make a second copy of the same 14 files.
  The two landings would then collide on `tools/generate_billing_ledger.py` and
  `simulation/arrears_engine.py`.

**Disposition:** the claim is released, with this record as its reason. The worker's own
`promote_worktree_landing --work-id` records the landing. If the worker dies before it lands, take
the worktree `/var/tmp/se-n29-walk` and its message `/var/tmp/n29/msgbba0` as they stand.
Re-gate them on origin and land them. Do not rebuild from the patch.

The successor `the-1118-repayment-share-is-dated-the-day-its-cash-arrived` is separate work: the
repayment dating at `tools/generate_billing_ledger.py:1118`. It is not the remainder of this item.
