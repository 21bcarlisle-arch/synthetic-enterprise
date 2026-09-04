**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The publisher checks `behind_origin` once, at the end of a cycle the tree outruns five times over

**Found:** 2026-09-04, delivery seat, after fixing three separate causes of publish latency and
watching the site stay stale anyway. Measured from `git log origin/main` and the publisher's own
timings, not inferred.

---

## The measurement

```
origin commits in the last 6 hours : 73
median gap between them            : 3.4 min
one publish cycle (measured 12:48 -> 13:05, first cycle with no annotation hour) : ~17 min
```

**The tree falls behind roughly five times during a single publish cycle.** `BEHIND_ORIGIN` is
checked once, at commit time, after those seventeen minutes have already elapsed. By then origin has
moved and the check cannot pass except by luck.

Observed outcomes this afternoon, every one of them after a GREEN gate and a verified provenance:

```
13:05  Done, but THE PUBLISH DID NOT LAND (outcome: behind_origin)
14:27  Done, but THE PUBLISH DID NOT LAND (outcome: behind_origin)
```

Between those two I merged origin into the shared tree by hand — `b0ba91858`, 13:34. It was four
behind again by 14:19, forty-five minutes later. That was the third manual sync of the day and it
bought less than one cycle.

## Why this was invisible under the other three defects

The publish path had three independent latency defects today, each of which looked like the whole
answer while it was in front of me:

1. a throttle stamped only on success, so a step that always failed was never throttled (83435c633);
2. a sweep that ended on success and walked backwards on failure, paying a full cycle per marker
   (3d369242c);
3. an annotation that cannot finish at any budget the path is allowed to give it (013225ab6).

Fixing all three took the cycle from 77 minutes to 17 and made this one visible: the cycle is now
fast enough that the RACE is the binding constraint rather than the duration. A slower publisher
lost to its own cost; a faster one loses to the tree.

## What the repair is, and it already exists one module away

`tools/surgical_land.py` solves exactly this problem and says so in its own log line:

    [surgical-land] attempt 1/3 lost the race: HEAD 7d33c1986 -> ded79e205; re-gating the new base.

It re-gates on the new base and retries, bounded. The publisher has no such retry: it computes its
subject once, gates once, and then refuses if the world moved underneath it. **A one-shot check
against a moving target is not a guard, it is a coin toss with 3.4-minute odds.**

So the repair is to give the publisher the same lost-the-race retry, or to have it commit THROUGH
`surgical_land` rather than through its own `git commit`. Both touch the commit path, which is a
wall, so this needs its own design and its own controls — it is not a bounded-tick change.

## What is NOT the repair

**A daemon that fast-forwards the shared tree on a timer.** It was my first instinct and it is
wrong twice over. It cannot win either — at a 3.4-minute median it would be behind again before the
publisher reached its commit — and `surgical_land --merge` leaves the WORKTREE behind HEAD, which
arms a silent revert that has to be disarmed by hand. I hit that today: after the 13:34 merge,
`background/process_run_complete.py` read +1/−59 against HEAD, missing all 59 lines of another
lane's landed two-rooms repair. Automating a merge without automating that disarm would arm one
every twenty minutes.

## The class

`publish_gate_and_wedge`, and the shape worth naming: **a check whose subject changes faster than
the work it guards.** The check is correct, the refusal is honest, and the condition is unreachable
in the direction that lets work through. It is the sibling of the deadline control filed this
morning — *"a control keyed to a rising measurement eventually refuses the work it protects"* — with
the rising measurement replaced by a moving one.

## What would close this

A publish cycle that LOSES the race re-gates on the new base and lands, rather than reporting
`behind_origin` and dropping the work. Not written as a **Discharged:** field, deliberately: that
field is a claim that the repair has landed, and `finding_severity` grades it as one — my first
draft used it for an exit CONDITION and was correctly refused as a FALSE-DISCHARGE.
