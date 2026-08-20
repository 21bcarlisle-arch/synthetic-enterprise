**Severity:** RECORDED · **Lane:** H_harness

# Proposal — the shared tree must stay committable at all times

> **This is a PROPOSAL for the director's review, not a build.** He asked for it explicitly and
> asked that it not be built tonight. Nothing here is implemented.

---

## The class, measured

On 2026-08-19, uncommitted work sitting in the shared working tree wedged **every lane's
commits and the publisher** — not once but repeatedly. Each instance was a different lane, each
was doing correct work, and none of them knew they had stopped everyone else.

| # | Whose work | What it did | What it blocked |
|---|---|---|---|
| 1 | EP6 pass 12 | three `simulation/` files, wall crossing in flight | the census gate refused every commit |
| 2 | KNIFE3 step 39 | `growth_desk.py` removing `counted_in_guard` while committed callers still passed it | **19 errors** in one gate run; four simulation suites red |
| 3 | seam-door-call-conformance | two untracked files, module with no wired caller | the orphan ratchet refused every commit |

Alongside these, three *committed* drifts of one shape stopped publishing: the map's
`simplifications_count` disagreeing with the store (EP1 8≠9, EP6 8≠9, EP1 11≠12).

**The cost, measured rather than estimated:** publishing did not land between 00:43Z and 12:20Z,
and again between 19:17Z and past midnight. A full day of finished site work sat uncommitted.
Four separate gate runs of 25–35 minutes each were spent on refusals that had nothing to do with
what was being committed.

## Why the existing mechanisms did not catch it

The gate runs its tests in the **working tree** while measuring its trees from the **index**.
That is deliberate and mostly right — but it means any lane's uncommitted edit is inside the
blast radius of every other lane's commit, and the refusal message names the *committer*, not
the cause. I misattributed the cause twice in one evening for exactly that reason: I reverted
`simulation/` and called the result "clean HEAD", when a third lane's uncommitted `company/`
file was still in it.

The tree also has no notion of **whose** uncommitted work is whose. `git status` shows a flat
list; nothing says "these seven files belong to three lanes, none of them yours".

## The proposal

**1. All lane work happens in an isolated git worktree.** One per lane, created at draw time,
removed at land time. The shared tree is then only ever touched by a landing, which is atomic
and gated. This is already how `surgical_land` and the publish gate think; it is not how the
lanes work.

**2. The shared tree stays committable at all times, as an invariant with a name.** "Is the
shared tree clean?" becomes a thing the supervisor can ask and answer before drawing, rather
than something discovered 30 minutes into someone else's gate run.

**3. Loose uncommitted shared-tree work is salvaged automatically, not tolerated.** Exactly the
operation performed by hand three times tonight: stash to a named `salvage/<lane>-<date>` branch,
byte-for-byte, verified against a raw copy, and reported. **A car park, not a demotion** — the
work is preserved and resumes in its own worktree. Tonight's three:
`salvage/ep6-wall-protocol-typing-20260819`, `salvage/knife3-growth-desk-20260819`,
`salvage/seam-door-call-conformance-20260819`.

**4. Derive `simplifications_count` instead of storing it.** It is a hand-maintained copy of a
number the store already computes; it can only ever drift, and each drift stops publishing for
everyone. Either derive it at read time or have whatever appends a record update the map in the
same breath.

## What I would want the director to weigh

- **Worktrees cost disk and setup time** (~200–500ms each, plus a checkout). At the current draw
  rate that is cheap; at high fan-out it may not be.
- **Automatic salvage moves someone's work without asking.** Tonight that was right because the
  alternative was a stopped line, and nothing was lost. As a standing rule it needs a bound —
  probably "only when the tree is refusing commits", not "whenever anything is uncommitted".
- **It does not fix the pollution class.** Two of tonight's red tests pass individually and fail
  in a batch; isolated worktrees would not have changed that.

## What is NOT proposed

No new gate, no new control, and no change to any wall control. The director's standing
instruction is that nothing gets built until the site publishes and keeps publishing; this
document exists to be read tomorrow, not acted on tonight.
