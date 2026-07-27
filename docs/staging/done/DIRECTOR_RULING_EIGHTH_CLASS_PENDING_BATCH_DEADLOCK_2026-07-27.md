# [DIRECTOR-RULING] — EIGHTH CLASS: the pending-batch deadlock. 42 hours of rest declared legitimate while mints sat open. (2026-07-27)

**Type:** [DIRECTOR-RULING] via advisor bridge. Priority zero.

## The finding (advisor-verified from origin, day-by-day)

**Saturday 06:00–11:09Z: 31 work commits** — all four director rulings consumed and built (book-scaled trading facility fixing the hardcoded £5m, expected-collection detector, activation infra with liquidity/cover ledger fields, SSP part-(a) reframe to merit-order, merit-order SRMC DISCOVER drawn and discharged, several HARDENs). That work is good and is not in question.

**Saturday 11:09Z → Monday 05:07Z: two commits in 42 hours**, both the planner writing *"rest-with-proof … premise FALSE"* at midnight. The live heartbeat reads every lane empty **including `planner=.`** → *"REST-LEGITIMATE (whole authorized set empty)"*.

Per the director's standing ruling, a further stall class is an **R10 breach of R17**, not a new incident. This is the eighth.

## Hypothesis to confirm or refute with evidence (R9), then fix as a class

**H1 — the pending-batch gate is deadlocking.** The gate added on 2026-07-24 prevents minting a new batch while one is pending. Saturday's planner minted several items (bad-debt reconciliation bridge, W1_6, run-rotation FRAMEs, two further next-steps). If those are **open but blocked**, then: the gate refuses to mint *because a batch is pending*, while the blocked items are not drawable, so rungs 1–6 report empty — and the machine rests honestly inside a deadlock of its own making. **Blocked is being counted as pending.**

**Class fix if H1 holds:** the gate must count **drawable** pending items, not merely open ones. A batch whose items are *all* blocked does not suppress minting — it triggers two things at once: **escalate every blocker** as one batched [ACT] to the director, **and mint around them** from the remaining ratified goals. A blocked batch is a reason to plan more, never a licence to rest.

**H2 — the deadman was silenced by the liveness fix.** `chore(liveness)` commits land roughly every 30 minutes. A deadman measuring "time since the last git commit" therefore sees a healthy machine forever. Verify; if confirmed, its clock must count **work** commits only — liveness, publish and other chore commits are explicitly excluded — with an R15 test proving a liveness-only window still pages.

## Non-negotiable additions

**Enumeration honesty.** Publishing *"whole authorized set empty"* while minted work is open is a false claim, and it is the same class already fixed twice at lower levels. Any lane reporting empty while items exist in `in_progress/` must instead report them **with their blocking reason**. An enumeration that cannot see open mints is not an enumeration.

**Escalation duty.** Rest exceeding **2 hours** while any mint is open, or exceeding **6 hours** in any circumstance, must raise an [ACT] to the director naming what is blocked and on whom. A machine that rests for 42 hours must be shouting, not resting quietly. Silence for a working day is itself the defect.

## Report, in one NTFY

(1) Every open mint enumerated, with **why each is not drawable** — director-walled, dependency, gate, or classifier. (2) H1 and H2 confirmed or refuted with journal evidence. (3) The class fixes deployed, each with an R15 pair reproducing **this weekend's exact state** as the failing test. (4) The first post-fix draw.

**Risk & proportionality:** touches the draw/mint gate and the deadman clock — failing tests first, shadow rails apply to scanner changes, own commits. Tag: **priority zero; class fix; then resume the product queue.**

— Advisor bridge, carrying the director's standing ruling, 2026-07-27.
