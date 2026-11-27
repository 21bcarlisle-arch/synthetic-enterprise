# ADVISOR QUESTION — would batch-then-bisect landing cut time spent in the commit gate?

Staged by the advisor on the director's behalf, 2026-10-15. **Low priority —
rank it yourself.** A question, not an instruction to build.

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

## Where it came from

A practitioner post on running several coding agents in parallel through git
branches and a merge queue. Most of it describes problems this project has
already met and solved more thoroughly (gates that read the whole tree, the
landing tool that gates the tree a commit would create, scoped commits, serial
by default). One idea in it is not present here.

## The idea

A merge queue does not gate each change on its own. It lets several waiting
changes queue, gates the **combined** tree once, and only on failure splits
the batch and re-gates the halves until the culprit is found. When most
changes pass, many gate runs become one.

## What the advisor checked

At `9d03e103`: the landing path (`tools/surgical_land.py`,
`tools/pre_commit_test_gate.py`, `background/delivery_lane.py`) has no
batch-then-bisect behaviour. "Batch" there refers to batching notifications
and to a test selection; "bisect" appears only in unrelated places. CLAUDE.md
records that a commit takes more than ten minutes.

## The question

Would it pay here? Answer from your own numbers, not from the idea:

- how often more than one change is actually waiting to land at once
- how often the gate fails, because every failed batch costs extra gate runs
  to find the bad change, and a high failure rate makes batching a loss

If the numbers say it would not pay, say so in one line and close this.
That is a complete and useful answer.

## Decided, and open

**Decided:** worth a look, at whatever rank it earns.
**Open (yours):** whether it pays, and if so, the mechanism. Nothing about
the design is specified here on purpose.

## Reserved

- No weakening of what the gate checks. Batching changes when the gate runs,
  never what it refuses.
- A batch must never let a change land that would have been refused on its
  own.

## Risk

**Touches:** at most the landing path. **Blast radius:** if built, every
commit from every lane — so a defect here is project-wide. **Probable failure
mode:** a batch that passes while one member would have failed alone (an
interaction that happens to cancel), letting a bad change in. **Mitigation:**
the reserved rule above, proven by a test that a deliberately bad member is
always caught.

**Proportionality:** answering is reversible and narrow — just do it.
Building it touches the shared landing contract — implement with named
mitigations.

## Epoch arc

Epoch 1 — harness throughput, not company machinery.

## Answer (worker tick, 2026-11-27): it would not pay. Closed.

**Changes do queue.** Of 1,718 non-merge commits on `origin/main` from 2026-10-28 to 2026-11-27,
41% arrived under 600 s after the previous one, and the median gap is 773 s. That is about one gate
run, so the lock is close to saturated and a batch of 2 would often be available.

**The gate refuses too often for batching to win.** The only per-run gate record,
`docs/observability/commit_hook_duration.jsonl` (the auto-process commit, runs over 60 s,
2026-08-25 to 2026-11-27), has 103 of 247 runs refused (42%). Over the last 30 days it is 5 of 8.
A batch of k passes with probability (1-p)^k. For k=2, a failed batch costs about 3 runs (the
combined run, then each half). The expected cost is 0.34·1 + 0.66·3 ≈ 2.3 runs against 2 run
serially, and the break-even is p < 0.29. Larger batches break even at an even lower p.

**The reserved rule rules it out anyway.** A combined tree that passes does not show each member
would pass alone, because B can mask A's red. So "never land a change that would be refused on its
own" still needs a gate per member, and batching then saves nothing.

**GAP:** there is no per-commit refusal record for ordinary lane commits, because
`surgical_land` and the tree lock log nothing. The 42% comes from the one chain that is logged. It
is a proxy, not the rate for every lane. Even so, the per-member argument above does not depend on
it.
