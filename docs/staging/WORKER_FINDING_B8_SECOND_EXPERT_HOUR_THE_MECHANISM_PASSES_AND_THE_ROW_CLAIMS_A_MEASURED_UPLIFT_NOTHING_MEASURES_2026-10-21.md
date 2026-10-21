**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`
**Knowledge:** none -- a blind review graded against the tree; no new domain claim

# B8's second Expert Hour: the mechanism passes and the claim does not. The row promises an uplift "proven by measured uplift", and at this scale nothing measures it (2026-10-21)

*Worker tick, 2026-10-21. This pass re-runs the 2026-10-11 one
(`docs/staging/done/SEAT_FINDING_B8_EXPERT_HOUR_THE_RUNS_HOLDOUT_FLIPPED_ITS_COIN_BEFORE_THE_GUARD_AND_KEPT_ONE_ARM_ONLY_2026-10-11.md`),
because each disqualifier it raised (Q5, Q7, Q8, Q10 and Q11) has had a build or a printed answer since.*

## How it was run

- **The reviewer.** A fresh instance with no tools. It was shown only the `tools/blind_review.py` packet: the domain was UK domestic energy retail pricing and retention, and the persona the same retention-holdout veteran as on 10-11.
- **The description.** It was restated to match today's design. The coin is flipped only over would-offer renewals, and the decision is read on both arms. The cut is floored at the renewal's own cost floor. The outcome window is unset, so no row closes. The decision is expected value under a published prior. The price match was tried and withdrawn. The run's figure is that 3-4 of 92 offers pay.
- **The record.** Its priors, its first doubt and a 14-question battery (8 disqualifying) were recorded with `--record` at 2026-10-21T04:00:00Z, in `docs/observability/blind_review_ledger.jsonl`, before any of its answers were graded.
- **Its limit.** Restricted context gives blindness, not independence: the reviewer is the same model family as the builder.

**Its first doubt, verbatim in substance.** The decision rests on a prior from the wrong population (default-tariff stock), the wrong window (30-day switching) and the wrong comparison (a saving against the market, not a cut against our own price). With the window unset and the holdout off, "the learning leg is decorative". What the company is actually claiming is "we imported two gradients and a margin model, and the arithmetic says almost never cut". That may well be the right answer, but it is not evidence that the offer works.

## Adjudication against the code, not the description

| # | Disqualifier | Verdict | Evidence |
|---|---|---|---|
| 1 | The response depends on the post-cut gap to the market, and is zero when no competitive fix exists (2022) | **PARTLY** | The offer is gated on the market: no offer is made unless `_market_beats_the_fix` and `_offer_can_buy` (the discount must win the fix against the published default). So in a 2022 with nothing to switch to, nothing is offered (`simulation/run_phase2b.py`, the retention block). But the belief itself is linear in the cut in pounds (`stay_per_pound.mean x cut_gbp`), and it is not a function of the gap that remains after the cut. The prior's comparison mismatch is named in the module ("a different decision") and is not converted. |
| 2 | A negative remaining margin buys no offer | **CLOSED** | `_cut_on_value`: when the margin is 0 or less, the lifetime is 0 or less, so `with_cut < without` for any cut 0 or more and any effect 0 or more. Never cuts. |
| 3 | With the window unset, can any row close? | **CLOSED by admission, and it is the open defect** | `RETENTION_OUTCOME_WINDOW_DAYS = None`, and `closed_before` returns `[]`. The module and the packet both say the company learns nothing from its own holdout, and the prior decides alone. The reviewer accepts the admission as an answer. But the admission contradicts the row's own claim (below). |
| 4 | Home moves are kept out of the price-churn outcome | **CLOSED** | `RetentionHoldout`: "A move-out is not a loss notice and does not count against the row". The outcome reads `CoSRegister.losses_notified()` only. |
| 5 | The cut is costed on the household's own forward volume and charged to every acceptor, deadweight included | **CLOSED** | `decide` sizes `cut_gbp = cut_per_mwh x billed_kwh / 1000` on the term's own EAC. `_cut_on_value` charges it to `p0 + effect` of the book, so the share that would have stayed anyway (`p0`) pays too. |
| 6 | The minimum detectable effect at about 46 per arm, and a value-of-information case | **PARTLY** | `decisions_needed_per_arm` exists, and 10-11 printed about 19,600 per arm against about 30 decisions a year. The holdout is off on every standing policy. No value-of-information figure has been computed, either for what holding out costs or for the book size at which the holdout would pay. |
| 7 | The coin falls after eligibility on identical rows, and the held-out arm gets the business-as-usual renewal | **CLOSED** | The 10-11 Q11 fix: `would_offer` is read before the coin on both arms. The held-out arm is re-fixed at the uncut rate (`_no_offer_reason = "held_out"`). The coin is `sha256(account, day)` and draws on nothing the world drew. |
| 8 | Saves and cooling-off cancellations count alike on both arms, and the primary outcome is defined before the save | **PARTLY** | `saved_on_loss_notice` is carried on both arms, so the pre-save outcome can be derived. But the estimate counts a save as a stay, so the primary outcome is defined after the save. The world has no cooling-off cancellation (no mid-term exit). That is a world gap, recorded here and not filed separately: at the founders' scale it moves nothing. |

| Supporting | Verdict | Evidence |
|---|---|---|
| 9: converting a 30-day default-stock gradient to a renewal window | **OPEN, named** | The module calls the gradients observational and "generous to the offer". The reviewer argues the opposite direction for fix-enders: their response is steeper, so the prior biases LOW. The two directions are not reconciled. That is a knowledge question for `how_households_respond_to_supplier_contact.md` §6. |
| 10: end-of-fix churn by year | not graded here | This belongs to the world's churn calibration rows, not to B8. |
| 11: observable covariates for heterogeneity | **PARTLY** | The L2 harness reads `SAVE_POSITION_OBSERVABLES` (acquisition route, days on default, ever actively renewed). The run's belief pools them all. |
| 12: the size of the 3-4 paying cuts | **OWED** | It can be printed from the published `retention_log`. Not printed this turn. |
| 13: the cost floor's definition | not re-graded | The floor is the renewal chain's own (`DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR`). Its composition is outside B8's scope. |
| 14: extending the spread sensitivity to 3-5x | **OWED, cheap** | 10-20 printed 0.43x-3x. The reviewer's engaged-population range runs to 5x. |

## Verdict: FAIL, held at L2, on the claim and not the mechanism

All five mechanism disqualifiers that 10-11 left open are now answered in code, and none of today's eight finds a live defect. What fails is the row. Its name promises price sensitivity "DISCOVERED from observed responses ... with a holdout group so 'this segment justifies its treatment' is proven by measured uplift rather than asserted". In the run today:
- no holdout row ever closes (the window is a named `None`),
- the holdout is off on every standing policy, and
- even with a window set, about 46 rows per arm against about 19,600 needed leave the belief at the prior's under any spread from 0.43x to 3x.

So the decision is the published prior's. That is an honest outcome, and arguably the right one for a 400-home supplier. But it is not "measured uplift". This is D48's shape (2026-10-14): the measure is honest and the row over-claims.

**What would move it to L3, in order:**
1. **The claim.** The row has to state what the run does: it decides on expected value under a published prior, runs a holdout that cannot decide at this scale, and names the scale at which it would. The title is B8's BACKLOG wording, so rewording it changes no ruling of the director's. It is still left for the seat's own pass on the row (G9's "asked to see" does not apply, and the map-row byte budget is tight). It is recorded here, not done.
2. **Q6, a value-of-information figure.** Compute what holding out costs per year (the paying offers withheld from the held-out half: about 2 a year on 3-4 of 92) against the book size at which the interval decides. One printed table, no world change.
3. **Q3, the window.** The reviewer's practice basis is "fix end plus 30-90 days". In this world the decision IS the fix end, and there is no mid-term exit, so any window under a year reads as the decision-day outcome (10-11's measurement: 9 of 10 later losses sat at 365 days). A window of 30-90 days would therefore make rows close without changing their stay, so the learning leg goes live and the decision does not move. That is K4's "practitioner starting point", from a blind persona, not a practitioner. It is a domain constant and needs its origin, so it is not set this turn.
4. **Q9 and Q14** are knowledge and printing, and do not block.

Reverse: this commit adds a finding, one ledger row, one simplification entry and the map row's `expert_hour.last`. Revert it to undo. No code or policy moves.

## 2026-10-21 (07:20Z): Q6 pre-registration, written before the table is printed

**What is measured.** There are three quantities, each in pounds per year, on the published run's `retention_log`
(ad8afadc5, 92 offers, 2016-2025). For every row, `c` = `retention_cost_gbp` (the cut), `p0` = 1 - `company_churn_estimate`
(the company's own stay belief), `L` = `expected_term_margin_gbp`. Each row is valued as `_cut_on_value` values it, so
V(theta) = (p0 + theta c)(L/(1-p0) - c) - p0 L/(1-p0), where theta is the true stay bought per GBP.
1. **Holdout cost (today's design).** Half the expected value of the offers the prior says pay, `0.5 x sum max(0, V(mu))`. That is what the held-out arm gives up, in expectation, under the company's own belief.
2. **EVPI.** The expected value of PERFECT information on theta under the prior N(mu, sd = mu): `sum E[max(0, V(theta))] - max(0, V(mu))`, in closed form. No holdout at any size can be worth more than this.
3. **Decision-relevant scale.** The households per arm needed to tell the median row's break-even effect from zero at the module's own 95%/80%, converted to a book size at the run's own rate of would-offer rows per household-year.

**Prediction.** EVPI is under GBP 5 a year for the 400-home book. The holdout cost is under GBP 10 a year. The book size at which one arm reaches the decision-relevant count is over 100,000 households.
**What refutes it.** EVPI over GBP 5 a year refutes the prediction, and would mean the prior's spread leaves real money on the table. A book size under 100,000 also refutes it.
**A structural point, noted before printing.** A row is written only where the company would offer. So today's holdout randomises only among renewals the prior already says pay, and it gathers no evidence at all on the roughly 88 of 92 where the prior says no. That is the side where a wrong prior would cost money.

## 2026-10-21 (07:30Z): Q6 graded. The holdout costs about as much as perfect information is worth, and buys almost none of it

Printed on the published `retention_log` (ad8afadc5, 92 offers over 10 years), with the module's own constants. The holdout cost and EVPI are per year.

| belief on theta | offers that pay | EV of the paying offers | holdout cost/yr | EVPI/yr |
|---|---|---|---|---|
| prior midpoint, sd = mean (the run's) | 4/92 | GBP 199.10 | **GBP 9.95** | **GBP 10.18** |
| CMOL end | 3/92 | 32.36 | 1.62 | 15.41 |
| CMOC end | 4/92 | 393.64 | 19.68 | 5.14 |
| midpoint, sd = 3x mean | 4/92 | 199.10 | 9.95 | 46.60 |
| midpoint, sd = 5x mean (the reviewer's Q14 range) | 4/92 | 199.10 | 9.95 | 86.20 |

- **The median row** breaks even at 0.000860 stay per GBP, which is **9.4x the prior mean**, and the prior gives that probability 0. Telling its break-even effect (0.0069 of staying, p0 0.529) from zero at the module's 95%/80% needs **83,160 decisions per arm**. The run makes 9.2 offers a year, so that is about 18,000 years of this book's offer flow, or a book millions of homes in size for one year.
- **Where the EVPI sits.** 99.6% of it sits on the **4 rows the prior already says cut**, and 95% on one prospect (PROS-2022-0400, with term margins of GBP 5,380 and GBP 3,512). There the risk is that the prior is too generous and the cut is wasted. The 88 no-cut rows together carry under GBP 0.50 of EVPI over the decade.

**The prediction, graded.**
- "EVPI under GBP 5/yr": **refuted** on the high side, at GBP 10.18. It is one household's large margin, not the book.
- "Holdout cost under GBP 10/yr": **held**, just, at GBP 9.95.
- "Book over 100,000 households": **held** by an order of magnitude and more.
- **The structural point is corrected beside the claim.** I wrote that today's holdout "gathers no evidence on the side where a wrong prior would cost money". That is wrong. The money at risk is on the cut side, which the holdout does randomise. The no-cut side is worth almost nothing to learn about, because the prior puts no weight near those rows' break-even.

**What it means for the row.** At the founders' scale the holdout costs about GBP 10 a year, which is the whole of EVPI. EVPI is the ceiling on what any information is worth, and a holdout yielding about 0.4 rows a year captures a vanishing share of it. So **holdout off on every standing policy is the value-maximising setting at this scale**, not a gap. This closes Q6 with a number. The L3 claim the row can honestly make: the company decides on expected value under a published prior, prices what an experiment would cost and be worth, and declines it below the scale where it pays. That reword is the seat's pass on the row (item 1 above), and it is still not done here.

Probe: the pre-registration's V(theta) and EVPI formulas, run over `tools.run_output_store.load_run_output('docs/reports/run_output_latest.json.gz')['retention_log']`. EVPI is the normal closed form E[max(0, A+B theta)] = m Phi(m/s) + s phi(m/s), with m = A+B mu and s = B sd. It takes about 5 s.
