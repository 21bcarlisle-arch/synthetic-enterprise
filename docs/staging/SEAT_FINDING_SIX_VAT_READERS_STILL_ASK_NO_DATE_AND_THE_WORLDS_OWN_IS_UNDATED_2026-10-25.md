**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Six VAT readers still ask no date, and the world's own reader is undated

*Delivery seat, 2026-10-25. Left over from landing the dated domestic-electricity zero rate
(SI 2026/987, 2026-10-01 to 2027-03-31) in `uk_vat_rates.json` `dated_exceptions`.*

`company.compliance.domain_invariants.vat_rate_for_segment` now takes `fuel=` and `on=`, and
honours the exception when it gets both. `renewal_rate_chain.cap_ceiling_ex_vat` passes both. The
other readers still call it with the segment alone, so they get 5% for a forward electricity day
in the window:

- `company/billing/invoice.py:51`: the bill's own VAT;
- `company/billing/dd_review.py:56,101`;
- `company/interfaces/dd_review_outcome.py:349,373`;
- `company/pricing/tariff_comparison.py:34,40`;
- `company/pricing/renewal_rate_chain.py:289` (`_stayer_default_ex_vat`);
- `company/billing/dual_fuel_bill.vat_rate_for_supply`, which reads `VAT_RATE_BY_MARKET` and has no
  date.

The world's reader is undated as well: `simulation/price_cap_enforcement.DOMESTIC_VAT_RATE` is
the reduced rate on every day. That makes it the world's half of the same rule, which is the VAT
shape CLAUDE.md names.

No current run is wrong, because 2016-2025 lies outside the window. Every forward year that
reaches 2026-10 is wrong. HMRC lets a bill that spans 1 Oct 2026 be split by the date the energy
was consumed, so a dated biller has to apportion the period, not just read one day.

A second edge to know about: `get_cap_unit_rate_for_date` carries the last published window
forward, and that window is Oct-Dec 2026, inclusive of 0%. So from 2027-04-01 the ex-VAT ceiling
drops by 1/1.05. The carried-forward figure has the wrong VAT basis for that date. The fix belongs
with the forward-years cap path, not with the reader.
