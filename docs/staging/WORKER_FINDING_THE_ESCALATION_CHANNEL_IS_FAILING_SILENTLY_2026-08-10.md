# [WORKER-FINDING] The P0 escalation channel is over quota and drops silently — `send_ntfy` returns None and every caller ignores it

**Severity:** BLOCKING · **Lane:** H_harness

**Found:** 2026-08-10 ~20:10Z, while sending the RUNG-1 unwedge NTFY for this tick.
**Disposition:** FILED, NOT FIXED — the only real remedy is in the reserved classes.
**Rank:** proposed P1. This is the channel every other escalation rides on.

## OBSERVED, with evidence (R9)

The RUNG-1 cause NTFY for this tick **did not reach the director's phone.** `send_ntfy`
returned `None`. Probed directly, with the same command the function builds:

```
$ curl -s -d 'connectivity probe' https://ntfy.sh/se-XclDE4WvNUXlbg1bGGgVwiXrnjkfckLe
{"code":42908,"http":429,"error":"limit reached: daily message quota reached;
 increase your limits with a paid plan, see https://ntfy.sh","link":"..."}
```

`background.ntfy_utils.NTFY_AUTH_TOKEN` is **False** — the topic is unauthenticated, so the
quota is ntfy.sh's free per-source daily cap. It is a DAILY cap, so **every NTFY sent since it
was hit today has been dropped**, including any wedge alarm.

## THE DEFECT IS THE SILENCE, NOT THE QUOTA

`send_ntfy` parses the response for an `id` and returns `None` when there isn't one. Then:

```python
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        msg_id = json.loads(result.stdout).get("id")
    except json.JSONDecodeError:
        msg_id = None
    ...
    append_mirror_entry("out", message, topic=NTFY_TOPIC)      # runs regardless
    append_entry("ntfy", message, direction="out", ...)        # runs regardless
    return msg_id
```

An HTTP 429 body parses as valid JSON with no `id`, so it takes the `msg_id = None` path
without ever reaching the `except`. Three consequences:

1. **The failure is unlogged.** `result.stdout` contains an explicit, human-readable error and
   nothing reads it. There is no log line, no alarm, no transition (R5).
2. **The record says sent.** Both the ops-repo mirror and the director-input log append an
   `"out"` entry unconditionally, so the audit trail records a delivery that did not happen.
   Verified: this tick's message IS in `/home/rich/synthetic-enterprise-ops/ntfy-mirror.md`
   and IS pushed — the content survives, the delivery did not.
3. **Callers cannot tell.** Every call site in this repo ignores the return value, so a
   dropped escalation is indistinguishable from a delivered one at every level above.

This is `feedback_fail_silent_control_patterns` on the channel that CLAUDE.md makes a P0 wall:
"ESCALATION IS NTFY, NEVER THE WINDOW ... EVERY escalation → NTFY async". A wall whose only
transport fails open to silence is not a wall. It is also
`feedback_monitor_returning_only_rc_cannot_satisfy_r5`: a send that reports only "no id"
carries no diagnostic payload, when the payload was sitting in `result.stdout` the whole time.

## WHAT I DID NOT DO, AND WHY

I did not change the transport. Raising the quota means a paid ntfy plan — **spending real
money**, one of the four reserved classes — and adding a second channel or a credential is a
change to what this machine may do, which is director-console-only and which the agent may
never widen for itself. So this is filed rather than acted on.

## RECOMMENDATION

Two halves; I recommend both, and the first needs nobody.

1. **Make the failure loud (mine, no authority needed, not done in this bounded tick).**
   `send_ntfy` should read `result.returncode` and the response body, `log()` the error text
   verbatim on a non-delivery, and record a transition so a persistent-drop pages through
   whatever channel still works. The mirror/director-log append should record the *outcome*,
   not just the attempt — an `"out"` entry that means "we tried" is a record that lies. Sized
   S; the risk is that its own tests must not POST, which the existing `PYTEST_CURRENT_TEST`
   guard already handles.
2. **The transport itself is the director's** (reserved: real money). Options, with my
   recommendation: a paid ntfy.sh plan lifts the cap for ~£3/mo and changes nothing else;
   self-hosting ntfy on the box removes the cap for £0 but adds an operational service to
   maintain and needs an ingress path to the phone; an auth token on the existing topic does
   **not** help, because the cap is on the free tier, not on anonymity. **Recommended: the
   paid plan** — smallest change, no new failure mode, and it keeps the P0 channel a channel.
   Until then, cadence is the lever we do control: batching digests instead of per-transition
   sends would keep the daily volume under the cap.

## Until it is fixed

The content is not lost. Every message is mirrored, scrubbed, to
`/home/rich/synthetic-enterprise-ops/ntfy-mirror.md` in the private ops repo and pushed, so
today's undelivered escalations — including this tick's RUNG-1 cause — are readable there.
