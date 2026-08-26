# [WORKER-FINDING] An agent's hand-written timestamp read the LOCAL clock and labelled it `Z` — and the inflated elapsed became an escalation rationale (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Found:** reading a recurrence section appended to
`WORKER_FINDING_THE_ONLY_ESCALATION_CHANNEL_FAILS_SILENTLY_2026-08-10.md` by another lane's tick.
Corrected in place there; filed here as its own class.

**Scope, stated first because it bounds the alarm:** this is a **prose** defect, not a data one.
Every machine-written stamp checked is correct UTC. The class is agents narrating time by hand.

## Observed, with evidence

```
$ date -u   ->  2026-08-10T22:35:01Z
$ date      ->  2026-08-10T23:35:01+0100        # BST, UTC+1

the appended section cited:  "23:45Z", "23:46Z", "~95 minutes (22:13Z -> 23:46Z)"
```

Those readings are ~70 minutes **in the future** against `date -u`. They are the local BST clock
wearing a `Z`. Converted honestly, 23:46 BST = 22:46 UTC, so the measured outage was **~21–33
minutes** (first verified 429 at 22:13Z), not 95 — inflated roughly 3×.

**The generated artefacts are clean**, checked rather than assumed:

```
newest sim-runner-log stamp   [2026-08-10 22:24 UTC]     consistent with real UTC
publish_provenance written_at 2026-08-10T21:53:44Z       in the past, consistent
```

So nothing published to the site or the ledgers is wrong. The corruption entered where a model typed
a time instead of reading one.

## Why it is worth a finding rather than a fix-in-place

The number was **load-bearing**. It appeared as: *"it has now silently eaten every escalation from
this machine for an hour and a half"* — the argument for promoting that atom to the next harness
draw. An escalation rationale resting on a figure a single `date -u` refutes is the exact shape R9
exists to prevent (evidence before narrative), and R14's "no figure without its clock" applied to an
**elapsed** rather than a financial figure.

The promotion itself survives the correction — a P0 escalation channel failing silently for twenty
minutes is already unciteable, and 21 minutes makes the case. That is precisely why the inflation was
gratuitous: it bought nothing and cost the claim its credibility.

Related: `feedback_the_record_can_outrun_the_code`, and the whole clock-truth family (R14).

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_no_hand_written_timestamps`** — cheap and mechanical: a staging-doc lint that flags any
`\d{2}:\d{2}Z` or ISO-`Z` literal in a `docs/staging/**` document which is **in the future** against
`date -u` at commit time. A future `Z` stamp in a report is never right, so the check has no
judgement in it and cannot false-positive on a legitimate past reading. R15: mutation — plant a
future-stamped line and the lint must red; a correctly-stamped doc must stay quiet.

**Recommendation:** normal priority, and deliberately **not** urgent — no artefact is affected, and
the corrected finding already stands on its own evidence. Worth mechanising only because the
cheapest possible check (`is this timestamp in the future?`) catches the whole class, and because
agents on this project write director-facing elapsed figures constantly.
