**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is a harness/provenance state, not domain understanding.

# The register repair landed in the one tree the pair move is forbidden to use, and the floor is three hours later than every document says

Filed against the Lane 0 item *"pair-move the 20260910 run and its floor so the independent grading
reaches the page"*. **The pair move itself is NOT done** — the floor it waits on does not exist yet.
Section 4 is the corrected arrival time; sections 1–3 are what I found while establishing it.

---

## 0. Premise re-measured 2026-09-10T17:5xZ — UNSPENT, and the item's own claim about the register is FALSE

The drawn item says: *"`launch_liveness --check` now genuinely grades this floor."* At origin/main
it did not. Run from a clean worktree on `origin/main` at the start of this turn:

```
longjob-noise-floor-20260910.service: UNREGISTERED -- this job is RUNNING and the register has
  never heard of it, so `--check` cannot grade it, the deadman cannot page on its death, and any
  document saying it is in flight will never be contradicted.
longjob-arms-rerun-20260910b.service: UNREGISTERED -- ...
check: PASS on the records held -- but 2 RUNNING job(s) are covered by no record at all, so this
  PASS is not about them (`--unregistered` refuses)
```

The rest of the premise **stands, unspent**: the published floor is still `2026-09-09T15:17:31Z`,
older than the candidate run `2026-09-10T14:04:08Z`; `site/data/value_arms.json` still carries no
`belief_against_control_outcomes` key.

## 1. Why the register said UNREGISTERED, when a landed finding says it was repaired

`SEAT_FINDING_THE_LAUNCH_REGISTER_GUARDS_ITS_DOOR_AND_NOTHING_GUARDED_THE_WALL…` (at `083d84bf2`)
states the operational repair: *"`noise-floor-20260910` is now registered in the live register with
its real launch time."* That is true — **of `/home/rich/synthetic-enterprise` only.**

`docs/observability/.launch_records.json` is a **tracked** file, in `HEAD`, not gitignored. Its
contents therefore differ per tree, and the repair was written into the shared tree's working copy:

| tree | records held |
|---|---|
| `/home/rich/synthetic-enterprise` (shared) | 11, including both running jobs |
| `origin/main` (`6006b8dd2`) | **2**, neither of them a running job |
| `/var/tmp/se-floorrun-20260910` (the floor's own worktree) | **2** |

**The bite is the composition with that same finding's own conclusion.** Section 5 of it establishes
that the pair move *must* be done from a worktree on origin/main, because the shared tree lacks the
run artefact and its producer is many commits behind. So the register was repaired in the one tree
the work is forbidden to be done from, and is unrepaired in every tree it is allowed to be done
from. Both statements were true and the pair of them is the defect. This is the
*hand-off-written-from-an-isolated-worktree-goes-to-a-store-no-tick-reads* shape, with the twist
that here the store is **tracked in git** — so it looks like shared state and behaves like local
state until someone commits it.

**Repaired in this commit**, in the tree that can land it. Both running units are now recorded at
origin/main with their real launch times (`14:50:22Z` and `15:06:45Z`, from `ps`/systemd, not the
moment I got round to it), and both legs now grade them:

```
noise-floor-20260910:  RUNNING -- ActiveState=active
arms-rerun-20260910b:  RUNNING -- ActiveState=active
check:         PASS (no stale liveness claim; every running longjob-* unit is covered)
unregistered:  PASS (every running longjob-* unit has a live record)
```

Fields were copied from the shared tree's entries verbatim, so a later `se-origin-reconcile` sees
two registers that agree rather than two that conflict.

## 2. There are TWO nine-seed `floor-all` runs in flight for 2026-09-10, not one

Nothing I have read names this. They were launched 16 minutes apart:

| | `longjob-noise-floor-20260910` | `longjob-arms-rerun-20260910b` |
|---|---|---|
| started | 14:50:22Z | 15:06:45Z |
| seeds | `11111…99999` (5-digit) | `111111…999999` (6-digit) |
| leg | `--redraw-mode all` | `--leg floor-all` |
| writes | `…noise_floor_20260910.json` | `…noise_floor_2026091**0b**.json` |
| producer tree | `/var/tmp/se-floorrun-20260910`, pinned `4e7938f67` | `/home/rich/synthetic-enterprise` |
| that tree vs origin/main | **in** origin/main | **15 behind, 9 ahead** |

**The drawn item names the right one.** The `…_20260910b.json` floor now in flight is being produced
by a tree 15 commits behind origin/main — the exact condition section 5 of the prior finding says
disqualifies a pair-move source. Whoever does the pair move must take
`value_cycle_ab_s1_noise_floor_20260910.json` and **not** the `b` file, which will appear on disk
looking newer and equally plausible. Two artefacts one letter apart, from two producers, is the
`ALTERNATING verdict` shape waiting to happen.

The divergence is **widening**, not static: the prior finding measured 11 behind / 6 ahead a few
hours ago; at 17:5xZ it is **15 behind / 9 ahead**. The run artefact
`value_cycle_ab_s1_three_arm_20260910.json` is still absent from the shared tree's `HEAD`.

## 3. Both jobs' stated arrival times were computed for a box running one job

They are sharing one machine. The floor job alone reports `Memory: 5.8G (peak 6.7G)`. The
arms-rerun's own systemd `Description` says `~3.9h`, i.e. ~19:00Z; it is roughly 11% through its
work after 2h44m. Neither estimate survived the other job starting.

## 4. The floor arrives ≈22:30Z, not 19:50Z — two independent estimators, derived not guessed

The drawn item and the prior finding both put the floor at ~19:50Z / "roughly four hours out". At
17:50Z it is **38% done**. Measured two ways that do not share a mechanism:

**A — pass count.** The completed 3-seed floor run (`…_20260909.json`, 3 seeds) logged **18**
`Starting treasury` banners, so a seed costs **6 passes**, not 3. Nine seeds is therefore **54**
passes, and *this is where the published estimates went wrong* — 27 is the number you get from
"three arms per seed", which is what the docstring says and not what the log counts. At 17:50Z the
run has started 21 of 54 in 3h00m → ~8.5 min/pass → **≈22:28Z**.

**B — the log's own cumulative counter.** `8,471,900` settlement periods processed at 17:50:54Z,
with the in-flight pass at `2025-06-07` ≈ 94% through the decade → 20.94 pass-equivalents →
~404,600 periods/pass → ~21.85M for the job → 38.8% done → 46,900 periods/min → **≈22:36Z**.

Two estimators, one from banner counts and one from a period counter, agree within 8 minutes:
**≈22:30Z, roughly 2h40m later than every document currently says.** Stated as a *floor*, not a
point: it assumes contention continues, and it will move earlier if the arms-rerun finishes or is
killed first.

**Why this matters operationally rather than cosmetically.** A lane that polls at 19:50Z finds no
artefact and a live unit, and the two readings available to it are "still running" and "died
silently". The register repair in section 1 is what makes that distinguishable — but only now that
it exists in a tree the polling lane is allowed to read.

## 5. What this does NOT settle

- **The pair move is not done.** It is blocked on an artefact that does not exist, now expected
  ≈22:30Z. The mechanism is already established and needs no further measurement:
  `SEAT_PREREG_WHAT_THE_20260910_PAIR_MOVE_CHANGES_AND_WHICH_PAIR_THE_BOUNDS_COME_FROM_2026-09-10.md`
  refuted its own predictions 1 and 2 and confirmed the canonical pair
  (`THREE_ARM_PATH`/`NOISE_FLOOR_PATH`) is what restores `contrast_bounds`, taking
  `is_it_available_today` to `true`. The remaining work is mechanical: copy both, re-run
  `tools.generate_value_arms_data`, land run+floor+`site/data/value_arms.json` in one commit, from a
  worktree on origin/main.
- **Nothing here says either floor will finish.** Section 4 is an arrival estimate, not a promise.
- **I did not kill the rival run**, and I do not recommend it blind: `…_20260910b.json` is a
  9-seed floor on a 6-digit seed set and may be wanted for its own reasons. What it must not be is
  silently substituted for the floor the pair move names.
- **The floor still carries no book-identity stamp** — owed work, unchanged, see
  `SEAT_FINDING_THE_NOISE_FLOOR_CARRIES_NO_BOOK_IDENTITY_SO_THE_PAIRING_RULE_IS_A_STAMP_PROXY_WRONG_IN_BOTH_DIRECTIONS_2026-09-09.md`.
- **No control was written for section 1.** The register being per-tree while looking shared is a
  real class, but a guard that fires on "this tree's register disagrees with another tree's" would
  refuse constantly and legitimately during normal divergence. The honest repair is the reconcile
  lane, which exists.
