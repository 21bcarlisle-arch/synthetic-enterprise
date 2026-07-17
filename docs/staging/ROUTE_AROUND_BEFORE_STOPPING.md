# FIND THE TWO-WAY DOOR BEFORE STOPPING — decompose walls, escalate only the irreducible core (P1, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high
(behavioural fix; folds with the door-classifier and Rule 0). Director: *"I want
it to crack on and find a two-way-door way to do things"* — and: it stops to talk
via the window too often, which is a silent stall when he isn't watching.

## The distinction (this is a DIFFERENT fix from door-defaults-to-act)
- ONE_WAY_DOOR_DEFAULTS_TO_ACT (422eaee9) fixed the classifier's bias on
  *reversible* actions — proceed unless provably a door.
- THIS fixes behaviour at a *genuine* wall. Today's case: two sessions on one
  tree (a real data-loss wall). The right instinct is NOT "stop and ask the
  human." It is: **find the reversible way to make progress anyway, do that
  autonomously, and escalate ONLY the irreducible core that truly needs the
  human.** The executor PROVED it can do this (it proposed folding via a
  throwaway worktree off origin — a two-way door around the wall) — it just
  didn't do it BY DEFAULT; it stopped and presented options first.

## The principle to encode
When blocked by a genuine one-way door, the executor must, IN THIS ORDER:
1. **Decompose the wall.** Separate the blocked action into (a) the parts that
   are reversible / have a safe two-way-door form, and (b) the irreducible core
   that genuinely requires the director (real money, security control, values,
   platform-admin, irrecoverable-loss-with-no-safe-alternative).
2. **Do all of (a) autonomously** via the reversible route — throwaway worktree,
   branch, draft, off-origin copy, idempotent operation, read-only diagnosis.
   Progress that can be made safely MUST be made, not parked.
3. **Escalate only (b)** — the smallest possible irreducible decision — and while
   waiting, KEEP WORKING other drawable atoms. A wall on one atom must never idle
   the whole loop.
4. **Prefer the two-way door by construction.** Before escalating, ask "is there
   a reversible way to achieve the same end?" Idempotent merges, off-origin folds,
   branch work, shadow runs are almost always available. Stopping to ask is the
   LAST resort, not the first.

## Why this matters (director's real point)
A stop-to-talk-via-the-window is, when the director isn't watching, **a silent
stall** — indistinguishable from a crash until the deadman fires. Every needless
window-stop is a potential multi-hour idle. The executor must treat "ask the
human in-window" as expensive and rare, and "route around and keep moving" as the
default — escalating a crisp, minimal decision asynchronously (NTFY/staging) while
continuing other work, never halting the whole fan-out to wait.

## What must NOT change
Genuine irreducible one-way doors still stop and still escalate — but they
escalate the MINIMAL core, asynchronously, while other work continues. The walls
are unchanged; what changes is: (1) decompose before escalating, (2) do the safe
part autonomously, (3) never idle the loop waiting, (4) escalate async not
via a blocking window-stop.

## Relationship to the map
Folds with Rule 0 (default state is working), door-defaults-to-act (reversible
proceeds), and per-atom streaming (a blocked atom blocks only itself). Together:
the loop keeps flowing, reversible work proceeds, walls are decomposed to their
minimal core, and only that core waits — asynchronously.

## DoD
Executor blocked-path behaviour changed to decompose-and-route-around:
safe/reversible sub-actions proceed autonomously (throwaway worktree, branch,
off-origin, idempotent, read-only); only the irreducible core escalates, and it
escalates ASYNC (NTFY/staging) while the loop keeps drawing other atoms; a
blocking in-window stop-to-ask becomes the rare last resort. Check: given a wall
with a reversible workaround (e.g. fold via throwaway worktree), the executor
takes the workaround autonomously and does NOT stop to ask.