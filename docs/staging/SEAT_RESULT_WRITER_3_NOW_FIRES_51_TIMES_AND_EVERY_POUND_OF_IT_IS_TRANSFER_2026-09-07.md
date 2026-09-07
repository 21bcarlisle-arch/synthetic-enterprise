**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the renewal arm prices no gas) · **Class:** no_caller_and_never_runs

# RESULT — writer 3 now fires 51 times, and every pound of it is transfer

The one-variable pair asked for by step 1 of
`SEAT_RESULT_THE_ID_REPAIR_IS_LIVE_AND_BOUGHT_NOTHING_BECAUSE_NO_SETTLED_ROW_CARRIES_A_TERM_START_2026-09-07.md`.
**The pre-registered prediction is CONFIRMED on four legs of five, and the leg it got wrong it
got wrong in an instructive way.**

## The pair

Same command both legs, same fast-mode world, differing only by the stamp landed in `99b2700de`.
The non-settlement sources were hashed before the BEFORE leg and again before the AFTER leg and
were byte-identical, so the one variable really is the one variable.

```
python3 -m tools.run_annual_report --fast --save-json <leg>.json --output <leg>.md
```

| | BEFORE | AFTER |
|---|---|---|
| decomposed renewals | 1,878 (1,516 elec / 362 gas) | 1,878 (1,516 elec / 362 gas) |
| writer 3 eligible | 296 (110 elec / 186 gas) | 296 (110 elec / 186 gas) |
| **writer 3 firings** | **0** | **51** (5 elec / 46 gas) |
| writer 2 firings | 127 (80 elec / 47 gas) | 127 (80 elec / 47 gas) |
| eligible renewals where W2 fired and W3 did not | 44 | **0** |
| every cause | margin_surcharge 127, portfolio_premium 1,847, price_cap 106 | margin_surcharge 127, portfolio_premium 1,847, price_cap **107**, profitability_uplift **51** |

My own BEFORE leg reproduced the previous pair's AFTER leg exactly — 1,878 / 296 / 0 firings /
127-1,847-106 — which is the check that the world is deterministic and the pair is clean.

## Grading the prediction, beside the claim

> **Leg 1, the hard leg: "writer 3's firing count inside the eligible 296 must be ≥ 44, and the
> W2-fired-W3-did-not residue must fall to 0 or very near it."** — **CONFIRMED**, and more
> sharply than I stated. 51 ≥ 44, and the residue is **exactly 0**: there is now no eligible
> renewal that writer 2 surcharged and writer 3 did not uplift. I had hedged that I *expected a
> small non-zero residue* from `MIN_RECORDS_FOR_JUDGEMENT` and window-clipping. **That hedge was
> wrong** — the two writers agree on the sign for all 44, which is the strongest available
> evidence they are reading the same quantity from two sources.

> **Leg 2, the count: "20–150 of 296."** — **CONFIRMED.** 51.

> **Leg 3, the money: "positive but under 1%."** — **CONFIRMED.** Net margin
> £139,261.55 → £140,143.53, **+£881.97, +0.63%**. Enterprise value +£1,229.81 (+0.98%).

> **Leg 4, what will NOT move: "the renewal count, `portfolio_premium` 1,847 and `price_cap` 106.
> If either moves, the stamp has changed control flow somewhere I did not intend and the pair is
> contaminated."** — **REFUTED, and my reasoning was the error, not the run.** The renewal count
> and `portfolio_premium` held exactly. **`price_cap` moved 106 → 107.** The pair is not
> contaminated: the price-cap clamp sits *downstream of writer 3 in the same chain*, so an uplift
> that pushes a rate into the lawful ceiling is the clamp doing precisely its job. I named an
> invariant that is not one. The correct invariant was the two genuinely independent figures, and
> those held. Keeping this here because a wrong prediction beside the result is the only evidence
> the experiment was designed before its answer was known.

> **Leg 5: "writer 2 stays at exactly 127."** — **CONFIRMED.** 127, both legs, same split.

## The finding that matters more than the count

**The entire margin gain is revenue charged to customers.**

```
total_revenue_gbp   667,939.86 -> 668,820.97   (+881.10)
total_net_gbp       139,261.55 -> 140,143.53   (+881.97)
total_capital_gbp     6,600.51 ->   6,600.96   (   +0.45)
```

Costs are flat to within a pound. £881 of revenue in, £882 of net margin out. Writer 3 is a flat
`NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 5.0` recovery surcharge — 51 firings × £5/MWh — and by
construction it moves value from customers to the supplier without making any. Against the
mission's first test (*value is created and THEN shared; transfer is not creation*), **this repair
buys the supplier a working policy and buys the customer nothing.** That is not an argument
against fixing it: a policy that cannot be taken is a defect whatever its sign, and one that
returns 0.0 indistinguishably from "this account is profitable" is worse than one that fires. But
the £882 must never be published as value created, and the price-cap clamp catching one more
renewal is the world correctly refusing part of the transfer.

46 of the 51 firings are gas — consistent with 186 of the 296 eligible being gas, and with 42 of
the 44 W2-eligible firings being gas. The gas book is where this was costing.

## Two writers, one question, still unsettled

Writers 2 and 3 sit four lines apart and answer "was the prior term loss-making" from two
sources — the world's `prev_term_margin[cid]` hand-down and the settled book read back. This pair
establishes they **agree on the sign wherever both are asked** (residue 0 of 44). They still
disagree on *population* (127 against 51) and on *threshold* (5% of revenue against any loss), so
the run now publishes two counts for one question. **Which one the supplier means is a definition
question, and CLAUDE.md names that shape as this project's most expensive recurring failure.** It
belongs settled before either count reaches a page. This pair does not settle it; it makes the
second count exist and proves the two are commensurable.

## Also fixed on the way through

`tests/simulation/test_settlement_fold.py::test_the_run_builds_exactly_one_fold_and_feeds_it_where_the_list_is_extended`
was red at HEAD *and* at origin/main, unrelated to this work except that it blocked the land. It
counted raw substrings of `settled_fold.add(` and went red the day a comment in the run loop
quoted that call to explain the ordering below it — two "feeds", one of which was a sentence. Its
`src.index` assertion had the same latent defect, finding that comment ~1,000 lines above the
`extend` it asserted to be below. Now reads code lines only, and poison-proved to still go red on
a second *real* feed. **A control that cannot tell a call from a mention of a call fails in the
direction that punishes explaining the code.**

## What is next

1. **Settle the definition.** Two writers, one question, two populations and two thresholds.
   Decide which the supplier means, then delete or subordinate the other. Nothing should publish
   either count first.
2. **`profitability_uplift_log` still never reaches the saved payload** — `extract_report_data`
   carries writer 2's log and not writer 3's, so `_section_profitability_uplift` renders nothing
   even now that there are 51 entries to render. Counted here off `rate_decomposition_log`
   instead. See
   `SEAT_FINDING_WRITER_3S_OWN_LOG_IS_DROPPED_AT_THE_REPORTING_REDUCTION_SO_ITS_PUBLISHED_SECTION_CANNOT_EVER_RENDER_2026-09-07.md`.
3. **`NET_NEGATIVE_UPLIFT_GBP_PER_MWH = 5.0` has no sourced origin.** It was a placeholder that is
   now load-bearing on 51 real repricings and £882 of transfer. It is exactly the shape the
   knowledge-first rule exists for, and it should carry either a published anchor or an honest
   `None` with a named reason.
