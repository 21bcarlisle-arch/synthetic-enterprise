**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the published ceiling is anchored on the cgroup now, and the producer structurally cannot reach the constant that landed

**Filed:** 2026-09-22. Claim
`confirm-the-producer-runs-at-1250-without-an-episode-and-anchor-the-published-ceiling-on-the-cgroup`.
Pre-registration:
`docs/staging/records/SEAT_PREREG_WHAT_MOVES_WHEN_THE_CURVES_ANCHOR_STOPS_PRICING_ONE_CHILD_2026-09-22.md`,
filed before the edit and before any regeneration.

## 0. Premise and duplicate, re-measured before the work

The item's two cited commits `b518ddec9` and `f31e3b1cd` are ancestors of `origin/main`, as the
draw said — they are **this item's own enabling precondition**, not its subject. The subject is
the two clauses those commits deliberately left owed, and both were still owed. The named
duplicate claim is **this item's own id**, held in `.seat_work_in_hand.json` by this draw.
**Nothing was spent.**

## 1. Clause (1) — the observation cannot be made, and the reason is not about memory

The drawn instruction was: observe the next `sim-runner.service` cycle, the first to run at
1,250.0. **No such cycle can arrive.** `sim-runner.service` executes from the SHARED tree
(`/proc/<main pid>/cwd -> /home/rich/synthetic-enterprise`), and that tree is **diverged from
`origin/main`: 4 ahead, 9 behind**, with a working copy of `simulation/net_new_acquisition.py`
that reads `SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0`.

| instrument | reading |
|---|---|
| shared-tree `HEAD` | `957d5a04f` — `b518ddec9` IS an ancestor of `origin/main`, NOT of this |
| `git rev-list --count HEAD..origin/main` | 9 |
| `git rev-list --count origin/main..HEAD` | 4 (so it is a divergence, not a lag) |
| shared working copy of the constant | **1200.0** |
| last completed cycle | `run_complete_20260922T000654Z.md`, finished 00:31:29Z |
| that cycle's git | `86504d951` — `git merge-base --is-ancestor b518ddec9 86504d951` → **NO** |

**THE GENERAL SHAPE, which is worth more than this instance.** A constant that lands at
`origin/main` is **inert in the producer** until the shared tree advances, and *nothing in the
landing path says so*. `promote_worktree_landing` reports success against `origin/main`; the
delivery lane binds against `origin/main`; a turn's own gates run against `origin/main`. Every
instrument a landing lane can see says the value shipped. The only instrument that would
disagree is the producer's working copy, and no lane reads it. So **"the first cycle at the new
value" is a clause that can be written into a hand-off, believed, and never become observable**,
and the next reader of `weight_drift("sim_run")` will read a peak from the OLD constant and
quietly treat it as corroboration of the new one. That is a fail-silent, and it is the
flattering direction.

This is a consequence of a divergence that is already filed and owned —
`WORKER_FINDING_REPEATING_ALARM_TREE_DIVERGENCE_2026-09-15.md`,
`WORKER_FINDING_REPEATING_ALARM_PUBLISH_REFUSED_ORIGIN_AHEAD_..._2026-09-20.md`,
`WORKER_RESULT_THE_FORK_IS_CLOSED_AT_ORIGIN_AND_THE_SHARED_TREES_ADVANCE_IS_HELD_BY_ONE_FILE_NEITHER_DOOR_CAN_TOUCH_2026-09-21.md`.
**I did not attempt the advance** — 824 dirty paths, a live worker tick in that tree, and a
lane that owns it; a second writer there buys nothing and can lose another lane's work.

**What IS confirmed, and it is the negative half of the clause.** No `resource_headroom`
episode opened: the episode file's `state` is `"ok"`, and `weight_drift("sim_run")` returns
`drifted: false, observed_peak_mb: 5734.4, samples: 8` — **identical to the hand-off reading,
which is exactly what a producer that never changed constant should return.** The identical
number is not corroboration of 1,250.0. It is the evidence the cycle never happened.

**The ~5,951 MB prediction is therefore still unscored and is NOT claimed.** It becomes
observable on the first cycle after the shared tree advances.

## 2. Clause (2) — the anchor, done

`simulation/premise_population.load_whole_run_rss_curve` anchored on the probe report's
`peak_rss_mb`: `ru_maxrss` of the ONE child `tools/settlement_ceiling_probe.py` spawns.
Production runs that child under `sim_runner.py`, and the kernel — and `admit()` — counts the
pair. New `PRODUCTION_PARENT_RSS_MB = 227.0`, from the two instruments reading the same run at
the same budget (systemd cgroup 5,734.4 MB; probe child 5,507.4 MB), is added to the **anchor
only**.

```
before   1197.0 + (6008.025 - 5507.4) / 4.3402115  = 1312  customer-years   <- published
after    1197.0 + (6008.025 - 5734.4) / 4.3402115  = 1260  customer-years
```

**Why it is not read live, and this is the trap rather than a preference.** The cgroup figure
is only comparable to the child figure at the SAME budget. The moment the constant moves,
`weight_drift` reports the peak of the NEW book, so `live_cgroup − probe_child` stops being the
parent and becomes the parent *plus the marginal cost of the ceiling's own increase* — an offset
that grows every time the ceiling is raised. The pairing is historical by construction; a fresh
probe run re-establishes it, a fresh read does not. Written into the constant's note.

**The second home that had to go.** `tests/simulation/test_net_new_acquisition.py` carried
`CGROUP_PEAK_MB_AT_THE_ANCHOR = 5734.4` and `CGROUP_PEAK_ANCHOR_CUSTOMER_YEARS = 1200.0` — the
correction, hand-copied into the control because the loader did not apply it. **The control was
right about the world and the loader was wrong about it, and the site published the loader's
number.** Both literals are deleted and the anchor is read off the curve, with a leg asserting
`production_parent_rss_mb > 0` so a revert to the single child reds the control instead of
passing it. The x moved 1,200.0 → 1,197.0 in the process: the probe *committed* 1,197.0 at a
budget of 1,200, and only the committed figure is a measurement.

## 3. Predictions, scored

1. **Ceiling becomes 1,260, not the result doc's 1,263 — CONFIRMED,** for the stated reason
   (the doc anchored at the budget 1,200; the curve anchors at the committed 1,197.0).
2. **Slope does not move — CONFIRMED.** 4.340211503740005 before and after; a constant offset
   cancels in a difference of two peaks. This was the leg most likely to catch a wrong edit.
3. **The ceiling control stays green with its margin falling from 62.3 to 10.0 cy — CONFIRMED**,
   and it stayed green with both hand-carried literals deleted, which is the stronger form.
4. **`memory_slack_multiple_over_the_budget` ~1.008 — CONFIRMED exactly (1.008).** The BASELINE
   I predicted it from was wrong: I wrote 1.0498, the feed on disk said 1.0933, because the
   published feed was a cycle stale and still divided 1,312 by a budget of **1,200**. The same
   regeneration moved `capacity_customer_years` 1,200 → 1,250. **A stale feed makes a published
   ratio wrong in BOTH terms, and I only predicted one of them.**
5. **No other consumer reds — CONFIRMED.** `tests/simulation/test_premise_population.py` 50
   passed; the three ceiling controls passed; `site/` door tests over the bound, 18 passed.

## 4. The disagreement, restated

`SETTLEMENT_CUSTOMER_YEAR_BUDGET` 1,250.0 against a published ceiling that was 1,312 and is now
1,260. The gap closes from **4.7% to 0.8%**, with the constant still on the conservative side.
The published ceiling no longer implies a 6,235 MB peak against a 6,008 MB budget.

## 5. Owed, and named rather than done

1. **Clause (1) is still owed and is now a hand-off with a stated precondition**, not a thing a
   future turn can "just check".
2. **The 0.25 share of the guest is still `--rss-share`'s CLI default**, against the admission
   governor's own 23,008.1 MB for the same box — 3.83x larger. Unchanged by this work and still
   the highest-value follow-on: establish it and the memory leg very likely stops binding, the
   funnel's 3,135.5 binds, and the question becomes whether the world can supply the book.
3. **The prose literals `"1,312 customer-years against the budget's 1,200"` and `"slack of
   1.09x"` in `tools/generate_value_arms_data.py` are NOT touched here.** A live lane holds
   `the-ceilings-downstream-still-fits-a-value-that-never-shipped` over exactly those strings.
   They are now stale against the regenerated feed by this commit's own doing, and that lane is
   where they get fixed — a second writer in that file buys nothing.
