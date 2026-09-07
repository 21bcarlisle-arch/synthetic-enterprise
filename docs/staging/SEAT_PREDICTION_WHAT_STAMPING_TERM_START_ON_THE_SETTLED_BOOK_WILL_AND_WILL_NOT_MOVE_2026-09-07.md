**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas)

# PREDICTION — what stamping `term_start` on the settled book will and will not move

**Written 2026-09-07 13:40 BST, BEFORE the A/B answers it.** The BEFORE leg was launched at
13:36, before a line of the change was written; the AFTER leg differs by the stamp and nothing
else. This is step 1 of the "what is next" in
`SEAT_RESULT_THE_ID_REPAIR_IS_LIVE_AND_BOUGHT_NOTHING_BECAUSE_NO_SETTLED_ROW_CARRIES_A_TERM_START_2026-09-07.md`,
pre-registered separately from it exactly as that result asked, so the world-side change and the
company-side id repair stay attributable apart.

## The change being measured

Four settlement emitters build a record and none of them stamps the term that produced it:
`run_hedged_term`, `run_deemed_term`, `run_flex_term` (`simulation/hedged_settlement.py`) and
`run_gas_term` (`simulation/gas_settlement.py`). Every one already takes the term start as an
argument. `settlement_daily.CARRIED_FIELDS` has listed `"term_start"` among the fields a day
carries from its first record the whole time, so the fold is already built for a field the
writers never wrote.

No wall is crossed: the term start is the supplier's own contract boundary, sitting beside
`unit_rate_gbp_per_mwh` and `hedge_price_gbp_per_mwh` on the same record. It is not a fact about
the household. `data_regime` is untouched.

## What the measurement is

The eligible population is already measured and is **296 renewals — 186 gas, 110 electricity** —
being those that clear `UPLIFTABLE_TARIFF_TYPES = {fixed, pass_through}` and
`term_index >= MIN_TERM_INDEX_FOR_UPLIFT`. All 296 currently reach the prior-term lookup and all
296 get `None`, because `prior_term_starts` is empty before any margin is summed. Writer 3 fires
0 times in the BEFORE leg, on both fuels.

## The prediction, in the order I would bet on it

**1. The hard leg — a directional inequality that needs no distribution.** Writer 2 and writer 3
compute *the same quantity from two sources*: `prev_term_margin[cid] = sum(net_margin_gbp)` over
the term just settled, handed down by the world (`run_phase2b.py:2928`), against writer 3's sum
over the same term read back out of the folded settled book. Their thresholds differ, and differ
one way only:

```
writer 2  fires when   loss_fraction = -margin/revenue  >  0.05     (margin_feedback.py:47)
writer 3  fires when   margin < 0.0                                 (customer_profitability.py:232)
```

Writer 3's test is strictly weaker. **So on the 296 eligible renewals, writer 3's firing count
must be greater than or equal to the number of writer-2 firings inside that same 296**, and
strictly greater by however many prior terms lost between 0% and 5% of revenue. If writer 3
comes back with FEWER firings than writer 2 has on the same rows, the two are not reading the
same quantity and the stamp is not what I think it is — that is the finding instead, and it
would point at the fold, not at the writers.

**2. The count.** Writer 2 fires 127 times across all 1,878 decomposed renewals (6.8%). The 296
are a different population — contracted rather than SVT, and second-term-or-later. I predict
writer 3's firing count lands in **20–150 of 296**, i.e. materially above zero and materially
below all of them. A count of exactly 0 would mean no eligible account had a single loss-making
prior term anywhere in 2016–2025, which I do not believe on a book that ran through 2021–22; a
count at or near 296 would mean the whole eligible book is loss-making and the finding is about
the book, not the writer.

**3. What it is worth in money — small, and I want that on the record before the number
arrives.** `NET_NEGATIVE_UPLIFT_GBP_PER_MWH` is a flat 5.0. It is not a per-customer search, so
whatever fires, the uplift is the same rate on each. I predict the portfolio net-margin
difference between the two legs is **positive but under 1%**, and I would not publish it as
evidence for or against the value thesis either way.

**4. What will NOT move.** The decomposed-renewal count stays at 1,878 (1,516 elec / 362 gas) —
the stamp adds a field, it does not create or destroy a renewal. `portfolio_premium` stays at
1,847 and `price_cap` at 106. If either moves, the stamp has changed the run's control flow
somewhere I did not intend and the pair is contaminated.

**5. Writer 2's own count is the tell-tale.** It reads the world's hand-down and not the book, so
**`margin_surcharge` should stay at exactly 127.** If it moves, the two legs differ by more than
the stamp.

## ADDENDUM 13:52 BST — the hard leg, sharpened to a number, still before the answer

The grading instrument (`/var/tmp/se-termstart/grade.py`) reconstructs writer 3's eligible
population by joining each decomposed renewal to `account_state_log` and re-applying
`UPLIFTABLE_TARIFF_TYPES` and `MIN_TERM_INDEX_FOR_UPLIFT` read from the module that owns them.
Validated against the previous pair's AFTER leg: it reproduces the published 296 (110 elec, 186
gas) exactly, joins 1,878 of 1,878 with none unjoined, and returns the published cause counts
(`margin_surcharge` 127, `portfolio_premium` 1,847, `price_cap` 106) and writer 3 = 0.

Run on the BEFORE state it also decomposes something the earlier funnel did not:

```
writer 2 firings inside writer 3's eligible 296 : 44   (2 electricity, 42 gas)
eligible renewals where W2 fired and W3 did not : 44   (i.e. all of them)
```

This is a decomposition of already-published BEFORE-state figures, not a peek at the answer, and
it makes prediction leg 1 a number rather than an inequality:

> **After the stamp, writer 3's firing count inside the eligible 296 must be ≥ 44, and
> "eligible renewals where W2 fired and W3 did not" must fall to 0 or very near it.** Writer 3's
> test (`margin < 0`) is strictly weaker than writer 2's (`loss > 5% of revenue`), so any
> eligible renewal writer 2 surcharged must also be one writer 3 uplifts — unless the two are
> not reading the same quantity after all.

**A residue above ~5 refutes the "same quantity, two sources" reading** and says the world's
hand-down and the settled book genuinely disagree about the prior term — which would be a bigger
finding than this one, and the next thing to chase. I expect a small non-zero residue from the
one place the two legitimately differ: `MIN_RECORDS_FOR_JUDGEMENT` and the `max(term_start)`
selection can pick a different "prior term" than the world's `prev_term_margin[cid]` where a
term was clipped by the reporting window.

## GRADED 2026-09-07 14:05 BST, beside the claim rather than instead of it

**Four legs of five confirmed; leg 4 refuted, and the error was mine, not the run's.**

| leg | predicted | measured | verdict |
|---|---|---|---|
| 1 (hard) | W3 eligible firings ≥ 44; residue → 0 or near | 51; residue **exactly 0** | **CONFIRMED** |
| 1 (hedge) | "a small non-zero residue" from clipping | 0 | **the hedge was WRONG** |
| 2 | 20–150 of 296 | 51 | **CONFIRMED** |
| 3 | net margin +ve, under 1% | +£881.97, **+0.63%** | **CONFIRMED** |
| 4 | renewals, `portfolio_premium` AND `price_cap` all unmoved | first two held; **`price_cap` 106 → 107** | **REFUTED** |
| 5 | `margin_surcharge` stays exactly 127 | 127 | **CONFIRMED** |

Leg 4 was a badly chosen invariant, not a contaminated pair. The price-cap clamp sits
*downstream of writer 3 in the same chain*, so an uplift that pushes a rate into the lawful
ceiling moves that count by construction. I asserted independence for a figure that is not
independent, and said its movement would mean contamination — it does not. The two genuinely
independent figures (the renewal count and `portfolio_premium`) held exactly.

Full working, the money decomposition, and what it means for the thesis:
`SEAT_RESULT_WRITER_3_NOW_FIRES_51_TIMES_AND_EVERY_POUND_OF_IT_IS_TRANSFER_2026-09-07.md`.

## What this does not settle, and is the next question after it

Writers 2 and 3 sit four lines apart and answer "was the prior term loss-making" from two
sources. Once writer 3 can answer at all, the run publishes two counts for one question. Which
one the supplier *means* is a definition question — the very shape CLAUDE.md names as this
project's most expensive recurring failure — and it belongs settled before either count reaches
a page. This pair does not settle it. It only makes the second count exist.
