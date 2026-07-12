# GOVERNED_COMPANY_AND_THREE_LANES — decision rights + wall-split parallelism (P1)

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
