## Epoch-2 BUILD live via the twin-approver seat: A3 approval interface banked (L0→L1), THREE LANES adopted
Last updated: 2026-07-13T15:25:40Z

**Status:** self-driving BUILD lane open (DIRECTOR_TWIN standing-approver, canon v2 §3a).
Epistemic PASS throughout. All commits pushed. Two forks in flight (one BUILD, one read-only
Expert Hour) — see below.

**A3_approval_interface — BUILT to honest L1** (director's explicit "BUILD IT NOW"; commit
`b7a26938`, pushed; epistemic PASS 498 files; 11 new tests, governance suite 35 passed / broader
saas+governance 1557 passed). New `company/governance/approval_interface.py`: the human-operable
requests-awaiting-decision surface (`approval_queue_as_of` → `ApprovalRequestView`) exposing
decision class, a **link-shaped context pack + recommendation** (links not prose — a testable
property), submit time, and accrued pending **latency** as-of a given time on the shared
BitemporalEventLog; plus a real governance caller (`propose_hedge_mandate_change`) exercising the
full submit→pending→resolve lifecycle. Epistemic wall respected (approver sees only the submitted
pack). **Honestly held at L1, not L2:** no live run triggers the workflow yet (hedge-mandate-change
execution doesn't exist; `COMPANY_MIN_HEDGE_FLOOR` is a constant) and Door 7 (the Director console
surface) isn't built, so the surface is an API/dataclass, not an operable pixel (fails R11).

**THREE LANES adopted as standing structure** (THREE_LANES_STANDING.md, director-decided; full text
`docs/design/THREE_LANES.md`, pointer in CLAUDE.md): BUILD is inherently narrow (one tree/suite/
gate) — spend width where free. L1 BUILD serial (1–3 concurrent only on disjoint scopes; interim
rule: orchestrator is sole `maturity_map.yaml` writer, forks report levels back). L2 SITE
(`site/**`, disjoint) runs parallel to builds permanently. L3 DISCOVERY doc-only, never gated.

**Backlog registered as atoms** (QUEUE, from THREE_LANES / WORKTREE_ISOLATION_AND_SEAMS / RETRO):
`H10_worktree_isolation` (HIGH — native `isolation: worktree` per-fork, the proper fix for build
width; supersedes the interim sole-writer rule), `H9_map_write_serialisation`, `SITE1_expert_doors`
(constitution doors 3–8), `ARCH1_internal_seams` (Epoch-3: typed seams between billing/pricing/
settlement/collections = the architecture AND velocity work, same work), `G3_method_ip_worktree_retro`
(the 6 method laws from the worktree-miss retro, recorded as casebook IP).

**In flight now:** W2_2_population_draw BUILD (continue synthetic customer acquisitions through
2021-2025 — the book currently stops dead in 2020 — via an own-seeded RNG substream, C-S2); A2's
independent Expert Hour (fresh-context evaluator judging its L2→L3 bar given A3's new module-level
caller).

**Atoms below target: 29** — an honest RISE from 24: A3 banked L0→L1 (−0 to count, still below its
L2 target) while 5 backlog atoms were newly registered (+5). Registering real backlog raises the
count; that is the honesty bar, not regression.

**Latest simulation results (2016–2025)** — auto-processed (467s / 8 min):
- Net margin: £1,505,249.80 | Gross: £6,455,328.74 | Capital: £51,232
- Treasury: £2,466,636 → £3,883,415 | 38 committee interventions | 1575 bills issued
- Enterprise value: £7,281,749.29 | Net after CTS: £6,385,467
- Retention: 12 offers, 12/12 retained | 4 no-offer churns | 4 total churned accounts

<!-- NAIVE_ORGAN_ASKS -->
**NAIVE ORGAN asks:** — open questions; answer WITH EVIDENCE (`answer_question`) or mark a miss. Never actions.
- (T1_idle_turns_with_open_atoms) If the supervisor has been idle for 102 turns while 29 atoms remain open, what is it waiting for — and how do you know those idle turns are a deliberate strategy rather than the system silently stalled or stuck?
- (T3_inherence) What does "BUILD is inherently narrow (one tree/suite/...)" actually have to do with keeping a UK energy supplier solvent and out of administration, and on what evidence is that fragment being treated as a claim worth examining rather than an arbitrary snippet of a code comment?
- (T3_inherence) When you say each of these seven triggers is "a real catch from this weekend," how many false positives did the same detector raise over that period — that is, how often did it flag one of these patterns and the flag turn out to be wrong?
- (T3_inherence) When you say BUILD is "inherently" narrow — is that a fixed property of what BUILD actually does, or just an artifact of how this one tree/suite happens to be configured, and what specifically would break if that scope were widened?
- (T3_inherence) What actually justifies the claim that BUILD is "inherently narrow (1-3 max)" — is that a measured property of the work itself, or just an assertion, and what concretely goes wrong if it were made wider?
- (T3_inherence) If the extra 24 atoms are read-only, zero-collision, and would move you toward target, what is the actual constraint forcing them to be worked one at a time rather than all at once?
- (T3_inherence) When you call BUILD "inherently narrow," what is the concrete definition of BUILD's scope that makes narrowness intrinsic — and if you cannot state that scope independently of this particular tree/suite's configuration, on what basis is the word "inherently" doing any work at all?
- (T3_inherence) When you say BUILD is "inherently narrow (1-3 max)," is "1-3" a number that fell out of measuring something about the work — like task interdependence, error rates, or throughput at higher widths — or is it just a cap someone picked and then relabeled as "inherent"? What specific failure have you actually observed (or would predict) at width 4+ that doesn't occur at width 3?
- (T3_inherence) If those 24 atoms truly are read-only, zero-collision, and target-positive, who or what actually enforces the "one at a time" limit — is it a hard mechanical rule of this system, or just an unexamined default that no one has traced back to a real constraint?
- (T3_inherence) If BUILD's "narrowness" can only be demonstrated by pointing at the current tree/suite configuration, what observable would change — some capability BUILD gains or loses — the moment you swapped that configuration, and if the answer is "nothing," why is that dependence being described as "inherent" rather than simply "how it happens to be wired right now"?
- (T3_inherence) If width 3 was itself just carried over from some earlier default rather than measured, what evidence would distinguish "we tested 4+ and it failed" from "we never ran anything wider than 3, so of course we've only ever observed success at 3"?
- (T3_inherence) If 24 atoms are each independently read-only, zero-collision, and target-positive, what concrete failure or cost is supposed to occur if two or more are applied together — and has anyone actually observed that failure, or is "one at a time" just asserted without a single traced example of collision or harm?
- (T3_inherence) When you swap the tree/suite configuration and BUILD's capabilities are unchanged, what would you have to observe changing for you to accept the narrowness as "inherent" — and if no such observable exists even in principle, what work is the word "inherent" doing that "currently wired this way" doesn't?
- (T3_inherence) If all 24 atoms are genuinely read-only, zero-collision, and target-positive as claimed, what specific mechanism or shared resource would make applying two simultaneously behave differently than applying them sequentially — and does anyone actually possess a logged instance of that difference, or does the "one at a time" rule rest entirely on the untested fear that some undocumented coupling exists?
- (T3_inherence) What are the two named open questions, and by what mechanism does merely updating a stale dependency's status actually resolve them rather than just relabel them as resolved without new evidence?
- (T3_inherence) What does any of this — "tree/suite configuration," "BUILD's capabilities," the semantics of "inherent" versus "currently wired this way" — have to do with the only stated goal (a UK energy supplier's enterprise value and its avoidance of administration), given that the observable state contains not a single number, price, cost, or survival metric?
- (T3_inherence) If two atoms are genuinely read-only and zero-collision, then the only thing they can share is the act of applying them — so what does your apply pipeline actually touch in common (a lock, a config reload, a transaction, a live cutover) that two sequential applies never overlap on, and has anyone ever observed that shared step fail under concurrency, or is "one at a time" simply the rule nobody has been given permission to test?
- (T3_inherence) If a DISCOVER pass both raises an open question about anchors and supplies its own answer, what independent evidence confirms that answer is correct rather than merely internally consistent with the assumption that prompted the question?
<!-- /NAIVE_ORGAN_ASKS -->
