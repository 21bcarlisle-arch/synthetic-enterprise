**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# Three of the director's four examples, found mechanically — and every one of them is in code no reader reaches

**Found:** 2026-08-30, on the first run of the constants gate the director asked for
(`tests/architecture/test_a_domain_constant_carries_its_origin.py`). Found *mechanically*, which is
the point: nothing else in the repository could see any of it.

## The severity was BLOCKING for about ten minutes, and measuring took it down

I filed this BLOCKING on *"a published figure may be wrong"* — VAT charged at the domestic 5% rate
to a business account is money and is against the real rules. **Then I measured, which I should
have done before filing.** Both defects below have **zero live exposure**:

| | measured |
|---|---|
| callers of `company/billing/invoice.create_invoice` outside the module | **all of them are tests** |
| rows in `company/data/invoices.db` | **0** |
| is `company/portal/app.py` served? | **no** — the only uvicorn unit in the repo is `background.file_api` |
| does any `site/` feed read `compare_tariffs`? | **no** |

So no figure a reader can see is wrong today. The instruments are wrong; the exposure is nil.
**LATENT.** Recorded this way round rather than quietly re-filed, because "a published figure may be
wrong" was an inference and the four rows above are a measurement, and the standing instruction is
that those are different things.

---

## 1. One legal VAT rule, seven declarations, and the July repair is still live as a defect

The scanner's collision report:

```
VAT_RATE
    company/billing/invoice.py:19   = 0.05
    saas/non_commodity.py:101       = {'resi': 0.05, 'SME': 0.20, 'I&C': 0.20}
```

One name, two values, and not even the same *shape* — a scalar in one file, a per-segment table in
the other. Reading outward from the collision found five more: `VAT_RATE_DOMESTIC` and
`VAT_RATE_BUSINESS` in `company/pricing/tariff_comparison.py`, `VAT_RATE_BY_MARKET` and
`_sme_vat_rate(daily_kwh)` in `company/billing/dual_fuel_bill.py`, and
`consumption_implied_vat_rate()` in `company/compliance/domain_invariants.py`.

**And this exact defect was already found and fixed once, in one of them.**
`saas/non_commodity.py` carries the repair in its own comment: *"BILL_CORRECTNESS_ADDENDUM.md
Defect 1 (2026-07-08): 'I&C' was missing from this dict, so `vat_rate()`'s fallback silently charged
I&C accounts the domestic 5% rate instead of the legally-required 20% business rate."* Seven weeks
later `company/billing/invoice.py` computes `vat = subtotal * 0.05` for every account of every
segment, under a comment reading "5% VAT on domestic energy (UK reduced rate)".

**The July repair fixed the instance and left the class.** The fallback that caused it is still
there — `VAT_RATE.get(segment, VAT_RATE["resi"])` — so any segment not in the dict still gets 5%.
And the control written to guard it, `test_vat_rate_never_silently_defaults_a_business_segment`,
**enumerates the segments it knows** and asserts their values, so it cannot fail on the thing its
own name promises: an *unknown* segment silently billed at the domestic rate.

**The most correct implementation is the least reachable.** UK VAT on business energy drops to the
5% domestic rate below a de minimis threshold. `_sme_vat_rate(daily_kwh)` models that; every
segment-keyed implementation *cannot express it at all*, because a low-usage SME is a business by
segment and domestic by law. So the "correct" per-segment table is itself wrong for a real class of
account. Meanwhile `saas.non_commodity.vat_rate()` — the one with the documented repair — has **no
live caller anywhere outside its own module**.

## 2. The standing charge that matches neither fuel, and it is the dual-fuel sum

The director's third named example, found in the same sweep:

```python
# company/pricing/tariff_comparison.py
STANDING_CHARGE_RESI_P_PER_DAY = 53.0   # Ofgem average 2024 (published)
```

The fuel-aware authority, `saas.non_commodity.STANDING_CHARGE_GBP_PER_DAY`, says:

| | resi | SME |
|---|---|---|
| electricity | **27.0 p/day** | 55.0 |
| gas | **25.0 p/day** | 40.0 |

**53.0 is not either of them — it is very nearly their sum (52.0).** A dual-fuel daily total is
being used as a single-fuel standing charge, and `compare_tariffs` is unambiguously single-fuel: it
calls `sim_interface.get_forward_price("electricity", ...)` and nothing else. Every option it
returns therefore overstates the standing charge by ~26 p/day, about **£95 a year**.

Because the error is a constant added to all three options equally, the **ranking is unaffected and
the annual costs are all wrong** — which is the version that survives casual checking longest. The
comment claims a published Ofgem 2024 average, and it matches neither of the two published averages
nor the repository's own commons.

## What is owed, and why none of it was done tonight

**None of this is a rename, and repairing it as one would be the behaviour this finding is about.**
Choosing the VAT authority means choosing which of seven implementations is right, and the honest
answer is probably *none of them* — the rule is consumption-conditional, so a segment-keyed constant
cannot be correct at any value. That is a knowledge-layer question, and the director's first
standing change says a number I need is a question to research, never a value to pick. Picking one
tonight is precisely what is forbidden.

**Owed, in order:**

1. Establish the VAT rule from the published record — VAT Notice 701/19, the de minimis thresholds
   and whether they moved across 2016–2025 — and file it in the **commons**, not in a module.
2. Establish the published standing charges per fuel per year, likewise. `docs/domain_artefact_library/regulatory/`
   holds no standing-charge artefact today; `ofgem_default_tariff_cap_windows.json` explicitly
   excludes it (*"EXCLUDED — this is a unit-rate ceiling only"*).
3. **One authority each**, consumption-conditional for VAT and fuel-keyed for standing charge, that
   the others call. Delete, do not wrap.
4. `vat_rate()` and `standing_charge_rate()` **refuse an unknown segment or fuel** rather than
   defaulting to domestic/electricity. Refusing to bill is safe; under-billing a business is a legal
   error. Both currently carry the same silent-fallback shape and both have a control keyed to the
   segments it already knows.
5. Then decide whether `company/billing/invoice.py` and `company/pricing/tariff_comparison.py`
   should exist at all. **Both are unreached.** A wrong module nobody calls is cheaper to delete
   than to correct, and this repository has already paid once for a correct module sitting unwired
   beside an incorrect live one (the £55/£150 CAC pair). Here *neither* is live, which is a
   different and easier problem.

## The second collision, recorded rather than fixed

```
MAX_CHURN_PROBABILITY
    company/crm/churn_model.py:77 = 1.0
    saas/churn_model.py:37        = 0.95
```

The director's second named example. The two sit on opposite sides of the SIM/company seam and
nothing at a call site says which it got; a cap of 1.0 and a cap of 0.95 are different claims about
whether any customer is ever certain to leave. Left for the same reason: which is right is a
question about the model, not about the name.

Both surviving collisions are held in
`test_a_domain_constant_carries_its_origin.KNOWN_NAME_COLLISIONS`, which is an **exact set** — so
fixing either **reds the gate** until its entry is removed, and that removal is the record the work
happened. A count could not have asked for that.
