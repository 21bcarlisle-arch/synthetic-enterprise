**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the Lane 0 done-test for "did the NTFY leave?" reads a FAILURE log, so it is unsatisfiable on every healthy send and satisfiable only while the channel is broken

Filed from executing the Lane 0 item `tell-the-director-the-three-cadences-that-were-set` on the
scheduled tick of 2026-09-26. **The work was done and the message landed** (id `hgcxzzZBvQ0v`); this
document is about the *verification the item prescribed*, not the work.

## What the item said, and what the code does

> Verify it left: `docs/observability/ntfy-delivery-log.md` must gain a `[DELIVERED]` line, and its
> last one before this is 2026-09-23T09:16Z.

That line cannot appear. `background/ntfy_utils.record_delivery_outcome` returns before writing any
log line when the send succeeded and the previous state was already delivered:

```python
# R5: a healthy send stays quiet unless it is the RECOVERY transition.
if delivered and not transition:
    return
```

The file says so in its own header — *"Every POST to the director topic **that did not land**,
verbatim"* — and both existing `[DELIVERED]` lines (2026-09-11, 2026-09-23) sit immediately after a
`[NOT DELIVERED]` line, which is what `transition` means. Measured here: the send returned a
server-assigned id, and the log's last entry is still `2026-09-23T09:16:43Z`, byte-identical to the
value the item itself quoted as the *before* reading.

| witness | before | after this send |
|---|---|---|
| `ntfy-delivery-log.md` last entry | 2026-09-23T09:16:43Z | 2026-09-23T09:16:43Z — **unmoved** |
| `send_ntfy` return | — | `hgcxzzZBvQ0v` (server-assigned) |
| `.ntfy_delivery_state.json` `last_checked` | 2026-09-23T09:16:43Z | **2026-09-26T16:38:45Z** |
| `.ntfy_delivery_state.json` `consecutive_failures` | 0 | 0 |
| `was_sent_by_us("hgcxzzZBvQ0v")` | — | `True` |

**The mechanism is not the defect.** Quiet-on-healthy is deliberate (R5, and the log exists to make
drops loud). The defect is a done-test whose satisfiability is *anti-correlated* with the health of
its subject: it can only go green in the window where delivery has just been failing.

## Why this is expensive, not merely wrong

A done-test that reads "not sent" on a successful send does not stall — it invites the retry. The
next invocation handed this criterion sees an unmoved log, concludes the POST evaporated, and sends
again. The failure mode of a false negative on this particular channel is **the director's phone
buzzing twice with the same message**, which is the exact class the pytest guard three functions up
was written to stop.

## Second strike of a named class

This is the second recorded instance of *a Lane 0 item naming an exit criterion its own prescribed
mechanism is structurally incapable of producing*. The first, two days ago:
`docs/staging/done/SEAT_FINDING_A_LANE_0_ITEM_PRESCRIBED_A_VERB_THAT_STRUCTURALLY_CANNOT_REACH_ITS_OWN_EXIT_CRITERION_2026-09-24.md`
(`--landed <historical-sha>` can never clear `lane_0_drawn_never_landed`, because the stamp is the
commit's own). Both items' instructions were correct and both their exit criteria were unreachable — so
the pattern is not carelessness in one draw, it is that **nobody runs the exit criterion against the
code before it is handed out**. `G4_unified_failure_register` (drawn in this same tick, lane
G_data_learning, level 0->3) is where a global per-class strike count belongs; this is the second
strike to put in it.

## The rule for the next draw

**An NTFY send is verified by the id `send_ntfy` returns and by
`docs/observability/.ntfy_delivery_state.json` (`last_checked` advancing, `delivered: true`,
`consecutive_failures: 0`) — never by a new line in `ntfy-delivery-log.md`.** All three of those
paths are gitignored, so "no commit" is a fact about the send, not a choice: there is nothing for
`delivery_lane --landed` to bind.

## Residual

Not fixed here, and deliberately: the repair is one sentence in whatever composes Lane 0 verification
prose, and finding *that* composer is a larger job than this finding. What is landed is the rule
above, in the staging root, where the next draw's reader will hit it.
