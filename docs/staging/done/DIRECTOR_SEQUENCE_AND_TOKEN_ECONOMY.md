# DIRECTOR_SEQUENCE_AND_TOKEN_ECONOMY — RY endorsed, re-sequenced (P1)

**Staged:** 2026-07-08 ~09:25 BST by advisor, director-confirmed ("I agree").
**Tier:** 2 — director decision on existing proposals, proceed immediately.
**Applies to:** the Phase RY 4h opt-out window (expires ~11:51 BST). This is the
redirect: RY is ENDORSED but must not auto-start at window close. Sequence below.

## Context: token economy is a P1 constraint this week
48% of the weekly usage allowance is already consumed as of Wednesday morning,
partly by the identical-result auto-process loop. Until the weekly reset, weigh
every autonomous action for token cost. Prefer bounded, cheap, verifiable work
first; defer expensive novel work toward the reset.

## Sequence (director-set)
1. **Runner true-retirement verification (first, now).** The 07:38 fix (comment out
   of start_worker.sh + gated kill) is not "done" until R2 is satisfied: no runner
   process present AND no further respawn across at least one restart of the
   background stack. Evidence = the process table and an observed quiet period, not
   the commit. Additionally, close the waste at its root: add a **change-detection
   gate** to the auto-process pipeline — if a run_complete's inputs/results are
   identical to the previously processed run (same git state, same headline
   figures), skip the report/LATEST/site regeneration and the commit entirely. Log
   one line instead. Dozens of identical £1,535,308 commits per day is pure burn.
2. **WEBSITE_FRESHNESS_AND_DEDUP.md (already staged, P1).** Bounded, cheap,
   director-repeated. Run it second (or in parallel with 1 if file-disjoint).
3. **Phase RY (endorsed, deferred start).** Proceed as drafted in NEXT_PHASE.md
   only after 1 and 2 are consumer-verified complete. Given the 48% burn, if the
   weekly reset is near when 1–2 close, prefer starting RY after the reset. RY's
   scope and design are approved as filed — no re-proposal needed, no new opt-out
   window; just start when sequencing permits.

## P-5 director re-rank (post-RY backlog)
Ranked order after RY closes:
1. NUDGE_PHYSICS remaining mechanisms (Layer 2 breadth).
2. Hedge-outcome grading — PARKED until sufficient shadow-live entries have
   accumulated to grade; re-propose with the entry count as evidence of readiness.
3. Live NBP gas source — BLOCKED pending a Tier 1 director decision on the external
   endpoint; prepare the decision brief (candidate sources, cost, verification
   plan) but do not connect anything.
Update PRIORITIES.md to reflect this rank and this instruction's sequence, with
freshness stamp. PRIORITIES.md remains the sole arbiter.

## Definition of done
NTFY confirming: (a) runner verified dead per R2 with evidence stated, (b)
change-detection gate live and demonstrably skipping an identical run, (c) website
pass complete per its own R1 criteria, (d) PRIORITIES.md updated, (e) RY start
timing stated. Keep the NTFY to one message.
