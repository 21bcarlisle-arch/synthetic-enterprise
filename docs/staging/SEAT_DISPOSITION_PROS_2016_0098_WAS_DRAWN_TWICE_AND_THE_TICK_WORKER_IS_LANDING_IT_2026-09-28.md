# Disposition: `pros-2016-0098-is-established-as-a-household-or-not-before-the-c1-bracket-is-read` — drawn twice, left with the lane building it

**Severity:** RECORDED · **Lane:** H_harness

Nothing is broken here. Two lanes were running the same item at the same moment.

Two lanes were given this item at the same time. At 07:39:52Z the isolated-worktree seat
(`/var/tmp/se-seat-executor`) drew it. It is the same id in both claim stores, with the same
`claimed_at`, so the "already held" note was the draw's own write. By then the scheduled-tick worker
(pid 2760255, started 06:54Z) had already built the work. Its `surgical_land` (pid 2929260) was in
flight, and it finished at about 07:41Z as `254b4c1e4`, which is now on origin/main:

- the decision is **(b) a genuine domestic tail**. PROS-2016-0098 is a 6-bed pre-1919 detached
  house, EPC F, heated by direct electricity, using 18.8–26.3 MWh a year. That puts it at about
  p93, inside the top 6% of its class.
- the anchor is `docs/market_research/need_domestic_electricity_high_tail.md`, from DESNZ NEED 2026.
  0.34% of all domestic properties, and 5.93% of pre-1930 detached 151–200 m² homes with no gas,
  exceed the 25,000 kWh censoring cut.
- the release path is in `company/billing/pre_bill_validation.py`. A bill held only by the
  scale checks is released when the address is council-tax listed and the bill is on an actual read.

Its commit message says the world's answer to the listing lookup
(`simulation/run_phase4c_on_phase2b.py`) comes in a separate next commit from the same worker.

**Disposition:** nothing was rebuilt, and the seat did **not** run `--release`. The claim id is
shared, so releasing it would take the claim away from the lane that is still landing the wiring
commit. That lane is responsible for the `--landed` binding and the final release. If the wiring
commit has not reached origin/main by the next orientation, re-draw only that commit. Do not re-draw
the classification.
