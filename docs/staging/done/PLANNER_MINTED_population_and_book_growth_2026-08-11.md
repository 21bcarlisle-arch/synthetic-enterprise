# PLANNER MINT — population and book growth, three atoms on the Epoch-2 shelf (2026-08-11)

**Source:** `DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md` (advisor-staged
`[DIRECTOR-RULING]`), drawn on a scheduled worker tick under the §2+§4 mint-source mechanism
(`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`): *"mint one atom per named
deliverable from its WORK THIS CREATES block; state which are already covered."*

**Advances:** EP16_anchored_generators, EP17_varied_population_draw, EP1_clv_three_horizon — a
materially larger population must stay externally anchored (EP16) and is the Epoch-4 varied-draw
atom's own subject (EP17); an opening book won by acquisition is what a CLV number is for (EP1).

**Filed in `done/` deliberately.** The mint obligation is DISCHARGED by this document; the work
itself now lives in the map, which is the queue. A `PLANNER_MINTED_*` doc left in the staging root
reads as an unconsumed mint (`supervisor._pending_planner_mints`) and would suppress the HARDEN
tier while nothing was actually pending.

---

## The mint — one atom per deliverable

All three are filed **inside the Epoch-2 commitment set** in `docs/design/maturity_map.yaml`
(immediately after `EP5_settlement_true_ups`), `loop_stage: idle`, `provenance: director_ruling`,
lane `W2_customer_generator`, value_stream `meter_to_cash`.

`idle` is the shelf's own convention and is what the ruling asked for — *"attach to the futures
shelf rather than jump the queue … draws as capacity allows"*. Per CLAUDE.md's epoch-gating rule
an idle atom is parked **for BUILD only** and is DISCOVER/FRAME-workable **now**, which is exactly
what deliverable 1 (a proposal) is. Nothing here waits on anything to be opened.

| Deliverable | Atom | Lane | Level | Depends on |
|---|---|---|---|---|
| 1. Proposed SIM population target with the probe's measured cost beside it | `PB1_population_target_and_its_price` | W2_customer_generator | 0 → **2** | `AO12_scale_probe_10k` |
| 2. Proposed opening book size + the acquisition path that produces it | `PB2_opening_book_won_not_assigned` | W2_customer_generator | 0 → **3** | `PB1_…` |
| 3. The growth curve as earned outcome, mechanisms named | `PB3_book_growth_as_earned_outcome` | W2_customer_generator | 0 → **3** | `PB2_…` |
| 4. Attachment to the futures/commitment-set shelf | **ALREADY COVERED** — `FUT1_attach_forward_hook` (level 2, landed) | H_harness | — | — |

### Exit criteria (as written into each atom's map text, not paraphrased here)

**PB1** — (a) a proposed target N with its reasoning; (b) per-stage cost *read from AO12's own
report artefact* (peak RSS, wall time, output size), never re-derived, never asserted; (c) an
affordability verdict **computed** from that record rather than judged, honouring the ruling's own
governor — if the probe says the scale is unaffordable on current storage, that is the answer;
(d) **fail-CLOSED on an unmeasured stage**: a stage the probe never reached is an unknown cost,
not a zero.

**PB2** — (a) a proposed opening size with an externally-anchored plausibility case, not a round
number; (b) the book **arrives by acquisition over the wall** — won, never assigned, never seeded
as a second cast beside the population; (c) the wall proven to hold, R15 both ways: a company-side
read of SIM population state must RED; (d) the opening book measured to be a genuine subset of the
drawn population.

**PB3** — (a) churn, acquisition cost and the competitor field named and wired (`W2_3_competitor_field`,
`B4_competitor_field`, `B10_competitor_switching_response` are the existing organs); (b) **the
falsifier is the exit test** — the ruling states the property directly, so a world configuration in
which the book *shrinks* must be demonstrated, not argued; (c) no step change that is not a modelled
acquisition or loss event; (d) belief-vs-truth gap on book size reported (the gap is the score).

## Why deliverable 4 is not a fourth atom

`FUT1_attach_forward_hook` is the **landed** mechanism (level 2) for the exact property deliverable
4 names: any finding or mint may declare which future atoms it advances, and each future atom
accretes a visible ledger derived from primary state. Minting a second atom to do that would be a
second way to do one thing. It is discharged concretely instead, two ways:

1. these three atoms are filed **on the shelf**, in the Epoch-2 commitment set, rather than
   scattered into whichever lane caught them — which is the accretion the deliverable asks for; and
2. the `**Advances:**` line at the head of this document, which the register reads from primary
   state and renders into `docs/design/FORWARD_ATTACHMENT_LEDGER.md`.

## What this mint deliberately did NOT do

- **It did not raise the population.** R13: the curriculum is the director's. The ruling authors the
  *direction* and hands the *numbers* to the worker — so PB1 proposes a value; no atom here changes
  `SE_DRAW_POPULATION` or any draw parameter as a side effect of being minted.
- **It did not mint the queryable-projections prerequisite.** The ruling names storage work as PB1's
  prerequisite, but `DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10.md` is its **own**
  unconsumed mint source still in the staging root, with its own WORK THIS CREATES block. Minting its
  atom from here would consume another ruling's block sideways and leave that doorbell pointing at
  work already done under a different name. PB1's map text names the dependency in prose; it is not a
  `depends_on` edge because the edge contract requires an existing atom id and there is not one yet.
- **It did not touch AO12.** The probe is unrun; PB1 depends on it and says so.

— Worker tick, 2026-08-11.
