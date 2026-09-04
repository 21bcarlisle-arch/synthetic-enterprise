# PREREGISTRATION — whether dating staleness from process start ends the ten-minute restart loop

**Written 2026-09-04, BEFORE the change is made or measured.** Seat lane.

## What is observed now, at HEAD

`background/process_reconciler.evaluate_boot_sha_drift` calls `boot_sha.changed_paths_since(sha)`,
which is `git diff --name-only <boot_sha> --` — the daemon's boot COMMIT against the WORKING TREE.
`deploy_restart.restart_plan` restarts every unit whose resulting set is non-empty.

Three modules (`background/boot_sha.py`, `background/gap_ledger_reconciler.py`,
`background/head_red_register.py`) have carried UNCOMMITTED working-tree edits in the shared tree
since mtime 1788415856 (~27.4h). They are in the import closure of six daemons.

`journalctl` shows deadmans-switch, naive-organ and staging-watcher stopped and started at
10:18:30, 10:28:31 and 10:38:31 — a ten-minute cycle.

## The mechanism I claim, stated before the fix

Restarting stamps `boot_sha := current HEAD`. The uncommitted edits are still in the working tree.
So `changed_paths_since(HEAD)` returns the same three files IMMEDIATELY after the restart, `stale`
is true again, and the next tick restarts the daemon again. **The remedy cannot clear the condition
that triggers it**, so the loop is permanent by construction, not by timing.

A daemon imports off DISK. A file whose disk bytes were last written 27.4h ago was already in that
state when a process that started 10 minutes ago loaded it. That process is not behind on it.

## The change

Intersect the changed set with the files whose mtime on the loading disk is NEWER than the
process's start (`now - running_age_s`). That set is the code the process genuinely does not have.
Verdict and clock stay on the SAME set — the property `1b98c8360` established, which must not break.

## Predictions, recorded before measuring

1. **deadmans-switch, naive-organ, staging-watcher, supervisor go GREEN** (0 changed, `0.0` behind).
   Their files' mtimes predate their starts. `restart_plan` then holds them and the loop ends.
2. **worker-seat-manager stays RED.** It started ~932,499s ago; `background/secrets_location.py`
   has mtime ~215,000s ago — written AFTER it started, so it is genuinely behind. *This is the
   discriminating prediction: if the fix made every row green it would be a constant-green control
   wearing a filter's clothes, and worker-seat-manager is what forbids that reading.*
3. **The six identical `97646.4` values disappear.** That figure was `max(now - mtime)` landing on
   `head_red_register.py` in six different daemons' sets, so the column was a property of ONE FILE,
   not of any daemon — the same not-per-daemon defect `unincorporated_for_s`'s own docstring claims
   to have retired, live again by a different route.
4. **No published `unincorporated_for_s` will exceed its row's `running_age_s`.** At HEAD six of
   eleven do, by up to 27 hours against processes ten minutes old. This is bounded by construction
   once the set is filtered by start time, so it is a property to key a control to, not a figure.

## What would refute me

- The four daemons stay stale after the filter → the mtimes are not what I read, or the changed set
  is not import-restricted, and the cause is elsewhere.
- worker-seat-manager also goes green → the filter is over-broad and I have built a fail-open
  control that says "current" whatever the world does. **I would rather the fix be refused than
  land that**, which is why prediction 2 is written here first.
- The restarts continue after landing → `restart_plan` is not the only restarter, and I have fixed
  a reading rather than the loop.

---

## RESULT, written after measuring — kept beside the predictions, not revised into them

Replayed on the shared tree's live mtimes and running ages.

1. **REFUTED IN PART, and correctly.** `staging-watcher` and `supervisor` went green as predicted.
   `deadmans-switch` and `naive-organ` stayed RED — and they should have. Their remaining changed
   module is `background/boot_sha.py`, **mtime 31 seconds old**: a lane is editing it right now, so
   that change genuinely landed after they started and they genuinely lack it. My prediction was
   built on the six-daemon set all being the 27.4h files; two of them had a real fourth file I had
   not looked at. The prediction was too strong, the mechanism claim was right, and the fix does not
   depend on this leg: **the loop breaks structurally** because the condition is now one a restart
   can clear, whatever any single row reads on a given tick.
2. **CONFIRMED.** `worker-seat-manager` stayed red (up 10.8 days, module rewritten 60h ago). The
   filter is not a constant-green.
3. **CONFIRMED.** The six identical `97646.4` values are gone; every row now differs by daemon.
4. **CONFIRMED**, with one exception that is a NEW defect rather than a miss — see below.

## A defect found by the measurement, which the predictions did not anticipate

`unincorporated_for_s` can return a **negative** number. `daemon_deployment_report` samples
`now = time.time()` once and stats the files afterwards; a file written in between has `mtime > now`.
I hit `-73.9` reproducibly while replaying against the artefact's stale `now`. Filed in the finding
and deliberately **not** fixed in the same commit: the obvious clamp to `0.0` would break the
`bool(time) == bool(verdict)` invariant, and that is a separate judgement.

## Known limit, stated now rather than discovered later

mtime is a PROXY for "the disk content changed since this process started". It is the honest one
available (a fast-forward or an edit both rewrite mtime at the moment the tree acquired the
content), but a touch with no content change would read as a change. That direction is fail-CLOSED
— it over-reports staleness — which is the correct way for this control to be wrong.
