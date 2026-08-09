# [WORKER-FINDING] The ALARM TEETH cure was committed but never deployed, and the one control built to catch that excludes the two daemons that broke (2026-08-09)

**Found during:** the director's second publish-wedge episode (~10h, 02:58→12:58 UTC, 32 markers).
**Why this is filed as the answer to "why did the alarm not preempt the draw":** because the alarm
*could not* carry the severity, and the detector that would have said so is blind by construction to
exactly the daemons involved. Both are mechanism defects, not attention defects.

## The one-sentence cause

`fa9a73c72` ("UNWEDGE + ALARM TEETH ... the 7h episode's cure was built and left uncommitted",
2026-08-08 **23:44 UTC**) committed both draws of the cure. Every daemon that would execute it had
already been running since **13:50 UTC** (supervisor, staging-watcher, dispatcher) and **18:09 UTC**
(sim-runner, background-worker) that same day. **Committed ≠ running (R2).** For the whole ten hours
the machine was executing the pre-cure code, so it alarmed with the pre-cure alarm.

## Observed, with evidence

**1. The alarm that fired is byte-for-byte the PRE-cure template.**

On-disk (post-cure) `_fire_publish_gate_alert` builds:

```
"...Latest cause: {} (rc={}, git={}). {} Markers pending: {}."      # + _episode_phrase(...)
```

`fa9a73c72~1` (pre-cure) builds:

```
"...Latest cause: {} (rc={}, git={})."                              # ends here
```

What actually went out at 10:44:50 and 11:50:46 UTC (`synthetic-enterprise-ops/ntfy-mirror.md`):

```
... piling up unpublished. Latest cause: test failure or processing error
(rc>0 -- a real regression is possible) (rc=1, git=dfefd0a14). How: Check ...
```

No episode phrase, no `Markers pending:`. The running process is on `fa9a73c72~1`.

**2. The episode-memory fields are absent from the live state file.**
`docs/observability/.publish_gate_state.json` right now carries only
`{alerted_at, failures[4], wedge_since}` — no `episode_failures`, no `cited_findings`. On-disk code
writes all of them (`process_run_complete.py:1908-1909`). A pre-cure writer cannot write fields it
does not know about.

**3. `wedge_since` reads 11:41:43 UTC** for an episode that began at 02:58 UTC, with 4 failures
recorded for one that has failed ~40 times. The alarm therefore truthfully described a fresh
14-minute wedge — *the exact disease Draw 2(a) was built to cure*, still occurring because the cure
is not running. (The mid-episode reset itself is already filed separately:
`WORKER_FINDING_EPISODE_MEMORY_WIPED_MID_EPISODE_2026-08-09.md`.)

**4. The ALARM→DIAL wiring does not exist in the running supervisor.**
`grep -c "ALARM->DIAL"`: on-disk `background/supervisor.py` = 1; `fa9a73c72~1` = 0. The block that
lifts a cited finding to RUNG 1 priority zero landed in the same commit. So nothing could raise the
cure's draw priority — and with `cited_findings` never written (2), it would have had an empty list
to raise even if it had been running.

**5. The boot-SHA drift detector is correct, its data is correct, and it excludes both culprits.**
The stamps are right:

| session | boot SHA | HEAD |
|---|---|---|
| sim-runner, background-worker | `de2c3d7d8` | `83c2bce93` |
| supervisor, staging-watcher, dispatcher, … | `cb017fd8a` | `83c2bce93` |

Run in the daemons' own environment, `evaluate_boot_sha_drift()` returns:

```json
{"head": "83c2bce93…",
 "stale": ["deadmans-switch","ntfy-responder","staging-watcher","supervisor","worker-seat-manager"]}
```

**`sim-runner` and `background-worker` are not in that list** — the two daemons whose stale code
caused both faults. The population filter is
`process_reconciler._systemd_owned_sessions()`:

```python
owner == "systemd" and e.get("launched_by", "tmux") == "systemd"
```

Both have `owner: systemd` but no `launched_by`, so they default to `tmux` and are filtered out —
while in reality they are user-scope systemd units (`/proc/<pid>/cgroup` →
`app.slice/sim-runner.service`), `systemctl --user is-active` → `active`, and their unit's
`ExecStartPre` is what wrote the stamps in the table above. **The detector excludes them because the
manifest says they are not systemd-launched, and the manifest is wrong.**

**6. The same drift makes seven daemons double-launchable — and this exact defect was closed at the
INSTANCE twice already (R10 breach).**
`startlist()` — start_worker.sh's tmux launch set — still contained `sim-runner`,
`background-worker`, `dispatcher`, `discovery-daemon`, `sanity-daemon`, `naive-organ`,
`token-proxy`; all seven are simultaneously `active` **and** `enabled` under user systemd. The
manifest's own rule is "never two launchers", and its cutover contract says each cutover "flips this
field + its state in ONE atomic change, so the manifest never lies about what is running or how".

The decisive evidence that this is a class, not an instance, is written in the manifest itself. Two
rows already carry the fix, each with its own incident:

* `staging-watcher`: *"CUTOVER COMPLETED 2026-07-29 … the unit was installed+enabled+ACTIVE while
  this flip was never made, so BOTH launchers ran it (tmux 419018 + systemd 3081438) and one
  staged-file doorbell fired twice."*
* `ntfy-responder`: *"Half-done cutover … left TWO launchers — systemd PID 266098 + tmux PID 419021
  — so ONE director NTFY became TWO queued instructions."*

On 2026-07-29 the defect was diagnosed precisely, and **two rows were patched while seven identical
rows were left standing** — including the two daemons that broke today. R10 forbids exactly this:
*"An absurdity-class defect may NOT be closed with an instance fix."* The second-order cost is the
one that mattered here: an un-flipped row is not merely double-launchable, it is **invisible to
boot-SHA drift**, so the 2026-07-29 patch silently decided which daemons the staleness detector
would be allowed to watch.

## Inferred, not asserted (R9)

* **That a correct drift flag would have shortened the episode.** The five sessions it *did* flag
  have presumably been flagged for hours; I have not established where that line goes or whether
  anything reads it. `health_check` appends `"✗ deployment drift: daemon(s) on stale code"` to
  `problem_lines` — a report, not a draw. Whether a report can preempt a draw is the open half of
  this finding, and it is the same shape as Draw 2(b): a signal that addresses a reader instead of
  moving the dial.
* **Which commit installed the units without flipping the manifest.** Not bisected.

## What closing it looks like

1. **Truth-telling first (done in this pass):** flip `launched_by: systemd` for the seven daemons
   that are demonstrably systemd-active+enabled. This is not a design change — it makes the manifest
   describe the observed world, and it simultaneously (a) removes the double-launcher and (b) puts
   sim-runner and background-worker into the drift detector's population.
2. **R15 — the mutation the control must fail on is exactly this one:** a daemon that is
   `systemctl --user is-active` *and* carries a boot SHA ≠ HEAD must be reported stale **regardless
   of what `launched_by` claims**. Today the control passes with both culprits stale, so it cannot
   fail on its own named defect. The population should be derived from *observed* systemd activity,
   with the manifest as the cross-check that alarms on disagreement — not as the filter that silently
   shrinks the population.
3. **R10 — close at the class:** "a control whose population is a declaration rather than an
   observation" is the class. The declaration can drift; the observation cannot. Audit the other
   reconciler checks for the same shape.
4. **The deployment step itself.** `boot_sha` is explicitly REPORT-ONLY ("the deploy step —
   systemctl restart — is separate, G-D2"). Nothing closes the loop from "stale detected" to
   "restarted". Ten hours is the cost of that gap.

## The sim-runner fault is the same disease, one layer down

The `--save-json` failure the director reported is not a separate story. KNIFE pass 1 (today) moved
the RUN entry point out of `saas.reporting.annual_report` (now render-only: `--from-json` /
`--output`) into `tools.run_annual_report` (which does take `--save-json`). The **callee** half of
that refactor was committed. The **caller** half — `background/sim_runner.py` switching its argv to
`tools.run_annual_report` — is sitting in the working tree **uncommitted** at the time of writing:

```
$ git diff background/sim_runner.py
-                sys.executable, "-m", "saas.reporting.annual_report",
+                sys.executable, "-m", "tools.run_annual_report",
```

So HEAD itself is broken — a restart from a clean checkout would fail exactly the same way — and the
running daemon, booted 2026-08-08 18:09 UTC, was still issuing the pre-KNIFE argv against a callee
that had changed underneath it. That is the caller/callee disagreement, and it is the **third**
instance today of the same pattern: *the fix existed and the world did not have it.*

## The uncomfortable symmetry

The cure for the 7-hour episode was *built* and left uncommitted; that was caught and committed at
23:44 UTC. Twelve hours later the same cure was *committed* and left undeployed. Both times the work
existed and the world did not have it. R2 has been prose in CLAUDE.md throughout
("a code fix is deployed only once the running process has been restarted with it") — and
MAKE_IT_STICK already predicts this outcome for prose: *"every rule that DECAYED was an exhortation;
every rule that HELD was a MECHANISM."* The mechanism for R2 exists (`boot_sha`), which is why this
finding is a filter bug and not a design gap.

## Related

* `DIRECTOR_PRIORITY_UNWEDGE_AND_ALARM_TEETH_2026-08-08.md` — the cure this failed to deploy.
* `WORKER_FINDING_EPISODE_MEMORY_WIPED_MID_EPISODE_2026-08-09.md` — same alarm, adjacent cause.
* `ADVISOR_FINDINGS_REGISTER_ERROR_CHANNELS_ARE_INERT_2026-08-09.md` — same shape, different organ.

— Worker finding, 2026-08-09, during the second publish-wedge episode.
