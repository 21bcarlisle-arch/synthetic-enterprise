<!-- MINT-CONSUMED BANNER (worker tick 2026-08-11) — this ruling's WORK THIS CREATES block has been
FULLY MINTED per the §2+§4 mechanism ("mint one atom per named deliverable; state which are already
covered"), so its mint-source obligation is DISCHARGED and it moves to in_progress/ rather than
re-granting a mint turn on every tick. Receipt, with the exit criteria and the reasoning:
docs/staging/done/PLANNER_MINTED_population_and_book_growth_2026-08-11.md.
MINT COVERAGE MAP:
  [1] Proposed SIM population target + the probe's measured cost — MINTED: PB1_population_target_
      and_its_price (W2_customer_generator, L0->2, depends_on AO12_scale_probe_10k).
  [2] Proposed opening book size + the acquisition path — MINTED: PB2_opening_book_won_not_assigned
      (W2_customer_generator, L0->3, depends_on PB1).
  [3] Growth curve as earned outcome, mechanisms named — MINTED: PB3_book_growth_as_earned_outcome
      (W2_customer_generator, L0->3, depends_on PB2, couples_with W2_3_competitor_field).
  [4] Attachment to the futures/commitment-set shelf — ALREADY COVERED, NOT re-minted. FUT1_attach_
      forward_hook is the landed (L2) mechanism for exactly this property; a second atom would be a
      second way to do one thing. Discharged concretely: all three atoms are filed ON the shelf
      (inside the Epoch-2 commitment set, after EP5_settlement_true_ups) and the receipt carries the
      `**Advances:**` declaration, now rendered into docs/design/FORWARD_ATTACHMENT_LEDGER.md.
STILL OPEN (why this is in_progress/ and not done/): the WORK, all of it. The three atoms are
`loop_stage: idle` on the shelf's own convention, which is what §"Sequencing" asked for — parked for
BUILD only, DISCOVER/FRAME-open now. UNBLOCKS: PB1's proposal half is drawable immediately as
DISCOVER/FRAME work; its COST half waits on AO12_scale_probe_10k actually running (level 0, unrun),
because the ruling makes the probe's measurements the price list rather than an estimate.
NOT DONE HERE, and deliberately: the population was NOT raised (R13 — the numbers are the worker's
to propose, but a curriculum change is not a mint side effect), and the queryable-projections
prerequisite the Sequencing paragraph names was NOT minted from here — DIRECTOR_INSTRUCTION_
QUERYABLE_PROJECTIONS_2026-08-10.md is its own unconsumed mint source with its own WORK THIS CREATES
block, still in the staging root, and consuming it sideways would leave that doorbell pointing at
work already done under another name.
-->

# [DIRECTOR-RULING] — Grow the world first, then win a book out of it (2026-08-11)

**Type:** [DECISION]. The published company runs a ~13-account book. That is a stress test of the money machinery, not a supplier. Ruling: it should grow — in this order, and by acquisition, never by assignment.

**1. The SIM population grows first.** The world's premise population is raised materially above today's research draw (target the worker's to propose with the AO12 10k-probe's measurements as the price list — the probe exists precisely to say what scale costs before it is bought). A larger world is the precondition; the company cannot plausibly acquire from a stock that isn't there.

**2. The company starts with a subset, and a larger starting number than today.** The opening book is a subset of that population, sized so the company reads as a small real supplier rather than a fixture. The starting number is the worker's proposal against measured cost; the director's requirement is only that it be materially larger than 13 and defensible as a plausible small supplier.

**3. Growth is gradual and earned.** From that start, the book grows through the acquisition physics already built — won and lost against the market, not incremented. Churn, acquisition cost, and the competitor field are the mechanisms; a growth curve that cannot be lost is not a growth curve.

**The wall holds throughout, non-negotiable:** the company learns its book through onboarding and interface events only. The population draw stays hidden; the subset arrives by acquisition. Nothing here licenses the company to read the SIM's population directly.

**Sequencing:** this is Epoch-2-adjacent work and should attach to the futures shelf rather than jump the queue; it draws as capacity allows and as the product interleave arms. Cost is the governor — if the probe says the scale is unaffordable on current storage, that is the answer, and the queryable-projections/storage work is its prerequisite, not a workaround.

## WORK THIS CREATES (canonical, in-document)
1. A proposed SIM population target with the probe's measured cost beside it. 2. A proposed opening book size and the acquisition path that produces it. 3. The growth curve as earned outcome, with the mechanisms named. 4. Attachment to the existing futures/commitment-set shelf so this accretes rather than scatters.

— Ruled 2026-08-11; staged by the advisor; sequencing and numbers are the worker's, the ordering and the wall are the director's.
