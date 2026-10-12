**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `unminted`

# The save, the mover offer and the payment work against the director's four principles (2026-10-11)

**Fate (2026-10-12, clear-the-decks):** DONE -- b05429544. four-principles audit reached origin and was sent to the director by NTFY after landing

The director asked at 10:30 (`docs/staging/console/DIRECTOR_CONSOLE_2026-10-11.md`) for each capability
to be checked against four principles. **P1** world first: the household side is built from research,
with ranges where evidence is missing, before the supplier side. **P2** freeze, then solve: the world
is calibrated and fixed, with predictions filed, before a supplier solution is tested against it.
**P3** separate lanes: the supplier reads only through the seam, and strategies are graded on fresh
seeds and across the world's ranges. **P4** truth stays an instrument: probes and holdout truth are
for grading only.

This audit was read at origin `d06b039e7` on 2026-10-11 and **re-read row by row against origin
`2b005a8f6` on 2026-10-12**, before landing. No code was changed. Each remedy below is its own item.
Two commits since the first reading touch its rows, and each is marked where it lands: `77cc6a9a9`
(the hedge volume reads only what the company holds) closes the consumption-forecast leak in §2 P4
and §4, and `f853cd2ff` (a household answers an arrangement offer) is the first work done under the
principles (§6). Line numbers below are origin's at `2b005a8f6`.

## The answer in one paragraph

*Sent to the director by NTFY on 2026-10-12, id `yzf66zm0kGie` (delivery state: delivered), after the landing `b05429544`.*

None of the three is clean. **No capability reads a truth probe at decision time.** I searched
`company/` and `saas/` for the decision probe, the coin-drawn decision set and the holdout truth, and
found only comments that say they are kept out. So P4 holds where it is asked directly. It breaks
one level down. The world loop (`simulation/run_phase2b.py`) **computes the supplier's inputs itself
and hands them in as plain values**. That is how true settled kWh reached the hedge volume and the
mover offer (that one input is closed since, by `77cc6a9a9`; the shape that let it through is not). Every capability breaks P2 and P3. The world response and the
supplier policy landed in the same commits, the world was changed alongside the supplier, and each
result rests on one seed at one point in the world's range. The payment and debt world is the
furthest behind on P1. Of the eight household responses the director listed, only the DD-shock
responses exist, and they ship at a value outside their own labelled range.

## 1. The reactive save on the loss notice

| Principle | Break | Evidence | Remedy (lane) |
|---|---|---|---|
| P1 | **Holds in substance.** The world's answer is the world's existing renewal roll asked again at the save price. It was not built for the save. No save probability was added, and the published save rate (0 to 4.1%) checks the output. | `simulation/save_on_loss_notice.py:12-16`; `run_phase2b.py:3626-3637` | none |
| P2 | The world and supplier sides of the save landed together, in each of its two commits, and the world's switch file was turned on in the same commit as the supplier's sizing. No world prediction was filed before the supplier was tested. | `bfcae065d`, `afd818b22` (14 paths: `company/crm/save_offer.py` with `simulation/save_on_loss_notice.py` and `docs/design/curriculum/save_on_loss_notice_activation.json`) | Pre-register the world's save-rate prediction at the two ends of `world_save_response_scale`, then re-grade (world lane, then supplier) |
| P3 | (a) It was graded in the settled run on **one seed** (the production book to 2025-06-07: 2 offers, 1 save, +£1,582) and at **one world response** (`world_save_response_scale` = 1.0). The two ends of the range were graded only on the lean decision set. (b) The supplier's observable, the published best-deal gap, is a table **in a world file**, and since `d06b039e7` the renewal desk reads it too. (c) The save's inputs are put together **by the world loop**. | (a) `afd818b22` message, "ARMS"; activation JSON `world_save_response_scale.value` 1.0. (b) `simulation/save_on_loss_notice.py:96-124`, handed by the run loop to `company/interfaces/growth_desk.py:410` (renewal, `run_phase2b.py:3290`) and the save (`:3682`). (c) `run_phase2b.py:1200-1211` `_price_match_inputs` | (a) Grade on the authorised fresh seeds × scale ∈ {low, 1, high} (supplier lane). (b) Move `PUBLISHED_BEST_DEAL_GAP_SHARE` to a published-market observable read through the seam (interface-steward). (c) See §5 |
| P4 | **Holds at decision time.** The design choice was not tuned on truth: the director asked for the save, and the price match is a design choice recorded as such (`c50645793`). | `company/crm/save_offer.py:79-87` | none |

### 1a. The renewal cut sized by the price match (`d06b039e7`, 14:46, after his 10:30 instruction)

| Principle | Break | Evidence | Remedy (lane) |
|---|---|---|---|
| P1 | **Holds.** No household response was added; the renewal roll is the world's existing one. | `d06b039e7` touches no world response | none |
| P2 | **Breaks, after the principles were issued.** One commit changed supplier sizing (`DecisionPolicy.retention_cut_sizing`, `growth_desk.retention_cut_share_at_price_match`) **and** a world file (`PUBLISHED_BEST_DEAL_GAP_SHARE` extended back to 2016 Q1). Its predictions were filed, but they were predictions of the supplier's offers, not of the world. | `d06b039e7` stat: `company/interfaces/growth_desk.py` with `simulation/save_on_loss_notice.py` | The best-deal gap series moves out of the world file first (§1 P3 (b)); the standing switch waits for that (interface-steward, then supplier) |
| P3 | **Breaks.** Graded on **one seed**, holdout on, to 2019-12-31 (+£577, which the commit itself says "is not yet a result"). Its observable is the same world-file table handed in by the run loop. | `d06b039e7` message; `run_phase2b.py:3290` | The standing-policy switch is graded on fresh seeds across `world_save_response_scale` before it is turned on (supplier lane) |
| P4 | **Holds at decision time.** No probe or holdout truth is read. | import census of `growth_desk.py` | none |

## 2. The move-with-us offer

| Principle | Break | Evidence | Remedy (lane) |
|---|---|---|---|
| P1 | **Supplier first.** The offer landed 39 minutes before the world's answer. The world's answer has no mover evidence behind it: it reuses a *renewing* household's P(stay), scaled by k ∈ [0,1]. k is a labelled range, which is the right form. Its basis, though, is a proxy chosen to suit the supplier's offer, not household research. | `182337029` (12:58, supplier) then `f1fed7c89` (13:37, world); `simulation/move_with_us_answer.py:221-234` | Research what is known of movers' supplier choice at a move (home_moves.md G8.4 says no take-up rate is published). Either keep k as the whole answer with ranges stated, or build a mover-specific response from evidence (world lane) |
| P2 | One commit changed the world and the supplier together: it widened the offer to default-tariff movers **and** added the world's default-tariff answer **and** a new world destination draw. | `68793db33`: `company/crm/move_with_us_offer.py` + `simulation/move_with_us_answer.py` + `simulation/move_destination.py` + `simulation/household_demand.py` | Freeze the mover world (k range, destination draw) with its predictions filed, then re-grade the offer (world, then supplier) |
| P3 | Graded on **one seed** (40 founders, budget 0, base seed). The result turns entirely on k (0 vs +£1,580). It was graded across k, which is right, but on one seed. The offer's consumption input is put together by the world loop (§5). | `68793db33` message "Measured, 40 founders, budget 0, base seed"; `run_phase2b.py:4075-4080` | Fresh seeds × k ∈ {0, mid, 1} (supplier lane) |
| P4 | **Broke through its input; closed since the audit by `77cc6a9a9`.** At `d06b039e7`, `annual_kwh` was `company_eac_kwh` from `_company_eac_estimate`, which summed the **settled** fold's true kWh. On origin it asks `company/interfaces/sim_interface.supplier_annual_volume_kwh` with only the register reads that arrived before the term and the registry EAC/AQ. The value still reaches the offer as a plain number from the run loop (§5). | `run_phase2b.py:1165-1197`, `:3081`, passed in at `:4140`; `tests/simulation/test_the_hedge_volume_reads_only_what_the_company_holds.py` | Spent for this input. The general remedy is §5 |

## 3. The payment and debt work so far

| Capability | Break | Evidence | Remedy (lane) |
|---|---|---|---|
| Expected-loss provision from a forward cash forecast (`16ba6249c`) | **P1/P2.** A supplier piece built before the world's payment behaviour exists or is frozen. Its roll rates are learned from a book in which households answer no plan offer, early contact or breathing space. It reads only the company's own ledger (import census), so **P3/P4 hold**, and it has no production caller yet. | `company/finance/cash_forecast_provision.py:27-28`, imports `:38-40`; no caller outside tests | Do not run the accuracy measurement until the payment-behaviour world (step 2 of the handoff) is frozen. Then grade on fresh seeds (supplier lane) |
| Provision as the company's own aged-receivables stock (`42b2eb254`) | **P3/P4 hold.** It is a stock over the company's payment-seam ledger, read after the run by value date, and one mutation reds if a world input reaches it. It makes no decision. **P2:** it has not been read on a run yet, and its six predictions are filed. | `42b2eb254`; `run_phase2b._company_provision_by_year_end` | Read it on the frozen world (supplier lane) |
| DD-shock response (`d2dddf804`, world) | **P1, mostly held.** Built from research (`what_bill_shock_is.md` DD4b), with no supplier policy referenced and three labelled ranges. **But every toggle ships at 0, below each range's own low end** (cancel 0.01-0.10, failure uplift 0.25-3.0, complaint 0.02-0.24). So the default world is one the evidence says is too quiet, and a supplier graded at default meets no penalty. **P2:** no predictions filed at the range ends. Measured on one 40-founder seed, which held 2 shocks. | `simulation/dd_shock_response.py:20-23`; `d2dddf804` message; `docs/market_research/assumption_toggles.yaml` `dd4b_*` | Set the frozen world's value inside the range or name it as a sensitivity end, and file predictions at low and high (world lane) |
| The rest of the household payment side | **P1, the first gap — being closed now.** The director's list has eight responses: a lower-payment offer, breathing space, early contact, a changed DD amount, a changed DD date, mandate cancellation, a switch to manual payment, and stopping paying. At `d06b039e7` only mandate cancellation existed, and only as a reply to a DD shock, and a plan offer was answered `accepted=None`. **On origin, `f853cd2ff` answers the plan, lower-payment and pause offers from the household's own money, with five ranged toggles shipped off** (§6). Early contact is step 2 and landed during the re-read (`9ca9624fc`, one toggle, shipped off); own-reasons cancellation and the DD amount/date answers are steps 3-4 of the same freeze, still landing. A household's payment outcome in the arrears engine still does not read plans. | `simulation/plan_offer_response.py:9-17`; `simulation/arrears_engine.py:469` `payment_outcome` (stress and RNG only) | The household payment-behaviour lane from research, with labelled ranges, frozen with predictions (world lane). This is handoff step 2 |

## 4. Supplier policy living in world files

| Where | What policy | Principle | Remedy (lane) |
|---|---|---|---|
| `simulation/dd_balance_book.py:125-130`, `:141-160`, `:207`, `:337-470` | The DD review's **rule** (`last_year_spend` or `consumption_at_rates_in_force`), its **annual cadence**, and whether it **seeks the balance**. The amount is asked through `company/interfaces/dd_review_outcome.py`, but which rule and when are chosen in the world. The DD-shock trigger (§3) is computed from it, so the world's response keys on a supplier policy that the supplier cannot change per account. | P3 | The review becomes a company decision, `company/billing/dd_review_runner.py`, per account, and the world receives the amount set (supplier lane + interface-steward) |
| `simulation/run_phase2b.py:1165-1197` `_company_eac_estimate` | At `d06b039e7` the supplier's consumption forecast (trailing 12 months of true settled kWh, first-term fallback times the household multiplier) lived in the world loop. **P4 closed by `77cc6a9a9`:** the forecast is now `sim_interface.supplier_annual_volume_kwh` over arrived reads and the registry figure. What remains is P3: the world loop still selects which reads arrived and hands the number in. | P3 | Covered by §5 (interface-steward) |
| `simulation/arrears_engine.py:205-207`, `:635-680`, `:749`, `:785-848` | The world's arrears path carries collections policy: the notice schedule (+7, +21 days, "payment plan offered"), the write-off date convention, DCA placement and debt-sale timing, and the per-bucket provision rates. It runs **in parallel with** the company's own `collections_journey`, so there are two dunning paths and only one of them is the supplier's. | P3 | Make the company journey the only dunning path, and have the world answer only the household's side (payment, cure, default). A world-and-supplier split, sequenced after the payment-behaviour world (world + supplier lanes) |

**A correction to the item.** The item placed the collections view at `simulation/arrears_engine.collections_view`. On origin it is company-side: `company/billing/arrears_engine.py:891` `collections_snapshot`, called from `company/billing/payment_observation_consumer.py:2125` over the company's own ledger. So the credited-account dunning defect (`SEAT_FINDING_A_CREDITED_ACCOUNT_IS_DUNNED_..._2026-10-11.md`) is a domain correctness defect inside the supplier's lane: the view sums overdue items gross, while SLC 27.16 nets credits. **It is not a breach of the line.** Its remedy is the supplier lane's, as filed.

## 5. The structural break behind P4

The world loop computes the supplier's inputs and passes them to supplier functions as plain values:
`_price_match_inputs`, `company_eac_kwh`, `unit_rate`, `company_fwd`. Nothing checks that a value
handed in this way is something a supplier could observe. The hedge leak happened this way, and the
mover offer inherits it. **Remedy (interface-steward):** every value a supplier decision takes from
the run loop is named once in a typed seam record, and a control refuses one built from a world-only
source. This is the one mechanism that would have caught the hedge leak, so it should come before the
per-capability fixes.

## 6. The first work done under the principles: the household's answer to an arrangement offer (`f853cd2ff`)

| Principle | Reading | Evidence |
|---|---|---|
| P1 | **Holds.** World only, and knowledge first: every choice has a published range and its gaps are named before the build. The household answers the offer it is sent, with no reference to who sends it. | `docs/market_research/domestic_repayment_plan_take_up_and_keep_rates.md`, "The world's answer to an offer"; five toggles in `assumption_toggles.yaml` (`plan_take_up_share` 0.32-0.53, `plan_break_share` 0.45-0.65, `plan_weeks_to_recover` 46-96, `plan_lower_payment_failure_elasticity` 0.25-1.0, `plan_pause_resume_failure_share` 0.09-0.40) |
| P2 | **Holds, with one caveat stated by its author.** The four mechanisms ship off (book_diff IDENTICAL BOOK), no supplier arm has been run against them, and predictions of the world's own behaviour at low and high were filed at 04:49Z, before steps 2-4 were run and before `f853cd2ff` landed (05:05Z). The plan-offer rows were seen at step 1 and are marked "not blind" in the file itself; every other row is blind. | `/var/tmp/wp_runs/freeze/predictions.md`, sha256 `b9985b061629671d2d26b98ef3b9ce43f76befa17afc0c3f30bf4d1206f58455`; freeze record draft `/var/tmp/wp_runs/freeze/head.md` |
| P3 | **Partly.** The only supplier-side change is the seam (`answer_plan_offer` gains an optional offer shape). The low/high runs are one book (40 founders, budget 0, one seed). That is a world calibration, not a supplier grade, so one seed is the right size for it; the supplier grade that follows must use fresh seeds. | `f853cd2ff` stat; message "Low setting, same book" |
| P4 | **Holds.** The household reads its own stress; nothing crosses to the supplier but the answer. | `simulation/plan_offer_response.py` |

The predictions file lives in `/var/tmp` and is not yet in the repo. It is quoted by hash here so that
the freeze record, when it lands, can be checked against what was filed. Its named refutations: any
non-zero count where 0 is predicted, a plan count differing from step 1, or more than 7 own-reasons
cancellations at high.

## Order I recommend

1. The payment-behaviour world (P1), frozen with predictions (P2). **In flight:** step 1 is `f853cd2ff`, step 2 `9ca9624fc`; steps 3-4 were landing at the re-read (§6).
2. The seam record for run-loop inputs (§5). The one company consumption forecast is done (`77cc6a9a9`).
3. Re-grade the save and the mover offer on fresh seeds across their world ranges (P3).
4. Move the DD review and the world-side collections policy into the supplier's lane (§4).

## Queued (2026-10-12)

Each remedy still open is a seat continuation with a lane (`python3 -m background.seat_continuation --list`):

| Id | Lane | Remedy |
|---|---|---|
| `four-principles-a-typed-seam-record-for-run-loop-inputs` | W4_the_wall | §5 |
| `four-principles-the-best-deal-gap-is-a-published-observable-through-the-seam` | W4_the_wall | §1 P3 (b), §1a P2 |
| `four-principles-dd-shock-and-the-plan-world-filed-at-their-range-ends` | W2_customer_generator | §3 DD-shock, §1 P2, §2 P1/P2 (world predictions at the range ends; mover k from research) |
| `four-principles-the-save-mover-and-renewal-cut-graded-on-fresh-seeds-across-world-ranges` | C_customer_ops | §1 P3 (a), §1a P3, §2 P3; after the two above |
| `four-principles-the-provision-is-measured-only-on-the-frozen-payment-world` | E_finance_treasury | §3 provision rows |
| `four-principles-the-dd-review-and-dunning-move-to-the-supplier` | D_billing_metering | §4 rows 1 and 3 |

## Limits

I read the code and commit messages. I ran nothing. The 2026-10-12 re-read checked each cited
commit is an ancestor of origin and each cited function at its current line. The seed counts come from the commit messages
and were not recounted from artefacts.
