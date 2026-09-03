# [SEAT FINDING] The census overlays its LAUNCH TREE's data, so a worktree launch manufactures the reds it then reports

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Filed:** 2026-09-02, from a direct reproduction, not from reading.
**Discharged:** `tests/background/test_publish_gate_subject_is_head.py::test_the_untracked_overlay_reads_the_MACHINES_data_not_the_importing_worktrees`,
`tests/background/test_publish_gate_subject_is_head.py::test_mutation_resolving_the_overlay_from_the_importing_tree_reds`,
`tests/tools/test_head_green_census.py::test_an_overlay_pointing_at_a_FOREIGN_TREE_is_caught_by_where_it_RESOLVES`,
`tests/tools/test_head_green_census.py::test_a_subject_that_cannot_see_the_data_RUNS_NO_SUITE_and_reads_UNPROVEN`,
`tests/tools/test_head_green_census.py::test_the_shortfall_reason_reaches_the_censuss_own_JSON_surface` — both legs are landed at 49e840ec6. Leg 1 resolves the overlay source to the MACHINE's main worktree, so a linked-worktree launch can no longer symlink its own partial sim/cache into the subject; leg 2, overlay_shortfall, makes the census run NO SUITE and read UNPROVEN when the subject cannot see the machine's data, and carries the reason on its own JSON surface rather than emitting reds that are indistinguishable from real ones.

**At least 29 of the 49 reds in run 2 of the HEAD-green census are artefacts of the tree the
census was launched from. They are not red at HEAD.** The register drawn from them is asking for
work that is not owed, and it is `bc57c8e30`'s own route into the draw that is carrying them.

---

## The defect, in one paragraph

`background/process_run_complete._overlay_untracked_data` symlinks the machine's untracked DATA —
`sim/cache` (a 291 MB Elexon/NESO cache) and `node_modules` — into a HEAD checkout, because
`git archive HEAD` cannot contain them. It resolves the source as `PROJECT_DIR / rel`, and
`PROJECT_DIR` is **the tree the module was imported from**, not the machine.

For the publish gate that is always `/home/rich/synthetic-enterprise`, so it has never fired. The
census inherited the helper *"so the census and the gate cannot drift apart about what a checkout
of HEAD means"* — a good reason — and the census **can be launched from a linked worktree**. When
it is, it symlinks that worktree's `sim/cache` into the subject. A worktree's `sim/cache` is
whatever a stray run happened to leave there.

## Reproduced, from this worktree, with the census's own helper

```
census PROJECT_DIR : /var/tmp/se-seat-executor
prc    PROJECT_DIR : /var/tmp/se-seat-executor
overlay src for sim/cache: /var/tmp/se-seat-executor/sim/cache   exists: True   entries: 1
subject: /var/tmp/head-green-census-1wefj003
subject sim/cache exists: True | symlink: True
  resolves to: /var/tmp/se-seat-executor/sim/cache
  entries: ['elexon_ssp_live_rolling.json']
elexon_demand_full.json present: False
```

**One of the machine's twelve cache files.** The shared tree holds all twelve; this worktree holds
one. `git check-ignore` confirms why the checkout cannot supply them itself:
`.gitignore:3:sim/cache/`.

Run the affected module from here and 25 tests fail on that one absent file:

```
25 failed, 41 passed, 1 xfailed in 0.16s
FileNotFoundError: [Errno 2] No such file or directory:
    '.../sim/cache/elexon_demand_full.json'      (every one of the 25)
```

**`process_run_complete` already knows this number.** The constant's own comment, written when the
overlay was introduced:

> a checkout without them fails 85 tests for reasons that have nothing to do with whether HEAD is
> publishable (measured: `FileNotFoundError: sim/cache/elexon_demand_full.json` **under 25 of them
> alone**).

Twenty-five. The same file, the same count, in the census's own dependency — written down before
the census existed and never connected to it.

## Why it is 29 and not 85 — the detail that identifies the launch tree

A checkout with **no** overlay fails 85. Run 2 failed 29 on this cause. The difference is the
signature of a **partial** overlay: this worktree's one file, `elexon_ssp_live_rolling.json`, is
enough to keep the SSP-only tests green while everything needing demand, MID or fuel-mix dies.
That is not what "no overlay" looks like and it is not what "shared tree" looks like. It is what
*this* tree looks like.

Corroborating: both delivery seats working this item have `/proc/<pid>/cwd ->
/var/tmp/se-seat-executor`, and run 2's launcher wrote `/var/tmp/census_run2/head_at_launch.txt`
from that seat.

## THE SCOPE, and it is the part that must not be overstated

**The nightly census is NOT affected.** `head-green-census.service` sets
`WorkingDirectory=/home/rich/synthetic-enterprise`, which holds all twelve cache files. So:

| run | launched from | cache seen | contaminated |
|---|---|---:|---|
| run 1, 04:30, nightly | shared tree (systemd) | 12/12 | **no** |
| run 2b, 12:52, by hand | `/var/tmp/se-seat-executor` | 1/12 | **yes, ≥ 29 reds** |
| tonight, 03:34, nightly | shared tree (systemd) | 12/12 | **no** |

**Tonight's run is clean and needs no repair to be recordable.** This finding does not delay it.
What it corrects is the *reading of run 2*, and that reading is already published in the graded
pre-registration.

## What it does to the run-2 grading

The clauses about the **collapse** are untouched — `tests/background/` 820 → 2 and `OSError`
760 → 0 are real, and a missing cache file cannot explain a fixture-setup failure disappearing.
**C1, C2, C3 and C5 stand exactly as graded.**

What moves is the **residual**:

- **49 is not the count of work owed at HEAD. At least 29 of it is the launch tree.** The honest
  residual is **≤ 20**, and the C3 ten — which are nightly-observed and reproduce here — are the
  solid core of it.
- The register's shape claim, *"`tests/sim/test_renewable_capacity_trend.py` — 25 of the 49, one
  file, over half the entire backlog, triage as one item"*, is right that it is one item and
  wrong that it is work: **it is one artefact and the correct disposition is to drop it, not to
  triage it.**
- `tests/simulation/test_publish_market_feed.py` (4) reproduces here as `assert None is not None`
  and `assert 0 == 3` — no electricity prices — which is the same absent cache surfacing through
  a fail-open that returns `None` instead of raising. Same root, different exception name, and a
  second reason the cause histogram cannot be used as a partition.

**Four of run 2's 29 `FileNotFoundError`s are not located by this reproduction** and are recorded
as unlocated rather than assumed. That is the honest bound on the "at least 29".

## Why this is BLOCKING and not RECORDED

The census is the instrument that certifies every other claim here, and this makes its red list
**depend on the accident of which directory it was started in**. It fails in the direction that
costs most: it invents reds, routes them into the draw through the register, and a worker drawn
onto `test_renewable_capacity_trend.py` would have spent a tick reproducing nothing. It is also
silent — `_overlay_untracked_data` *"never raises: a missing overlay makes tests fail loudly"*,
and loudly is precisely the problem, because the loud failure is indistinguishable from a real red.

This is the R15 shape one level up from the one the census already guards: **a control whose
subject is not the thing it claims to measure.** `verdict()` refuses a run that proved nothing;
nothing refuses a run that measured the wrong tree.

## The repair

Two legs, and the first is the one that removes the class:

1. **The overlay's source is the MACHINE's data, so it resolves to the main worktree** rather than
   to whichever tree imported the module. For the publish gate, main worktree == `PROJECT_DIR`, so
   its behaviour is unchanged by construction — this can only ever fix a linked-worktree caller.
2. **The census fails closed when its subject's overlay is incomplete**, and says so on its own
   surface. A census that cannot see the machine's data has not measured HEAD, and UNPROVEN is the
   answer it already knows how to give.

Leg 1 is landed with this finding and is mutation-proven. Leg 2 is named here and handed on: it is
the leg that makes the class un-recurrable rather than this instance fixed, and it wants the
census's own `--json` surface to carry the reason.

> **LEG 2 IS LANDED, 2026-09-02. `tools/head_green_census.overlay_shortfall`.**
>
> `run_suite` now checks the subject BEFORE launching the suite: each declared overlay entry that
> the machine actually has must be present in the subject and must **resolve to the machine's own
> directory**. A shortfall returns `""`, which routes through the UNPROVEN fail-safe that already
> exists — so the suite is not run at all, no red list is produced, and `_record_observation`
> records nothing. Nothing manufactured can reach the register or the draw. The reason travels on
> `observed` to `result["overlay_shortfall"]` and is composed into `result["reason"]`, so it is on
> the `--json` surface the repair asked for by name.
>
> **What it catches, and it claims no more:** ABSENT (the overlay never arrived — both of
> `_overlay_untracked_data`'s own silent paths, the missing source and the swallowed `OSError`)
> and FOREIGN (the entry resolves elsewhere — still reachable after leg 1, because the overlay
> skips any `dst` that already exists, so a REUSED checkout carries the link an earlier process
> made from an earlier idea of where the data lived).
>
> **What it cannot catch, stated because a control whose scope exceeds its claim fails later:** if
> `_machine_data_dir()` itself names the wrong tree, this agrees with it — two reads of one
> derivation can only agree. That is leg 1's subject and leg 1's test holds it.
>
> **It is keyed to the property, not to today's answer.** Nothing here knows about twelve cache
> files; a pin on the contents would go red when the machine's data legitimately changed and green
> when the overlay broke. Six controls, each naming its own defect, **six mutations applied and
> all six killed** (`python3 -B`), including the fail-DIRECTION one: a machine with no `sim/cache`
> of its own is NOT a shortfall, or the census would refuse to run on a box that has simply never
> populated the cache.
>
> **Run against the real instrument, not only fixtures** — `head_subject_checkout()` from the main
> worktree: `shortfall []`, subject `sim/cache` resolving to
> `/home/rich/synthetic-enterprise/sim/cache`, **12 entries**. So **tonight's 03:34 nightly run is
> not blocked or delayed by this control**, which is the property that mattered most given what it
> is being landed the day before.

## Route

The 25 + 4 are struck from what the register asks for by the repair, not by a disposition —
the next census run from a corrected tree re-renders the register and they leave it because they
pass. Nothing here forgives a red; it removes a measurement that was never a red.
