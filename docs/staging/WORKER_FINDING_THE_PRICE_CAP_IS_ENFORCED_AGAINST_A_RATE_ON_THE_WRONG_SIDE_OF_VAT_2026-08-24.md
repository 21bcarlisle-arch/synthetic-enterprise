**Severity:** BLOCKING · **Lane:** W1_market_weather · **Atom:** `W3_1b` / `simulation/price_cap_enforcement.py`

# The domestic price cap is enforced against a rate on the wrong side of VAT, so the ceiling sits 5% above the law

## The defect, in one line

`simulation/hedged_settlement.py:319` clamps a domestic rate with

```python
_cap = binding_cap_unit_rate_gbp_per_mwh(commodity, current_date)
if _cap is not None:
    billed_rate_gbp_per_mwh = min(uncapped_rate_gbp_per_mwh, _cap)
```

`uncapped_rate_gbp_per_mwh` is **EXCLUDING VAT**. `_cap` is **INCLUDING VAT at 5%** — the
commons artefact says so in its own `basis` block, and
`simulation/price_cap_enforcement.binding_cap_unit_rate_gbp_per_mwh`'s docstring repeats it
verbatim under an R14 heading. The clamp therefore permits an ex-VAT rate equal to an inc-VAT
ceiling, which is a customer-facing rate of `cap × 1.05`. **The world's enforcement of the cap
is systematically loose by 5%, always in the supplier's favour.**

## Why this is not a permitted difference of reading

The regulation-commons doctrine deliberately lets the two lanes read the same published law
differently, and `company/pricing/ofgem_price_cap.py` says so at length: the carry-forward, the
`min(Ofgem, EPG)` selection, the segment filter and the annual blend are all *this company's*
reading, "allowed to be wrong". A supplier that misreads the cap is the point.

This is not that. **The world is not a reading of the law — it is the law.** When
`simulation/` enforces a ceiling, that ceiling is what a domestic customer could lawfully be
charged, and a 5% error there is not a supplier's mistake to be discovered; it is the market
being wrong. The company's identical error at
`company/pricing/renewal_rate_chain.py:265-276` (`min(unit_rate, cap)`, same two bases) is
comparatively harmless — it is a belief, and the world would clamp it. The world's is not.

## The basis, established rather than assumed

Both halves were checked on the live ledger rather than inferred from names.

**Our rate is ex-VAT.** On invoice 2412 (`PROS-2017-0038`, Jan 2024):
`consumption_kwh × unit_rate_p_per_kwh / 100 = 377.3 × 0.37843 = £142.79`, and
`commodity_amount_gbp = 142.78`. They are the same number, and `vat_gbp` is a separate line
equal to 5% of `(commodity + non_commodity + standing_charge)`. The printed rate is derived the
same way (`tools/generate_billing_ledger._printed_unit_rate` fits p/kWh against the
ex-VAT commodity amount), so the whole chain is ex-VAT.

**The cap is inc-VAT.** `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`:

```json
"basis": {"units": "GBP per MWh",
          "conversion": "Ofgem publishes p/kWh typical-household unit rates; p/kWh x 10 = GBP/MWh",
          "vat": "INCLUDING VAT at 5%",
          "standing_charge": "EXCLUDED - this is a unit-rate ceiling only (R14: the basis travels with the figure)"}
```

The artefact carries its basis. Two modules read the number and drop it.

## How it was found, and what is NOT claimed

Found while measuring something else: `PRICE_DIFFERENTIAL_PCT = 0.0` is hard-coded in three
places (`simulation/customer_events.py:38`, `simulation/run_phase4c_on_phase2b.py:106`,
`tools/run_phase4b_on_phase2b.py:33`), asserting that this company prices exactly at the market
average, and nothing has ever checked it. Measuring it against the published cap produced this
table — mean electricity unit rate actually invoiced, against the cap window containing 1 July
of each year:

    year   n     ours (ex-VAT)   cap (inc-VAT)
    2019   565      149.6            185.6
    2020   806      132.6            178.1
    2021   796      153.1            189.5
    2022   783      304.2            283.4
    2023   772      317.1            301.1
    2024   715      236.6            223.6
    2025   324      236.2            257.3

**No breach is claimed from this table and the arithmetic here is deliberately not carried
further.** Three reasons it cannot support one: it is an annual mean over a rate that moves
within the year; a term struck under the Oct-2021 window lawfully runs into 2022 at the
Oct-2021 ceiling, which is exactly the case
`company/pricing/ofgem_price_cap.py` was rewritten to handle; and the pre-2019 rows have no
published anchor at all. The table is what sent me to read the clamp. **The finding is the
basis mismatch in the code, which is true independently of how often it binds.**

## What is owed before this is fixed

The repair itself is two characters of arithmetic — compare like with like, either by grossing
the rate to inc-VAT or by de-VATing the ceiling — and it is not the work. The work is:

1. **Measure what it moves (R14).** This changes a published ceiling, so revenue, margin and
   every downstream figure move with it. The measurement must be one interpreter, one tree, one
   minute, with the variable swapped between two passes — the cross-tree method that produced
   two wrong answers for the settlement fold on 2026-08-24 is not to be repeated here.
2. **Count how often the clamp actually binds.** `cap_bound` is already stamped on every
   record, so this is a sum over one run, not an estimate. A loose ceiling that never binds
   moves nothing and is still worth fixing; a loose ceiling that binds often is a headline.
3. **Decide the company side separately and deliberately.** The recommendation is to fix ONLY
   the world and leave `renewal_rate_chain`'s reading as it is, because that turns a silent
   shared error into a visible belief-versus-truth gap — the company prices to a ceiling 5%
   above the real one and the world clamps it. That is the coupled triad working, and it is
   strictly more informative than making both sides right at once.
4. **Give it a control that can fail.** A rate and a ceiling compared without their bases is
   the class, not the instance: R14 already says every published financial figure carries its
   clock, and this is the same rule applied to VAT. The fix is a class fix or it will recur the
   next time somebody reads a published table into a comparison.

## Not covered by an existing class document

Checked against all five (`publish_gate_and_wedge`, `controls_that_cannot_fail`,
`measurements_that_mirror`, `uncommitted_and_orphaned_work`, `no_caller_and_never_runs`). This
is a domain-correctness defect in world physics and belongs to none of them.

— Worker seat, 2026-08-24 23:50. Filed rather than fixed on purpose: the fix moves published
figures and the measurement that must accompany it needs a run, which this session did not have
time to do properly. The arithmetic is one line; the honesty is the rest.
