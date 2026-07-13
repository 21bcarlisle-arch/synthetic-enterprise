# RETRO: why we missed worktrees for six weeks — five method findings (QUEUE)

**Staged:** 2026-07-13 by advisor, director-requested ("let's remember this
learning"). Disposition: QUEUE. **Record these in the casebook / method lane —
they are IP, not housekeeping.** Each is stated as a general law with the
specific evidence that produced it.

## Finding 1 — SEARCH THE FIELD WHEN YOU HIT A WALL (new standing rule)
The harness best-practice re-check currently fires at epoch boundaries and major
releases. That is far too slow for a field turning over monthly (the sources
that solved our problem are dated Feb-Jul 2026; the native
`isolation: worktree` subagent directive did not exist when this project
started).
**New trigger: any structural wall = an immediate check of published practice,
BEFORE theorising.** "We are stuck on X" is the strongest available signal that
someone has already published the answer to X. Applies to the agent AND the
advisor.

## Finding 2 — A REVIEW ONLY ANSWERS THE QUESTION YOU ASKED
The June review was scoped "is our harness well-built?" (hooks, evaluators,
pruning, fallback models). It never asked "how do we run several builders at
once?" — so it never found worktrees. The review was correct and the question
was too small.
**Law: when a review comes back clean, ask what question it did NOT ask.** Add a
standing "what was out of scope, and why?" section to every review artefact.

## Finding 3 — FIRST-PRINCIPLES REASONING IS NOT EVIDENCE (R9, advisor edition)
The advisor reasoned parallel building was inherently narrow — one tree, one
suite, coherence risk — and called it "physics". It sounded rigorous. It was
wrong in a specific, checkable way, and thirty seconds of search would have
shown an entire ecosystem that had solved it.
**Law: a confident derivation about the state of a fast-moving field is a
HYPOTHESIS, not a finding. Verify against published reality before acting on
it.** (Third R9 breach by the advisor this weekend — the other two: claiming the
published net was "frozen"; accusing the agent of grooming when it was
recovering a blocked pipeline. All three came from reasoning over artefacts
instead of reading the evidence.)

## Finding 4 — BOTTLENECKS ARE ONIONS; THE LAST LAYER IS INVISIBLE UNTIL IT IS THE LAST
Empty draw -> capped at 1 -> livelock -> BUILD-gated -> map write-contention.
Each fix REVEALED the next. The map was not a bottleneck when one agent worked
one atom; contention cannot be discovered without contention.
**Law: do not expect to see the real constraint before you have removed the fake
ones. Fix, measure, look again — and never assume the last fix was the last
fix.** Corollary: the FIRST diagnosis of a slow system is almost never the real
one.

## Finding 5 — THE ARCHITECTURE WORK AND THE VELOCITY WORK ARE THE SAME WORK
Worktrees solve FILE collisions; they do not solve LOGICAL ones. Two agents
reaching into hedged_settlement.py still collide in meaning. The fix is typed
internal seams — which is Epoch 3, which we had filed as "go-live architecture"
and therefore as *later*.
**Law: when a structural fix keeps getting deferred as "architecture", check
whether it is also the thing capping your throughput. If it is, it is not later
— it is now.** (This is why the monolith choice was right AND incomplete: a
monolith stays modular only by discipline, and we had not yet paid that bill.)

## Meta-finding — WHO CAUGHT WHAT
Every one of the last five structural findings was surfaced by the DIRECTOR
asking a naive-sounding question ("why can't it work in parallel?", "does this
not argue against your monolith?", "surely others have hit this?"), not by the
machine's self-audit and not by the advisor's analysis. Both of us were inside
the system, reasoning from its own frame.
**Law: the outside question is the highest-value input in the whole loop.
Protect the director's ability to ask naive questions — never train it out of
him with jargon, and never let the machine's confidence discourage it.** This is
the human seat's real job in an autonomous company, and it is the seat that
cannot be automated away.

## DoD
Findings 1-5 + the meta-finding recorded in the method/casebook lane; Finding 1
wired as a real trigger (structural wall -> published-practice check, before
theorising) with a test that it fires; Finding 2 added as a required section in
every review artefact template. These are the durable IP — treat them as such.
