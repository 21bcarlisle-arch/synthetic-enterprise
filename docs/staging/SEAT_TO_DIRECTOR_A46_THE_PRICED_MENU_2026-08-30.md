**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# The book-depth menu you asked for, priced — and the column that made me change my recommendation

You ruled on 2026-08-28 that book depth is curriculum and therefore yours, *"flagged, not
delegated"*, and named the settlement ceiling your top item at 05:55Z on 2026-08-29. **The pricing
was mine and it is done. The decision is yours and it is below with a recommendation attached.**

Full working: `docs/design/A46_THE_PRICED_MENU_2026-08-30.md`.

**Correction, and you should read it before the menu.** An earlier version of this letter told you
the measurement was *"a clean two-point slope taken with the publisher stood down"*. **It is not a
slope.** `docs/observability/settlement_ceiling_slope_20260829.json` says, in its own words:

> `"decidable": false` — *"1 CLEAN point(s); a slope needs at least two. A contaminated point is
> still a valid single observation and is reported above — it is only barred from the slope."*

The 2,000-customer-year point carries `campaign_record_agrees: false` — *"another process wrote
book_growth_campaign.json during this run (it said 1195.4), so this point's committed customer-years
are not its own"*. The hold covered our own producer, which is what contaminated the *previous*
attempt; it did not cover whatever wrote that file. **So we have one clean point and one
contaminated observation, and the marginal-cost column below says so rather than drawing a line
through them.** That is a result about this machine and it belongs in the table.

It does not change the recommendation, because the recommendation never rested on the slope.

---

## The menu

**M = measured on this box. P = projected arithmetic, no run needed.**

| ceiling (customer-years) | run wall clock | peak memory | accounts booked | marginal cost of the next customer-year | accounts the method could price |
|---|---|---|---|---|---|
| **1,200** — what we run today | **928.6 s** (M, clean) | **3,952.4 MB** (M, clean) | **90** (M) | *one clean point; no slope* | **0** (M) |
| **2,000** | 2,097.6 s (M, **contaminated**) | 6,784.5 MB (M, **contaminated**) | 261 (M, contaminated) | *one clean point; no slope* | **0** (M) |
| **3,136.5** — the whole funnel | — | — | 505 (P) | *one clean point; no slope* | **0** (M) |
| anything **above 3,136.5** | — | — | 505 (P) — **buys nothing more** | n/a | **0** (M) |

The 2,000 row is **one contaminated observation, deliberately barred from the slope** — it is shown
because it is still a real reading of wall clock and memory, but nothing is differenced against it.

The bottom two rows cost nothing to know: the founding book is 778.1 customer-years and settling
every one of the 505 accounts the campaign won costs 2,358.4 more, so at **3,136.5** the sample rate
reaches 1.0 and there is nothing left to buy. **A ceiling above 3,136.5 is spending on nothing.**

*The interval half of the menu — what a 25/30/60/120/240-minute publish cycle affords — came back
`not decidable` at every row, for the same one-clean-point reason. It is printed in full at
`docs/design/A46_THE_PRICED_MENU_2026-08-30.md` §2b rather than interpolated here.*

## The column I did not expect, and it is the whole answer

**At every interval on that menu, the number of accounts the method could actually price is ZERO.**

Not small — zero, and for a reason no ceiling reaches. A household the company *won* carries a
`tariff_type` of `None`; the pricing arm admits only `fixed` and `pass_through`. The nine founders
pass only because their record omits the field entirely. **The method has never priced a customer
this company won**, and no book size changes what that guard reads.

So the thing the ceiling was supposed to buy — evidence that the method works — it cannot buy.
Today that evidence is **six decisions across five accounts**, and the confidence interval a random
signal produces on six decisions runs from 0.13 to 0.87. Booking four hundred more accounts leaves
it at six.

## What I recommend, and what I am doing unless you say otherwise

**Leave the publish interval alone and leave the ceiling at 1,200.** I am proceeding on that basis;
it reverses in one constant.

Buying a bigger ceiling spends the one budget that is genuinely scarce here — how often this company
reports to you — on precision for comparisons that already exist, while the comparison that decides
whether any of this is worth anything does not move at all.

**The ruling I would ask you for next is a different one.** The world has no standard-variable
product, so a won household's tariff was never *decided* rather than forgotten. Giving the drawn
book that product — from the published domestic fixed/SVT split — is what opens the gate, and it is
a baseline-world change, which puts it on your side of the wall and not mine. It is written up and
costed in `docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` (settled 2026-08-28 as what
is *owed*, not yet as what is *authorised*). **It also makes our in-scope surface smaller as a share
of the book, not bigger** — which is how you can tell it is a fidelity change and not one I want
because it would enlarge my own experiment.

One caveat against my own case, because it cuts the other way: opening that gate reaches 662 of the
1,349 renewals the arm did not price. The other **687 (51%) are deliberate scope** — term 0 has no
prior term to price against, and the arm has never been fitted to gas. The gate is the larger single
constraint but it is not the only one, and a ceiling bought as if it were would over-buy.

## Where I was wrong

I filed four predictions before the run, and they are marked beside themselves in
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_CLEAN_CEILING_SLOPE_MUST_SHOW_2026-08-29.md`.

The one worth your time is **prediction 4**, which said the honest deliverable would be *"a table
mapping chosen interval → affordable ceiling, put in front of the director."* That was right in form
and complacent in substance: a table of intervals and ceilings is exactly the artefact that would
have let you spend the cadence for nothing. What turned it into a decision was a column I had not
thought to put in it, supplied by a different finding that landed the same night.

**A menu is only priced if it carries the column that does not move.**
