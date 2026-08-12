# [WORKER-REPORT] The P0 escalation channel now says when it drops — one BLOCKING instance discharged from the controls-that-cannot-fail class

**Severity:** RECORDED · **Lane:** H_harness

**Drawn:** RUNG 1c, OPS12 clause 3 — `CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` is BLOCKING in
`H_harness`, and its "what is owed" list named nine instances. This tick repaired one of them, chosen
because it is the class member the other escalations ride on.

## What was wrong (both findings named the same defect)

`background/ntfy_utils.py::send_ntfy` parsed the response for an `id` and returned `None` when there
was not one. An HTTP 429 quota body — `{"code":42908,"http":429,"error":"limit reached: daily message
quota reached..."}` — is **valid JSON with no `id`**, so it never reached the `except`, and:

1. **Nothing was logged.** The human-readable error sat unread in `result.stdout`; curl's rc and the
   HTTP status were discarded before anyone could see them.
2. **The record said sent.** Both the ops-repo mirror and the director-input log appended an `out`
   entry unconditionally, so the audit trail asserted a delivery that did not happen.
3. **Callers could not tell.** Every call site discards the return, so a dropped escalation was
   indistinguishable from a delivered one at every level above.

ESCALATION IS NTFY, NEVER THE WINDOW is a P0 wall, so this is the only path from this machine to the
director — a wall whose only transport fails open to silence.

## What landed

`background/ntfy_utils.py`:

- **The status of the POST TO THE TOPIC** is captured (`curl -w '\n%{http_code}'`, split by
  `_split_trailing_status`, which tolerates a body with no suffix so older fakes are not mangled).
  The finding's own diagnostic warning is honoured: `curl -I https://ntfy.sh/` returns **200** while
  the topic is limited, and a HEAD on the topic 404s whether healthy or limited, so the obvious
  reachability probe EXONERATES the failing channel. This never becomes a host probe.
- **`record_delivery_outcome()`** writes the failure verbatim (curl rc, HTTP status, response body,
  stderr) to `docs/observability/ntfy-delivery-log.md`, and the outcome to
  `.ntfy_delivery_state.json`: `delivered` / `reason` / `since` / `since_epoch` / `consecutive_failures`.
- **`delivery_state()`** answers "am I deaf?" **without sending on the channel under test** — the
  finding established that this channel cannot be probed cheaply, so every real send is the only
  available observation.
- **Both audit trails now record `out-undelivered`** when the message did not land. An `out` entry
  for a message that never left the box is a record that lies.
- **R5 honoured:** a drop is logged every time (each one is a director message that did not arrive,
  not a repeated unchanged status); a healthy send is silent *except* on the recovery transition.

## R15, both ways — the control is proven to fire on its own named defect

Seven new tests in `tests/background/test_ntfy_utils.py`, fixtured on the **real** quota body from the
finding. Mutation: revert the failure branch to the original silent `None` and revert
`direction` to the unconditional `"out"` →

```
FAILED test_quota_drop_is_recorded_not_silent
FAILED test_undelivered_message_is_not_recorded_as_sent
FAILED test_consecutive_drops_accumulate_and_recovery_is_a_transition
FAILED test_curl_transport_failure_is_distinguished_from_a_quota_drop
4 failed, 27 passed
```

Restored → `33 passed`. The other direction is tested too (`test_a_healthy_send_stays_quiet`): a good
send writes no log line, so this is not a control that fires on everything.

**The isolation guard is deliberately not a blanket one.** `record_delivery_outcome` no-ops under
pytest only while either path is still the real file, so no test can pollute the live record, but a
test that redirects both exercises the real body. A bare `PYTEST_CURRENT_TEST` guard — the pattern
used by `ntfy_mirror` and `director_input_log` — would make this mechanism **unfalsifiable under its
own suite**, which is the exact R15 class it was written to fix.
`test_delivery_recording_is_a_no_op_until_a_test_isolates_it` pins that behaviour.

## The new control was itself caught by an existing one — and by this class's own open blocker

`tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned` went RED
on `.ntfy_delivery_state.json` the moment it existed: a new state file written on a failure path and
read by an alarm is exactly the self-clearing-alarm shape. The census working as designed, so the
disposition is `real`, not a plea:

- `since_epoch` (episode start) and `consecutive_failures` (episode length) are now guarded through
  `episode_monotonic.guard_episode`. An unearned reset is what pages a multi-hour silent-escalation
  outage as a fresh one — the class's own cardinal sin.
- **The close condition is a server-assigned message id**: the strongest evidence this channel can
  produce, read off the SERVER's response body and never off the state file it closes (R15
  anti-tautology).
- **`since_epoch` is numeric on purpose.** `guard_episode`'s water-marks are numeric-only and skip a
  string field *silently* — which is `WORKER_FINDING_THE_MONOTONIC_GUARD_IS_NUMERIC_ONLY`, an open
  BLOCKING member of this very class, and the one carrying its 25 recorded hours. A human-readable
  ISO `since` alone would have been a guard that cannot fire, i.e. this repair would have joined the
  class it was discharging. The readable `since` is kept alongside, unguarded and not load-bearing.
- Both directions tested: `test_an_open_deafness_episode_cannot_be_shortened` (a drop cannot move the
  start or lower the count) and `test_a_real_delivery_does_close_the_episode` (the guard can still
  clear, or the alarm could never stand down). `--check` on the census exits 0.

## What is NOT done, stated plainly

- **Part 2, the durable outbox.** An undelivered message is now *visible* but still *evaporates* with
  the process. `consecutive_failures` is the counter a retry/backoff design needs; nothing uses it.
- **Part 3, alarm on deafness.** No daemon reads `delivery_state()` yet, so sustained deafness is
  recorded but not surfaced. The deadman and the daily self-note are the two organs that do not
  depend on the failing channel — that is where it belongs.
- **The transport is RESERVED.** Lifting the quota means a paid ntfy.sh plan: **spending real
  money**, one of the four reserved classes. Recommendation to the director stands unchanged (paid
  plan, ~£3/mo, smallest change, no new failure mode). Until then cadence is the lever we control.
- **R2 — committed is not running.** Long-lived daemons that imported `ntfy_utils` before this commit
  keep the old function in memory; they pick the fix up on their next restart. Nothing here claims a
  live behaviour change in an already-running process.

## Class bookkeeping (derived, not hand-kept)

`WORKER_FINDING_THE_ONLY_ESCALATION_CHANNEL_FAILS_SILENTLY_2026-08-10.md` (archived) moves BLOCKING →
RECORDED with the discharge recorded in the document itself;
`WORKER_FINDING_THE_ESCALATION_CHANNEL_IS_FAILING_SILENTLY_2026-08-10.md` (live) moves BLOCKING →
LATENT, keeping the open parts visible in the register rather than closing them by archiving.
`python3 -m background.finding_classes --render` re-derives the class document from the filesystem:
**"what is owed" falls 9 → 8** and the class stays BLOCKING, correctly — eight members remain.
`--check` PASSES (0 failures) across all five classes.

---

Evidence: `background/ntfy_utils.py`, `tests/background/test_ntfy_utils.py` (33 passed; 4 red under
mutation), `docs/staging/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` (owed 9 → 8),
`python3 -m background.finding_classes --check` → PASS.
