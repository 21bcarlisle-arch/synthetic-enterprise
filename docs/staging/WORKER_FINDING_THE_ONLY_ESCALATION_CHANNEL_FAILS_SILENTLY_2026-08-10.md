# [WORKER-FINDING] The only escalation channel fails SILENTLY — a rate-limited NTFY returns None and nothing anywhere says the director was not told (2026-08-10)

**Found:** sending a watch update at 22:13Z. `send_ntfy` returned `None` where earlier sends that
evening returned real ids (`TFc8F7njXCgA`, `4YyNCElIn9WN`). I checked instead of assuming.

**Severity:** ESCALATION_IS_NTFY_NEVER_WINDOW is a **P0 wall** — the executor may never ask in the
pane, so NTFY is the *only* path from this machine to the director. That path can be down while
every caller believes it is up.

## Observed, with evidence

```
$ curl -s -o /dev/null -w '%{http_code}' -d 'probe' https://ntfy.sh/<topic>
429
```

`ntfy.sh` is rate-limiting the topic. Two director-facing messages did not arrive: the 22:13Z watch
update (the breathing status) and a follow-up probe. Neither raised anything anywhere.

The mechanism, `background/ntfy_utils.py::send_ntfy`:

```python
    msg_id = json.loads(result.stdout).get("id")
except json.JSONDecodeError:
    msg_id = None
...
if msg_id:
    record_sent_id(msg_id)
```

A 429 response body is not JSON carrying an `id`, so the parse raises, `msg_id` becomes `None`, and
the function **returns None with no stderr, no log line and no alarm**. The docstring is honest —
"the id (or None if the request or id-parsing failed)" — but it collapses two very different
outcomes into one value, and the failure is the quiet one.

## Why this is the fail-silent pattern by this project's own doctrine

R15 names it exactly: *an unavailable check is a FAILED check*. Here an unavailable **channel** is a
failed notification, and the code treats it as an ordinary return. Worse than a control that cannot
fail — this is a control that fails and reports nothing, on the one path the P0 rule says must
always work. Compare `feedback_fail_silent_control_patterns` and
`feedback_monitor_returning_only_rc_cannot_satisfy_r5`.

Most call sites in this repo do `send_ntfy(msg)` and discard the return, so the honest statement
after any of them is not "the director was told" but "a POST was attempted". Several of today's
NTFY-citing completion claims rest on that assumption.

## Contributing cause (stated, not blamed)

`.sent_ntfy_ids.json` holds 500 entries and the token log records 157 lines today. Between the
autonomous daemons and a long interactive session, per-topic burst limits on the free tier are
reachable — so this will recur, and did not need anything to be broken.

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_ntfy_delivery_is_verified`** — three parts, smallest first:

1. **Say so.** `send_ntfy` distinguishes transport failure from id-parse failure, logs the HTTP
   status to `docs/observability/ntfy-responder-log.md`, and returns something a caller can test.
   A silent `None` on a 429 is the whole defect.
2. **Retry with backoff and a durable outbox.** A 429 is transient; the message is not. An
   undelivered director message must survive the process, not evaporate with it.
3. **Alarm on deafness.** If no NTFY has been *confirmed delivered* in N minutes while work is
   escalating, that is itself the alarm — surfaced through the daily self-note and the deadman,
   which do not depend on the failing channel.

R15 both ways: mutation — force a 429 and the caller must observe a failure (test reds if it
returns a bare `None`); and a healthy send must stay quiet.

**Recommendation:** part 1 at P1 — it is a few lines and converts a silent P0-channel failure into a
visible one, which is the whole difference between "the director was not told" and "nobody knew the
director was not told". Parts 2–3 at normal priority behind the drain. Until part 1 lands, treat
every "NTFY sent" claim as "POST attempted" unless the returned id was checked.

---

## RECURRENCE — measured ~23:45Z the same evening, and it is still down

The census tick (`WORKER_REPORT_THE_STACK_WAS_ONE_DEEP_2026-08-10`) tried to send its transition
NTFY and **checked the return value because of this finding**. Two sends, ~90 seconds apart:

```
send_ntfy(...)  ->  None        (first attempt, ~23:44Z)
send_ntfy(...)  ->  None        (retry,          ~23:46Z)
```

The channel has therefore been down for **~95 minutes** (22:13Z → 23:46Z), across at least four
director-facing messages. Two things this adds to the original finding:

> **CORRECTION (22:36Z, original author of this finding).** The ~95 minutes is wrong and the
> substance is not. Those readings are **BST labelled `Z`**: `date -u` on this box returned
> `2026-08-10T22:34:16Z` while this section was already citing 23:45–23:46Z, i.e. timestamps
> ~70 minutes in the future. 23:46 BST = 22:46 UTC, so the measured outage is **~21–33 minutes**
> (first verified 429 at 22:13Z), not 95. Left in place rather than overwritten, per R9: the
> recurrence is real, the sends did fail, the two diagnostic points below are correct and valuable
> — only the duration was inflated, and by roughly 3x.
>
> This matters beyond pedantry for two reasons. It is R14's own rule (no figure without its clock)
> applied to an *elapsed* rather than a financial figure, and the inflated number was being used as
> the escalation rationale — "it has now silently eaten every escalation for an hour and a half"
> promotes this to the next draw on a strength the evidence does not support. **The promotion still
> stands on the corrected number**, because a P0 channel failing silently for twenty minutes is
> already unciteable; it just should not be argued from a figure that a clock check refutes.
> Filed as its own class: `WORKER_FINDING_BST_LABELLED_AS_Z_2026-08-10.md`.

**1. It is not transport, and the obvious diagnostic says the opposite.** `curl -I https://ntfy.sh/`
returns **200** — the host is up and reachable from this box. Only the *topic* is limited. So the
first check anyone reaches for ("is ntfy up?") **exonerates the failing channel**, which is the same
shape as `feedback_named_blocking_test_passes_when_you_run_it`. A future part-1 implementation must
report the status of the **POST to the topic**, never a reachability probe of the host.

**2. `HEAD` on the topic URL is not a probe either** — it returns **404** whether the topic is
healthy or limited, because ntfy publishes by POST. There is no way to test this channel without
sending on it, which is precisely why part 2's durable outbox matters more than it first looked: you
cannot ask "am I deaf?" cheaply, so the only honest design is to make every real send observable.

**Consequence for tonight's record, stated plainly:** the census batch is landed and pushed
(`origin/main` @ `474467179`, fetch-verified) but **the director has not been told by NTFY**. The
receipt on origin is the only channel that worked. Nothing was retried a third time — a third
identical POST into a rate limit is not evidence-gathering, it is noise against the limit that is
already the cause.

This recurrence promotes part 1 from "P1 recommendation" to **the next harness draw**: the defect is
no longer hypothetical-under-load, it has now silently eaten every escalation from this machine for
an hour and a half, and the only reason that is known is that two ticks in a row happened to check a
return value they were not obliged to check.
