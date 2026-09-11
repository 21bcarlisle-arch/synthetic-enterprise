**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas) · **Class:** controls_that_cannot_fail

# RESULT — the origin rule matched the word "rate" and not the unit, so the director's own example was out of scope

Found by following one thread, not by an audit. The drawn Lane 0 item's premise was spent (below),
and the residue its own result doc named was step 3: *"`NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 5.0` has
no sourced origin ... exactly the shape the knowledge-first rule exists for."* Asking where that
constant came from produced a second question — **why did the control built for exactly this never
ask?**

## The defect

`tools/domain_constant_origins.DOMAIN_NAME` was `r"(RATE|PRICE|PROBABILITY|THRESHOLD|CAP)"`. It
matches the WORD "rate". It does not match a rate spelled in its units, and there is no cheaper way
to hide a price from it than to name it `..._GBP_PER_MWH`.

Measured across `company/` and `saas/`: **82 constants were out of scope on a spelling, 67 of them
declaring no origin at all** — a third again on top of the 188 the ratchet was guarding. The list
is entirely domain quantities; not one calendar fact or unit conversion is in it. Among them:

| constant | why it matters |
|---|---|
| `company/pricing/tariff_comparison.STANDING_CHARGE_SME_P_PER_DAY`, `..._IC_P_PER_DAY` | **the director's OWN cited example of the class** — *"a standing charge that matches neither fuel"*. Its `_RESI_` sibling one line above IS in scope and reads CITED, so the file looked covered. |
| `saas/tariff_pricing.TARGET_MARGIN_GBP_PER_MWH = 2.00` | the flat control arm that `price_cap_ebit_allowance.md` §D was written about, whose recorded basis is "none stated" |
| `company/market/network_charges._DUOS_PENCE_PER_KWH`, `_TNUOS_PENCE_PER_KWH` | published network charges carried as bare numbers |
| `company/crm/customer_profitability.NET_NEGATIVE_UPLIFT_GBP_PER_MWH` | the thread that started this |

**This is not the "control that cannot fail" shape one level up — it is a control aimed slightly to
the left of its target.** It could fail, it was mutation-proven, its own docstring records three of
four mutations surviving the first run and being repaired. Every one of those repairs was correct.
None of them asked whether the scan was pointed at the right population, and the population was
missing the director's own worked example.

## The repair

`DOMAIN_UNIT = re.compile(r"_GBP_PER_|_P_PER_|_PENCE_PER_|_PCT\b")` beside `DOMAIN_NAME`, joined by
`in_scope()`. A constant named `..._GBP_PER_MWH` is a price by construction and one named `..._PCT`
is a rate, threshold or probability by construction; neither can be anything else. **This is not
the wider net the file already declines** (COST, FEE, MARGIN, FACTOR, WEIGHT — 593 constants, a
re-baseline against a question nobody asked). It is the director's own five words found where they
were hiding.

Deliberately excluded: counting and conversion suffixes — `PERIODS_PER_DAY`, `_DAYS_PER_MONTH`,
`_HOURS_PER_DAY`, `KWH_PER_THERM`. 24 hours in a day is arithmetic, not a number anybody picked,
and demanding an origin for it would spend the rule's credibility on noise. That cut is the whole
difference between this and the wider net: money-per-unit and percent only.

## Baselines moved, and why each

| ratchet | was | now | reason |
|---|---|---|---|
| `UNSOURCED_DEBT_CEILING` | 197 | 255 | the measurement after widening |
| `UNSOURCED_DEBT_FLOOR` | 150 | 208 | same 47 of headroom; a floor left at 150 under a 255 ceiling lets `_classify` discharge a hundred constants silently |
| `CONSTANT_POPULATION_FLOOR` | 190 | 263 | same 33 of headroom; population went 214 → 296 |
| `DOMAIN_NAMED_POPULATION_FLOOR` | 235 | 319 | same 16; 296 literal + 39 promoted = 335 |

**The debt did not get worse — the scan got honest, and the ceiling rise records exactly that.**
The rule for the next one is written into the constant: **the ceiling may rise ONLY when the SCAN
widens, never when the CODE does.** Debt admitted by widening the subject already existed; debt
admitted by a new unsourced constant is the thing being refused. A commit raising it without
moving `DOMAIN_NAME`/`DOMAIN_UNIT` is landing the 256th picked number.

`promoted()` moved too (29 → 39), which is the check that matters: a widening that raised the
literals and left the promoted count flat would mean the new regex reaches only unfixed-shaped
constants, and would then score every proper repair of one as a deletion.

## What it caught on its first run — one concept, two homes

`_FLAT_TOLERANCE_PCT = 5.0` in **both** `company/market/portfolio_position.py` and
`company/trading/net_open_position_register.py`, immediately red on
`test_no_concept_is_declared_in_more_than_one_module`. Not a reconciliation — a rename, the
`MAX_CHURN_PROBABILITY` shape exactly:

* `portfolio_position` bands a **hedge ratio around 100%** → `_FLAT_HEDGE_RATIO_TOLERANCE_PCT`
* `net_open_position_register` bands **net open exposure around zero**, as rung one of a
  GREEN/AMBER/RED ladder → `_FLAT_NOP_EXPOSURE_PCT`

Different denominators, different zero points, same name and same value — "a reader who has met one
of them believes they know what the other means", which that file names as *worse* than an
unsourced constant. Neither name contains any of the five words, so nothing in the repository could
see it before today. **A control widened by one regex found a live collision within a second of
being run**, which is the strongest available evidence the widening was not cosmetic.

## The drawn premise, graded

The Lane 0 item's stated work — the one-line `_billing_account_id` fix at
`customer_profitability.py:156` — **was already landed** in `28ba48dd4`, its A/B pair run, and its
pre-registered prediction graded (and refuted) in writing beside the claim. `99b2700de` and
`eb7b26f27` carried the real cause and the measurement afterwards. The doorbell's own premise check
said as much: `40fe58f85` was already an ancestor of `origin/main`. **Spent, and not re-done.** The
work in this turn is the residue its result doc listed, which was still open.

Item 2 of that list (`profitability_uplift_log` never reaching the saved payload) landed in
`9419e2633` and is closed. Item 1 (writers 2 and 3 answering one question with two populations and
two thresholds) is still open and is a definition question — CLAUDE.md names that shape as this
project's most expensive recurring failure, and it should be settled before either count reaches a
page.
