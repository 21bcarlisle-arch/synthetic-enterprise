**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the first cycle at `SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1250.0` has not run, and the
blocker is the shared tree's working copy, not the ahead/behind count the item was drawn on

**Filed:** 2026-09-22, ~00:53 UTC. Drawn as Lane 0 delivery,
`observe-the-first-producer-cycle-at-1250-once-the-shared-tree-advances`. No pre-registration was
filed because the outcome (unobservable) was clear from the precondition check itself, before any
measurement whose answer was unknown — see §1.

## 0. Disposition

**Not landed. Not premise-spent — the premise (a cycle will eventually run at 1250.0) is not
retracted, just not yet true.** Released after filing this. The item's own `DO NOT DRAW BEFORE`
clause needs to change: "the shared tree advances" (ahead/behind commit counts) is not the right
gate. The right gate is stated in §2.

## 1. The item's stated precondition is now met, and the observation is still impossible

The item was drawn against "4 ahead, 9 behind" on the shared tree
(`/home/rich/synthetic-enterprise`), with `b518ddec9` absent. That has changed:

- `b518ddec9` (the fix this item exists to observe) is now an ancestor of both the shared tree's
  `HEAD` and `origin/main`.
- `git show HEAD:simulation/net_new_acquisition.py` in the shared tree reads
  `SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1250.0`.
- The shared tree is now `ahead 5, behind 1` of `origin/main` — much closer than the item's
  snapshot.

So the commit-history precondition the item named is satisfied. **The cycle still has not run at
1250.0**, because `sim_runner.py` loads the module off disk, not off `HEAD`, and the disk copy is
dirty:

```
$ git -C /home/rich/synthetic-enterprise status --porcelain simulation/net_new_acquisition.py
 M simulation/net_new_acquisition.py
$ git -C /home/rich/synthetic-enterprise diff HEAD -- simulation/net_new_acquisition.py \
    | grep SETTLEMENT_CUSTOMER_YEAR_BUDGET
-SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1250.0
+SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0
$ stat -c %y simulation/net_new_acquisition.py
2026-09-21 16:41:38 +0100
```

The dirty edit's mtime (21 Sep 16:41) predates every commit in the ceiling chain — `c4bee75e3`
(21:15:59), `b518ddec9` (00:26:39), `f31e3b1cd` (01:19:21) — so this is not a live in-progress
repair racing the landings; it is stale, uncommitted local work that the three landings (built as
content-only commits, per the `surgical_land --content` pattern) never touched, because that
pattern lands bytes into history without ever writing the shared worktree.

`background.origin_reconcile`'s own log confirms this is a known, owned blocker, not a guess:

```
[2026-09-22 00:44 UTC] ... Refused by 8 path(s): ... simulation/net_new_acquisition.py
(modified here, and origin changes it too); ...
THE STEP IS TO LAND OR REVERT THOSE PATHS ... `python3 tools/isolate_hunks.py --survey <path>`
lists the hunks and `python3 -m tools.surgical_land --content <path>=<isolated> <path>` lands
your bytes ...
```

`sim-runner.service` restarted at **01:03:50** today (`ExecStartPre=boot_sha` exited 0), i.e.
*after* `b518ddec9` landed at 00:26:39 — and still loaded the dirty 1200.0 copy, because the
working-tree dirt predates the restart too. The most recent completed run's marker
(`docs/staging/run_complete_20260922T000654Z.md`) names `Git: 86504d951`, which is not an
ancestor of `b518ddec9` — independent confirmation that no run has executed under the new
constant.

## 2. The corrected `DO NOT DRAW BEFORE`

Do not draw this again on an ahead/behind count. Draw it only once **both**:

1. `git -C /home/rich/synthetic-enterprise diff HEAD -- simulation/net_new_acquisition.py` is
   empty (the working copy, not just `HEAD`, carries 1250.0) — currently false, blocked on
   whichever lane holds the 5 modified / 2 untracked paths named in the 00:44 UTC
   `origin_reconcile` refusal, and
2. A `run_complete` marker postdates that reconciliation and names a SHA that is a descendant of
   `b518ddec9`.

`origin_reconcile` already owns closing (1) on its deadman cadence; this is not a probe to launch,
per the item's own instruction — it is a state with an owner.

## 3. A related, separate finding: the daemon boot-stamp mechanism cannot see this class of gap

While checking whether the running `sim-runner` process could be independently attributed to a
commit (rather than inferred from disk state), I read `background/boot_sha.py`, the module
CLAUDE.md's own rule table cites for exactly this ("A daemon running STALE code is flagged by
construction"). **It has no `if __name__ == "__main__":` block** — contrast
`background/origin_reconcile.py:1712`, which has one. The unit's
`ExecStartPre=-/usr/bin/python3 -m background.boot_sha sim-runner` therefore imports the module,
executes nothing, and exits 0 — `stamp()` is never called from that invocation.

Evidence: `docs/observability/.daemon_boot/sim-runner.json` is stamped `ts=1789697984.358213`
(2026-09-18 03:19:44), but `systemctl --user status sim-runner.service` shows
`Active: active (running) since Tue 2026-09-22 01:03:50 BST` with `ExecStartPre` reporting
`code=exited, status=0/SUCCESS` — a restart the stamp file never recorded. Every other stamped
daemon file under `.daemon_boot/` is similarly stale relative to known restarts.

This does not silently defeat `reconcile-watch`'s "boot-sha drift" alarm — that alarm already
fires (`00:43 UTC boot-sha drift: ... sim-runner (44 modules behind) ...`) and is directionally
correct by accident: comparing a frozen Sep-18 stamp against current `HEAD` still reports "behind"
after any later restart, whether or not the stamp itself updated. But the **count is wrong** (it is
measuring drift from the wrong boot instant), and nothing distinguishes "sim-runner hasn't
restarted since Sep 18" from "sim-runner restarted three times since but the stamp never took" —
the second is this repo's actual state, and the remedy differs (fixing `boot_sha.py`, not
restarting a daemon that has already restarted). Filed rather than fixed here: it is a different
subject (daemon boot-liveness infrastructure) from this claim's subject (observe one cycle), and a
one-line fix landed under this claim's binding would misattribute it.

## 4. Why this matters for the item's own stated trap

`resource_headroom.weight_drift("sim_run")` reading an **identical** `observed_peak_mb=5734.4`
across 8 runs is exactly the fail-silent-in-the-flattering-direction the item pre-registered
against — and it is now confirmed, not just guarded against: no run in that window executed under
1250.0, so identity was never evidence of corroboration. The prediction in the item
(peak → ~5,951 MB, +217 MB, 0.43× of 13,824 MB) remains unscored. It should stay unscored until
§2's two conditions hold.
