# GOVERNED_COMPANY_AND_THREE_LANES — decision rights + wall-split parallelism (P1)

**STATUS (2026-07-12): DoD's 4 items all actioned this pass, standing item
NOT fully closed.** Built: decision-rights register + pricing decision-
events (`company/governance/decision_rights.py`, wired to
`simulation/renewals.py`, maturity-map atom `A2_decision_rights_register`
level 0->1); lane-wall dev-time hook piloted and demonstrated both
directions (`.claude/hooks/lane_wall_hook.py`, atom
`H6_lane_wall_development_pilot` level 0->1). Registered only, not built:
`A3_approval_interface` and `A4_sim_approver` atoms, with the two honesty
disciplines recorded verbatim. Written: the overdue parallel-lanes proposal
(`docs/design/PARALLEL_LANES_PROPOSAL.md`). Stays in `in_progress/` (not
`done/`) because the standing item itself isn't closed -- A3/A4 have no
build date, the parallel-lanes proposal's own recommendations (worktree
adoption, marker-file lane-keying for multi-agent fan-out) aren't yet
acted on, and only 1 of 6 decision classes is wired to a real call site.
Full text below is the original staged instruction, unchanged.

**Staged:** 2026-07-12 by advisor; director-decided in live conversation
("human-in-the-loop governance interface... and for the SIM an invisible
agent acting as that human; turns forking into a benefit not a risk").
**Place in the arc:** Lane A's path to L4 (governed, decision artefacts);
extends the wall doctrine (Epoch 3) to development itself; supplies the frame
the overdue parallel-lanes proposal (SELF_DIRECTION item 3) must answer to;
sim-approver is Epoch-4 tournament machinery. Registration + thin-start +
pilot — NOT a big-bang build. Sequence: does not displace M2 hot-lane work.

## Part 1 — The Decision-Rights Layer (the governed company)
A real company does not let anyone, human or AI, make unbounded commercial/
legal/financial decisions. Build that as a first-class organ:

1. **Decision-rights register (Lane A atom, build thin NOW inside M2):**
   a versioned, director-owned register of decision classes requiring
   approval — e.g. pricing moves beyond threshold, hedge-mandate changes,
   credit/collections policy changes, customer-harm remediations, legal/
   contractual commitments, spend above X. Each class: trigger (event /
   threshold / cadence), required context pack, approver, SLA. Start by
   LOGGING the pricing organ's decisions as proper decision-events on the
   bitemporal spine (request -> context -> decision -> rationale, two
   timestamps). Cheap, immediate, seeds the taxonomy.
2. **The approval interface (Epoch 2/3 boundary):** requests-awaiting-
   decision as events + a surface/API a human can actually operate (the
   Director console door already in the site constitution hosts it).
   Approval LATENCY is real physics: a pricing window that closes while a
   request waits is a genuine governance cost — model it, never wish it away.
3. **The approver as adapter (the elegant part):** sim-twin = a policy-agent
   playing the human approver so tournament lives don't need the director
   ten thousand times; real-twin = the director via the interface. Go-live =
   swap the adapter — identical pattern to Bacs/meter flows, applied to
   governance itself.
4. **Two honesty disciplines (non-negotiable):**
   - The sim-approver's policy is DIRECTOR-AUTHORED CURRICULUM — written,
     versioned, his — never learned/tuned by the agent from outcomes (Law B:
     the company must not train its own board into permissiveness).
   - The approver sits OUTSIDE the company's wall like a real board: it sees
     the submitted context pack, not SIM ground truth, not company internals
     beyond what is submitted. A board that can grep the codebase is not a
     board.
   Governance actions land in the obligations/compliance surfaces (F lane
   sees the decision trail).

## Part 1b — Scrutiny economics (director addendum, 2026-07-12)
Governance is not just a control; it is a MEASURED, COSTED subsystem. Extend
the decision-rights layer with:

1. **The scrutiny dial (director-owned, like the curriculum rack):** named,
   versioned supervision levels (e.g. Light-touch / Standard / Heightened /
   Paranoid) that flex which decision classes require approval, thresholds,
   and review cadences. **Escalation physics:** the compliance/risk organs
   RECOMMEND dial changes — incidents, breaches, or near-misses generate a
   recommend-more-scrutiny event with rationale; sustained calm generates
   recommend-less. The approver (sim-agent now, human later) PICKS — from
   options or freeform — and the pick is itself a logged decision. When
   things go wrong, scrutiny rises: that is real-company physics, modelled.
2. **Roles & disagreement (schema now, settle later):** default = RAPID-style
   single accountability — each decision class names ONE Decider; others
   hold Input/Agree/Perform roles; director is tie-break escalation. Voting
   is deliberately NOT the default (heavy for this scale) but the register
   schema carries role fields from day one so multi-human governance is
   configuration, not rebuild. Marked DIRECTOR-TUNABLE, not settled.
3. **Time-and-cost accounting per decision (the FTE model):** every decision
   class carries expected review EFFORT (minutes of human attention) and
   expected ELAPSED SLA. Every decision-event logs actuals — the sim-approver
   draws realistic effort/elapsed from those expectations (anchored, varied);
   real mode measures them. Rate card by decision tier: C-suite rates for
   strategic classes, descending to operational rates for routine reviews
   (extends and will eventually REPLACE the flat B2 oversight assumption
   with a decision-derived oversight cost line). Fractional humans assumed.
4. **Context packs are LINKS, not prose:** every approval request carries
   links to the exact website surfaces/data (passported, evidence-linked)
   needed to decide, plus the company's recommendation. Consequence: the
   Expert-Hour legibility standard becomes operational — "can an approver
   decide from the pack within the expected effort time" is now a testable
   property of the SITE as well as the decision.
5. **The output that matters:** a standing surface computing FTE-required =
   sum(effort)/capacity BY SUPERVISION LEVEL and by seniority tier, with
   cost — "how many humans, of what kind, does this company actually need
   at each scrutiny setting" — derived from logged decisions. This is the
   thesis's second chart (the dual ledger says what AI removes; this says
   what human remains, measured) and it prices the director's own time.

Register these as Lane-A atoms alongside the decision-rights register; the
thin start (pricing decision-events) should log expected/actual effort
fields from its FIRST event so the dataset accrues from day one.

## Part 2 — Three-lane development (fork as enforcement, not risk)
The wall is the one shard boundary disjoint BY DEFINITION — sim/ and
company/ cannot overlap because non-overlap is the founding law. Therefore:
1. **Pilot now, cheap:** hook-profiles per work-type — supplier-lane work
   runs under a profile that DENIES reads of sim/** (and vice versa),
   extending the epistemic wall from runtime into development (builder
   blindness, not just runtime blindness). Prove it on real M2 tasks; log
   denials.
2. **Target shape (for the parallel-lanes proposal, now due Monday):** three
   lanes — SIM-builder / company-builder / governance+harness — separate
   contexts (sessions or worktrees), communicating ONLY through typed
   interface contracts; the contract files are the negotiated artefact.
   Single-writer preserved per lane; integration serialized per tree.
   The proposal must evaluate this frame against tree-lock/worktree/daemon
   reality and recommend mechanics, replacing generic sharding.
3. Rich's framing goes in the casebook: separation chosen for governance
   turns out to be the safe parallelism boundary — one design, two payoffs.

## DoD
Register atom live with pricing decisions logging as decision-events;
hook-profile pilot demonstrated (a supplier-lane sim-read denied, logged);
approval-interface + sim-approver registered as atoms (2/3 boundary and
Epoch 4 respectively) with the two honesty disciplines recorded verbatim;
parallel-lanes proposal (Monday pack) answers to the three-lane frame; one
digest line per landed piece. Pixel rule applies to any surface work.
