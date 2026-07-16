# FRAME — W1_9_dsr_flex_markets — Demand-side response / flexibility markets

- **atom**: `W1_9_dsr_flex_markets` | lane `W1_market_weather` | epoch/dial 3
- **level_current**: 0 → **level_target**: 3 | **depends_on**: `W1_6_physics_price_signal`
- **stage**: BUILD-gated (`loop_stage: idle`). This is DISCOVER/FRAME work only — no BUILD code.

## 1. What this atom is & real-world grounding

Demand-side response (DSR) / flexibility is the set of markets and products through which a party is
paid to **shift, shed, or turn up** electricity demand (or behind-the-meter generation/storage) in
response to a system need. A real UK supplier participates either directly, or via an **aggregator /
Virtual Lead Party (VLP)** that pools many small sites into a dispatchable portfolio. The real venues:

- **Balancing Mechanism (BM)** — Elexon-settled, NESO-dispatched. Assets submit Bid-Offer data;
  NESO issues Bid-Offer Acceptances (BOAs) in-day to balance the system. Independent Aggregators
  reach the BM as VLPs under **P415**. Settlement is per-Settlement-Period (half-hourly) against
  imbalance/BOA volumes.
- **Capacity Market (CM)** — a *capacity* obligation (availability), not energy. DSR CMUs win
  agreements at auction (T-4 / T-1), must deliver during **Capacity Market Notices / stress events**,
  and are penalised for non-delivery. Revenue is £/kW/year availability, distinct from energy.
- **NESO Demand Flexibility Service (DFS)** — the consumer-facing turn-**down** service (evolved from
  the 2022/23 winter scheme); domestic + I&C consumers reduce vs a baseline in declared windows and
  are paid £/MWh. Now folded toward standardised **BM/ancillary** routes over time.
- **Ancillary / balancing services** — the dynamic frequency-response family (**Dynamic Containment /
  Moderation / Regulation**), Short-Term Operating Reserve successors, and local **DNO/DSO flexibility**
  (Piclo/LEO-style constraint-management tenders). Each has its own availability + utilisation pricing.

The economics: a supplier/aggregator earns **availability** payments (being ready) plus **utilisation**
payments (actually delivering, measured against a counterfactual **baseline**), net of the cost of the
demand change (customer incentive, lost production, battery cycling). Baseline methodology and delivery
measurement are where the money — and the disputes — live. *No specific prices/volumes are fabricated
here: any £/MWh, £/kW/yr, or MW figure is a **benchmark required (source: NESO/Elexon)**.*

## 2. COUPLED TRIAD (mandatory)

- **SIM adds (world depth):** a flex-need generating process on top of the W1_6 physics price signal —
  system stress/scarcity events, frequency deviations, local network constraints — each exposing a
  *dispatch signal* and a *clearing/utilisation price*, plus a **baseline-measurement physics** (true
  counterfactual demand) and a settlement lag. The SIM knows the true system need, the true baseline,
  and the true delivered reduction. Portfolio delivery is stochastic (rebound, customer non-response).
- **COMPANY discovers/copes (through the wall — may be wrong):** it sees only **observables** — published
  dispatch instructions, cleared prices, its own metered delivery vs its *own estimated* baseline, its own
  availability/utilisation settlement lines. It must *build a belief* about when flex is worth bidding,
  how much its portfolio will actually deliver, and what baseline it will be measured against. It cannot
  read the SIM's true baseline or true need. Over-promising, baseline-gaming that backfires, and
  mis-forecast delivery are all allowed failure modes.
- **HARNESS measures (belief-vs-truth GAP):** company's *expected* flex revenue & delivered MW vs SIM's
  *true* utilised MW and true settlement; baseline-estimate error (company baseline vs SIM true
  counterfactual); dispatch-follow accuracy; CM/DFS non-delivery penalty exposure. The **gap is the
  score**, reported per coupled pair (W1_9 SIM ↔ company flex-participation ↔ this harness) each digest.

## 3. Level decomposition (target L3)

- **L1** — SIM emits a single flex-dispatch signal + utilisation price derived from the W1_6 price
  signal (scarcity → call). Company can enrol a fixed flex capacity and be paid utilisation on a
  perfectly-delivered basis. Baseline = trivial. One venue (BM-like). Harness measures revenue only.
- **L2** — Add **availability vs utilisation** split, a **baseline methodology** with a true-vs-estimated
  gap, stochastic portfolio delivery (rebound/non-response), and a settlement lag (C-S3). Second venue
  (Capacity Market availability with stress-event delivery + non-delivery penalty). Harness measures the
  baseline-error and delivery-shortfall gaps.
- **L3** — Multiple concurrent venues (BM/VLP, CM, DFS-style turn-down, DNO/DSO local constraint) with
  **conflicting/overlapping calls** and stacking rules; company must *choose* where to offer scarce flex
  and manage double-counting exposure; curriculum-controlled event difficulty. Time-scale-invariant
  dispatch logic (C-S5). Full triad gap reported per venue.

## 4. Dependencies & sequencing

- `depends_on: W1_6_physics_price_signal` — flex value **is** the price/scarcity signal; without a
  physics-grounded price there is no honest dispatch trigger or utilisation price to bid against. Building
  flex on a placeholder price would bake in a fake economics.
- **BUILD-gated now** because W1_6 is upstream and not yet settled. **Unblocks BUILD when** W1_6 reaches
  the level that exposes a stable scarcity/price observable at the SIM/company seam.
- DISCOVER/FRAME (this artifact), red-team of baseline-gaming failure modes, and venue-taxonomy research
  are all available **now** and do not move BUILD level.

## 5. Open questions / director gates (R13 curriculum vs baseline)

- **Curriculum (director-owned):** flex-event frequency/severity, which venues are live in which world/era,
  penalty harshness for non-delivery — these are *difficulty dials*, named + versioned scenarios, never
  agent-tuned to make company results look good.
- **Baseline (fidelity-only):** the true system-need process, true-baseline physics, and settlement
  mechanics change only for reality-fidelity, decided blind to company P&L.
- **Gate:** which real venues to model at L3 and their sequence (BM-via-VLP first vs CM first?) — director
  call. **Gate:** is aggregator/VLP a distinct company role or a supplier capability? **Benchmark gate:**
  all £/MWh, £/kW/yr, MW, and baseline-window figures need NESO/Elexon sourcing before any L2+ claim.

## 6. Portability & scale-readiness lenses

- **Second market:** venues keyed by a typed *flexibility-product* abstraction (availability/utilisation/
  capacity), not hardcoded GB names → a second geography's flex market fits behind the same seam.
- **Second product:** flex-need + dispatch is an event type, not a new engine → behind-meter storage/EV/
  generation flex fit the same brain.
- **C-S1** dispatch/settlement events must be tolerated singly, late, out of order (no batch-completeness
  assumption). **C-S2** replaying a dispatch history reproduces identical settlement; flex draws from a
  **named seeded RNG substream** (delivery stochasticity can't shift other subsystems). **C-S3** dispatch
  call and settlement are *separate events in time* — never same-step resolution (matches BOA→settlement
  lag). **C-S4** flex positions/settlement persisted only via the append-only event log. **C-S5** L3 states
  whether dispatch logic is time-scale invariant; any HH-granularity assumption registered as a named
  simplification. **SIMPLICITY GUARD:** simplest constructs — no venue-adapter cathedrals.

## 7. Typed-flow seam note

DSR/flex participation crosses the SIM/company wall and MUST be a **typed, versioned message adapter**
exposing **observables only**: `FlexDispatchInstruction` (venue, window, direction, cleared price),
`FlexSettlementLine` (availability + utilisation, metered delivery, measured baseline), `FlexEnrolment`
(offer/bid submission). The company NEVER receives the SIM's true baseline or true system need — only what
a real party would see on a settlement statement. Async request/response per C-S3; forward-only, no direct
call into SIM internals.
