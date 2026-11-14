**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

# A long job waiting on another pid holds its full declared peak, so no commit gate is admitted (2026-11-14)

**What was found** (worker tick, 11:55Z, landing the seat-executor pair).
`longjob-value-test-churn-roll-family` was launched at about 11:42Z with `--peak-mb 11500 --wait-for-pid 1875257`.
For now its unit holds only the `wait-then` wrapper (`sh` at 2 MB and `tools.wait_for` at 16 MB). It waits
on `longjob-vt-published-config-redraw` (pid 1875257: 4.9 GB RSS, 8.5 GB peak, declared 11500).
`resource_headroom.running_long_jobs` counts any declared unit that has a live process at its declared peak,
so the box ledger reads 23,000 MB declared against a 23,010 MB budget. `resource_headroom.admit("commit_gate")`
then returns `admitted: False, budget exhausted`, while `available_mb` is 16,667.

`co_residence` takes the waited-on pid out of the sum when it **admits** the waiter. Once the waiter is running,
nothing takes it out again, so one 11.5 GB job is counted twice until the job it waits on exits.

**What it costs.** Every commit gate on the box queues (`resource_headroom.queued`, 4 h deadline) for the rest of
the vt run, about 13:30Z, which is roughly 1.5 h. So does every long job without `--wait-for-pid`: both of this
tick's landings were refused for 27.5 GB against 23.0 GB. The cost is lost time, not a wrong figure, so it is LATENT.

**Fix shape (not built).** In `running_long_jobs`, a unit whose processes are only the `wait-then` wrapper and
`tools.wait_for` counts at its RSS until the wait ends. The control: a census of {waiter, the job it waits on}
admits a 2,190 MB commit gate, and reverting the fix refuses it.

**Workaround used.** `--wait-for-pid 1875257` on the landing itself (`longjob-land-seat-executor-pair`). That job
now adds its own 3,000 MB to the same double count while it waits.
