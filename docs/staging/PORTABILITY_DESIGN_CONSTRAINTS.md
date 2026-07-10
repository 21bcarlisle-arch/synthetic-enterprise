# PORTABILITY_DESIGN_CONSTRAINTS.md

**Status:** Director-approved standing design constraints. Staged standalone by director decision (2026-07-10), ahead of the Epoch-2 framing batch. Effective immediately as design constraints; creates no new build work. Governance tier: Tier 3 (novel constraint registration, no scope change) — 4h opt-out applies; ambiguity classifies up.

**Place in the epoch arc:** This does not change the epoch arc or any current sequencing. It registers standing constraints on how Epoch 2 (Value Cycle) and Epoch 3 (Walled Interfaces) work is shaped. Rationale: the director has confirmed the long-range destination is a single multi-segment, multi-geography, multi-product retail supplier running one integrated self-learning suite. Nothing multi-market or multi-product is to be built now. These constraints exist so that when a second market or second product arrives (post-Epoch-3 at earliest), it is a data-and-adapter exercise, not a refactor.

## Two standing design lenses

Apply as explicit review questions at phase design and phase close:

- **Epoch 3 lens:** *Would a second market fit behind this seam?* A new market must be enterable by supplying new boundary implementations, new anchor values, and new obligation entries — with no change to the company brain.
- **Epoch 2 lens:** *Would a second product fit inside this brain?* A new product line (e.g. broadband, white-label insurance, boiler cover) must be expressible as new event types with its own revenue schedule, cost structure, tax treatment, fulfilment obligations, and customer-behaviour effects — with no new billing engine. Note: energy is the hardest case (wholesale risk, three clocks converging over ~14 months); most bundled products are degenerate cases where clocks collapse.

## Seven constraints

Requirements, not designs — solution architecture is yours:

1. Boundary crossings are typed by *function* (settlement feed, meter-read channel, regulatory publication, tax authority…), never by counterparty. Elexon, DCC, Ofgem, HMRC are the GB implementations of universal roles.
2. The domain-invariants and anchor libraries must structurally separate invariant *classes* (universal) from anchor *values* (jurisdiction- and product-scoped data). Test: loading a second market's values must require no schema or code change.
3. No clock speed or settlement granularity may be structural. GB's 48 half-hourly periods, the ~14-month reconciliation window, and DD seasonality conventions are market parameters, not constants.
4. No monetary amount or tax treatment may be hardcoded. Tax is data, resolved per product line per jurisdiction (energy VAT vs insurance IPT is the near-term concrete case: one bill, multiple tax regimes).
5. Customer-pillar anchor provenance is recorded per jurisdiction (ONS/EHS/DESNZ are GB sources, not *the* sources).
6. *Product* becomes a first-class dimension wherever *fuel* is one today — bill lines, events, invariants, archetype propensities. Dual-fuel already forced this halfway; the requirement is that generalising fuel→product is never blocked by structure.
7. The obligations register is keyed by regulatory regime, not implicitly Ofgem. Harm-tiering is universal; SLC14 is a GB instance. (R10 note: cross-product mis-selling — e.g. boiler cover sold to a customer who cannot benefit — is a domain-absurd-but-internally-consistent class; the invariant library gains a product dimension.)

## Non-negotiables

No second market or second product is built, stubbed, or scaffolded now. No existing phase scope changes. Where honouring a constraint in already-built code would require rework, log it as a portability debt item rather than fixing it opportunistically — the director will rank remediation at a phase boundary.
