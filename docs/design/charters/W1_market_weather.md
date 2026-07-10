# W1 — Market & Weather: lane charter

**Dial reached 4 (hot) 2026-07-10** (docs/design/MATURITY_MAP.md Section 8) — charter earned per
the map's own rule ("a lane earns its charter when its dial reaches 3+").

## Mission

Historical market/weather data must be revealed to the company exactly as a real trading desk
would have seen it, over time — never as a single frozen snapshot the company can see the whole
of on day one. "A real trading desk never sees tomorrow's settlement prices" (this lane's own
`real_world_twin`, `docs/design/maturity_map.yaml`).

## Shared architecture note — one spine, two faces

W1 (this lane) is the **company-side / pricing-decision face** of the reveal-over-time spine.
`D2_three_clocks` (lane D, its own charter: `docs/design/charters/D_billing_metering.md`) is the
**billing-side face** of the *same* architecture, not a separate one — per the director's own
placement correction closing `docs/review_gates/done/POINT_IN_TIME_SNAPSHOT_TIER1.md`: *"this is
Epoch-2 core... sibling to D2_three_clocks... one architecture not two."* Anything built here
must stay consistent with what D2 needs, and vice versa.

## Sub-capability tree

- **W1 (this atom, `W1_reveal_over_time`)** — point-in-time blindfold at the *source*, not just
  in company/ code: a structural as-of access layer, not a per-caller-remembered filter.
- **W1_2_generate_futures** — synthetic futures generation beyond the real 2016-2025 history
  window (depends on W1).
- **W2_2_population_draw** — per-run population generation (depends on W1, different lane's
  concern but rides the same spine's timing discipline).
- **G2_event_log_shared_with_spine** — the event log this charter's own bitemporal log
  generalises, shared with lane G (Data & Learning).

## What L2/L3/L4 mean in this lane's terms

- **L1 (current, pre-this-phase):** per-caller-trusted as-of filtering (`_price_history_as_of()`
  patched at its one known call site — a correct, minimal, reactive fix, not a structural one).
- **L2:** a real, tested, structural as-of access object (`PointInTimeView`,
  `company/interfaces/point_in_time_view.py`) exists and is proven correct in isolation — THIS
  PHASE's deliverable — but existing call sites have not yet migrated onto it.
- **L3:** every live company-side read of price/forward data that could plausibly see
  look-ahead-biased data goes through `PointInTimeView`, not a raw function call; the old
  per-caller-trusted pattern (`estimate_price_volatility()` et al.) is either migrated or proven
  safe by other means (e.g. already self-contained, like `calculate_sigma_recent()`).
- **L4:** the bitemporal axis is populated with REAL settlement-run restatement data (Elexon
  Initial/II/IF/SF timing), not just a single as-of date — i.e. the company can be shown to make
  a *provably different, correct* decision when fed a genuinely-revised historical figure, versus
  today's single-snapshot model where revision doesn't exist as a concept at all.

## Named best-practice references

(All independently sourced and cited in `docs/design/MARGIN_REALISM_W1_DISCOVER_FINDING.md` /
`docs/market_research/ASSUMPTIONS.md`, "W1 Reveal-Over-Time" — not invented for this charter.)

- **"Look-ahead bias"** — the standard quant-finance term (QuantConnect/LEAN glossary).
- **QuantConnect's "Time Frontier"** and **Zipline** — both architecturally prevent look-ahead
  bias via event-driven/streaming data delivery, the same shape as this spine's intent.
- **"Point-in-time join"** (Feast, the open-source ML feature store) and **"bitemporal history"**
  (Martin Fowler) — the specific pattern this phase's `BitemporalEventLog` implements: two time
  axes (valid time / transaction time), not one.
- **Marcos López de Prado, *Advances in Financial Machine Learning* (Wiley, 2018)** —
  `PurgedKFoldCV`'s "purging"/"embargo" concepts, a named engineering pattern for this exact
  problem class.
- **Elton, Gruber & Blake (1996)** — ~0.9%/year overstated mutual-fund returns from the sibling
  bias (survivorship bias), the real, quantified cost of getting this class of thing wrong.

## Lane roadmap

1. **DONE this phase:** `BitemporalEventLog` + `PointInTimeView` built and tested in isolation
   (29 tests, `tests/company/interfaces/test_bitemporal_event_log.py` +
   `test_point_in_time_view.py`), scoped to price/forward observables per the closed gate's own
   sizing. `.claude/hooks/block_point_in_time_read.py` live as the near-term detector
   (director-authorized 2026-07-10) for the exact known-dangerous shape while migration is
   incomplete.
2. **Next (not this phase):** migrate `company/trading/hedge_decision.py::
   estimate_price_volatility()`'s one call site onto `PointInTimeView` — the real, live target
   this whole object exists for. Full campaign sequencing (which call sites, what order) arrives
   via the advisor's epoch framing, per the director's own instruction this phase.
3. **Later:** weather/generation/demand observables through the same object, if a similar
   caller-trusted gap is found there (not yet audited — an honest, explicit scope limit, not an
   oversight).
4. **L4:** real Elexon settlement-run timing (Initial/II/IF/SF) populates the bitemporal axis for
   at least one real fact type (candidate: settled consumption, which genuinely gets revised).

## Simplifications register

- `PointInTimeView`'s bitemporal methods (`get_fact_as_known`/`get_history_as_known`) currently
  raise if constructed without a `bitemporal_log` — no live caller populates one yet; this is
  scaffolding proven correct in isolation, not yet load-bearing in a real decision path. Silent
  simplification would be an R10-class defect; this is registered, not silent.
- The bitemporal log's `superseded_by_run` field is informational only (not yet used to drive any
  real behaviour) — a placeholder for when real Elexon run-timing data is wired in (L4 above).
- No weather/generation/demand adapter exists yet for `PointInTimeView` — price/forward only, per
  the closed gate's own explicit scope limit.
