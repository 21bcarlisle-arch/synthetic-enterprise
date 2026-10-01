**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The PB4 swap landing was drawn twice, and the worker holds it

Claim `land-pb4-swap-with-value-arms-retaken-in-the-new-world`. The isolated seat executor
(pid 2088732, started 16:19:55) drew it. The scheduled worker (pid 2082292, started 16:17:20) had
already drawn it 2.5 minutes earlier: the same LANE 0 text was appended to its tick doorbell.

**The premise is not spent.** 258aeeb44 being an ancestor of origin means the HELD swap and its
design doc landed. The swap itself (the fenced diff), the value-arms retake and the `DEFAULT_TABLE`
repoint have not. The PATH CHECK's two `already landed` verdicts are about the design doc and the
anchor JSON, which are the item's inputs, not what it is meant to produce.

**The rival is real. It is not this draw's own write.** The
`docs/observability/.seat_work_in_hand.json` entry is stamped 16:19:54, which is this draw's own
write. But `ps` shows the worker running `pytest tests/tools/test_generate_value_arms_data.py` in
`/home/rich/wt-pb4-land` (`.se_worktree_owner` = 2082292). That worktree already has the swap applied
to `simulation/customer_events.py`, `departure_level_anchor.py`, `experienced_bill_shock.py` and their
tests.

**Disposition:** the executor stepped aside and built nothing. It did NOT `--release` the id: the
worker shares it, and releasing would return work in hand to the pool for a third draw. The worker's
`--landed` binds to the same id.

**The defect:** the LANE 0 draw can hand one item to the scheduled worker's doorbell and to the
isolated executor within minutes of each other. The DUPLICATE-WORK CHECK reported the executor's own
claim write as "another writer". The real rival is only visible to `ps`. Since a value-arms retake
costs about 53 minutes per seat, a double draw of this item costs hours, not one turn.
