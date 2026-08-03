# Cumulative HDD windows / thermal memory — citation record

Last updated: 2026-08-03
Research by: BUILD fork (`sim/weather_hdd.py::get_cumulative_hdd`), director instruction
2026-08-03, `docs/design/PREMISE_FABRIC_PHYSICS_DISCOVER.md` §4 item E.

---

## The gap this closes

`sim/weather_hdd.py::get_hdd()` is memoryless: HDD(D) is a function only of D's own mean
temperature. Real gas demand depends on the *recent history* of temperature, not just today's,
because of building thermal mass and (at system level) storage/linepack drawdown — a cold snap's
third day draws more gas than its first day at the identical temperature. This document is the
citation record for the decay shape used to fix that (`get_cumulative_hdd`), per the standing rule
that no window/coefficient in this codebase may be fabricated.

## Primary source

National Grid plc, **"Gas Demand Forecasting Methodology"** (2020, v1).

- URL fetched: `https://www.nationalgas.com/sites/default/files/documents/Gas%20Demand%20Forecasting%20Methodology%202020_v1.pdf`
- Fetch status: **fetched successfully** 2026-08-03 (binary PDF, 1.5MB; converted to text locally
  with `pdftotext -layout` for extraction — the WebFetch tool's own summarisation could not parse
  the compressed PDF content and returned no answer, so the raw text extraction is the actual
  evidence, quoted below with page/line references from that local extraction).
- This is National Grid's/National Gas's own published methodology document for GB gas demand
  forecasting (National Gas Transmission is the GB gas system operator; the Composite Weather
  Variable, CWV, is also referenced in the Uniform Network Code per this document, "Section H").

### What it says (quoted, `observed-with-evidence`)

Prose definition (document page 11, "Components of CWV"):

> "The effective temperature is half of yesterday's temperature added to half of today's actual
> temperature. Effective temperature takes into account the previous day's temperature due to
> consumer behaviour and perception of the weather."

Formal recursive formula (Appendix 1.1, local text-extraction line ~1064):

> `Et = 0.5 * Et-1 + 0.5 * ATt` (effective temperature)

where `Et` is effective temperature for gas-day `t`, `Et-1` is the previous gas-day's effective
temperature, and `ATt` is today's actual temperature. Unrolled, this is an infinite-lookback
exponentially-decaying weighted average of all past daily temperatures, with the weight of the
day `k` days back equal to `0.5 ** (k + 1)` of the total (i.e. roughly halving once per day of
lookback). The Composite Weather Variable (CWV) that National Grid's whole gas demand forecast is
regressed against is built from this effective temperature (plus wind chill and seasonal-normal
adjustments, not adopted here — see below).

## What was adopted vs. adapted (so the citation is not overclaimed)

**Adopted directly from the source:** the *shape* of the decay — a recursive/geometric weighting
that halves roughly once per day of lookback, and the underlying physical justification (consumer
behaviour / building response lags the current day's weather).

**NOT adopted / engineering adaptations, ours not National Grid's — flagged explicitly:**

1. **Applied to HDD, not raw temperature.** National Grid's formula smooths *temperature* before
   computing demand. `get_cumulative_hdd()` instead applies the same decay weighting directly to
   the already-computed daily HDD signal (HDD is a monotonic-under-clip transform of temperature
   in this codebase already, so this is a reasonable adaptation, but it is not literally National
   Grid's CWV pipeline — no wind chill, no seasonal-normal adjustment, no warm/cold weather
   cut-offs are reproduced here).
2. **Finite window, not infinite recursion.** The true `Et` recursion has infinite lookback. This
   codebase truncates it to `HDD_WINDOW_DAYS = 10` days (weight of the 10th day back,
   `0.5 ** 10 = 0.0009765625`, i.e. under 0.1% of the total mass) and renormalises the retained
   weights to sum to 1. The truncation depth (10 days) and the renormalisation are engineering
   choices made for testability and finite computation, not part of the cited methodology.

Both adaptations are also stated in the `sim/weather_hdd.py` module docstring, next to the code.

## R12 compliance note

The decay factor (0.5) and window depth (10 days) were fixed from this external source and its
own stated materiality threshold (<0.1% residual weight) — **before** looking at any company P&L
or margin output, and are not to be re-tuned if a future output metric looks implausible (R12: that
would be a tuning-to-benchmark violation; any implausibility should trigger R4 diagnosis of the
mechanism instead).
