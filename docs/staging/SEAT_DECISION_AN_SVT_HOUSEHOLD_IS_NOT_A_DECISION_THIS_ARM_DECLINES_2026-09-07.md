**Severity:** RECORDED · **Lane:** W2_customer_generator · **Atom:** the value arm's reach

# An SVT household is not a decision this arm declines — it is a population the funnel should never have been dividing by

**Decided:** 2026-09-07, delivery seat, claim
`the-arm-prices-a-quarter-of-its-book-and-the-refused-three-quarters-are-svt`.
**Pairs with** `SEAT_FINDING_THE_158_UNLABELLED_REFUSALS_ARE_THE_DRAWN_GAS_BOOK_AND_THE_CENSUS_EXPLAINING_THEM_MISREAD_137_ELECTRICITY_LEGS_2026-09-07.md`,
which names the other bucket. Neither answer was inferred from the count.

---

## 1. The decision

**`renewal_margin_uplift` has no decision to make at an SVT segment boundary, and its refusal there
is correct. The defect is the ratio downstream of it: `priced_share_of_renewals_offered` divides a
count of renewals by a count of term boundaries, and those are not the same thing.**

The published headline — **10.59%**, 216 of 2,039 — is not a measure of the method's reach. It is
mostly a measure of what fraction of a domestic book sits on a default tariff, which is a published
fact about GB and not a result of this company.

## 2. The reason, which is prior to the numbers

*Declining* presupposes that a decision existed. At an SVT boundary none does.

- **2019 onwards.** The rate is the Ofgem default tariff cap, set per region, payment method and
  consumption level — not by the supplier and not per customer. What this world emits as a
  "segment boundary" on SVT is a cap revision. No notice is served, no offer is made, and no rate
  is struck. (`docs/market_research/svt_rates_active_passive_2016_2025.md` §1, post-cap table,
  confidence H.)
- **2016–2018.** SVT rates were supplier discretion — but a *published tariff-level* rate per
  supplier and region, appearing in Ofgem's SVT league tables. Still never a per-household strike.
  (Same source, §1, "Pre-Cap Period: 2016–2018 (supplier discretion)", confidence M, ±15%.)

`renewal_margin_uplift` moves a **struck unit rate** by £/MWh, from the supplier's own settled
book. On an SVT household there is no struck rate for it to take as its argument. The guard is not
a policy choice that could be relaxed; there is no object.

`tools/product_gate_refusal.PRODUCT_REFUSAL_MEANINGS["svt"]` already says this, and says it keyed
to the property rather than to today's answer. **It is right and nothing here changes it.**

## 3. What a real supplier *does* decide for an SVT household — and it is a different desk

The per-customer commercial decision is a **conversion** decision: whether to serve this household a
fixed-deal offer, and which one. Roughly two thirds of a domestic book rolls to SVT by default
rather than actively renewing (`svt_rates_active_passive_2016_2025.md` §2, ~35% active / ~65%
passive pre-crisis), and the all-domestic default share sat between ~58% and ~90% across the window
(`gb_domestic_default_tariff_share_2016_2025.md` §3, per-year bands with sources).

That is an **acquisition-shaped decision about an existing customer**, not a renewal-margin one, and
this company does not currently make it anywhere. Naming it is the finding this half produces:
**the arm's reach is small for a correct reason, and the commercial gap it exposes is real and sits
in a desk we have not built.** It is filed as owed work in §5 and is not folded into this arm.

## 4. What each number counts, before anything is divided

| stage | count | is there a rate a supplier struck for this household? | belongs in a reach denominator? |
|---|---|---|---|
| `product_not_upliftable` — SVT | 1,350 | **No.** Cap-set, or a published tariff-level rate | **No** |
| `product_not_upliftable` — unlabelled | 158 | Unknown — 18 drawn gas legs, a record-shape defect | **Not yet.** See the finding |
| `acquisition_term` | 252 | Yes, but it is the *first* term — no prior rate to move | **No** — it is not a renewal |
| `declined` | 63 | Yes; the arm looked and chose not to move it | **Yes** |
| `priced` | 216 | Yes; the arm moved it | **Yes** |
| **total** | **2,039** | | **279** |

**216 of 279 = 77.4%.** That is the arm's reach over the renewals at which a rate was struck and a
prior term existed. The same run, the same numerator, an honest denominator.

Neither figure alone is the answer, which is why the decision is to publish both and name each:

- **2,039** is the book's term boundaries. It is context, and it is where the composition claim
  lives (66% of this book's boundaries are SVT, against a published GB default share of ~58–90%
  across the window — the world is in range, and that is the fidelity reading).
- **279** is the decision population. It is the denominator of any claim about the *method*.

The 10.59% ratio is neither, and it is currently the one on the page.

## 5. What this creates

1. **`/harness/` publishes reach against the named decision population, not the term-boundary
   count.** Both numbers on the page, each with the sentence saying what it counts; the skill claim
   divides by 279. The funnel keeps every stage count unchanged — this is a publishing change, not
   a measurement one. **This is the load-bearing follow-on and it is not yet done.**
2. **A concordance re-read.** The arm's concordance sits inside the null at n=170. That n is drawn
   from the priced population and is *unaffected* by this decision — the denominator changing does
   not add one observation. Recorded here so that a later reader cannot mistake a reach of 77% for
   evidence the method works: **it is not, and the null still holds.**
3. **The gas fidelity determination** (finding §"What is next" item 1). If it lands, 158 boundaries
   move from `product_not_upliftable` into the decision population, taking it from 279 to 437 and
   reach from 77.4% to 49.4%. **That prediction is filed before the determination is made**, and
   the determination must be decided on fidelity grounds blind to it.
4. **An owed desk: the SVT conversion decision** (§3). Not minted here — it is a director-scope
   question about whether this company makes retention offers to its own default-tariff book, and
   it is the single largest unexercised commercial surface in the run.

## 6. Not a target

R12. None of these counts is a thing to improve, and specifically this is not a cue to relax
`UPLIFTABLE_TARIFF_TYPES` so the SVT book gets counted. The decision moves a *divisor on a page*.
It moves nothing the company does.
