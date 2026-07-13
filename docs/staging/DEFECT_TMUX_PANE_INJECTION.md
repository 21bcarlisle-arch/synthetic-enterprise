# DEFECT: Repeated text injection into claude tmux pane

**Priority:** P2 — degrading director console usability now; likely also polluting agent context.
**Staged by:** advisor (director-reported defect, 2026-07-13)

## Symptom

300+ `[Pasted text #NNN]` entries accumulating in the Claude Code prompt while long-running turns are in flight. Arriving in bursts of ~4. Director observed live over ~1 hour.

## Evidence gathered so far

- Injection continued while `dispatcher.py` (PID 1491156) and `ntfy_responder.py` (PID 2293009) were SIGSTOPped — **both ruled out as sole cause**. NOTE: both may still be stopped — check `ps` for `T` state and `kill -CONT` if so.
- Scripts using tmux send-keys: `autonomous_runner.py`, `session_watchdog.py`, `staging_watcher.py`, `tmux_relay.py`. Of these, session_watchdog and staging_watcher were running throughout.
- `docs/staging/` root currently holds **13 `run_complete_*.md` files staged today at ~10-minute intervals** (07:28, then 15:26→17:26 continuously). sim_runner.py appears to be emitting a staging artefact per run; each staged file plausibly triggers a send-keys injection. This matches the observed cadence and is the prime suspect for the volume.

## Required

1. Diagnose which process(es) inject and why. Candidate mechanisms: staging_watcher firing per run_complete file; session_watchdog misreading long-running turns ("Levitating…", "Waiting for background agent") as stuck and poking repeatedly.
2. Fix the root cause, not the symptom (R3/R10 apply — if this is an absurdity-class defect, extend the guard class).
3. Apply R5 strictly: transition-only injection. A new run_complete is arguably a transition, but 13 identical-class notifications in 2 hours is noise — batch or digest them.
4. Decide whether sim_runner should be staging run_complete files to `docs/staging/` root at all, or to a lane that doesn't trigger pane injection.
5. Add source-attributable logging for every send-keys injection (timestamp, source script, payload hash) so future incidents are diagnosable in seconds, not an hour of director SIGSTOP forensics.
6. Clean up the run_complete backlog in staging root once processed.

## Report

NTFY findings and fix summary on completion (transition-only).
