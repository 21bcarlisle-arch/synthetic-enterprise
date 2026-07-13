## Epoch-2 BUILD live via the twin-approver seat: A3 approval interface banked (L0→L1), THREE LANES adopted
Last updated: 2026-07-13T13:53:33Z

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

**Latest simulation results (2016–2025)** — auto-processed (494s / 8 min):
- Net margin: £1,505,249.80 | Gross: £6,455,328.74 | Capital: £51,232
- Treasury: £2,466,636 → £3,883,415 | 38 committee interventions | 1575 bills issued
- Enterprise value: £7,281,749.29 | Net after CTS: £6,385,467
- Retention: 12 offers, 12/12 retained | 4 no-offer churns | 4 total churned accounts