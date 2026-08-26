**Severity:** BLOCKING · **Lane:** W1_market_weather · **Atom:** `W3_1b` / `simulation/price_cap_enforcement.py`

**Discharged:** `tests/simulation/test_price_cap_vat_basis.py::test_a_capped_deemed_rate_grossed_up_by_vat_equals_the_published_ceiling`,
`tests/simulation/test_price_cap_vat_basis.py::test_the_worlds_ceiling_cannot_be_obtained_without_naming_its_vat_basis`,
`tests/simulation/test_price_cap_vat_basis.py::test_the_two_accessors_differ_by_exactly_vat_and_agree_on_where_there_is_no_cap`,
`tests/simulation/test_price_cap_vat_basis.py::test_the_artefact_still_declares_the_basis_this_repair_assumes`,
`simulation/price_cap_enforcement.py` — the world now clamps an ex-VAT rate against an ex-VAT ceiling, the
number can no longer be obtained without naming its VAT basis, and all four controls were made to fire on
their own named mutations before being trusted.

# The domestic price cap is enforced against a rate on the wrong side of VAT, so the ceiling sits 5% above the law

---

## DISPOSITION, 2026-08-25 — repaired, measured, controlled

All four items this document said were owed were done before the repair was landed. Taken in the
order the document set them.

### The repair

The world's accessor split in two, and the basis-less name was DELETED rather than aliased:

| name | basis | caller |
|---|---|---|
| binding_cap_unit_rate_gbp_per_mwh_inc_vat | the published one, inc-VAT at 5% | the divergence diagnostic, which compares the two lanes' readings and needs the published basis on both sides |
| binding_cap_unit_rate_gbp_per_mwh_ex_vat | de-VATed, for comparison against a settled rate | the deemed clamp in the settlement module, which is the only place the ceiling binds |

The de-VATing is arithmetic on a number, not a second reading of the law: there is still exactly
one place in this lane where the published schedule is interpreted, and it is not the wrapper.
Deleting the old name is the part that matters. A back-compatibility alias would have left the
defect one autocomplete away, which is how it lasted this long — the docstring said "including VAT
at 5%" under an R14 heading the entire time, and being right in a docstring stopped nothing.

### 1. What it moves (R14), measured — one interpreter, one tree, two passes

The method the document demanded, and the one it named as not-to-be-repeated was avoided: a single
process, the real cached Elexon SSP series, a real PC1 domestic shape, the shipped settlement
function called twice, with the ONLY difference being which accessor the settlement module's own
name was bound to. Both passes settled the same 112,722 half-hours, 2019-01-01 to 2025-06-07.

The measurement ran in a throwaway git worktree, not the shared tree, because a live sim runner
reads the working tree every cycle and the pre-repair pass requires the tree to be briefly wrong.
The worktree was reaped in the same tick.

    year   periods   bound A   bound B   newly   rev A £   rev B £   Δrev £   Δrev %
    2019    17,513        35        53      18    208.66    208.55    -0.11   -0.05%
    2020    17,566        77        85       8    174.96    174.71    -0.25   -0.14%
    2021    17,517     3,120     3,396     276    452.51    444.84    -7.68   -1.70%
    2022    17,514     6,241     6,692     451    766.65    747.75   -18.90   -2.47%
    2023    17,512        45        64      19    477.26    476.93    -0.33   -0.07%
    2024    17,566        34        38       4    355.53    355.40    -0.13   -0.04%
    2025     7,534        32        41       9    193.53    193.40    -0.14   -0.07%
    ALL    112,722     9,584    10,369     785  2,629.11  2,601.58   -27.53   -1.05%

A = pre-repair (the loose ceiling), B = repaired. Net margin over the span moves from -£2,451.46
to -£2,478.99 on the same customer: the deemed book was already loss-making through the crisis,
and the correct ceiling makes it slightly more so.

**R13, stated rather than assumed.** This is a BASELINE world change made for one reason — the
enforced ceiling was not the published one — and it was decided from the law before the table
existed. The table is a diagnostic of what the correction moves, never its justification. It
happens to move margin DOWN, which is the direction that makes the point: the pre-repair error ran
in the supplier's favour every single time it bound.

### 2. How often the clamp actually binds — counted, not estimated

8.50% of domestic deemed half-hours over the span, rising to 17.8% in 2021 and 35.6% in 2022. This
is not a loose ceiling that never binds. Correcting it adds 785 newly-binding half-hours (+8.2%
more binding periods), 93% of them in 2021-22.

**What is NOT claimed.** The £ figures are one PC1-typical customer settled continuously across the
whole span — a rate-level result, not the book. The real deemed book is a subset of customer-days,
so the population effect is this shape scaled by actual deemed exposure, and that number lands on
the next full run rather than here. The percentages and the binding counts are the transferable
part; they depend on spot against the ceiling, not on whose meter it is.

### 3. The company side — left wrong on purpose

`company/pricing/renewal_rate_chain.py` still clamps its own ex-VAT rate against the inc-VAT
ceiling, and the company's cap module still exposes basis-less accessor names. Untouched,
following §3 above, and the naming ratchet is deliberately scoped to the world module so it does
not creep across the wall. The company now prices to a ceiling 5% above the real one and the world
clamps it: a silent shared error has become a visible belief-versus-truth gap, which is the
coupled triad doing the job it exists for. Making both sides right at once would have destroyed the
measurement.

### 4. The control, and the four mutations it was made to fail on

`tests/simulation/test_price_cap_vat_basis.py`, four controls, each run against its own named
defect in an isolated worktree and observed to fire:

| mutation | fires |
|---|---|
| restore the pre-repair clamp (the ex-VAT binding swapped back to inc-VAT) | the outcome control |
| add the basis-less back-compat alias to the world module | the naming ratchet |
| the ex-VAT accessor returns the inc-VAT number unchanged | the outcome control AND the accessor control |
| the ex-VAT accessor swallows a missing cap into 0.0 (fail-open shape) | the accessor control |
| the commons artefact is re-sourced on an ex-VAT basis, code unchanged | the basis-assumption control |

The instance is checked at the OUTCOME — the rate that came out of the shipped settlement function,
grossed up by VAT, against the published level read straight from the artefact by a path that does
not go through the module under test. Checking the accessor instead would have been tautological:
the accessor was never wrong.

The class control is the one that earns its place. The class is not "somebody divided by the wrong
number"; it is that a published figure carrying a basis in its metadata can be read into a
comparison that carries none, and the comparison looks fine. So the enforcement is that the number
has no basis-less name to reach for, checked by AST over the module rather than by asking the next
author to remember. That is R14 with VAT in the place of the settlement clock.

### Three tests that had encoded the defect as an expectation

`tests/simulation/test_hedged_settlement.py` asserted that a capped deemed rate EQUALS 208.0, 40.7,
283.4 — the published inc-VAT levels — and passed green for as long as the clamp has existed. They
now assert the de-VATed level, through a helper that spells 0.05 out rather than importing it from
the module under test, since importing it would make the expectation pass under any VAT rate at
all. This is worth naming separately: the suite was not silent about this defect by accident, it
was actively asserting it.

### Not closed by this, named rather than absorbed

1. **The population £ needs a run.** Item 1's table is rate-level. The next full run republishes
   revenue and margin for the real deemed book, and the figures move by roughly the shape above,
   weighted by deemed exposure. No published figure has been restated here.
2. **The world does not clamp FIXED-term rates at all.** Only the deemed path consults the ceiling.
   `run_deemed_term`'s own docstring claims the same clamp convention is applied to fixed terms
   elsewhere; it is not, and has not been since the company's renewal chain took ownership of that
   rate. Whether a domestic FIXED tariff should face the world's ceiling is a real fidelity
   question (in reality the default tariff cap reaches SVT/deemed, not fixed terms, so the current
   behaviour may well be right) — but the docstring asserting otherwise is wrong either way. Not
   fixed here: it is a separate question, and this document is about a basis mismatch.
3. **`PRICE_DIFFERENTIAL_PCT = 0.0`**, hard-coded in three places and asserting this company prices
   exactly at the market average, is still unchecked. It is what sent the previous seat to read the
   clamp, and it is still nobody's atom.

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
