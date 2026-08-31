# What the end-to-end journey walk found — one household, eight joins, three things nobody was holding

**Canon:** `docs/staging/DIRECTOR_CANON_END_TO_END_AND_ONTOLOGY_2026-08-31.md`, work items 1 and 2.
**The walk:** `tests/architecture/test_the_journey_walk.py`.
**Subject:** `SYN-2016-009` — 109 bills, 109 meter reads, 7 demand estimations and a departure. The
longest complete chain in the book, chosen by measuring all 43 households that carry every stage.

The canon asked for one walk that genuinely asserts joins rather than a suite that asserts nothing,
and for a statement of what it found. This is that statement.

---

## The joins that hold

| join | what it asserts |
|---|---|
| **meter → bill** | the volume measured is the volume billed, on every period with both |
| **bill composition** | commodity + non-commodity + standing charge + VAT **+ catch-up** = total |
| **standing charge** | daily rate × days in period = the charge |
| **VAT → the law** | the rate a real bill implies is a rate the *published record* carries |
| **belief → truth** | the company's EAC and the world's, and the error between them, count one account |
| **departure** | the churned list and the event logs tell one story — **across both routes** |

---

## Three things the walk found, and only one of them is a defect

### 1. A bill has FIVE terms, not four — and the rule was already written down where I did not look

The composition leg failed on its first run, on two of C1's twenty-seven bills, both by about
**£6.24**. The code was right and my assertion was wrong: an estimated read had over-charged, and
the next actual read carried `catchup_adjustment_gbp: −6.24` to correct it.

> **CORRECTED 2026-08-31, later the same day.** This section originally said the walk had found *"a
> composition rule with an unlisted term"* and that only a walk could have shown it. **That is
> wrong, and the correction matters more than the original claim.**
> `company.compliance.domain_invariants.BILL_FOOTS` states the five-term rule explicitly —
> *"commodity + non-commodity + standing charge + VAT, PLUS any catch-up (back-billing) adjustment
> stamped onto the total outside the four category fields"* — and carries a note recording the exact
> same defect being found and fixed once before, when an earlier build omitted the term and wrongly
> held 147 legitimate catch-up bills.
>
> So the term was listed, in the right place, by the invariant that owns the question. What the walk
> actually demonstrated is narrower and still worth having: **the rule is stated in a home its next
> reader did not find.** That is a discoverability problem, not a missing rule — and it is a
> straightforwardly better argument for the concept work than the one I made, because it is about
> where a definition lives rather than whether it exists.
>
> Also stale in that note: it says *"147 catch-up bills in run_output_latest.json"*. The current run
> has **959** of 11,167. The rule is unaffected; the population is 6.5× bigger than the comment says.

**What survives of the original point.** Only *exercising* the join showed the term was
load-bearing on a real household, and a census of field names would have listed
`catchup_adjustment_gbp` beside the other four with nothing to say which are components of a footing
rule. That distinction — inventory versus exercise — still holds. What does not hold is the claim
that nobody had written the rule down.

### 2. The journey's end has two homes, and a reader of one of them is wrong

`C1` is in `churned_billing_accounts` and has **zero** entries in `customer_events`. It left by
drifting off the standard variable product, and those departures go to `svt_departures` — a second
list under a second name.

**The separation is correct** (an SVT departure carries no renewal-decision fields, so unioning the
lists would hand every reader rows of `None`) **and it means any reader of one list is wrong about
the book.** The walk found it from the opposite end to the C1b finding that named it: not "the
capture cannot see the route" but "the household visibly never left". The C2 published reason mix
still reads one list.

The walk unions both. That is what the C1b author said was owed.

### 3. `average_unit_rate_gbp_per_mwh` is the commodity leg, and it is published as if it were the price

`saas/bill_generator` computes it as `commodity_amount / MWh` — the wholesale leg alone. What the
household actually paid is the whole bill over the same volume, **1.4× to 2× higher**. On C1's first
bill: **114.17 published against 228.64 actually paid — exactly double.**

It is volume-weighted by `tools/generate_customers_json` into `avg_rate_gbp_per_mwh` and reaches
`site/data/customers.json`: **126.92 published where revenue over volume is 175.89.**

**This is the canon's "same word doing two different jobs" case, not a defect to rename away.** A
bill legitimately has a commodity rate *and* an effective rate, and both are worth having. What was
missing is anything saying which one the field is. The walk now pins it, so the next reader who
needs "what the customer paid" cannot take this field and be quietly wrong.

**What is owed:** whether the published surface should carry the effective rate as well, or instead,
is a judgement about what that page is for — and it belongs to whoever owns the page. Named here,
not decided here.

> **DONE, AND SHARPENED, 2026-08-31 the same day.** Two corrections and a fix.
>
> **First correction: "a live surface" overstated it.** No page renders `avg_rate_gbp_per_mwh`.
> `site/explore/` reads `unit_rate_p_per_kwh` off the billing ledger and decomposes the whole stack
> honestly — Energy, network/policy/levies, and standing charge spread over use. The field reaches a
> *served JSON payload* with no reader, which is a different and smaller claim than the one I made
> to the director.
>
> **Second correction, and it is bigger than the first: the misreading had already happened.**
> `tools/couple_value_based_pricing.compare` took the field as `current_rate_gbp_per_mwh` — "what
> this customer currently pays" — and derived `base_rate = current_rate − TARGET_MARGIN` from it.
> An entire pricing arm was anchored on the commodity leg. **Measured across the whole book:**
>
> | | commodity leg | effective | |
> |---|---|---|---|
> | book, volume-weighted | **102.57** £/MWh | **156.42** £/MWh | **1.53× understated** |
> | per account | median ratio **1.59×** | | worst **4.17×** |
>
> The walk predicted this reader in as many words. It was already there.
>
> **Fixed.** `tools/generate_customers_json` now publishes `avg_commodity_rate_gbp_per_mwh` and
> `avg_effective_rate_gbp_per_mwh`, each named for what it is, plus
> `effective_rate_bills_excluded` so the denominator is declared; the ambiguous name is gone.
> `couple_value_based_pricing` reads the effective rate.
> `tests/tools/test_a_published_rate_says_which_rate_it_is.py` holds it — including a leg keyed to
> the *reader* rather than the field, because the generator could publish both perfectly and a
> caller could carry on taking the wrong one, which is exactly the state this repo was in.

---

## And a fourth thing, which is a defect inside a single row

**Four of this household's 109 bills carry a correction spanning up to TWELVE earlier periods.** One
totals **−£5.78 on 328 kWh consumed** — an effective rate of **−17.60/MWh**.

Nothing is wrong with the bill. What is wrong is dividing it: the money spans thirteen periods and
the volume spans one, so their ratio is not a rate at all. **It is the "two true numbers whose legs
are different populations" defect sitting inside one row**, and any surface that divides a bill
total by a bill volume inherits it silently — the sign is the only reason this one was visible.

The walk excludes catch-up bills from its rate comparison and says why. **Anything else computing a
£/MWh from a bill needs the same exclusion**, and nothing currently does.

> **MEASURED AT BOOK SCALE AND FIXED, 2026-08-31.** One household's four bills turned out to be
> **959 of 11,167** across the book, and `company/billing/invoice._unit_rate_from_bill` — which
> divides `total_amount_gbp` by `total_consumption_kwh` and stamps the result on every invoice —
> was one of the surfaces inheriting it.
>
> | | median | min | max | negative |
> |---|---|---|---|---|
> | catch-up bills, `total / kwh` | 17.90 p | **−173.52** | 398.09 | **178 invoices** |
> | catch-up bills, `(total − catchup) / kwh` | 20.21 p | 3.33 | 81.51 | 0 |
> | every other bill, `total / kwh` | 19.48 p | 3.20 | 100.03 | 0 |
>
> Netting the adjustment out lands the catch-up rows inside the ordinary population. **178 invoices
> carried a negative unit rate**, and the sign is the only reason any of them was ever visible —
> every other catch-up bill was wrong by an amount nothing announced. Fixed by netting rather than
> refusing: the money for *this* period's volume is exactly what is left when the adjustment for
> other periods is removed, and an invoice with no rate at all would lose a real figure to avoid a
> wrong one.
>
> The same exclusion is applied to the published effective rate, where it costs **no account**
> (251 before, 251 after — so no household silently loses its rate) and pulls the worst from
> 720.24 to 437.41 £/MWh.

---

## What the walk cannot reach, said rather than skipped

**The canon's journey begins at weather. This walk begins at the meter read.** The run artefact
carries no per-customer weather or temperature series — demand arrives already resolved as an EAC,
so there is nothing to assert between weather and consumption for one household.

That is a **gap in the evidence, not a join that holds**, and a leg of the walk asserts that the
gap stays named: if a weather join is ever added, the not-reached statement must come out with it.

**And the first household I chose could not exercise every stage.** C1 is on the standard variable
product, never reaches a renewal decision, and so has no EAC belief at all — the demand leg
*skipped*. A skipped join asserts nothing, and a walk with a silent skip reports more coverage than
it has, which is the failure this whole standard exists to close. Choosing the subject by
*measuring* which households carry every stage is part of the method, not housekeeping.

---

## What this says about the concept work, which the canon deliberately left open

The walk was supposed to inform the shape of the concept work. On this evidence:

**A registry of names would have caught none of these.** Not one of the three findings is two
declarations of one concept — the shape everyone expects. They are: a composition rule with an
unlisted term; one concept correctly living in two places with no reader told; and one name honestly
covering two quantities. **A census would have inventoried `average_unit_rate_gbp_per_mwh` once and
found nothing wrong with it.**

So the useful unit is not "the definition of a concept" but **"the assertion at the join"** — which
is cheaper, already fails loudly, and cannot drift from the code because it *is* the code. That
points away from a registry as the first artefact and toward more joins, each one earning its place
by catching something.

**The one place a shared definition did pay** is the VAT join: it reads
`docs/domain_artefact_library/regulatory/uk_vat_rates.json` — the published document — rather than a
fourth copy of the rate. That is the canon's mechanical test satisfied (*"the code reads the
definition"*), and it is worth noting that it works because the definition is **external and
published**, not because it was registered internally.

**Recommendation, for the decision the canon reserves:** define concepts where an *external
published record* exists to define them against, and assert joins everywhere else. The first kind
cannot drift because reality holds the other end; the second kind cannot drift because a test does.
A concept with neither is a name in a file, and that is the bureaucracy the canon says would be
worse than the disease.
