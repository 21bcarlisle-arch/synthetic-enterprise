**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — whether the world's SVT account-day share sits above or below the published one

**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`departure-level-emerges-from-the-household-not-the-solver`, BEFORE the sourcing below was run.

A prediction, filed before its measurement. It becomes evidence only when
graded, and it is graded in
`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
§10 beside the result.

Filed 2026-09-04 by the delivery seat, at `c9ac07327`, **before** any published figure for the
years the commons does not already carry was looked up, and before the comparison was run as code.

---

## What is being predicted, and why it needs pre-registering at all

The drawn item sends this turn at the **composition question**: what share of the GB domestic book
sat on a standard-variable or default tariff in each year 2016–2025. §9 of the finding above already
stated, in advance, what it expected that sourcing to do:

> *"`reach` is the factor it would move, `reach` closes 1 year of 7 at its arithmetic ceiling, and
> this world's reach is 0.67–0.98 — **already at or above any published default-tariff share**. If
> the sourcing comes back saying the real share was lower, the world's reach is too HIGH and the
> hazard gap widens."*

That is a claim with a direction and it was made without the sourcing in hand. It is graded here.

## The disclosure this pre-registration owes, because part of the answer is already derivable

**I have already done part of this arithmetic by hand, from the table §9 published, before writing
this file.** Filing a prediction while concealing that would make this document worthless. So:

`reach` is *decisions over accounts* and the published statistic is a **stock** — the share of
domestic accounts sitting on a default tariff on a given day. Those are not the same quantity and
comparing them directly is this repo's before-you-divide defect. The comparable quantity is
`reach × exposure`, which is SVT account-days over book account-days settled, and that IS the
published statistic's shape. From §9's own table that product is, by hand:

| year | reach | exposure | reach × exposure |
|---|---|---|---|
| 2017 | 0.672 | 0.643 | ~0.43 |
| 2018 | 0.840 | 0.697 | ~0.59 |
| 2019 | 0.707 | 0.806 | ~0.57 |
| 2020 | 0.783 | 0.762 | ~0.60 |
| 2021 | 0.784 | 0.749 | ~0.59 |
| 2023 | 0.981 | 0.736 | ~0.72 |
| 2024 | 0.772 | 0.785 | ~0.61 |

So the *world* side of the comparison is known to me at filing time to two decimals. What is **not**
known is the published side for the years the commons does not carry, and it is those years, plus
the verdict itself, that this file is a prediction about.

## The predictions

**P1 — §9's "at or above any published default-tariff share" is REFUTED as stated, and refuted
because it compared the wrong quantity.** Against the commons' own anchor (`(b)` of
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`: ~57% at Sep 2017, ~54–56% pre-crisis 2019–20,
~80–90% late-2021→Apr-2023, ~67% Jul 2025), the world's account-day share is **BELOW** published in
at least four of the seven fitted years, and the shortfall is **largest in the crisis years**, where
the published share rises to 80–90% and this world's does not follow. `reach` alone is 0.67–0.98 and
looks high; `reach × exposure` is 0.43–0.72 and does not. I predict the sentence survives only for
2019 and 2020.

**P2 — the direction `simulation/svt_product.py` predicted in prose is CONFIRMED.** That module says
in its own docstring, written before any of this was measured, that *"the generated SVT share will
come out LOW against the published one"*, and names the missing cause: home-move-onto-incumbent does
not exist in this world at all. I predict the measurement agrees with it, and that this is the first
time that sentence has been checked against a number.

**P3 — the published share for the three years the commons does not carry (2018, 2021, 2024) lands
monotonically between its neighbours**: 2018 in 52–60%, 2021 in 60–80% (rising through the year as
fixed deals were withdrawn), 2024 in 65–80%. Filed so that a source that *disagrees* with the
interpolation is visible as a finding rather than absorbed.

**P4 — the sourcing turns up NO new published series, because the answer was already in the tree.**
I predict the honest result of this "research task" is a reconciliation, not a fetch: the anchor is
already in `docs/market_research/svt_rates_active_passive_2016_2025.md` §2–3, restated in
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b), and copied a third time as a Python
constant in `tools/svt_generated_share_check.py`, and no lane pointed at any of them from the
finding that needed it. If that is what I find, the deliverable is the reconciliation and a control
over the copies, not a new document restating them a fourth time.

## The constraint this measurement inherits, unchanged

No constant is picked, no solver aim point moves, `YEAR_LEVEL_ANCHOR` is not edited, and the
published share is a **CHECK on output and never an input** — which is `svt_product.py`'s own
standing instruction and is the thing that would be violated first if the answer came out
inconvenient.

## What would make this pre-registration worthless

If the comparison is run and only the years that agree are reported; if `reach` is quietly compared
instead of `reach × exposure` after all, because it flatters the world; or if P1 is graded against a
band widened after the numbers were seen. The grading in §10 must name every fitted year.

— Delivery seat, 2026-09-04.
