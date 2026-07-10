# SELF_DIRECTION_AND_PARALLELISM — stop idling, propose parallel agents (P1)

**Staged:** 2026-07-10 by advisor, director-decided.
**Place in the arc:** operating model. Fixes the "idle with an epoch of work
visible" failure and opens the path to real parallelism. Does not change what
gets built next (epoch-2 framing / Phase 2 continue) — changes HOW work is
sourced and how many lanes run.

## Problem 1: empty agenda must mean self-refill, not idle
Last night the agenda emptied and the agent went quiet for ~5 hours with an
entire epoch-2 map (six evidence findings, two "foundational rework") sitting
unstarted. The supervisor grants turns only when the agenda has items — but
nothing REFILLS the agenda. Net effect: the machine waits to be handed intent.
The autonomy the old retired runner had (inventing its own next work) was never
rebuilt after we made the agent safe. Rebuild it, bounded by the review gate.

**Requirement:** an empty agenda is itself a trigger. When no work is queued,
the agent's FIRST action is to refill from the roadmap — read PRIORITIES.md and
the epoch arc (CLAUDE.md), select the highest-value AVAILABLE work that needs no
director decision, queue it, and continue. Idle is only legitimate when the
roadmap genuinely holds nothing actionable (say so via NTFY if that ever happens
— it shouldn't for a long time).

## Problem 2: recalibrate one-way doors — flag-and-proceed, don't wait
The director's ruling: almost nothing here is truly irreversible. This is a
simulation with append-only history and git — wrong choices revert, bad runs
re-run, mistakes restate. The ONLY genuinely irreversible actions are ones with
real-world external consequences (spending real money, sending real messages to
real people, going live) — none of which exist yet.

**Requirement:** stop treating design/architecture/model decisions as one-way
doors requiring a director pause. For a reversible decision: record the
reasoning, choose the reversible/least-committal path, FLAG it in the log +
NTFY, and CARRY ON without waiting. Reserve a hard stop ONLY for genuinely
irreversible real-world-external actions (there should be ~none in current
epochs). Do not block progress waiting on the director for reversible calls;
the director steers after the fact. Bias hard toward momentum.

## Problem 3: propose safe domain-separated parallelism (your expertise, not mine)
The director wants more done in parallel and has asked whether more agents are
the answer — explicitly deferring to your knowledge of this harness over the
advisor's. Do NOT just spawn more Claude sessions on the same repo (that
recreates the writer-collisions we spent two days fixing). Instead PROPOSE, with
honest pros and cons, a design for domain-separated parallel work: agents/lanes
that own DISJOINT file scopes (e.g. build vs background-analysis vs
research/discovery) coordinated by the existing tree-lock, so concurrency comes
from separation, not from racing on shared files. Cover: how many lanes, scope
boundaries, how they hand off, how single-writer-per-file is preserved, how the
director reviews N streams without becoming the bottleneck, failure modes, and
what could go wrong. Rank options; recommend one. This is a proposal for
director ranking, not a build — but move fast to produce it.

## Non-negotiables unchanged
Historical Ground Truth, epistemic wall, R1-R10, single-writer-per-file,
push-before-notify, 0b evidence. Momentum and parallelism never override these.

## DoD / sequencing
Self-refill behaviour live (agent demonstrably picks its own next work from the
roadmap when the agenda empties); one-way-door recalibration in CLAUDE.md;
parallelism proposal filed for director ranking. Then IMMEDIATELY use the new
self-refill to continue the real roadmap: epoch-2 framing prep and CORE_FIDELITY
Phase 2 (segments/psychology) are the highest-value available work — pick them
up without waiting. One NTFY when self-refill + recalibration are live, with the
parallelism proposal linked.
