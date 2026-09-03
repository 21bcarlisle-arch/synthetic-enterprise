**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `the-company-estimator-learns-from-its-own-book`

# The company's acted belief IS independent of the record — and it is worse than the record

> **HALF THIS TITLE IS WITHDRAWN, same day, 2026-08-31.** "Independent of the record" **stands** and
> is the result. "**Worse than the record**" **does not**: the acted belief is this BOOK's departure
> hazard and the record is the GB MARKET's switching rate, so their distance is not an accuracy
> reading in either direction. The filename is deliberately left alone — the determination and the
> lane both cite it, and renaming a node voids every discharge that names it. Corrections are filed
> beside their claims in §3 and §4 below; the determination that settles it is
> `docs/design/THE_ACTED_BELIEF_IS_A_BOOK_QUANTITY_2026-08-31.md`, which chose **(b)**.

**Lane 0, delivery seat, 2026-08-31.** Both increments the direction named, and the plain answer
to the question the first one poses.

---

## 1. The guard was grading a table nothing downstream uses

`tools/couple_value_based_pricing._SIDE_TABLES` read the company side as
`company.crm.market_conditions.MARKET_SWITCHING_RATE_PCT_BY_YEAR` — the **prior**. The company
does not renew on the prior. `company/crm/competitive_pressure` blends it with the company's own
realised departures, and `enriched_churn_estimate` and `churn_model` both scale by the
**posterior** (`derived_market_pressure_multiplier`). So the guard was asking whether the table
the company *starts from* descends from the published record, while every churn estimate in the
book was priced off something else.

**And no control could have caught it,** which is the transferable part. Outside a run scope the
ledger is empty, `weight` is 0, and the posterior is byte-identical to the prior — that is
`competitive_pressure`'s deliberate fail-soft. Every test, and every non-run caller, sits in
exactly that state. A leg pointed at the wrong one of two quantities that agree everywhere the
tests can see is invisible to the tests by construction. It took reading what the *run* does.

The leg now reads the posterior, rebuilt from the company's own renewal ledger as booked out by
`tools/_ladder_chase_arm` at the end of a real run
(`docs/observability/ladder_chase_on_founder_2021.ledger_census.json`, run 0 — the flat-rules
control, which is today's company, in the chase-on arm, which is the committed world).

**Fail-closed on three branches, each proven by running it:** an unreadable census, a census with
no run, and — the one that matters — an **unarmed** ledger. An unarmed ledger's `reading()`
returns the prior by design; serving those numbers as "the company's acted belief" would have the
guard grade the prior while its artefact said it graded the posterior, and this whole change would
be undetectable from the output. All three resolve to *cannot tell*, which the verdict reads as
co-calibrated. Mutation-proven off-tree (mutated source exec'd as a throwaway module, so no
concurrent lane's pytest saw it): pointing the leg back at the prior, dropping the `armed` check,
and iterating the record's years instead of the ledger's each kill their control.

---

## 2. Does the posterior move on this book? **Yes — a long way, and downward.**

The direction pre-registered the honest possibility that it does not: *"the arm priced 20 of
1,369 renewals, so the evidence weight is around 0.5 at best and may be 0 for most years."* That
is not what the numbers say, and the reason is that the direction was looking at the wrong
counter. The **value arm** priced 20 renewals. The **pressure ledger** books from
`churn_desk.estimate_renewal_churn`, the company's single once-per-renewal belief site, so it
carries every renewal the company priced: **453 closed decisions** by 2022, not 20. The weight is
not 0.5, it is **0.82–0.89**.

| year | prior % | posterior % | ratio | w | closed decisions | predicted | realised | band % |
|---|---|---|---|---|---|---|---|---|
| 2016 | 17.30 | 17.30 | — | 0.00 | 0 | — | — | 17.0–17.6 |
| 2017 | 13.75 | 13.75 | 0.997 | 0.10 | 3 | 0.38 | 0 | 13.5–14.0 |
| 2018 | 19.75 | **3.04** | 0.102 | 0.82 | 85 | 14.59 | 1 | 19.5–20.0 |
| 2019 | 21.00 | **13.47** | 0.587 | 0.83 | 187 | 17.79 | 10 | 20.7–21.3 |
| 2020 | 22.75 | **15.32** | 0.638 | 0.88 | 280 | 25.78 | 16 | 22.5–23.0 |
| 2021 | 18.15 | **11.63** | 0.608 | 0.89 | 368 | 30.35 | 18 | 17.9–18.4 |

Outside the published band in **4 of the 6 years the run priced renewals in**, by up to **17.0pp**.
`co_calibrated` moves `true → false`. `sides_are_independent` moves `false → true`.

Years 2022–2025 are **not** in the table and that is deliberate: `reading()` will answer for them
by carrying the last closed window's ratio forward, but the run ended in 2021 and a year the
company held no belief in must not appear as a row saying what it believed.

---

## 3. What this is NOT, and the direction was right to warn

Nothing was added to manufacture the divergence — no noise, no offset, no second source chosen
because it disagrees. The route taken is the one the guard's own `what_would_discharge_it` names
as **(b)**: *"the company estimator re-fitted from its OWN observed departures rather than the
published market series, which is what a real supplier actually has and this one does not yet
use."* It now does.

**But the direction the belief moved is not a credit, and this is the sentence that matters.**
The company **over-predicted its own losses by about 1.6×** — 22 realised against 35.2 predicted
on 453 closed decisions — so the posterior drags its implied market rate *down*, away from a
record the world sits squarely on. That is independence and inaccuracy at once, exactly the clause
`tools/inference_claim` holds: *"the company's estimator differs from the world"* and *"the
company's estimator is bad"* produce the same number.

> **CORRECTED SAME DAY, 2026-08-31 — the second half of that paragraph is WITHDRAWN, and this
> document's own title is wrong in the same way.** "Independence and inaccuracy at once" is not a
> reading this measurement can carry, and the next paragraph is why: the posterior's *level* comes
> from a ratio computed on **one supplier's own book** at w = 0.82–0.89, while the published band
> is the **GB market's** switching rate. Those are two different quantities, so their difference is
> not an error. 2018's 3.04% against a 19.5–20.0% band is what a sticky book in a competitive year
> looks like. The 1.6× over-prediction and the 4-of-6 distance both stand as *measurements* — what
> is withdrawn is reading either as evidence the company is **wrong**, because a supplier that
> retains better than average sits far outside the band without being wrong about anything.
>
> §3 below saw this and said it ("coherent as *the market rate this company's acted belief
> implies*; not a market measurement") and then let the accuracy sentence stand anyway. Publishing
> both was the defect. The determination that settles it —
> `docs/design/THE_ACTED_BELIEF_IS_A_BOOK_QUANTITY_2026-08-31.md` — chose **(b)**: it is a belief
> about this book. The page clause is withdrawn on the page's own withdrawal record
> (`site/data/value_arms.json → withdrawn_claim`, withdrawals 3 → 4).
>
> **The independence leg in §1–§2 is untouched and stands.** The band test asks whether this side's
> series *is* the record, which needs no commensurability — only the company's own departures can
> move the posterior off the prior. One measurement, two questions, and only one of them is
> answerable from it. **This is the flattering direction and nothing replaces it:** the page does
> not gain an accuracy reading, it loses the ability to make one, and no such comparison exists on
> this side of the wall. That cost is the finding, not a defect to route around.

There is a second reading a reader must not be allowed to take. The likelihood is **one
supplier's book, not a market sample**. That is precisely why the leg is now independent of the
published series — and precisely why the number it produces is a poor estimate of that series.
The product is stated in the code: prior (a market-wide rate) × the correction the company's own
book put on its pressure multiplier. Coherent as "the market rate this company's acted belief
implies"; not a market measurement.

**And it changes nothing about publication, which is the system working.** `inference_claim`'s
second leg is now the binding one: the method's own ranking scores **0.333 against a null interval
of 0.133–0.867 on six decisions** — it cannot be told from chance. Every surface re-derived itself
from the verdict without an edit: `publishable_as_evidence_of_inference` is still `false`, and the
refusal now reads *"the two sides are independent, which removes the objection that we were
measuring our own reflection — it does not establish that the company knows anything."* That is
the standing rule doing its job on the exact day the leg it guards flipped.

**So the discharge lands on book depth, as the direction predicted — just not for the reason it
predicted.** Not because the evidence weight is 0 (it is 0.89), but because six scored decisions
cannot clear a null. Item two is the same item.

---

## 4. One stale claim corrected beside its subject

`tools/inference_claim`'s claim 3 read *"The company sits outside the published band in 8 of 10
years, by up to 17.3pp"* in the present tense. That measured the hand-authored multiplier table
replaced on 2026-08-31, survived the commons repair that put the company **on** the record, and
would now have survived this change too. The count is computed live in `accuracy` from whatever
the guard reads today, so the prose copy is deleted rather than corrected: a second source for one
figure, and the stale one is always the one a reader quotes.

> **CORRECTED 2026-08-31, same day: `accuracy` no longer exists — the key is `record_distance`.**
> The withdrawal above renamed it, dropped the `accuracy` key rather than aliasing it (a `KeyError`
> is the right answer to a consumer still asking a question the module no longer answers), and set
> `accuracy_reading_available: False` beside the counts so the refusal travels with the numbers.
> The point this section makes survives the rename intact and is worth restating, because **this
> section fell to its own defect within a day of being written**: it named a live key in prose, the
> key moved, and the prose became the stale second source it exists to warn against. The general
> form is the one already in the memory index — *a hand-authored claim and its machine-readable
> form are two artefacts and only one gets edited.* The durable fix is the door leg landed with the
> determination, which fails if the counts a reader SEES have no machine-readable companion beside
> them: `site/test_the_baseline_comparison_reaches_the_reader.py`
> `::test_the_counts_a_reader_SEES_have_a_machine_readable_companion_beside_them`.

---

**Landed:** `tools/couple_value_based_pricing.py`, `tools/inference_claim.py`,
`tests/tools/test_couple_value_based_pricing.py` (6 new controls, 3 mutation-proven),
`docs/observability/value_based_pricing_arms.json` (re-run).
