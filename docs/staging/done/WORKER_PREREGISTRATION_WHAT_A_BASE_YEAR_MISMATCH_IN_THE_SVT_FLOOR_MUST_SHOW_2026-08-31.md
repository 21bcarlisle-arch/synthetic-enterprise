# PRE-REGISTRATION — what a base-year mismatch in the SVT floor must show

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`
**Filed:** 2026-08-31, before any measurement below was run.
**Subject:** the repair form filed at `18a09617d` — `svt_inertia floor × market_switching_multiplier(year)`.

## Why this is being measured at all

`18a09617d` refused the whole-book anchor because `svt_inertia_hazard` has no parameter the market
could arrive through, and recorded a candidate repair: multiply the floor by
`market_switching_multiplier(year)`. That repair is filed, not implemented. Before another lane
implements it, one thing needs establishing that nobody has written down:

`SVT_INERTIA_ANNUAL_RECENT = 0.20` and `SVT_INERTIA_ANNUAL_LONG_STAYER = 0.10` are ABSOLUTE annual
rates. An absolute rate was measured in some market. `market_switching_multiplier` is a RATIO with
`MULTIPLIER_REFERENCE_YEAR = 2024`. Multiplying the two is only correct if the constants' own base
year IS 2024. `docs/market_research/svt_rates_active_passive_2016_2025.md` §4 states its basis
column as **"DESNZ: ~6M switches / ~28M accounts (2019–20)"**, which is not 2024.

If the base years differ, the filed repair applies a ratio to an already-levelled rate and the
level is wrong by the ratio between the two base years — the inverse of the failure class already
in this project's record, where normalising a published absolute rate destroys the only level
anyone could check.

## The predictions

**P1 — the error is a CONSTANT factor, not a year-shaped one.** The naive form
`floor × multiplier(y)` over the base-corrected form `floor × multiplier(y) / multiplier(base)`
is `multiplier(base)` and cancels the year entirely. Predict the ratio is identical in all ten
years 2016–2025 to within 1e-9, and equals `multiplier(base)` ≈ **1.376** for a 2019–20 base taken
as the mean of those two years' record rates.

**P2 — the naive form puts the floor ABOVE the level its own source inferred it at.** At 2020 the
source's inference window, the naive floor should read ≈ **0.286** against a source figure of 0.20:
the constant is being levelled up into a market it was already measured in.

**P3 — the base-corrected form returns the floor to its source figure inside the inference
window.** Predict the corrected recent-tenure floor averaged over 2019 and 2020 lands within
**0.005** of 0.20. This is the leg that would REFUTE the whole finding: if the corrected form does
not reproduce the source figure at the source's own years, then 2019–20 is not the base year and
the mismatch is not established.

**P4 — the correction moves the floor DOWN in every year, including 2024.** `multiplier(base) > 1`
for every year because 2024 is below the 2019–20 peak, so dividing by it reduces the floor
everywhere. Predict 10 of 10 years reduced, 2024 included — 2024 is the interesting one, because at
2024 the naive form looks like it does nothing at all (`multiplier = 1.00`) and that is exactly when
a base-year error is invisible.

**P5 — nothing in the tree implements the naive form yet.** Predict zero production call sites
compose `svt_inertia` with `market_switching_multiplier`, so this is a correction to a filed plan
and not a live defect. If this is REFUTED the severity rises: the mis-levelled floor would already
be in a capture.

## What would make this finding wrong

That §4's segment rows are not inferred against the 2019–20 all-customer row at all, but against
some other window the source does not name. §4 gives one basis year-range and gives it on the
all-customer row that the segment rows must average to; if a reader can establish a different
window for the segment rows specifically, P3 fails and this is withdrawn.

## Direction of the consequence, stated in advance

The naive form's own check at `18a09617d` — "all eight years under their target with headroom" —
is a check on an INFLATED floor, so it passes a fortiori under the correction. But the whole-book
total is pinned to the record and the two routes are therefore zero-sum: a floor 1.38x too high
pushes the renewal anchor the same amount too LOW, which is the near-total extinction of the
priceable route that `18a09617d` reported as `0.03` at 2023. So the correction RELIEVES the
pressure it found. I am recording that before measuring because it is the flattering direction and
I want it on the record that it was predicted rather than discovered.