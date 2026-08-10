# [WORKER-REPORT] The fifteenth wedge: the debris of the previous fourteen investigations (2026-08-10)

**Tick:** scheduled worker tick, 2026-08-10 ~13:05 UTC. **Draw:** `DIRECTOR_PRIORITY_BACKLOG_TRIAGE`
(the drain is the priority) — 79 of the 173 root staging files were `run_complete_*` markers, which
only archive at the END of a successful publish. The drain target and the publish wedge were the
same problem.
**Episode at draw:** `wedge_since` 2026-08-09T14:30 UTC, **22h36m**, **126 consecutive failures**,
79 markers queued. **Status: FIXED — publishing unblocked, mechanism landed with R15 proof.**

## What the alarm said, and why it named nothing

`.publish_gate_state.json` carried `episode_failures: 126` with `blocking_tests: []` and
`failures: []`. The log's last cycles named no test either:

```
12:37  Publish gate: could not make the HEAD checkout a git repo: git is not installed
12:39  Publish gate: `git init` in the HEAD checkout failed rc=128 -- fatal: cannot mkdir
12:12  Publish gate RED (rc=-15) -- no FAILED/ERROR summary line found
```

`observed`: git is installed. **`/tmp` is a 7.8G tmpfs — RAM, not disk — and held 5.0G, with swap
at 3.8G/4.0G (95%).** ENOMEM on a tmpfs surfaces at `fork` and `mkdir`, so it presents as a missing
binary and an unwritable directory. That is the third wedge's signature exactly.

## The measured population, and why the existing sweep could not see it

`_sweep_stale_head_checkouts` is real, tested, and runs before the disk pre-flight precisely to make
this self-healing. It globs `publish-gate-head-*`, and its test pins that it owns *"its own prefix
and nothing else"* — which is the right instinct for a daemon. But of the **3.9G reclaimed**:

| bytes | population | swept by the existing control? |
|---|---|---|
| 2.4G | `pytest-of-rich/pytest-{0,31,…,259}` — 13 abandoned roots | no — not the prefix |
| 1.1G | `gate_verify`, `wedge-diag2-*`, `headchk`, `gatechk2`, `gatechk.GNMR`, `headtree_probe`, `headprobe2`, `publish-gate-verify-*` | no — ad-hoc names |
| 190M | `publish-gate-head-9z78t7lu` | matched, and at 20 min old **correctly** spared |

**It reclaimed nothing.** The 1.1G row is the part worth keeping: those are the diagnostic checkouts
left behind by the investigations into wedges three through fourteen. Each cost ~130–190MB of RAM
and none was ever collected. **The fifteenth wedge was caused by the debris of the previous
fourteen** — the diagnosis process became the fault.

## The lesson (R15 shape, already in the register)

*Control keyed to ONE syntactic form.* The control was scoped correctly and the claim built on top
of it — "the exhausted-tmpfs failure is therefore self-healing" — was false, because the claim was
about the whole population and the glob was about one naming convention. A control's blast radius
is not the class it was written for; it is the class its predicate actually matches. **The 22h36m
outage is the cost of the gap between those two.**

## What landed

1. **Reclaimed 3.9G** (`/tmp` 5.0G → 1.1G, 64% → 14%; swap 3.8G → 1.3G), holders verified zero
   across every `/proc/*/cwd` and `/proc/*/fd` before removal. The live publisher (pid 2751990)
   and its suite (pid 2755495, cwd `publish-gate-head-reused`) were untouched and stayed up.
2. **`_sweep_stale_pytest_temp_roots`** in `background/process_run_complete.py`, called at the same
   pre-flight, before the disk check. Same 3h bound; the newest `PYTEST_TEMP_KEEP_NEWEST=3` roots
   are kept whatever their age, so a running suite's own `tmp_path` can never be taken from under
   it; `pytest-current` symlinks are never the deletion target (that would leave the bytes and lose
   the handle). pytest prunes its own roots, but a suite SIGKILLed mid-run — rc=-9, the known gate
   outcome — never gets to, so they accumulate exactly when the gate is already in trouble.
3. **Three tests**, incl. `test_the_checkout_sweep_alone_could_not_reclaim_what_wedged_it`, which
   rebuilds the measured population above and asserts the **pre-fix** control reclaims **0** from
   it — the false self-healing claim, pinned, so deleting the new sweep re-reds rather than quietly
   restoring a 22h wedge.
4. **R15 mutation proof:** neutering the sweep to `return 0` fails all three (3 failed, 14 passed);
   restored byte-identical (`cmp` clean), 17 passed.

## Not mechanised, deliberately — one convention owed

The 1.1G of ad-hoc diagnostic checkouts is **not** closed by a glob. No predicate distinguishes
`headchk` or `gatechk.GNMR` from a directory this process has no business deleting, and a daemon
free-firing at unowned `/tmp` paths is a worse failure than the leak. Closed as a convention
instead: **a wedge investigation materialises HEAD under `HEAD_CHECKOUT_PREFIX`** so the existing
sweep owns it. Recorded here rather than mechanised because the actor is the investigator, not the
publisher — worth a lint if it recurs.

## Second finding, filed not fixed (self-interrupt discipline: QUEUE)

At 12:36 the log records `Publish gate recovered -- cleared wedge state, re-armed alarm`, yet
`wedge_since` still reads 2026-08-09T14:30 and `episode_failures` 126. Concurrent publishers each
load, mutate and write back the whole gate-state JSON, so a **lost update** reverts another's
recovery. That is why the streak counter kept climbing across an interval containing a recovery.
Not fixed here — it is a state-write concurrency defect in its own right, not this wedge's cause,
and the tick is bounded. **Owed: an atom for compare-and-swap (or lock) on `.publish_gate_state.json`.**

— Worker tick 2026-08-10. Publishing unblocked; the marker backlog can now drain on its own.
