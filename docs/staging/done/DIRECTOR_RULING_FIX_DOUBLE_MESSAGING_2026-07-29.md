# [DIRECTOR-RULING] — Fix the double-messaging. Twice is once too many. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Fix this properly, not with a filter on the symptom.

## What the director sees

His single ntfy message *"Opus 5 doesn't exist on this plan…"* appears **twice** in the mirror — 17:32:19 and 17:32:27, eight seconds apart, identical text — and each was separately acked and queued as an instruction. The same doubling happened earlier today with a staged-instruction doorbell, and again with the ntfy app's own test notifications.

**This is worrying and it is not cosmetic.** One director message becoming two queued instructions means a single act could be executed twice. Most of the time that is harmless noise; occasionally it will not be.

## Diagnose the mechanism, do not filter the symptom

Find out **why**, with evidence, before adding any de-duplication:

- Is the ntfy app or the network delivering the message twice?
- Is the poller reading the same message on consecutive cycles because the read cursor advances only on success — or not at all?
- Are **two consumers** subscribed (responder and worker, or two instances of one daemon left running after a restart)?
- Is the retry path re-processing an already-handled message after a partial failure?

**A de-duplication filter added without knowing the cause hides a second daemon or a broken cursor rather than fixing it.** Say plainly which of these it is.

## Then make it correct by construction

Every inbound message gets a **stable identity** (its ntfy message id, or a hash of body plus timestamp) recorded on handling, and **processing is idempotent**: a message already handled is acknowledged and dropped, never re-queued, never re-executed. **At-most-once execution for anything that acts** — at-least-once delivery is fine, at-least-once *execution* is not.

R15 both ways: the same message delivered twice must execute once; two genuinely different messages with similar text must both execute.

## While you are in there

The ntfy app's own **test notifications were queued as instructions** and each triggered a model load. Inbound text carries no authority and is untrusted data. **Anything that is not plausibly a director instruction should be acknowledged and discarded without spawning a model** — a message costing a GPU load is a cheap way for noise, or anyone who learns the topic, to waste the day.

## Report

One line: the cause, the fix, and confirmation that a duplicate now executes once. **Do not ask permission** — this is reversible plumbing.

— Advisor bridge, carrying the director's instruction. 2026-07-29.

---

# OUTCOME — actioned 2026-07-29 (build-executor turn)

**One line:** Two responder daemons were running (a half-finished systemd cutover left both
systemd *and* start_worker.sh launching it); the fix removes the second launcher, makes a
second one impossible (singleton lock), makes execution at-most-once by claiming each ntfy
message id atomically, and makes the whole class alarm (`DOUBLE_LAUNCH`) — a duplicate now
executes once, verified live.

## The cause — named plainly, with evidence

Of the four hypotheses you listed, it is **the third: two consumers**. Evidence, all
`observed-with-evidence`:

- `ps` showed **two** `ntfy_responder.py` processes: PID 266098 (parent = systemd, 13:26) and
  PID 419021 (parent = `tmux new-session -s work`, 18:20).
- `docs/observability/ntfy-responder-log.md` shows the **same ntfy message id** acked twice:
  `AK0UhbkAV2Ko` at 17:37:31 and 17:37:42, staged as two different `from_rich_*.md`. A shared
  message **id** rules out double delivery by ntfy and rules out a retry path — it is one
  message read by two consumers.
- `background/.ntfy_responder_rate.json` held every event **twice, with identical timestamp and
  identical hash** — two processes registering the same arrival.
- **`staging-watcher` had the identical defect** (tmux PID 419018 + systemd PID 3081438), which
  is the doubled staged-instruction doorbell you also saw. Same cause, same day.

**Why it happened:** `background/process_manifest.yaml` declares `owner: systemd` for both, and
their `.service` units are installed, enabled and active — but neither entry ever got the
`launched_by: systemd` flip that removes it from `start_worker.sh`'s tmux launch set. The
reconciler's own contract says a cutover is ONE atomic change so there are never two launchers;
for these two it was done half-way.

**Why nothing caught it:** `reconcile()` computed `running = unit_active or tmux_present`. That
`or` answers "is it up?" and is blind to *how many* launchers are up — one and two read
identically as `OK`. Worse, `_live_unit_states` only queried units of *migrated* daemons and
`_live_tmux_running` only scanned *un-migrated* ones, so a half-migrated daemon was invisible to
both readers. An unread source cannot alarm.

**No de-duplication filter was added before knowing this.** The second daemon is gone, not hidden.

## The fix — correct by construction

1. **At-most-once execution.** Every inbound message is claimed by its **ntfy message id** via
   `O_CREAT|O_EXCL` (an atomic cross-process test-and-set) before any side effect. An
   already-claimed message is acked and dropped — never re-queued, never re-executed. Claiming
   happens *before* the flood guard, so a duplicate is not even counted as inbound rate.
   Fail-**closed**: if the claim ledger can't be written we cannot prove we won, so we don't execute.
2. **Keying on the id, not the body.** The pre-existing content-hash dedup would have swallowed a
   director deliberately sending the same text twice. Two different ids with identical text now
   both execute — that is your R15 "both ways", and it is a test.
3. **Singleton lock.** A second responder refuses to start (`flock`) and says why. Root cause
   removed, not filtered.
4. **The class alarms.** New `DOUBLE_LAUNCH` reconciler status fires whenever a daemon is live on
   both launchers; both live readers widened; manifest cutovers for ntfy-responder and
   staging-watcher completed.
5. **Message loss guarded.** De-duplicating delivery must never become dropping a distinct
   message: two genuinely different messages arriving in the same second previously collided on
   the `from_rich_<ts>.md` filename and one was silently overwritten. Now uniquified.

## While you were in there — the ntfy app's test notifications

Self-tests are now dropped at the very top of the inbound path, **before** the mirror, the input
log, the ruling ledger, the claim ledger and the status reply — so one costs nothing at all and
cannot spawn a model or emit a reply that feeds an echo loop. The match stays deliberately narrow
(`test notification from the ntfy`) so a real steer that merely mentions "test" still passes;
that guard has its own test.

## Verification

- **9 R15 mutations run, every one confirmed to fire** on its own named defect (5 on the
  responder, 4 on the reconciler).
- **Live, on the box:** starting a second responder now prints
  `NTFY responder ALREADY RUNNING (singleton lock held) -- this instance is exiting.` and the
  process count stays at 1.
- **Live reconcile after the fix:** `DOUBLE_LAUNCH: none`, `alarms: none` (it correctly reported
  all five before the PID-aware correction below).
- Suites: `test_ntfy_responder.py` 35 passed, `test_process_reconciler.py` 29 passed,
  `tests/background/` 1769 passed / 4 failed — the 4 are a **pre-existing, unrelated**
  wake-key test-isolation leak from `test_model_facing_secret_scrub.py` (it reloads `ntfy_utils`
  with the secret scrubbed); that file passes 24/24 alone and my changes do not touch it.
- Epistemic verifier: **PASS** (528 files).

## One honesty correction on my own fix

My first cut of the widened tmux reader used a `match in ps_out` substring scan over all of `ps`.
A systemd-launched daemon's own command line matches its own `match`, so `DOUBLE_LAUNCH`
false-positived on all five healthy daemons. **The test suite did not catch this** — the tests
inject `tmux_running` directly; the live check did. It is now PID-aware against the unit's
`MainPID`, with three regression tests pinning it. A control that fires on healthy input is worse
than none.

## Registered, not fixed (queued — one-at-a-time cutover is your 2026-07-17 ruling)

**Seven** daemons still have systemd units enabled at boot while remaining in start_worker.sh's
tmux launch set: `background-worker`, `dispatcher`, `discovery-daemon`, `sim-runner`,
`sanity-daemon`, `naive-organ`, `token-proxy`. They are single-launcher today only because those
units happen to be inactive — **each will double at the next boot**. The new `DOUBLE_LAUNCH`
alarm makes that loud rather than silent. Also registered: the wake-key test-isolation leak above.
