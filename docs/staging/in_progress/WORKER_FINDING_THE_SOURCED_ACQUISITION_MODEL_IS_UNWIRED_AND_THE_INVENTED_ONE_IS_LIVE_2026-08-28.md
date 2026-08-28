**Severity:** BLOCKING · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# Discovery: the repository already contains the researched acquisition model, and the live path spends the invented one

Director, 2026-08-28: *"COST_PER_ACQUISITION £150 resi and £400 SME, RESI_OFFER_COST_GBP £50, and
the quote cost derived from the acquisition cost, are all invented numbers with no source behind
them. And the retention one is wrong in kind, not just value."*

All of that is confirmed. **The larger finding is that the correct answer was already written down,
with sources, and reaches no code.**

Knowledge page: `site/data/knowledge_topics.json` →
`acquisition-and-retention-economics`, rendered at `/knowledge/acquisition-and-retention-economics/`.

---

## 1. There are two acquisition-cost models in this repository

| | **The researched one** | **The invented one** |
|---|---|---|
| Lives in | `saas/opex_ledger.py` | `saas/growth_mandate.py` |
| Domestic | £55 dual-fuel, £27.50 single, PCS commission | £150 flat |
| Business | **per-kWh trail**, 0.5–2.0p/kWh, billed over the term | £400 one-off |
| Source | `docs/market_research/B2_CATEGORY6_CAC_ANCHORS.md`, cited to CMA App. 8.3 and broker rate cards | none |
| Called by | **its own tests, and nothing else** | `company/interfaces/growth_desk.py` → the live campaign |

The researched module's own comment states the structural point exactly: *"I&C acquisition via a
broker is a real, ONGOING per-kWh commission — a structurally DIFFERENT cost shape (a trail
commission embedded in the unit rate for the life of the contract, not a one-off spend at signup) —
applied at billing time via `broker_commission_gbp()`, not at acquisition time."*

The research file goes further and makes the recommendation in terms: *"recommend modelling as an
ongoing per-kWh cost line (not a one-off acquisition cost), applied at billing time, rather than
forcing it into the same 'one-off CAC per new customer' shape as the residential channels."*

**That recommendation was written on 2026-07-10, implemented in `opex_ledger`, and never wired.**
`COST_PER_ACQUISITION["SME"] = 400.0` is the shape the research explicitly says not to use, and it
is the one the campaign spends.

## 2. The knowledge map already contradicted the constant

`docs/institutional/knowledge_map.md` line 71, at confidence **H**: *"PCW acquisition channel …
Commission: **£30-60/dual-fuel customer**."* The same map lists "cost per acquisition by channel" as
one of its top three gaps.

So the map simultaneously records a figure that contradicts the live constant and flags the area as
a gap — and neither reached the code. **This is the chain the director's P8 names: knowledge exists,
discovery never runs against it, so a constant gets chosen because a number was needed.**

## 3. The retention model is wrong in kind, and the law says so

`company/analytics/counterfactual_retention.py` carries **both** shapes at once:

- `RESI_OFFER_COST_GBP = 50.0` — a cash cost per offer, and
- `_TIER_CLASS_BY_DISCOUNT` — 3%, 5% and 8% **discounts**.

A discount already reduces revenue. Charging £50 beside it books the same intervention twice, once
correctly as foregone margin and once as a cash line that no supplier ever pays.

**And there is a licence condition on exactly this.** Ofgem's SLC 22B, the Ban on Acquisition-only
Tariffs, has since April 2022 prohibited offering a fixed-term deal to new customers that is not
also available to existing ones. Retention is possible only through a specific carve-out — in
Ofgem's words, *"The BAT's Market-wide Derogation … enables suppliers to offer bespoke,
retention-only deals to their existing customers when they are coming to the end of a fixed-term
deal."*

A retention offer is therefore **a tariff, offered at a defined contractual moment, permitted by a
named derogation**. It is a price. `RESI_OFFER_COST_GBP` models it as a payment, which is not a
smaller version of the right thing — it is a different thing.

**The sim spans the discontinuity and does not model it.** Before April 2022, acquisition-only deals
were lawful and were the most attractive prices in the market; that asymmetry is what drove the
switching volumes the world is calibrated on. From April 2022 they are banned. Our world applies one
set of retention physics across 2016–2025.

## 4. What else is invented in the same neighbourhood

- `ACQUISITION_WIN_RATE = {"resi": 0.20, "SME": 0.12}` — comment reads *"Lower than home-move rates
  … because we're competing blind"*, which is a rationale, not a source.
- `FIXED_COST_MONTHLY = 50.0` with the comment *"calibrate to match overhead ratio"* — an admitted
  placeholder. Ofgem's 2017 efficient operating-cost benchmark was **£78/customer/year electricity
  and £89 gas**; £50/month across a 15-account book is about £40 per account per year.
- `IC_OFFER_COST_GBP = 200.0`, `_RETENTION_EFFECTIVENESS = 0.20`,
  `ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT = 0.04` — no sources.

## 5. One near miss, recorded because it is the failure the page exists to prevent

A search summary offered "£90 per customer" as an Ofgem customer-acquisition benchmark. The source
(price cap EBIT consultation, May 2023) says at §4.24 that £90 is **depreciation and amortisation of
fixed assets**; §4.25 shares only the *six-year lifetime* with the CMA's acquisition-cost
amortisation. Publishing £90 as a CAC benchmark would have produced **an invented number with a real
citation attached** — worse than an invented number, because the citation stops anyone checking.

## 6. What the published record will not give us

The actual per-customer acquisition costs the six large suppliers reported to the CMA are **redacted**
in the published appendix — every figure that would settle it appears as an empty bracket. No
GB-energy-specific direct/brand-marketing CAC exists in any public source searched. So the honest
output is a **shape**, not a number, and the Knowledge page says so rather than picking a midpoint.

---

## The roadmap

**Ordered so that nothing is calibrated before it is understood. Not started — this document is the
discovery step, and the ordering is the deliverable.**

**R1 — Retire the invented table, wire the researched one.** Make `growth_desk` read
`opex_ledger.acquisition_cost_gbp()` and delete `COST_PER_ACQUISITION`. Domestic acquisition becomes
£55 dual-fuel. *Every published figure moves* — the campaign currently spends £112.50 a quote.
Cheapest step, largest effect, and it needs no new research.

**R2 — Give business acquisition its real shape.** Route SME/I&C through
`broker_commission_gbp()` at billing time. This deletes a cost the model currently charges at
signup and adds one that runs the length of the contract, so it changes the timing of the P&L and
not just its level.

**R3 — Make the retention offer a price.** Remove `RESI_OFFER_COST_GBP` and
`IC_OFFER_COST_GBP` as cash lines; let the discount tiers reduce revenue, which they already
compute. Assert the double-count is gone: a retained account should differ from a lost one in
revenue and not in operating costs.

**R4 — Model the BAT as a time-indexed licence condition.** From 2022-04-01, a fixed-term offer to a
new customer must be available to existing ones; retention-only deals are permitted by derogation at
end of fixed term. This belongs in `company/compliance/domain_invariants.py`, which already carries
`effective_from`/`effective_to`, alongside the regulation commons. It is the first thing on this list
that changes the *world* rather than the company, so it is R13 baseline work and must be argued on
fidelity.

**R5 — Amortise acquisition over a customer lifetime in the analytics, not the P&L.** The accounts
expense it as incurred (GAAP/IFRS, and our P&L is right to); the CMA's economic analysis amortises
over six years. Both are correct in their own frame and the model should be able to show both.

**R6 — Connect acquisition spend to collateral.** The CMA records the mechanism directly: growing
fast means acquisition costs up front, which *"weakened a firm's balance sheet … increasing the
perceived riskiness of the supplier and, therefore, the quantity of collateral that trading
counterparties required."* We have a growth campaign and we have `B6_collateral_cash_death_loop`, and
nothing joins them. This is the highest-value item and the one that needs the most other work first.

**Not on the roadmap, deliberately:** picking a direct/brand-marketing CAC. No published GB-energy
figure exists, and the honest response to that is to model the channels we can source and record
that we cannot source the third — not to average two guesses.

## Still live

---

## STATUS 2026-08-28 (delivery seat): R1 and R2 BUILT. R3-R6 still open — this is why the
## file sits in `in_progress/` and not in `done/`.
##
## (This heading said LANDED when written and nothing was committed — see the CORRECTION under
## the second STATUS heading below. Left in place, corrected in word only, because a wrong claim
## kept beside its correction is the evidence the mistake was found rather than tidied away.)

**R1 — DONE.** `COST_PER_ACQUISITION` is deleted from `saas/growth_mandate.py`, not re-pointed:
nothing can reach an unsourced figure through that name. `cost_per_acquisition_gbp(segment)`
replaces it, reading `saas/opex_ledger.acquisition_cost_gbp()`. Every call site moved —
`company/interfaces/growth_desk.py` (`decide_acquisition`, `replacement_cost_avoided_gbp`,
`quote_cost_gbp`), `acquisition_budget_gbp`, `growth_quote_budget`,
`saas/reporting/annual_report.py`.

One judgement was made that the roadmap did not specify, and it is visible in the code: the
residential rate is the **single-fuel £27.50, not the dual-fuel £55**. The acquisition event
fires per BILLING ACCOUNT (one fuel — `C1` and `C1g` are two accounts of one household), so the
dual-fuel commission charged per account would bill £110 for a household the source prices at
£55. £27.50 per account sums to exactly the sourced £55 for a dual-fuel household. The sourced
figure is the household's; the per-account rate is the arithmetic that lands it.

**R2 — DONE, and it is a real cost line and not a deletion.** `cost_per_acquisition_gbp` returns
a STRUCTURAL 0.0 for a broker-acquired segment, and the trail it replaces is charged:
`saas/opex_ledger.build_broker_commission_ledger_events()` accrues the sourced per-kWh rate on
billed volume, monthly, and it reaches the P&L through
`company/interfaces/growth_desk.broker_commission_schedule` →
`close_the_books(broker_commission_events=…)` → `saas.ledger.make_broker_commission_event` →
account **6300**, the same account the deleted one-off booked to. Booking it to the same account
is deliberate: the cost did not go away, it changed shape and timing, which is what R2 is for.
`test_business_pays_no_one_off_because_it_pays_a_trail` asserts BOTH halves so a later edit
cannot keep the zero and drop the trail.

**THE CONTROL** is `tests/saas/test_sourced_acquisition_costs.py`. A module-scope money constant
on this path must carry a citation in an attached comment, or the suite reds. R15: it carries its
own mutation proof (the deleted `{"resi": 150.0, "SME": 400.0}` restored verbatim must be
caught), a not-always-red control, a FAIL-OPEN guard that reds if the scan finds nothing, and a
TAUTOLOGY guard — the first draft passed `OFGEM_CAC_COST_GBP = 90.0`, which cites nothing and
merely says "Ofgem" in its name, so the detector now reads comment text only.

**The control found two more uncited constants while being written**, both now fixed:
`CAC_ONE_OFF_GBP_PER_SINGLE_FUEL_CUSTOMER` was leaning on the citation of the constant above it
(and it, not the dual-fuel rate, is what the campaign now spends), and
`BROKER_COMMISSION_GBP_PER_KWH` named its source but not the research file.

**`FIXED_COST_MONTHLY` is registered as KNOWN-UNSOURCED, not fixed.** §4 above is right that it is
a placeholder. Ofgem's 2017 benchmark (£78/customer/year electricity, £89 gas) is PER-CUSTOMER and
this is a company-wide figure, so substituting it also means deciding how overhead scales with the
book — a different cost line, and not one to smuggle into the acquisition repair. It sits in
`_KNOWN_UNSOURCED` in the control, where `test_the_debt_register_cannot_outlive_its_debt` forces
the entry out the moment it is cited or renamed, so the exemption cannot rot into a hole.

> **A WRONG CORRECTION, WITHDRAWN, AND KEPT HERE BECAUSE IT IS THE MORE USEFUL RECORD
> (2026-08-28, the landing tick).** Mid-turn I "corrected" this section to say the shipped figure
> was **2,089 quotes at £46,408.25**, on the strength of running
> `tests/simulation/test_net_new_acquisition.py` green in the working tree. That correction was
> wrong and is withdrawn. **£23,709 is right.**
>
> What I actually did was measure a tree that was not this lane's. The working tree also carries
> the unlanded **80-founder book** (`docs/design/FOUNDER_BOOK.yaml` + `founder_book()` in
> `simulation/live_population.py`), and the campaign's size depends on the opening book — more
> founders is more opening capital is more quotes the company can afford. Isolating it by running
> the campaign against the 13-founder roster this commit actually creates gives **1,066 quotes,
> £23,708.90**, all in-window. The +1,023 quotes are the founder lane's, not this one's.
>
> **The rule I broke is the one in CLAUDE.md: when a result moves and more than one thing changed,
> you cannot attribute it.** A green test is not a measurement of your own change — it is a
> measurement of whatever tree you ran it in, and a shared working tree is by default several
> lanes deep. The commit gate is what caught it, by running the tree the commit *would* create;
> the working tree could not have told me, and did not.

**WHAT THIS DID TO THE PUBLISHED FIGURES — the reader is owed this.** Campaign acquisition spend
falls from **£135,285 to £23,709** (measured at the 13-founder book this commit creates). Two
causes, and they are separable:

1. *The price.* £112.50 a quote → £20.63. This is R1 doing exactly what §R1 predicted.
2. *A post-period tail that the price change made material, and that is now fixed.* The campaign
   plans to a settlement horizon of 2026-01-01 while the run reports to 2025-06-07. At £112.50 it
   could only afford to reach 49 prospects dated past the reported end (4.4% of the campaign) and
   that read as a schedule edge; at £20.63 it reached 143 (11.8%), and
   `test_c_the_window_filter_excludes_nothing_at_the_shipped_configuration`'s non-vacuity bound
   fired. **The bound was right and the behaviour was wrong.** A prospect whose in-market date is
   after the last reported day has not come to market, so the supplier cannot have paid to quote
   them — the Point-in-Time Blindfold, applied to the quote. `plan_growth_campaign` now takes a
   `quote_cutoff` and the live campaign passes `REPORT_END`. The tail is **zero**, not smaller.
   The bound was NOT widened; widening it to admit 11.8% would have been R12 goal-seeking.

   The in-window POPULATION is unchanged at 1066 prospects — the same customers were always the
   in-window ones. What moved is the price of each quote, not who was quoted.

## STATUS 2026-08-28 (delivery seat) — director said GO; R1-R5 BUILT, R6 in hand

**CORRECTION, written beside the claim rather than over it (2026-08-28, worker tick).** The two
STATUS headings in this file — this one and the "R1 and R2 LANDED" one above — both said *LANDED*
while the work existed only in the working tree. Nothing was committed: `git diff HEAD` returned
the whole of R1-R5. Two earlier ticks built the work and exited without landing it, and each wrote
"LANDED" for what it had built. **A commit claim written in the working tree it describes is
self-refuting** — the tree is the one place that cannot witness it. The word is corrected to BUILT
above; the commit carrying this correction is the first one that makes any of it true, and it is
the reason the rows below can be read as history rather than intention.

*"Go — start at R1 and work the whole roadmap without coming back for permission on each step."*
R4 he called mine too, and I agree it is BASELINE not curriculum: a licence condition read from
published law, carrying its real commencement date, decided blind to our P&L. That is the fidelity
half of R13, which permits it rather than reserving it.

| | what landed | the number that moved |
|---|---|---|
| **R1** | `COST_PER_ACQUISITION` deleted; `growth_desk` reads `opex_ledger.acquisition_cost_gbp()` | campaign spend £135,285 -> **£23,709** (1,066 quotes, the 13-founder book this commit creates) |
| **R2** | business acquisition is a per-kWh broker trail at billing time | SME one-off -> **structural 0.0**; trail booked to 6300 over the term |
| **R3** | the retention offer is a PRICE: `discount x term revenue`, and **zero when the offer fails** | `RESI_OFFER_COST_GBP`/`IC_OFFER_COST_GBP` gone, not re-valued |
| **R4** | SLC 22B registered, time-indexed to 2022-04-01, with a check and an obligations row | **12 of 155** post-2022 acquisition offers breach it |
| **R5** | acquisition cost shown expensed AND amortised over the CMA's six years | **£10,693 of £24,431** is carried beyond the reported window |

**R1/R2 were begun by a worker tick that exited without committing**, leaving `quote_cost_gbp` and
the annual report pointing at the deleted table. That half was finished rather than restarted.

**R3 took a different route to the one predicted above**, and the prediction was the better guide:
the blocking sub-item named here — `expected_term_revenue_gbp` on the `no_offer_churn_log` rows —
is exactly what unblocked it. `run_phase2b.py` now carries it. Three consequences, and only the
first is arithmetic: the cost is a share of REVENUE not a flat sum; **an offer that fails costs
nothing**, because a discount only applies to a term the customer stays for; and a miss with no
term revenue is *unpriceable*, reported as such, never 0.0 — a free offer is the most attractive
thing on any page.

**R3's unfinished half, named so it is not lost.** `run_phase2b` computes the right quantity and
still books it in the wrong PLACE: `ret_cost` is a revenue reduction booked as a cash cost event,
and `unit_rate` is never actually reduced. The customer who was "given" a retention discount is
still billed the full rate. The P&L total is the same either way, but revenue and margin are both
overstated for every retained customer — and the household side of retention is invisible, which
matters directly to the mission's "saving them money". **R3b: make the discount reach the billed
rate and delete the cash line.** It is deep surgery in `run_phase2b`'s settlement path and is not
attempted here.

**The attribution for R1, because two variables changed.** Sourcing landed together with a quote
cutoff. The split is recoverable from figures the test file already carried: £135,285 whole
campaign at invented prices -> £129,285 with the 49 post-period quotes removed and prices still
invented -> £23,709 at the same 1,066-quote population with sourced prices. **Cutoff -£6,000
(4.4%); sourcing -£105,576 (78.0%).** Identical population across the second step, so it is a
price effect and not a mix effect.

**R4's measurement, which is the part worth reading.** Swept over the run's own 973 contracted
terms — each account's first term classified as an acquisition offer, every later one a renewal,
compared within (segment, commodity) on a monthly tariff window: **12 of 155** domestic acquisition
offers struck after 2022-04-01 were priced below the best rate any existing customer could have
obtained that month. The same shape occurs **5 times before commencement**, when it was lawful and
was what the whole GB market did. This is an exposure the company grew into on a fixed date. The
mechanism is that pricing here is per-customer (dynamic pricing, portfolio premium, margin
feedback) rather than a published tariff table — **a supplier with genuinely per-customer prices
has no table to demonstrate 22B compliance against**, and that is the deeper finding.

*Two defects in my own first probe, recorded because they are the class I keep hitting.* Grouping
offers by DAY compared transactions rather than tariffs, and renewals rarely fall on the same day
as an acquisition, so 120 of 155 "breaches" were really "no comparator that day". And the "PRE: 0
breaches" line I printed first was the time-indexed check **declining to look** before
commencement — a control going quiet and reading as a clean record.

## What would have caught the original defect — the director asked

`tests/architecture/test_a_cited_constant_has_a_caller.py`. **One leg**: a module-level money
constant whose own comment cites a file under `docs/` must be reachable from outside its defining
module by non-test code. Reachability is TRANSITIVE, and it has to be —
`CAC_ONE_OFF_GBP_PER_DUAL_FUEL_CUSTOMER` is named nowhere outside `opex_ledger` even now; it is the
accessor that has the caller.

Proven on the real thing, not a fixture: `test_it_fires_on_the_real_pre_r1_tree` materialises
commit `a1aefccaf` and asserts the walker names the £55 constant. On today's tree it names nothing.

**What it deliberately is NOT.** The first draft was a register of priced quantities — a YAML file
with 176 hand-authored rows, a duplicate-quantity leg and a ratchet. The director's instruction the
same hour retired it: *"prefer the smallest mechanism that can fail ... when in doubt, do the work
rather than build the thing that watches the work."* The register also needed a human to attempt a
registration before it caught anything, where the one leg fires with no input at all. And its debt
list carried four constants a weaker direct-name probe called unwired — **all four were wrong**,
reached through accessors that probe could not see.

It is the COMPLEMENT of `tests/saas/test_sourced_acquisition_costs.py`, not a duplicate: that one
catches the unsourced-and-live half on a named path, this one the sourced-and-unreached half
repo-wide. Two halves of one sentence, and no third control.

**STILL OPEN:**
- **R3b** — the discount must reach the billed rate (above).
- **R6** — acquisition spend -> collateral. The prize, and the next thing in hand.
- **R7 — `company/crm/acquisition_cost.py` is the same defect in a second place, and it is
  BIGGER than the one just fixed.** Found 2026-08-28 while writing this commit's REUSE block: the
  capability index returned it as the nearest neighbour to the new amortisation module. It holds
  `_CAC_BY_CHANNEL_YEAR`, a 5-channel x 10-year table — 50 numbers, including `broker` at
  £140-£200 and `pcw` at £45-£72 — under a docstring citing "Ofgem consumer awareness surveys,
  CMA energy review, industry benchmarks" collectively, with no line tying any single figure to
  any single source. That is a *bibliography*, not a citation, and it is precisely the shape the
  new control was built to refuse: `tests/saas/test_sourced_acquisition_costs.py::_CITATION`
  would match the word "CMA" in that docstring and pass the whole table. **The control's
  `_SCANNED` list does not include this file**, so this is not a hole the control has been given
  and failed to catch — it is a path the control has not been pointed at yet.
  NOT DONE HERE, deliberately: the index says 2 callers, so pointing `_SCANNED` at it turns a
  fresh red on a live path, and the fix is 50 sourcing decisions, not one. Doing that inside the
  landing commit for R1-R5 would be the "widen the scope until nothing lands" failure. R7 is:
  add the file to `_SCANNED`, and either source the table per channel-year or register it in
  `_KNOWN_UNSOURCED` with the debt named — the register exists for exactly this.
  It also means the honest reading of the control's reach is *two modules on the acquisition
  path*, not "the acquisition path", and the docstring should not be read as claiming more.

**Superseded status note (kept for the record):**
**NOT YET DONE, and each still needs its own decision:**
- **R3** — `RESI_OFFER_COST_GBP = 50.0` / `IC_OFFER_COST_GBP = 200.0` are still live in
  `company/analytics/counterfactual_retention.py` and still double-count against
  `_TIER_CLASS_BY_DISCOUNT`. `tools/run_live_decisions.py` imports both. This is why
  `counterfactual_retention.py` is deliberately NOT in the control's `_SCANNED` list — adding it
  before the repair would only assert a known defect. **R3's commit adds it, and that list is the
  record of which half is done.** The blocking sub-item: pricing the offer as foregone revenue
  needs `expected_term_revenue_gbp` on the `no_offer_churn_log` rows (`run_phase2b.py:1762` has
  `unit_rate` and `eac_missed` in scope), and the "unpriceable" case needs a stated basis rather
  than a fallback number.
- **R4** (BAT/SLC 22B as a time-indexed licence condition — R13 baseline work, must be argued on
  fidelity), **R5** (amortisation in analytics, not the P&L), **R6** (acquisition spend →
  collateral) — untouched.

**Also unaddressed and named here so it is not lost:** `ACQUISITION_WIN_RATE`,
`_RETENTION_EFFECTIVENESS` and `ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT` (§4) are still
sourceless. They are rates, not money, so the control's money-constant detector does not see them
— a deliberate scope line, not an oversight.
