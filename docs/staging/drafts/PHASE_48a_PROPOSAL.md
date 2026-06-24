# Phase 48a — Forward Curve Term-Length Premium for I&C Contracts

**Status:** Draft proposal — REVIEW_GATE (1h active-hours gate).
**Proposed by:** Claude Code autonomous session, 2026-06-24

---

## Context

Rich flagged: "Don't we need an actual forward curve? This detail matters for I&C."

The current company forward curve uses an EWMA of past spot prices × (1 + 8% risk premium).
For all contract durations, the risk premium is flat — a 1-year I&C contract and a 2-year I&C
contract get priced at the same forward rate.

In reality, forward prices are term-dependent:
- NBP/EPEX CAL+1 (12-month forward) trades above the spot average
- CAL+2 (24-month forward) trades at an additional premium above CAL+1
- The company locks in at the forward curve for the contract duration — a 2-year
  deal exposes it to 2 years of price risk, which commands a higher premium

This is why I&C customers on 2-year fixed terms expect/pay more than those on 1-year.

---

## Proposed Change

Add a **contract duration premium** to `company/pricing/tariff_engine.py`:

```python
TERM_LENGTH_PREMIUM_PCT_PER_YEAR: float = 0.02  # 2% per year beyond the first
```

Applied in `CompanyForwardCurveEngine.get_forward_price()`:
```
forward_price = ewma_spot × seasonal × (1 + risk_premium + term_length_premium)
term_length_premium = max(0, (term_years - 1.0)) × TERM_LENGTH_PREMIUM_PCT_PER_YEAR
```

Where `term_years` is computed from the term length (12 months = 1.0, 24 months = 2.0).

### Example (I&C, 2022 crisis)

- 1-year contract: EWMA = £280/MWh × 1.08 = £302/MWh
- 2-year contract: EWMA = £280/MWh × (1.08 + 0.02) = £308/MWh
- 3-year contract: EWMA = £280/MWh × (1.08 + 0.04) = £314/MWh

### Epistemic status

The company observes forward prices from its own trading desk (which tracks NBP/EPEX).
The term-length premium is derived from the observable shape of the forward curve —
not from SIM internals. This passes the epistemic barrier.

---

## Files

- `company/pricing/tariff_engine.py`: add `TERM_LENGTH_PREMIUM_PCT_PER_YEAR` constant;
  modify `get_forward_price()` to accept `term_months: int = 12` parameter; apply premium
- `simulation/run_phase2b.py`: pass `term_months` to `get_forward_price()` at tariff signing
- `simulation/run_segments.py`: same — pass term_months at tariff signing
- `tests/company/pricing/test_phase48a_term_premium.py`: 6-8 tests

---

## Expected outputs

- 2-year I&C contracts priced ~2% above 1-year I&C
- Longer contract duration = higher locked-in price = better hedge against rising markets
- Annual report and basis risk logs reflect term-length premium
- Minimal impact on resi (all 12-month contracts)

---

## Fidelity delta

UK energy I&C contracts: 1-year fixed is standard; 2-3 year available at a premium.
Bloomberg/Refinitiv CAL+2 spreads historically 1-4% above CAL+1. The SIM now
reflects the observable forward curve term structure that any real energy trading
desk would use when pricing multi-year I&C deals.

---

## Gate timing

Using new gate protocol: 1h during active hours (06:00-22:00 BST).
Gate set: ~10:00 UTC 2026-06-24. Auto-proceed at ~11:00 UTC if no redirect.
