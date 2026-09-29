# Disposition: `locate-the-never-renewed-leak-on-seed-88888` re-drawn, and its ask is spent

**Item:** `locate-the-never-renewed-leak-on-seed-88888` · **Disposition:** release. The successor `grade-the-pros-2024-0082-capture-against-767bd9c03` now carries the remainder.

The item asked for three things. All three were done in `767bd9c03`, which is already on origin/main:

- **Each arm's first-bill date for PROS-2024-0082.** This cannot be read from `value_cycle_ab.json`, because that file keeps only a count. That is why a re-run was set up.
- **The call-site that sets the re-drawn elasticity.** It is `simulation/customer_events.py:650` (`roll_lifecycle_event`), and it runs only on renewal terms.
- **The prereg for the re-run.** It is `SEAT_PREREG_PROS_2024_0082_FIRST_BILL_PER_ARM_ON_SEED_88888_2026-09-29.md`.

**The re-run is in flight.** At 03:39 BST on 2026-09-29:

- `drive.py` was running as pid 1970916 in the worktree at `5f05e0068`.
- `capture.json` and `run.log` were still being written.
- A `tools.wait_for` waiter was watching that pid.

Doing this item's work again would launch a second copy over the same seed. So this draw releases the item and does not rebuild anything.
