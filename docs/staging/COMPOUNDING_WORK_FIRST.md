# COMPOUNDING WORK GOES FIRST — two re-ranks (P0, director-decided)

**Staged:** 2026-07-13 by advisor, **director-decided**. Disposition: INTERRUPT
for the re-ranks. **Note: item 2 is a NEW registration and therefore breaches the
advisor's own moratorium — deliberately, with the director's explicit
authorisation, because it is the one atom that makes every other atom cheaper.**

## The law behind both (add to CLAUDE.md — it is method IP)
**Work that SHORTENS THE FEEDBACK LOOP compounds. Everything else is linear.
Therefore it goes FIRST — regardless of which epoch it was filed under.**
Our epoch arc was sequenced by NARRATIVE (fidelity -> value cycle -> walls ->
evolution) — which is how you would EXPLAIN the project. It was never sequenced
by COMPOUNDING RETURN — which is how you would BUILD it. Where those two orders
disagree, build order wins.

## RE-RANK 1 — ARCH1 (internal seams) to BUILD, now, thin-started
Currently: Epoch-3 discovery lane, FRAME. **It is the thing gating parallel
building TODAY.** Worktrees solved FILE collisions; they do not solve LOGICAL
ones — two agents reasoning about hedged_settlement.py still collide in meaning.

**Decompose by JOURNEY, not by technical layer** (director's framing, and it is
the right one): onboarding; metering & data; billing; payments & collections;
pricing & hedging; settlement; service & complaints; vulnerability; regulatory
reporting. These have **naturally stable interfaces, because the messages between
them are already standardised in the real industry** — a meter reading, a bill, a
payment, a mandate, a settlement run.

**The consequence that makes this pay twice: the internal seams ARE the go-live
seams.** Shape them like the real message flows and you build the integration
boundary ONCE, getting parallelism, modularity AND the wall's external contract
from the same work. That is Epoch 3 arriving early and paying for itself twice.

**DO NOT BIG-BANG IT.** Cutting nine seams at once is a refactor programme that
would eat the week and make the count worse before better.
**Cut the seam where the next work lands:** the affordability cluster (W2_4-W2_10,
just opened for BUILD) touches **billing, payments & collections, and service**.
Cut those three interfaces first, build the cluster against them, and let the
seams ACCRETE IN FRONT OF THE WORK rather than behind it.

## RE-RANK 2 — EXPERIMENT-LOOP SPEED (new atom; the unregistered precondition)
**Nobody has registered speed as work, because it does not look like a feature —
it looks like the weather.** But:
- A full sim run takes **~10 minutes** (the recent failure burned 594s).
- The suite is **17,000+ tests**.
- **Every** build, validation, Expert Hour, gap measurement and cold-eyes walk
  pays that toll. It is why a "quick check" is never quick.

**And here is the arithmetic that makes it urgent rather than nice:**
**Epoch 4 requires the company to live and die MANY TIMES** — populations of runs,
across generations. At ten minutes a life, a thousand lives is a WEEK of
wall-clock PER GENERATION. **The evolutionary tournament is arithmetically
impossible at current speed.** Speed is not a later optimisation; it is an
UNREGISTERED PRECONDITION of an epoch we have already committed to.

**Requirements (mechanism yours):**
1. **MEASURE FIRST.** Profile the real cost per experiment cycle: sim run, test
   suite, publish pipeline, evaluator passes. Where does the time actually go?
   Report it. Do not optimise before measuring (R4).
2. Then attack the biggest terms. Candidates to weigh, not prescriptions:
   scoped/tiered test selection (full suite only at integration — already
   partially decided); parallel sim execution; caching/memoising deterministic
   stages; a fast-mode with reduced fidelity for inner-loop checks (with a
   guardrail so fast-mode results can NEVER be published as truth);
   incremental/partial runs.
3. **The third payoff, and it belongs to ARCH1:** a typed wall interface lets the
   company be tested against a **MOCKED interface** instead of a full sim run.
   Same work, three returns — modularity, parallelism, and fast tests. Design
   ARCH1 so that mock is a first-class citizen from day one.
4. **Target:** state the cycle time needed to make Epoch 4 feasible (work back
   from "N lives per generation, M generations, within a week") and report the
   gap between that and today. That number is the size of the problem.

## Non-negotiables
- Speed must never buy itself with fidelity. A fast-mode run is a DEVELOPMENT
  tool; it may never publish, promote an atom, or feed the board pack. Enforce it
  mechanically (fail closed), not by convention.
- No goal-seeking: cycle time is a diagnostic, not a target to game by deleting
  tests (R15 stands — controls must still fire).

## DoD
ARCH1 building, thin-started on billing / payments-collections / service, with
the affordability cluster built against those interfaces; internal seams shaped
as real-world message flows and documented as the go-live contract; experiment
cycle-time profiled and published; the Epoch-4 feasibility gap stated as a
number; a fast inner loop with a mechanical guarantee it can never publish.
Report both in the next digest.
