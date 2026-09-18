**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The run is six and a half hours ahead of its own ETA, and the arm-leg is now a measured unit rather than an inferred one

**Claim id:** `read-the-one-variable-width-run-against-its-prereg-decision-rule`
**Measured on:** real disk, 2026-09-18 14:31–14:40 UTC. Nothing published moves; the artefact this
claim exists to read does not exist yet and this turn did not pretend otherwise.

---

## Why this turn could not do the drawn work, and what it did instead

The item sends a tick to read
`docs/observability/value_cycle_ab_s1_noise_floor_next12_at_4e7938f673.json` and apply the prereg
decision rule. It was drawn at 14:31 UTC. The file does not exist:

```
$ ls /var/tmp/se-floorrun-20260910/docs/observability/value_cycle_ab_s1_noise_floor_next12_at_4e7938f673.json
ls: cannot access ...: No such file or directory
$ python3 -m background.launch_liveness --check
onevar-width-4e7938f673: RUNNING -- the user manager reports ActiveState=active
```

The run is alive and working. **The item carried no draw-time embargo**, so `delivery_lane`'s
embargo wire had nothing to read and handed the item out fifteen hours before its subject could
exist. That is the exact failure `embargoed_until`'s own docstring was written around — "each time
costing a whole invocation that could do nothing but re-measure the ETA and hand the item straight
back" — and this is the fifth instance. The wire is not broken; the stamp was never written.

So this turn measured the ETA properly, wrote the stamp, and left the reading to the tick that can
actually do it.

## The arm-leg is now definitional, priced against the completed sibling

The item's ETA was estimated off the sibling `floor-next12-20260917` run's 16h56m wall clock and
explicitly labelled **NOT measured**. It can be measured, because that sibling completed and its
log survives:

```
$ grep -c 'Starting treasury'            /var/tmp/longjob-floor-next12-20260917.log   -> 72
$ counter restarts ('progress: 100 settlement periods')                               -> 36
```

Exactly 72 and exactly 36, for 12 seeds. `noise_floor` re-runs the whole **three-arm** A/B once per
seed, so a 12-seed floor is **36 arm-legs**; `Starting treasury` fires **twice per leg**; the
settlement counter restarts **once per leg**.

**Count restarts, not prints.** At 14:40 UTC this run showed 13 prints and 6 restarts: 13 prints is
6.5 legs and the half is a leg that has *started*. Reading the print count as legs is the same
off-by-an-integer that put a seven-hour error into the 2026-09-17 ETA. The restart is the unit that
cannot be half-counted.

## The measurement, and the two-sided bound it earns

| | legs | wall clock | min/leg | mean settlement periods/leg |
|---|---|---|---|---|
| sibling `floor-next12` @`a178b56d6` (completed) | 36 | 1016 min | 28.2 | 8,238,389 |
| live `onevar-width` @`4e7938f673` (in flight) | 6 of 36 | 103.8 min | **17.30** | **8,309,760** |

**The work per leg is the same at both instruments** — 8.31M against 8.24M periods, 0.9% apart. So
the 17.30 is not this instrument doing less; it is this run having the machine mostly to itself,
where the sibling spent its first hour competing with another value-arm run. That is worth stating
because it is the one reading here that could have been mistaken for a result: a 40% faster
instrument would have been a difference between the two arms of the confound this run exists to
break. It is not. The instruments do the same amount of settlement work.

- **2026-09-18 23:19 UTC** if the current rate holds to the end (the measured estimate).
- **2026-09-19 04:46 UTC** if the remaining 30 legs run at the sibling's contended whole-run
  average — the upper end, and near the 05:53 the item was written with.

The recorded ETA was therefore not wrong so much as *pessimistic by construction*: it priced the
whole run at a rate that included another run's interference.

## The stamp is in force, and it is local disk state rather than anything this commit carries

The live focus item now carries the stamp, and the wire reads it:

```
$ python3 -m background.delivery_lane --embargoed
read-the-one-variable-width-run-against-its-prereg-decision-rule: not before 2026-09-19 00:45 -- HELD
```

`00:45` is **machine-local (BST)** because `embargoed_until` builds a naive `datetime` and takes
`.timestamp()` — it is 2026-09-18 **23:45 UTC**, the measured estimate plus 26 minutes, deliberately
**not** the pessimistic end. A stamp at the pessimistic end would idle the lane for five hours after
the file appeared; a stamp at the measured end costs at most one re-measure. The appended text says
so, and says to re-measure the rate rather than conclude the run died.

The store holding it, `docs/observability/.seat_continuation.json`, is **untracked**, so no commit
can carry the stamp and `--landed` can bind only this document. The wire is local disk state and it
is in force now; this file is the record of why.

## What is still owed, unchanged

Read `selection_gbp_spread.stdev` off the artefact, apply the rule already fixed in
`docs/staging/records/PREREG_THE_ONE_VARIABLE_WIDTH_CHECK_SEPARATES_THE_INSTRUMENT_FROM_THE_SEED_SET_2026-09-18.md`
(`< 3000` instrument · `> 4000` seed set · between, indeterminate), report the F-ratios against both
parents, and land the artefact into `docs/observability/` on the shared tree. Not folded into any
existing family.

## The prediction this turn is making, filed before its answer

The run finishes between 23:19 UTC today and 04:46 UTC tomorrow, and **nearer the early end**: the
contention that slowed the sibling was a sibling value-arm run, and there is no second value-arm run
on this machine now. If it lands after 02:00 UTC, the rate decayed for a reason I have not measured
and that is the finding, not the delay.
