# PRE-REGISTRATION — of the daemons the drift detector calls STALE, how many are actually UNSTAMPED-THIS-BOOT?

**Written 2026-09-24, BEFORE the measurement.** Claim id:
`a-landed-change-inside-a-running-daemon-is-inert-until-restart-and-nothing-measures-the-gap`.

## What is already established (measured, not predicted)

These were measured before this file was written and are not part of the prediction:

1. `background/boot_sha.py` has **no `__main__` block**. Every generated systemd unit declares
   `ExecStartPre=-/usr/bin/python3 -m background.boot_sha <session>`
   (`background/generate_units.py:53`), for all 10 systemd daemons, in both the committed units and
   the installed copies under `~/.config/systemd/user/`.
2. Running that exact declared command on the shared tree **exits 0 and writes nothing**.
   `docs/observability/.daemon_boot/staging-watcher.json` kept its mtime of 2026-09-17 10:27:42.
3. The `__main__` block was deleted by **3ecf355d8** (2026-09-04), an ancestor of `origin/main`,
   whose subject is about a *different* boot_sha defect. `boot_sha.stamp()` now has **zero
   production callers** — the only callers are tests, all with `BOOT_DIR` monkeypatched to tmp.
4. systemd started `staging-watcher.service` at 2026-09-24 03:30:22 BST (journal + `NRestarts=0` +
   `ExecMainStartTimestamp`); its stamp still reads `ts=2026-09-17T09:27:42Z`. A confirmed systemd
   start did not move the stamp.
5. `evaluate_boot_sha_drift()` on the live box reports **9 of 12** daemons `stale`:
   background-worker, deadmans-switch, dispatcher, naive-organ, ntfy-responder, sanity-daemon,
   sim-runner, staging-watcher, supervisor.

So the detector is in the **ALWAYS-RED** state that `55899dc99` (2026-08-09) was written to
abolish — "a detector for that failure mode that is always red will be ignored exactly as reliably
as one that is blind" — and that is why the 2h48m window in which `staging_watcher` ran without
`reask()` produced no observable change: the session was already, and permanently, `stale`.

## The open question

`loaded_code_drift` has three fail-safe rules (`unstamped`, `closure-unknown`, `sha-unresolved`).
None of them covers the live failure: **the stamp exists but was written at a PREVIOUS boot**, so it
describes bytes this process never loaded. That reads as a valid stamp and yields a `stale` verdict
indistinguishable from honest staleness.

Adding a fourth rule — *stamp timestamp predates this process's start time* → `stamp-predates-process`
— splits today's `stale` set in two.

## THE PREDICTION

Of the **9** sessions currently reported `stale`, I predict **9 of 9** flip to
`stamp-predates-process`, and **0** remain honestly `stale`.

Reasoning: no route has written a stamp since 2026-09-18 at the latest, and a daemon that has
restarted since its stamp cannot have a stamp describing its current process.

**The refutation that matters:** if fewer than 9 flip, then some daemons have *not* restarted since
2026-09-17/18, which would mean `deploy_restart.restart_plan` is not in fact restarting the sessions
it calls stale — a second, separate defect, and one this prediction would have hidden had I not
written the number down.

Secondary prediction: **0** sessions read `unstamped`, because every stamp file exists on disk —
the failure is a *stale* stamp, not an absent one, which is exactly why the existing `unstamped`
rule never fired.

## Open question this measurement does NOT settle

The stamps are dated 2026-09-17 and 2026-09-18 and carry the `dirty_blobs` field that `3ecf355d8`
introduced on 2026-09-04 — so they were written by the post-deletion code, which has no entrypoint
and no production caller. **I could not establish what wrote them.** Recorded here as an unresolved
thread rather than guessed at; it does not affect the repair, because the repair is that the
declared command must stamp and a control must prove it does.
