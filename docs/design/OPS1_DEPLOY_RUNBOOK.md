# OPS1 Deploy Runbook — taking the operational layer L2 → L3 (live)

**What this is.** The director-facing procedure to make the *built* OPS1 mechanisms *live* — the
one remaining step to L3 (`OPS1_operational_layer_rebuild`). Everything below reconstructs from the
committed repo alone (no hand-configuration, no hidden machine state) — that reconstruct-from-repo
property IS the IaC mandate, so the deploy being a documented, repeatable script is part of the
deliverable, not an afterthought. Deploy is **reversible** (see Rollback).

**Author:** lead orchestrator, 2026-07-17. Frame-only doc (DISCOVER/FRAME lane); no code change.

---

## What goes live on deploy
The mechanisms are all committed but only take effect once the daemons run current `HEAD` under
their regenerated units:
- **Booted-SHA stamps** (sub-step 5, G-D3): each unit's `ExecStartPre=-python3 -m background.boot_sha`
  records the HEAD the daemon booted from, so the reconciler can flag stale code.
- **Console-sanctity marker** (sub-step 1, held for review): goes live when the worker-seat comes up
  under the new code. **Strictly more-conservative** — it *adds* a spare exemption and keeps the
  inference belt, so deploying it can never newly reap a console; it only removes tmux-dependence.
- **Fresh code** for every migrated daemon (notification contract, reconcilers, fork-lifecycle, …).

## Preconditions
1. `git status` clean; `git rev-parse HEAD == git rev-parse origin/main` (deploy the pushed HEAD).
2. Units match the manifest: `python3 background/generate_units.py` produces no diff
   (a diff means the committed units are stale — commit the regen first).

## Deploy steps
1. **Regenerate units from the manifest** (idempotent; picks up any `ExecStartPre`/field changes):
   ```
   python3 background/generate_units.py
   ```
   If it changes `background/systemd/*.service`, commit + push before continuing (the drift-guard
   test asserts committed == `regenerate()`).
2. **Install** (idempotent; installs every `owner==systemd` unit + the schedule-manifest units,
   enables boot-start, `daemon-reload`; deliberately does **not** start anything — starting is the
   gated migration):
   ```
   bash background/install_schedule.sh
   ```
3. **Restart each daemon to run current HEAD** (the gated migration — one at a time, verify between):
   ```
   systemctl --user restart <session>.service     # e.g. worker-seat-manager, supervisor, deadmans-switch, sim-runner, …
   ```
   Each restart re-runs `ExecStartPre` (stamps the boot SHA) and re-imports at HEAD. Do the
   autonomy layer (worker-seat-manager → supervisor → deadmans-switch) last and with care — the
   worker-seat restart is what brings the console-sanctity marker live.

## Verification — the L3 acceptance gate
Deploy is complete only when all of these are clean:
- **No boot-SHA drift** (every daemon booted from current HEAD):
  ```
  python3 -c 'from background.process_reconciler import evaluate_boot_sha_drift; print(evaluate_boot_sha_drift())'
  # expect {"head": "<HEAD>", "stale": []}
  ```
- **Process reconcile clean** (no `MISSING`, no `UNIT_FAILED`/`UNIT_CRASHLOOPING`; held/dark as declared):
  ```
  python3 -m background.process_reconciler
  python3 -m background.schedule_reconciler
  ```
- **Health check green**:
  ```
  python3 background/health_check.py
  ```
- **Console marker**: launch a console via `background/console.sh` and confirm it is sanctified
  (`python3 -c 'from background.console_sanctity import is_sanctified; ...'`) — a sanctioned console
  is exempt from the reaper independent of tmux.

When all pass, bump `OPS1_operational_layer_rebuild` L2 → L3 (worker-built + director-deployed +
verified), and un-park it.

## Rollback (it is reversible)
Nothing here is a one-way door. To revert: `git revert <deploy-range>` (or check out the prior HEAD),
then re-run steps 1–3. Because the units are *generated from the committed manifest*, revert +
reinstall + restart deterministically restores the prior running state. The `.stack_disabled` flag
(`docs/observability/.stack_disabled`) is the durable "everything down" escape hatch if a restart
misbehaves.

## Why the director triggers this (not the loop)
Restarting the autonomy layer (supervisor / deadman / worker-seat) is a lifecycle action on the
running stack, and the console-marker was explicitly held pending review — so the go-live is the
director's call, in a watched window, per the mandate. The mechanisms are all built and tested; this
runbook is the last mile.
