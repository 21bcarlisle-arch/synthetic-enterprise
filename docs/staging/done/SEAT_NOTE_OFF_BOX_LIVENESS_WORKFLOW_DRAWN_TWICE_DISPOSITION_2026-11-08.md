**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted`

# `off-box-liveness-workflow` was drawn after the interactive seat had already built it (2026-11-08)

**Disposition.** The seat executor drew `off-box-liveness-workflow` at 14:20Z. The interactive session had
already built it: ops repo `2b628fed8` (14:09Z, on ops origin), which holds the hourly workflow, its decider and
6 tests. The `NTFY_TOPIC` Actions secret was set at 14:09:57Z. The executor built nothing and released the id
(`delivery_lane --release`).

**The record on main has not landed yet.** The interactive session's `surgical_land` from `/tmp/wt_offbox`
(started 14:14Z) exited at about 14:33Z without a commit. Its base, `6b70382ded`, predates `d087da7204`, which
had already moved the 8 Nov ruling to `advisor/done/`, so it has to re-gate. Its message carries the stop causes
**as that session reported them; the executor has not verified them**:
- 5-7 Nov: the host stopped the WSL VM at 03:31:52Z while Windows stayed up. Who stopped it, we cannot tell.
- 3-4 Nov: an expired OAuth session. The box was up and landing nothing, so this was not a stop.

That landing also carries the early-publish change (`publish_freshness.EARLY_PUBLISH_FROM`). If it has not
landed by the next orientation, the orienting seat takes it over from `/tmp/wt_offbox`'s diff.

**What the executor checked rather than trusted (R1).**
- Ops repo run 42488445238 (dispatched, `threshold_hours=0.01`, dry): `verdict: dead`, message "Skynet looks
  DOWN ... Sent once, from GitHub."
- Run 42488455849 (dispatched, default threshold, dry): `verdict: alive`, ops heartbeat 0.1h old.
- `pytest tests/` in the ops clone: 6 passed. They include a reachability test covering all three verdicts.

**What is not proven, stated rather than closed.**
1. **The send leg has never run.** Both runs were dry, so the step that sends the push with `curl` to
   `ntfy.sh/$NTFY_TOPIC` has not run against the live secret. To prove it, a non-dry forced run would have to
   reach the director's phone, and his 15 Oct ruling keeps that channel for a dead machine. So the first live
   send will be a real outage. If that step fails, the run goes red in the ops repo's Actions tab. The step
   also errors by name if the secret is empty. Recommendation: accept this. Do not send a test push.
2. **The once-per-outage memory can expire.** It is an `actions/cache` entry, and GitHub evicts entries
   unused for 7 days. An outage longer than a week would therefore push about once a week, not once in
   total. That is acceptable for a box that is still down.

**Reverse.** Delete this file. Nothing else changed.
