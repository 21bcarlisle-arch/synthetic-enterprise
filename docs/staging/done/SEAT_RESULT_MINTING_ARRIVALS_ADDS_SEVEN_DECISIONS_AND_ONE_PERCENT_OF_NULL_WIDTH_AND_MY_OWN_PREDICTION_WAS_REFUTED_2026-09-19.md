**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `does-minting-arrivals-widen-the-scored-decision-population`

# Minting arrivals adds seven decisions and one percent of null width, and my own prediction was refuted

*The drawn question is answered. `decisions_that_existed` goes **107 → 114**, scored decisions **104
→ 107**, and the 95% null half-width goes **0.11280 → 0.11164** — **1.0% narrower**. The rank leg did
not get cheaper. **P2, landed at `7bff15179`, was right about the direction and my P3a, landed at
`768895de2` four hours later, was wrong**: I predicted a fall to about 95 and the count rose. The
mechanism I reasoned from — arrivals spending their early terms on an unpriceable product — is real
and is swamped by one I did not count: an SVT account is offered MORE renewals, not fewer.*

---

## 1. The two legs, one variable

Two value-arm passes, one commit, one seed, one roster, differing in exactly one rebound symbol
(`simulation.population_draw._draw_tariff_type` → `None`, the pre-producer book). Both legs re-run
after the churn-journey repair at `3a8d15185`, which the arrivals-ON leg needed to complete at all.

| | OFF (no arrivals) | ON (as built) | Δ |
|---|---:|---:|---:|
| roster records labelled `svt` | 0 of 232 | **35** of 232 | +35 |
| `renewals_the_world_offered` | 2,824 | 2,943 | **+119** |
| `acquisition_term` | 227 | 227 | **0** |
| `product_not_upliftable` (all `'svt'`) | 2,490 | 2,602 | +112 |
| `no_observed_history` | 0 | 0 | 0 |
| `priced` / `declined` | 104 / 3 | 111 / 3 | +7 / 0 |
| **`decisions_that_existed`** | **107** | **114** | **+7** |
| accounts the arm priced | 66 | 70 | +4 |
| scored decisions | 104 | 107 | +3 |
| retained / left | 60 / 44 | 63 / 44 | +3 / 0 |
| `discrimination_auc` | 0.5566287878787879 | 0.5321067821067821 | −0.0245 |
| own-roster null sd (tie-corrected) | 0.05755173 | 0.05695865 | −1.0% |
| **95% half-width** | **0.11280** | **0.11164** | **×0.990** |
| distance of AUC from 0.5, in its own null sd | 0.98 | 0.56 | — |
| pass cost | 1,482s | 1,491s | — |

Cost: 2 launches of `background.launch_long_job`, four full passes in total (two of them lost to the
crash and the repair), about 100 minutes of the only box, 5.55 GB peak. **No seed family**, per the
drawn item's hard constraint; the null width is arithmetic once the counts exist.

## 2. P3a is refuted, and the mechanism I missed

**What I predicted** (`PREREG_..._2026-09-19.md`, filed 16:45 BST with both artefacts absent):
`decisions_that_existed` **below 107**, point 95, band 85–107, on the reasoning that an arrival
previously resolved to `"fixed"` at its opening term and was priceable from term index 1, and now
sits on SVT until its engagement roll exits it at index 4 or later.

**What happened: 114.** That half of the mechanism is visible and real —
`product_not_upliftable` rose by 112, every one of them `'svt'` — but the producer did not move
those terms out of a priceable population. **It ADDED 119 renewals to a book of 2,824.** An account
on the default tariff is offered a term boundary more often than one on a fixed deal, so the SVT
tenure generates its own boundaries, and the 19 of 31 accounts that exit reach priceable terms on
top of a renewal count that has itself grown. I reasoned about the composition of a fixed
denominator and the denominator was not fixed.

**P2's own discriminator holds and is checked, not assumed:** `acquisition_term` is unchanged at 227
and `no_observed_history` is 0, so the increment is new arrivals reaching the funnel and not the
term-index mechanism. That is exactly the read P1 and P2 required before attributing it.

**Kept beside the result rather than revised.** The prediction was wrong in direction and the
reasoning behind it was half right. What it cost is nothing — the measurement was the same
measurement either way — and what it buys is the record that the question was designed before the
answer was known.

## 3. The answer to the question that was actually asked

> *"state what that does to the width of the Mann-Whitney null … with an explicit sentence saying
> whether the rank leg got cheaper, the same, or not at all."*

**The same.** The null half-width goes from 0.11280 to 0.11164 — **1.0% narrower** — because the
null moves as `sqrt((n1+n2+1)/(12 n1 n2))` and three more scored decisions on 104 is a 2.9% move in
`n`. Halving that half-width needs **414** scored decisions against today's 107. **A route that
delivers +3 scored decisions per 35 minted arrivals would need roughly 3,600 arrivals on a 232-record
roster to get there**, which is not a roster repair but a different world.

**So this route is closed as a way to buy rank-leg power, and that is worth the hour.** The drawn
item said so in advance: *"it adds fourteen decisions and changes nothing" closes the route and tells
me the ask to the director is the only way.* It adds seven, and it changes the width by one percent.

## 4. What must NOT travel out of this document

**The decision count is a count of opportunities to be graded.** It is not evidence that the
selection leg improved, and no sentence here says it did.

**The AUC fell (0.5566 → 0.5321) and that is NOT a finding about the producer.** It is a different
population — three decisions larger, with a different cast — measured once, with no error bar on the
difference between two AUCs and no second seed. What IS sayable, because each is graded against its
own roster's null: **neither leg clears**, and the ON leg is further from clearing (0.56 null sd
against 0.98). The reading on the page does not change.

**Four of the seven new priced decisions are not scored** (`unmatched_decisions` 4, in 2018, 2020 and
2024, against 0 on the OFF leg): the arm priced them and the world rolled no lifecycle event at that
`(account, term_start)`. That is why +7 priced becomes +3 scored, and it is the funnel's own
`unmatched_meaning`, not an inference of mine.

## 5. Provenance

* Pre-registration: `docs/staging/records/PREREG_DOES_MINTING_DEFAULT_TARIFF_ARRIVALS_WIDEN_OR_NARROW_THE_SCORED_DECISION_POPULATION_2026-09-19.md`, landed `768895de2` before either leg ran.
* Instrument: `tools/arrival_decision_population.py`, controls in `tests/tools/test_arrival_decision_population.py`, three mutations run and each fired on its own leg.
* The crash that blocked the ON leg, and its repair: `3a8d15185`, written up in
  `SEAT_RESULT_THE_WORLD_THAT_MINTS_ARRIVALS_CANNOT_FINISH_A_VALUE_ARM_PASS_...md`. **The repair is
  proven inert on the OFF world by measurement, not by argument: the pre-repair and post-repair OFF
  legs return byte-identical scored rosters and identical counts** (104 priced, 3 declined, 107
  existed, AUC to the last digit).
* Artefacts: `docs/observability/arrival_decision_population_{off,on}_20260919b.json` and the fold at
  `docs/observability/arrival_decision_population.json`. The pre-repair OFF leg is kept at
  `..._off_20260919.json` as the inertness control.
