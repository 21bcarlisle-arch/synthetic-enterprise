**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — A49, the attention premium against NESO DFS)

# RESULT — the called-day premium is 1.20×, and the break-even needed 2.53×

**Verdict: the attention premium does not clear.** The extreme-day-only TOU tariff's **MERELY RARER**
verdict stands, and is now **settled against the real GB product** rather than carried as a hedge.

Pre-registered at `SEAT_PREDICTION_WHAT_NESOS_DFS_CAN_AND_CANNOT_SETTLE_ABOUT_THE_ATTENTION_PREMIUM_2026-09-07.md`,
landed `2ae8dc01a` **before any NESO source was fetched**. Six predictions: **four held, two refuted.**
Evidence: `docs/market_research/neso_dfs_called_day_response_2026-09-07.md`, landed `08fa62195`.

---

## 1. The answer

`SEAT_RESULT_THE_SKEW_IS_ENTIRELY_IN_THE_TROUGH...` (`8f5239deb`) named one number that could
overturn its verdict: a called-day response premium of **2.53×**. NESO's Demand Flexibility Service
is the only GB product that has ever paid households on called days at national scale, and it
published its own live-vs-test comparison.

| | multiple |
|---|---|
| break-even the extreme-day product must clear | **2.53×** |
| **NESO's own live-vs-test measurement** | **1.20×** |
| generous upper bound (unnormalised, per settlement period) | **2.04×** |
| per unit of price signal | **0.79×** |

> "Enthusiasm for consumer flexibility reached an unprecedented scale during the 'live events', with
> consumption reduction **20% higher than test events**." — NESO, Winter 2022/23 review

Same enrolled households, same product, same settlement. A live event was a nationally-reported
system-margin emergency; a test was a routine scheduled hour, two a month. That is the largest
salience contrast the real product ever ran, and **it bought 1.20×**.

It was not bought at a constant price either: live events paid **£4,559/MWh against the tests'
£3,000/MWh**. Per unit of price signal the called day therefore returned **0.79× — less response per
pound than the routine call.** The live events were also the only ones that **under**-delivered
against commitment (680.0 of 795.4 MWh procured, 85.5%), while tests over-delivered.

The 2.04× is a deliberately generous upper bound: it credits the called day with the *entire*
winter's portfolio growth (4 → 21 concurrent providers) and the price uplift as well. **Even that
does not reach 2.53×.** The conclusion is taken from the bracket, which is what makes it robust.

## 2. The number that would have flipped it, and why it is not a number

**40% ÷ 10% = 4.0×** clears the break-even comfortably. Centre for Net Zero, on Octopus's 700,000
DFS participants: a **40%** reduction among those who signed up and **opted in** to an event, **10%**
among those **simply invited**.

It is not a premium. The 40% is a selected subgroup; the 10% is the population average over
everyone invited, including every household that ignored the call. **If ~25% opt in and each cuts
40%, the population average is exactly 10%** — the two figures are one figure and an opt-in rate.
Dividing them measures *who answered*, not *how hard they pushed*.

The A49 model applies its response to every household on every qualifying day, so it needs the
population-average figure on **both** sides. This is the project's own named recurring failure —
*before dividing two numbers, say out loud what each one counts* — and taking it at face value would
have reversed a published verdict **on an arithmetic identity**. It was caught by writing the two
sides out, which is the only reason it did not land.

Corroboration, in the same direction: across 2024/25's top-10 participation events accepted prices
ranged **£100–£1,290/MWh (12.9×)** and participation did not rise with price. NESO: *"consumers
appetite to participate and engage are not wholly financially driven."* And CNZ finds DFS's P376
baseline **over-credits delivery by ~13%**, which pushes every called-day figure above *further
below* the break-even.

## 3. The pre-registration, scored beside the claim

| | prediction | outcome |
|---|---|---|
| P1 | rate ≥£1,000/MWh; code understates by ~3 orders | **HELD.** £3,316/MWh realised 2022/23; the test GAP was exactly the £3,000 point estimate. `4.5` is 737× low. |
| P2 | live events 5–15/winter; live+test 15–30 | **SPLIT/REFUTED.** Total 22 ✓. Live was **2**, below my band — and the real finding is better than the prediction: "~20 events" is the **test** count, and 20 of 22 were calendar-scheduled. |
| P3 | median <0.5 kWh/event; winter revenue <£10/household | **HELD, and understated.** 23p per household per test event (≈£5 across the crisis winter); **47.7p per registered MPAN for all of 2024/25**. 91% of domestic delivery is below 1 kW. |
| P4 | **premium <1.5× at common signal; verdict unchanged** | **HELD.** 1.20×, 0.79× per unit of price, 2.04× worst case. Verdict unchanged. |
| P5 | 30–70% of registered accounts deliver per event | **REFUTED.** **22.4%** at the single best-attended event of the winter (443,224 of 1.98m), below my band. Attention is a harder constraint than I predicted. |
| P6 | sourced, not world-derived; derivation stays a gap | **HELD, and more strongly.** NESO's live trigger was a discretionary day-ahead margin judgement, never a published rule — and 91% of the founding winter's events were **calendar**, not system-driven. |

I was right about the economics and wrong about how *few* people turn up. Both refutations moved the
answer further in the direction the verdict already pointed, which is why neither changed it.

## 4. What landed in the code, and the defect it removes

`_DFS_RATE_GBP_PER_MWH = 4.5`, in **two** files, commented "NESO DFS average 2022-24":

| winter | realised | vs `4.5` |
|---|---|---|
| 2022/23 | £3,316/MWh | **737× too low** |
| 2023/24 | **NOT ESTABLISHED** | — |
| 2024/25 | £241/MWh | **54× too low** |

`flexibility_potential.py`'s own docstring said suppliers earn "**£3-6/kWh**" — which *is*
£3,000–6,000/MWh. **The file disagreed with itself by a factor of ~1,000, in ten lines.**

It survived because the test asserting it recomputed the production formula from the same constants
(`expected_dfs = _EV_FLEX_KW / 1000 * _DISPATCH_DURATION_HRS * _DFS_RATE_GBP_PER_MWH *
_DISPATCH_EVENTS_PER_YR`). **A tautology: it passes for every value of the rate.**

`company/market/dfs_published_record.py` now holds the fact **once**, per winter, with 2023/24 as an
explicit `None` carrying its reason rather than an average of two irreconcilable secondary figures.
All three consumers read it.

**The partial fix would have been worse than the bug.** Correcting the rate alone gave **£461/yr for
one EV household in 2022/23**, against a service that paid **£6.94 per participant** across that
whole winter — because the offsetting error is crediting *rated* asset power (a 7.4 kW charger
turning down 7.4 kWh at every event) when 91% of domestic delivery is below 1 kW and 22.4% of
registrants show up. Revenue is now anchored on the published per-participant economics and weighted
by capability, so **a book of average participants reproduces the published total** (£11.10m modelled
vs £11.10m published for 2022/23; £950k vs £944k for 2024/25).

## 5. Controls, and one I got wrong

`tests/company/market/test_dfs_published_record.py` — 14 tests, each named for its defect.
**Poison round run first**, with a baseline round because a broken runner reports "killed" for
everything, and a target-present check because a patch that never applies looks like a survival.

| mutation | result |
|---|---|
| premium clears the break-even | killed |
| upper bound clears the break-even | killed |
| 2023/24 invented as established | killed |
| calendar tests merged into the system-called count | killed |
| default to the flattering crisis winter | killed |
| **fail-open: unestablished returns 0.0** | killed |
| re-mint the rate in a consumer module | killed |
| reference drifts off the published bins | killed |
| **price off rated asset power again** | **SURVIVED on the first round** |

The survivor is worth recording plainly. `test_a_book_of_average_participants_reproduces_the_published_total`
passed `REFERENCE_PARTICIPANT_FLEX_KW` into a function that *divides by*
`REFERENCE_PARTICIPANT_FLEX_KW`, so it read `base × 1` for any value of the constant — **I wrote the
same self-referential tautology into the very file written to replace one, and only the poison round
found it.** Fixed by checking the constant against the published delivery bins by an independent
route; both mutations now kill.

## 6. What is next

1. **The 2023/24 winter is a named gap**, closable by one document: the NESO *Winter 23/24 End of
   Year Report*. Secondary reporting gives 2,507 MWh and 3,759 MWh and does not reconcile.
2. **`_EV_FLEX_KW = 7.4` / `_BATTERY_FLEX_KW = 5.0` are rated power, not delivered power**, and the
   published domestic distribution says delivery is ~0.95 kW. They are now bypassed for DFS but are
   still live for the **Capacity Market** leg, which has had no equivalent pass.
3. **Do not re-cut the TOU panel.** The premium was the one number that could have moved the verdict
   and it has been settled against the real product. The remaining open item on that artefact is the
   **blind 17.5%** of value on negative-price days, which is a knowledge-layer gap.
4. **`W1_9_dsr_flex_markets` can move off `level_current: 0` on the rate and event count** — they are
   now sourced. The *world-derived* event rate cannot, and that is a finding rather than a deferral:
   NESO never published a rule, and 91% of the founding winter was a calendar.
