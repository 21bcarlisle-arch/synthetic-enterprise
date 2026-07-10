# B3 (hedge-tariff alignment) DISCOVER finding: mostly already built, verified not assumed

**Status:** Real, verified DISCOVER-stage finding, mostly POSITIVE. No code changed. Filed from
the seventeenth dial-weighted maturity-map self-refill draw, 2026-07-10.

## What MARGIN_REALISM Step 4 asks for

*"Volatility fix: cost is locked when price is locked — hedging aligns to priced tariff
commitments (fixed books hedged at signing horizon; SVT hedged to the cap-observation logic).
Residual margin variance = shape/volume/churn only."*

## What was checked

Read `simulation/run_phase2b.py`'s term-processing branch (the actual per-term hedge/settlement
logic) and cross-checked against real per-year hedge-fraction data
(`docs/reports/run_output_latest.json`, `years[yr].hedge_fractions`, which carries both
`start_hf` and `avg_hf` per customer per year).

**Fixed/pass-through tariffs:** `decide_hedge_fraction()` (VaR-constrained) is called once per
TERM, using `_price_history_as_of(elec_records, term_start_str)` -- volatility as of the term's
own start, not re-evaluated mid-term. The resulting `hf` is then evolved by
`evolve_hedge_fraction()` only at the NEXT term's renewal. Real data confirms this: for the
large majority of customers (`C2, C4, C6, C7, C8, C9, C_IC4, C2g, C4g, C1_2` — checked directly
in the 2020 data), `start_hf` equals `avg_hf` exactly, meaning the hedge fraction held constant
for the entire term. This IS "hedged at signing horizon" — the mechanism already does what Step
4 asks for the fixed-tariff book.

**Deemed tariffs (out-of-contract/SVT-adjacent, Phase 40c):** `run_deemed_term()` uses
spot-price + a `deemed_premium` with explicitly **no forward hedge at all** — the customer's cost
tracks the spot market directly, matching the real-world fact that SVT/deemed pricing rides the
Ofgem cap's own wholesale-cost observation window rather than a per-customer forward-hedge book.
This is the correct alignment for this tariff type, not a gap.

**Flex tariffs (Phase 41a):** `run_flex_term()` re-hedges **weekly** at a 7-day rolling reference
price plus a markup — matching an indexed/short-reset tariff's own commitment horizon (a weekly
reset, not a 12-month fixed commitment), with no capital cost carried since the hedge is
continuously refreshed at reference.

**One real, honest exception found, not glossed over:** a handful of I&C customers
(`C_IC1, C_IC2, C_IC3`) show `start_hf != avg_hf` within a single calendar year (e.g. C_IC1:
0.85 -> 0.8756). This is consistent with I&C accounts having genuinely shorter/more frequent
contract renewal cycles than domestic 12-month fixes (a real-world pattern — I&C contracts are
often 3-6 months) — meaning multiple distinct terms, each independently "hedged at its own
signing," fall within one calendar year and blend in the year-level `avg_hf` figure. This was
NOT independently re-verified against the raw per-term hedge_evolution log this session (that
log isn't retained in the report-extracted `run_output_latest.json` shape) -- flagged as the one
piece of this finding resting on a plausible inference rather than a full re-derivation from the
raw per-term record.

## Verdict

The core architecture Step 4 asks for is already substantially in place: hedge decisions and
resets are already differentiated by tariff type and already track each type's own real-world
commitment horizon, not a one-size-fits-all mechanism. This is a genuine, verified positive
finding, not an assumption -- level bumped from 1 to 2 on this basis.

## What remains open (not this atom's scope)

Step 4's own closing clause -- "Residual margin variance = shape/volume/churn only" -- is a
claim about `B1_margin_bridge`'s own driver set once alignment holds, not something to verify or
build here. `B1` (per its own DISCOVER finding) already has no separate "hedge-tariff mismatch"
driver in its bridge, which is consistent with (though not proof of) this finding rather than
evidence against it. The one unverified exception above (I&C multi-term-per-year blending) would
be the natural next thing to check if this ever needs revisiting.
