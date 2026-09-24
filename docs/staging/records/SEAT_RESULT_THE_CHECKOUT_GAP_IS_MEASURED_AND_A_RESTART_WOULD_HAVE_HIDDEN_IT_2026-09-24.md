**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The checkout gap is measured now — and the restart the item asked for would have hidden it

Claim id: `the-shared-checkout-is-the-second-gap-between-a-landed-commit-and-a-running-daemon`.
Prediction: `SEAT_PREREG_IS_THE_RESTART_GAP_DETECTOR_BLIND_TO_THE_CHECKOUT_GAP_2026-09-24.md`.
Parent finding: `../SEAT_FINDING_THE_DECLARED_BOOT_STAMPER_HAS_STAMPED_NOTHING_SINCE_2026_09_04_SO_NO_DAEMONS_CODE_VERSION_IS_KNOWN_2026-09-24.md`.

## The premise was NOT spent, and the draw's check asked the wrong oracle

The draw reported all five cited commits already ancestors of `origin/main` and flagged the premise
as possibly spent. They are — and that is the item's *subject*, not its deliverable. The item's
premise is that `origin/main` containing a commit says nothing about whether the box running the
daemons has it. Measured at draw time:

| | |
|---|---|
| shared tree `/home/rich/synthetic-enterprise` HEAD | `e664b5720` |
| vs `origin/main` (`72b1d1d7f`) | **3 ahead, 11 behind — DIVERGED**, so no fast-forward is possible |
| `merge-base --is-ancestor ec1012c01 HEAD` | **NO** |
| `merge-base --is-ancestor 7c77466ce HEAD` | **NO** |
| shared tree's `background/boot_sha.py` contains `__main__` | **no** (0 matches) |
| …contains `read_boot_ts` | **no** |
| shared tree's `process_reconciler.py` contains `stamp-predates-process` | **no** |

The repair is absent from the box, exactly as the finding's addendum said. Premise live.

## P3 was REFUTED, and the corrected reading is worse than the prediction

I predicted the 11 unmerged commits would contribute **zero** paths to every daemon's changed set,
because `changed_paths_since` diffs the boot stamp against *the disk* and `origin/main` appears
nowhere in it.

**Measured: 227 paths across thirteen sessions, not zero.** The mechanism I wrote down was wrong.

Why: the stamps are from 2026-09-17/18, far older than the shared HEAD, so the diff sweeps up
everything that moved in between — and 17 of the 28 gap paths had *also* moved there. They were
visible, but not for any reason connected to the gap.

The control that separates the two is the stamp a restart would write today (stamp == shared HEAD):

| of the 28 paths `origin/main` has that the checkout lacks | visible | invisible |
|---|---|---|
| `staging-watcher`, stamp `9ed1c2daa` (2026-09-17) | 17 | 11 |
| simulated post-restart, stamp == shared HEAD `e664b5720` | 11 | **17** |

Which paths of the gap are visible is decided by **stamp age** and **working-tree dirt** — both
unrelated to the gap. So the non-zero count is not a measurement of the checkout gap even when it
is non-zero. P1/P2's mechanism was wrong; **P4 stands and is the part that matters**: the
comparison is fail-OPEN about the checkout, and the overlap that makes it look covered is
coincidence. That is worse than the clean blindness I predicted, because it looks like coverage.

## The consequence that changes what should be done, and it inverts the item's own instruction

The item says: *"restart the daemons so the repaired boot stamper actually takes effect."*

**It would not take effect, and the restart would destroy the evidence.** Restarting re-runs
`ExecStartPre` against a checkout that still has no `__main__` in `boot_sha.py`, so it stamps
nothing new; and to the extent it stamps at all it moves each stamp to the shared HEAD, which is
the row in the table above where **17 of the 28 gap paths go invisible**. All eleven
`stamp-predates-process` verdicts would clear and not one daemon would gain a line of the repair.

**A restart closes gap 2 and blinds the detector to gap 1 in the same act.** The restart is
correct only *after* the checkout advances, and that ordering is now the thing the report says out
loud instead of a fact someone has to know.

## The other owed item was already discharged — inherited diagnosis, refuted by one control

The finding recorded as still-owed: *"`deploy_restart.restart_plan` restarts on `stale` and should
learn that `stamp-predates-process` is not a restart-able condition."*

Measured, by running `restart_plan` over a four-row synthetic report:

```
a.service  unresolved=stamp-predates-process stale=True  -> HOLD
b.service  unresolved=unstamped              stale=True  -> HOLD
c.service  unresolved=None                   stale=True  -> RESTART
d.service  unresolved=None                   stale=False -> HOLD
```

It already holds it. `unresolved` is tested **before** `stale`, and the fourth rule routes its
verdict through `unresolved` — so the rule's own landing discharged the owed item incidentally.
No change was needed and none was made.

It was, however, **entirely unpinned**: no control anywhere named the verdict, so correct behaviour
rested on the order of two branches any later edit could swap. That is the residue, and it is what
landed.

## What landed

1. **`background/deploy_restart.checkout_drift()`** — gap 1, measured directly. Stands on
   `origin_reconcile.fork_state` rather than re-asking git for the counts. The verdict comes from
   `merge-base --is-ancestor origin/main HEAD`, **never from an exit code** (`reconcile-watch`
   exits 0 every five minutes without advancing anything) and **never from `behind == 0`** (a
   diverged tree is what the box actually was). Fail-closed: unreadable origin → `origin-unreadable`,
   never `behind 0`; git rc 128 → unresolved, distinct from rc 1's honest "not an ancestor".
2. **`daemon_deployment_report()["checkout"]`** — the bound every row is subject to, published
   beside the rows. Each row answers "which modules it imports changed" against the disk; without
   this, eleven green rows on a checkout eleven commits behind were indistinguishable from eleven
   green rows on a current one.
3. **`format_checkout()`** — one line on the surface. On the live shared tree it reads:
   `MISSING 11 commit(s) from origin/main (28 path(s) the daemons cannot load whatever their stamp
   says; restarting them would clear the verdict and deliver none of it)`.
4. **Seven controls** in `tests/background/test_deploy_restart.py`, including the `restart_plan`
   pin above.

**Mutation-proven, each firing the leg written for it** (56 green unmutated):

| mutation | result |
|---|---|
| swap the `--is-ancestor` ref order | 1 failed — `..._asked_in_the_direction_that_can_fail` |
| collapse git rc 128 into rc 1 | 1 failed — `..._unable_to_answer_ancestry_is_not_the_same_as_not_contained` |
| `behind = behind or 0` on unreadable origin | 1 failed — `..._never_reported_as_level` |
| drop the `checkout` key from the report | 1 failed — `..._carries_the_bound_its_rows_are_subject_to` |
| test `stale` before `unresolved` in `restart_plan` | 2 failed — the new pin **and** `test_every_disposition_is_reachable` |
| render an unresolved checkout as the blank line | 1 failed — `..._renders_a_DISTINCT_line` |

Stated rather than left flattering: the diverged-tree leg injects `contains_fn`, so the mutation
"derive `contains_origin` from `behind == 0`" does **not** fire it. The ancestry direction and the
rc-mapping legs are what carry that property; the diverged leg only pins that the two counts are
both reported and neither is used as the verdict.

## Still owed, and deliberately not done here

* **The checkout is still 11 behind.** Advancing it is a write to the shared tree, and this turn's
  isolation is the reason it was allowed to run. It is diverged, so `origin_reconcile`'s
  `--ff-only` cannot clear it: the shared tree's 3 commits must reach origin first. That is
  `origin_reconcile.reconcile`'s own job on the deadman cadence, and it is now *measurable*
  whether it ever does it — which is what this turn was for.
* **The restart must wait for that**, per the inversion above. Doing it now is worse than not.
* **No page yet.** The verdict reaches `docs/observability/daemon_deployment.json` and the printed
  report; it does not reach `site/`. That is the next increment and is handed on.
