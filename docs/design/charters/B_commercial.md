# B — Commercial: lane charter

**Dial reached 3 (SPIKE_WEEKEND charter flood, 2026-07-11)** — charter earned per the map's own
rule ("a lane earns its charter when its dial reaches 3+").

## Mission

Poesys must report and reconcile its commercial performance the way a real UK energy supplier's
FP&A function would: a margin bridge that attributes year-over-year change to named drivers, a
true cost-to-serve mechanism that neither hides the AI-native cost advantage nor invents a fake
one, a hedge book genuinely matched to the tariff book it backs, and — eventually — a market that
pushes back (a competitor field), so pricing decisions are a real strategic trade-off rather than
uncontested. Four sub-capabilities, four different maturity stages.

## Sub-capability tree

- **B1 (`B1_margin_bridge`)** — year-over-year margin bridge with residual reconciliation:
  attributes each year's margin change to named drivers (commodity/hedge P&L, policy/network
  pass-through, bad debt, opex), not just "margin went up/down."
- **B2 (`B2_opex_cost_to_serve`)** — the full opex/cost-to-serve taxonomy: TRUE third-party costs,
  TRUE AI-compute/oversight costs, and a BENCHMARK ledger carrying a lower-quartile incumbent
  labour proxy, plus fixed-cost floor, break-even, segment capital/ROCE, and concentration risk.
- **B3 (`B3_hedge_tariff_alignment`)** — cost locked when price is locked: a fixed-tariff
  customer's hedge fraction should be decided once at term start and held constant; deemed/SVT
  customers should carry no forward hedge (matching the cap's own wholesale-observation window).
- **B4 (`B4_competitor_field`)** — a simulated field of ~8 rival suppliers exerting real price
  ceiling / undercut pressure, so far entirely unbuilt (level 0).

## What L2/L3/L4 mean in this lane's terms

**B1 — margin bridge (level 2→3, currently idle, blocked):**
- L2 (current): a real bridge exists (`saas/reporting/margin_attribution.py`) with a driver set
  already validated against real FP&A convention (see references below) — but the report renders
  TWO adjacent margin-bridge sections whose gross-margin deltas disagree for the same year
  transition, unlabelled (`docs/design/MARGIN_REALISM_B1_DISCOVER_FINDING.md`).
- L3: the two-pipelines disagreement is resolved — one true bridge, or both clearly labelled and
  reconciled to each other.
- L4: the bridge's residual-reconciliation term is itself explained, not just netted away — every
  £ of year-over-year change is attributed to a named driver, none left as an unexplained residual.

**B2 — opex/cost-to-serve (level 3/3, AT TARGET, harden):**
- L2: the three-part split (true third-party, true AI-compute/oversight, benchmark ledger) exists
  with anchored figures, honestly estimate-flagged where no clean public rate was found.
- L3 (current): the full B2 taxonomy is built — categories (4) infrastructure, (5) governance
  floor, (6) fixed/stepped/variable classification + CAC, break-even analysis, segment
  capital/ROCE, gross-margin concentration — all live on the Supplier > Financial tab
  (`saas/opex_ledger.py`, `company/finance/segment_capital.py`, `company/risk/
  concentration_risk.py`). Two director-owned numbers (ROCE hurdle, concentration limit) are now
  set; the AI-compute metered sub-component stays £0 pending representative usage data (an honest,
  registered gap, not a silent default).
- L4 (harden target): the benchmark-ledger proxy (Ofgem's bundled operating-cost allowance) is
  replaced with segment-specific lower-quartile figures if a cleaner source is ever found; the
  AI-compute metered figure goes live once representative usage logging exists.

**B3 — hedge-tariff alignment (level 2/2, AT TARGET, harden):**
- L2 (current): fixed/pass-through tariffs decide their hedge fraction once at term start and hold
  it constant to renewal (verified against real 2020 data, not assumed); deemed tariffs correctly
  carry no forward hedge; flex tariffs re-hedge weekly at a rolling reference — all three
  differentiated per their own real commitment horizon (`docs/design/
  B3_HEDGE_TARIFF_ALIGNMENT_FINDING.md`).
- L3/L4 (not targeted — this atom's `level_target` is 2, i.e. deliberately capped here): one
  honest open exception remains at this level — a few I&C customers show hedge fraction changing
  within a calendar year, plausibly genuine multiple real-world 3-6-month contract renewals rather
  than a bug, flagged as resting on a plausible inference, not independently re-derived from the
  raw per-term log.

**B4 — competitor field (level 0→1, idle, genuinely unbuilt):**
- L1 (target for this atom): a minimal field exists — even a small number of named rival
  suppliers with their own published-style tariffs, enough to give Poesys's pricing decisions a
  real external reference point instead of an uncontested market.
- L2/L3/L4 (future, not this atom's current target): richer competitor behaviour (their own
  hedging/margin logic, reactive pricing, market-share dynamics) — registered as later work, not
  scoped here.

## Named best-practice references

- **Centrica plc's real segment reporting** — Centrica's 2025 Annual Report and 2025 Preliminary
  Results (https://www.centrica.com/media/ckfb0qxj/annual-report-and-accounts-2025-untagged.pdf,
  https://www.centrica.com/investors/results-reports-and-presentations/2025-preliminary-results/)
  confirm Centrica reports via named reportable segments (Retail split into Home/Business
  divisions, plus Optimisation and Infrastructure) — validates this project's own prior finding
  (`docs/design/MARGIN_REALISM_B1_DISCOVER_FINDING.md`) that real UK suppliers use sector-specific
  named segments/drivers rather than a generic price/volume/mix bridge.
- **Ofgem's own price-cap cost stack + EBIT allowance methodology** —
  https://www.ofgem.gov.uk/decision/amending-price-cap-methodology-earnings-interest-and-tax-ebit-allowance-decision
  and https://www.ofgem.gov.uk/decision/default-tariff-cap-decision-overview confirm the real,
  published cost-stack decomposition (wholesale, network, policy, operating costs, payment-method
  uplift) plus a hybrid EBIT allowance with fixed and cap-scaling components, built on a
  capital-employed/cost-of-capital (ROCE) assessment — directly grounds B2's fixed-floor,
  break-even, and segment-ROCE design in a real regulatory methodology, not an invented one.
- **Tranche-based forward hedging matched to a fixed-tariff book** — Catalyst Commercial Services
  (https://www.catalyst-commercial.co.uk/energy-hedging/) and Clearsight Energy
  (https://www.clearsightenergy.com/energy-hedging-explained/) both describe the real UK
  commercial-energy practice of buying volume in tranches across a contract period rather than
  fixing 100% at signing, and note hedging is generally only cost-effective above roughly
  £50k/year or 50MWh/year of consumption — a real-world scale threshold worth keeping in mind if
  B4's competitor field ever needs to model rival suppliers' own hedging behaviour.

## Lane roadmap

1. **B1 — genuinely blocked, do not start:** the two-pipelines root cause is Epoch-2 core
   (shares the reveal-over-time spine's sequencing per the closed
   `docs/review_gates/done/POINT_IN_TIME_SNAPSHOT_TIER1.md` gate) — sequencing belongs to the
   advisor's epoch framing, which has not landed as of this charter. `depends_on: [D2_three_clocks]`
   in `docs/design/maturity_map.yaml` is the durable record of this.
2. **B2 — AT TARGET, harden loop:** only the AI-compute metered sub-component remains open, and
   it is blocked on representative usage data existing, not a design question.
3. **B3 — AT TARGET, harden loop:** the one open I&C multi-term exception could be independently
   re-verified against the raw per-term log if it becomes relevant to a later phase; not urgent.
4. **B4 — genuinely unbuilt, not started this pass:** the next real action is a minimal DISCOVER/
   FRAME pass (even a handful of named rival tariffs) once this lane's own dial-weighted turn
   comes up — not scoped further in this charter (documents only, per SPIKE_WEEKEND item 4).

## Simplifications register

- B1's two-pipelines disagreement (annual_report.py's ledger-based vs years[]-based margin bridge
  sections) is a real, live legibility+consistency gap, not yet fixed — same root cause as the E2
  two-pipelines finding, sequencing shared with the epoch framing.
- B2's AI-compute metered cost is a documented, deliberate £0 (R12: no fudge factors) pending
  representative usage-log data — not a silent omission.
- B2's benchmark ledger uses Ofgem's bundled "Operating, debt and industry costs" allowance as a
  lower-quartile-incumbent proxy because it bundles opex + bad debt + industry charges together;
  a cleaner segment-specific figure was not found this session, netted of bad-debt/industry
  double-counting rather than used raw.
- B3's one honest open exception (I&C multi-term hedge-fraction blending within a calendar year)
  rests on a plausible inference (genuine 3-6-month contract renewals), not a full re-derivation
  from the raw per-term log — registered, not silently assumed away.
- B4 has zero code today — `evidence: []` in the maturity map is accurate, not an oversight.
