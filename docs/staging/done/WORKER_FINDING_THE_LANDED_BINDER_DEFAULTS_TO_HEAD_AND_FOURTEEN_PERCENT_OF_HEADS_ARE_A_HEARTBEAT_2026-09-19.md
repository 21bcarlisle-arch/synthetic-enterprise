**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The `--landed` binder defaults to HEAD, and 14% of HEADs are a pure heartbeat

BLOCKING because it writes a FALSE DONE into the delivery ledger, and a credited row is never
redrawn. Same class and same consequence as the defect repaired beside it today; different door.

**Filed, not half-fixed.** The drawn item scoped the repair to `_landed_unbound`, which is done and
proven. This is the sibling hole that repair exposed. It is written down rather than patched in the
same tick because the fix is a judgement about what `--landed` MEANS, not a missing clause.

## What was repaired today, for contrast

`_landed_unbound` credited a claim with any commit touching one of its named paths inside its
window. `851dffdbb`, an auto-process republish touching 52 files, intersected the six paths of
`the-orientation-brief-misreports-the-machine-it-describes` at exactly
`site/data/tick_heartbeat.json`, and closed it. `_window_hits` now refuses an intersection confined
to `process_run_complete.LIVENESS_SURFACE_FILES`, and the live row is re-opened.

## The hole that is still open

`record_landing` (`background/delivery_lane.py`) takes `commit: str = "HEAD"`. The `--landed`
handler passes `args.commit`, which is `None` unless the caller names one, so the ordinary
invocation every tick is instructed to run —

```
python3 -m background.delivery_lane --landed <focus-id>
```

— binds **whatever HEAD happens to be**, not what the caller landed. `_commit_facts` returns that
commit's paths, `bind_paths` takes them, and `_remember_landing` writes them as the claim's
landing. Nothing on that route asks whether the commit carried work.

## Why it is reachable rather than theoretical

Measured on the real record, 2026-09-19:

| Question | Measurement |
|---|---|
| Pure-liveness commits in the last 200 | **28 (14%)** |
| `_commit_facts("47d7dd49e")` | `['docs/observability/agent_status.json', 'site/data/tick_heartbeat.json']` — confined to the surface |
| `_commit_facts("9119539e2")` | same |
| Rows in the live ledger already credited by a liveness-only intersection | 1 of 400 (the one repaired today) |

The shape that fires it: a tick commits, its gate refuses or its landing is swept, the publisher
moves HEAD to a `chore(liveness)` republish in the meantime — it makes several an hour by
construction — and the tick then runs the `--landed` line its own brief told it to run
unconditionally. The claim is credited with a heartbeat, leaves the missed list, and is never
redrawn. The tick exits believing it bound its work.

The census found only the one instance, which bounds the damage so far. **It does not clear the
finding**: an empty instance list is never evidence a rule-class defect is safe to leave, and here
the list is not even empty.

## What the fix is NOT

Reusing today's clause verbatim — refuse the binding when the commit's paths are confined to the
liveness surface. That is probably right, but it is not obviously right, and the difference is what
makes this a filing rather than a patch:

- `_landed_unbound` is a machine INFERRING a landing from git, so refusing a doubtful commit costs
  nothing but a redraw. `--landed` is a caller ASSERTING one. A refusal there has to be *said* to
  the caller, loudly, and the handler already has that route (non-zero exit plus
  `refusal_reason`) — so the work is mostly in the refusal's sentence, which must explain that the
  caller's own commit is not what HEAD is, or the next tick simply re-runs it.
- The deeper question is whether `commit="HEAD"` is the right default at all. A binder whose
  subject is "whatever the tree moved to since you looked" is the fail-open one rung above this
  one, and a liveness clause would close today's instance of it while leaving the shape: any other
  lane's commit at HEAD is credited to this claim just as readily, and no liveness test sees that.

**Recommendation.** Fix the default before the clause: have `--landed` bind the caller's own commit
(the tick knows its sha) and treat `HEAD` as a fallback that says so. Then the liveness clause is a
belt on a route that is already right, rather than the only thing standing between the ledger and a
false done. That is a larger change than a bounded tick should make unannounced, which is why it is
here.

## What would prove this finding wrong

A route by which `--landed` cannot reach a heartbeat HEAD — an existing guard on `record_landing`
that compares the commit against the caller, or a caller that always passes `--commit`. Neither was
found: the refusals `record_landing` documents are an unclaimed id, an unreadable commit, a commit
touching no files, and a commit older than the first draw. A heartbeat republish inside the window
passes all four.
