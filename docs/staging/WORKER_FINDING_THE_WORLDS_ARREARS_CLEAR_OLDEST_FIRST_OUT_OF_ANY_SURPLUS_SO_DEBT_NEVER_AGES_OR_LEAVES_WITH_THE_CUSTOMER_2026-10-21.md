**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `say-whether-the-crisis-bad-debt-gap-is-arrears-volume-or-provision-rate` (Lane 0 delivery)
**Knowledge:** none -- grades the world against the aged-debt and arrears-stock figures already recorded in docs/market_research/ASSUMPTIONS.md (2026-10-04 arrears-prevalence row) and docs/market_research/bad_debt_provisioning.md §3.1-3.2; no new domain claim

# The world's arrears clear oldest-first out of any surplus, so its debt never ages or leaves with the customer (2026-10-21)

**What it unblocks:** the BLOCKING crisis bad-debt finding
(`SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_..._2026-10-14.md`, section "2026-10-21 (night)").
That section splits the company's 2.5x shortfall under the 1% floor. Arrears volume carries x1.84 to
x2.25 of it and provision rate x1.11 to x1.36. The volume side is this item.

**What the switch-on run (ec7fd9942) shows, at year-ends:**
- **The receivable is the right size.** It is 8.8% of revenue in 2022, against Centrica's derived 8.9%.
- **The debt is the wrong age.** Live pay-on-receipt debt over 90 days is 8.8% of the PoR balance in
  2022 and 30.6% in 2023. Centrica's implied share is about 60% and about 75%.
- **Almost no debt leaves with a closing account.** The final-bill balance is 0.01% and 0.11% of
  revenue in 2022 and 2023, against Centrica's 1.8% and 1.9%.
- **No live DD balance ever reaches 30 days.** Centrica held GBP 66m of DD debt over 90 days in 2022.
- **2024 releases the aged debt.** Live PoR over 90 days falls from 4,589 to 1,942 and is paid, not
  written off. Over the same period Ofgem's arrears rose and Centrica's provision rose.

**The suspected mechanism:** `simulation/household_budget.BudgetPaymentBook.settle_month` pays
unpaid bills whole and oldest first out of any month's surplus. A household whose margin turns
positive clears its oldest debt first. The record says the opposite: aged debt (>12 months) is 52-65%
of the arrears stock, and PPM repayment plans average 6.6-7 years.

**Work, in order:**
1. **Grade first, before any change.** Extend `tools/grade_world_debt_against_ofgem.py` to report the
   world's arrears by age (>12 months share of the >91-day stock). Grade it against the 52-65% band.
   No tuning toward company results.
2. **Trace the DD zero.** Is a failed DD always re-presented and paid in the world, or does the
   company's method register re-file the account as PoR? Find out which side it is before counting
   it as world volume.
3. **Trace why leavers carry no debt.** Look at the 70% of indebted switchers who are allowed to
   leave (ASSUMPTIONS row 634), and at home-move leavers. Where does their unpaid balance go?
4. **Only then a world change,** knowledge page first (K8). Candidate: a household back in surplus
   repays at a plan rate, not by clearing everything at once. The rate must be sourced, or carried
   as a GAP.

**Prediction for step 1, filed before it runs:** the world's share of >91-day arrears that are
older than 12 months sits below 52% in 2022-23, and below 30% at Q4 2024.

## 2026-10-21 (late): step 1 graded. The prediction is refuted. The world's debt does age, and it does leave with the customer

**How it was read.** `python3 -m tools.grade_world_debt_against_ofgem age` (new in this commit) was run on two
captures that already existed. No new run was made. The captures are
`/var/tmp/budgetpay/world5_on_shared_shortfall.json` (the default dice) and `seed2_shared.json` (dice seed 2).
Both have both budget switches on and run to 2024-12-31. Both were captured after 78a36a84c (the income
re-draw) and 15a497992 (the shared shortfall). That is the same world as the ec7fd9942 switch-on arm: ec7fd9942
changed only the company side. The two captures share one cast, so the interval resamples accounts across
both. Only Q4 2023 is graded. Energy UK's 65% is for 2025, and no capture reaches a 2025 quarter end.

**The share of the >91-day stock that was due a year or more before the quarter end.** Bills are counted, with
the 95% account-clustered interval in brackets. Pounds come from each capture's `bills` side table.

| Q4 | elec bills | elec pounds | gas bills | gas pounds | Energy UK |
|---|---|---|---|---|---|
| 2021 | 87% [78-93] | 85% | 88% [76-96] | 90% | not published |
| 2022 | 70% [54-85] | 56% | 71% [50-91] | 64% | not published |
| 2023 | **73% [57-88]** | **47%** | **79% [58-95]** | **60%** | **52%: NOT MET, HIGH (bills)** |
| 2024 | 72% [55-88] | 67% | 72% [51-94] | 76% | 65% in 2025, beside |

**The prediction said below 52% in 2022-23 and below 30% at Q4 2024. It is wrong.** It stays here as
written. By bill count the world's stock is *older* than the record. By pounds it is close to the record:
47-60% in 2023 against 52%, and 67-76% in 2024 against 65% in 2025. The pound share is lower in 2023 because
the crisis-year bills are bigger and newer, not because old debt clears. Energy UK does not say whether its
share counts pounds or debts, so the bill verdict is not the whole answer. On neither basis is the world's
debt young.

**Where the world's >91-day stock sits, in pounds.** A closed account here is one not billed in December. That
is the tool's own denominator convention, and it stands in for "left".

| Q4 | live accounts | of which aged | of which DD method | closed accounts | of which aged |
|---|---|---|---|---|---|
| 2022 (default / seed 2) | 3,790 / 3,299 | 1,525 / 977 | 757 / 450 | **1,891 / 2,984** | 1,840 / 2,692 |
| 2023 | 7,092 / 6,830 | 2,088 / 2,778 | 2,204 / 1,803 | **2,369 / 3,107** | 1,974 / 2,918 |
| 2024 | 4,683 / 4,098 | 2,846 / 2,451 | 1,597 / 1,324 | **3,496 / 3,868** | 2,815 / 3,230 |

**What this does to the split in the BLOCKING finding.** That finding named the side as the world. On the
world's own truth that is not right:
- **Leavers do carry debt.** Closed accounts hold £1.9k-3.9k over 91 days, a quarter to a half of the stock,
  and almost all of it is over a year old. The company's final-bill balance was 0.01% and 0.11% of revenue in
  2022 and 2023. That is about £34 and £540. Revenue is derived from the seat's own figures: 1,825 / 0.53% ≈
  £344k and 1,529 / 0.31% ≈ £493k. So the company books between a fiftieth and a quarter of the closed-account
  debt the world holds.
- **DD-method debt does age.** £450-2,200 of DD-method bills are over 91 days unpaid in the world. The company
  reports no live DD balance aged 30 days or more.
- **Live pay-on-receipt debt roughly agrees.** The world's live non-DD stock over 91 days is about £4.9k in
  2023 and £3.1k in 2024. The company's PoR >90 bucket is 4,589 and then 1,942. The world's own 2024 fall is
  real: its live >91-day stock drops by about a third, which is the oldest-first clearance this item
  suspected. But its aged stock and its closed-account stock both *rise*. The total >91-day stock falls only
  14-20% (£9.5k to £8.2k, and £9.9k to £8.0k).

**So the volume gap is mostly in what the company books, not in what the world holds.** Steps 2 and 3 above
(trace the DD zero; trace where a leaver's balance goes) are now the item, and they are the company's or the
seam's question, not the world's. Step 4 (a world repayment-plan rate) is **withdrawn** on this evidence: the
world's aged share is already at or above the record. What I cannot yet say: whether the company loses the
debt when it re-files a failed DD account as PoR and when an account closes, or whether the world's settlement
reaches the company's ledger by a route the provision does not read. Prediction for step 3, filed before it
runs: most of the closed-account world debt never appears as a final-bill balance in the company's
`company_provision` at all, rather than appearing and being written off early.

**Caveats.** There are two dice seeds and one cast: one 400-founder book. "Closed" is "not billed in
December", which is a proxy. The captures are not the published run, so they are labelled unpublished.

## 2026-10-21 (late evening): steps 2 and 3 traced. The step-3 prediction is refuted

The trace is in the BLOCKING finding, section "the trace". In short:
- **Step 2.** The DD zero is the company's bucketing rule: a DD bill unpaid at 30 days or more is filed on the
  pay-on-receipt row. It is not a lost pound.
- **Step 3.** Every closed-account pound reaches the company. The company holds it, then writes it off at 365
  days, and world closed debt equals company held plus written off, to the penny in 2018-19. The prediction above
  ("never appears") is wrong, and it stays here as written.
- **Beside step 1's grade.** The age table above is per bill. The company ages its rolling balances oldest
  first, and on the same pounds that gives a >91-day stock 2-10x smaller. Which convention Energy UK's 52% uses is
  a GAP. So "older than the record" holds on the per-bill convention only.

What remains here is the world's indebted-leaver **flow**, which falls from about £1k a year (2017-18) to £100-324
(2022-23). The leaver census in the BLOCKING finding's next step asks whether that is founder-book selection or a
world rule.

## 2026-10-21 (night): the leaver census by route. A world rule, the one the record has: switching froze. Not selection, not the debt objection

**Instrument.** `/var/tmp/leaver_routes/dump2.py` re-runs the BLOCKING finding's `dump.py` configuration (shared tree,
HEAD 7a7ad95dc, both budget switches on, default dice, to 2023-12-31) and also keeps the run's move-out, SVT-exit and
renewal logs, which the first dump dropped. So the item's "needs no compute" was wrong: the leave route was not in any
existing output. It reproduced the same world exactly: 45,555 records, and the same leaver and debt totals as the
landed census. `census2.py` reads it. A leaver and its debt are defined as in that census: last bill at least 62 days
before the end, and the world's unpaid pounds 62 days after it. The route is the log event within 120 days of the
last bill. 4 of 1,060 leavers (2017-2023) match no route. One book, one dice seed, unpublished.

| year | accounts on supply | movers: left / in debt / GBP | switch at renewal | switch by SVT exit | switching rate (DESNZ) | in-debt share of leavers | renewal rolls / objection-eligible / blocked |
|---|---|---|---|---|---|---|---|
| 2017 | 798 | 32 / 1 / 21 | 63 / 2 / 154 | 94 / 7 / 890 | 19.7% (18.2%) | 5.0% | 128 / 9 / 1 |
| 2018 | 666 | 35 / 8 / 428 | 23 / 4 / 122 | 103 / 11 / 565 | 18.9% (19.1%) | 14.2% | 107 / 4 / 0 |
| 2019 | 572 | 36 / 10 / 466 | 10 / 0 / 0 | 83 / 10 / 362 | 16.3% (20.8%) | 15.3% | 86 / 2 / 1 |
| 2020 | 513 | 37 / 5 / 174 | 23 / 2 / 40 | 53 / 2 / 145 | 14.8% (20.2%) | 8.0% | 60 / 7 / 1 |
| 2021 | 463 | 26 / 4 / 130 | 13 / 1 / 136 | 25 / 2 / 85 | 8.2% (15.6%) | 12.1% | 69 / 7 / 3 |
| 2022 | 430 | 18 / 3 / 192 | 0 / 0 / 0 | 9 / 0 / 0 | **2.1% (3.05%)** | 11.1% | **0** / 0 / 0 |
| 2023 | 458 | 13 / 1 / 154 | 0 / 0 / 0 | 17 / 2 / 178 | **3.7% (6.3%)** | 10.0% | 26 / 1 / 0 |

The switching rate is the world's switchers over accounts on supply. The bracket is
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`, the whole-market rate over all accounts,
which is the same basis.

**Answers to what the item asked.**
- **Selection: no.** The in-debt share of leavers runs 5-15% with no trend and no crisis break. Indebted households
  leave as often as before. There are just far fewer leavers.
- **The debt objection: not the mechanism.** It blocks 0-3 departures a year, and **none in 2022-23**. In 2022 the
  world made no renewal roll at all. The world applies SLC 14 at the renewal roll only (`simulation/debt_objection.py`,
  gap 6), and every crisis switch was an SVT exit, which it never blocks. If it did block them at its 28.3%, it would
  stop about 0.6 of 2023's two indebted SVT leavers. That is under GBP 60.
- **The world rule: the switching freeze, sized like the record.** The world's switching fell from 19-20% (2017-18,
  record 18-19%) to 2.1% and 3.7% (record 3.05% and 6.3%). Both crisis years read below the record, but on 9 and 17
  switchers. In 2019-21 the world sits 4-7 points under the record, and that gap is the departure anchor's, not this
  item's.
- **Movers held roughly steady.** Electricity move-outs per electricity account were 3.9-6.7% a year from 2017 to
  2022, then 2.3% [0.8-4.9] in 2023 (Poisson 95%). That interval overlaps 2017's [2.3-6.2]. Moves fall in every tenure
  (from the move-ins' `vacated_tenure`), so this is not renters leaving a closed book first. A move cannot be
  objected to in the world. Movers' debt per indebted leaver rose from GBP 21-53 (2017-19) to GBP 64 and 154.
- **Arrears age at closing.** The oldest unpaid bill's age at the closing date, median over indebted leavers: movers
  48 days in most years (the final bill itself), 413 in 2022. Switchers 110-353 days. On 1-11 leavers a cell, these
  are descriptions, not estimates.

**Against `docs/market_research/bad_debt_provisioning.md`, 2021-2023.**
- The world made 8, 3 and 3 indebted leavers, leaving GBP 378, 192 and 332.
- Centrica's final-bill gross receivable is GBP 162m, 201m and 280m: +24% and +39% a year while switching froze.
- Centrica publishes no final-bill **flow** and no **count** of indebted leavers. That is a **GAP**, so the flow
  cannot be graded.
- Graded on a stock instead: the world's closed-account debt over 91 days (never written off, from "the trace") as a
  share of world gross receivable is 27%, 10% and 14%. Centrica's final-bill share is 27%, 20% and 17%. That matches in
  2021 and runs about half in 2022 and two-thirds in 2023. But in 2022-23 the world's denominator is the live
  receivable, and that grew 3.5x. So the stock is short because the live book swelled, not because leavers stopped
  carrying debt.
- The real final-bill stock still grew 73% over two frozen years. No published figure says which route carried it.
  The candidates are movers (whose move rate does not freeze), bigger crisis bills, and a write-off period Centrica
  does not disclose (GAP, `bad_debt_provisioning.md` §3.1). Each of these is a **GAP**.

**Verdict.** The crisis fall in new leaver debt follows a **world rule**, and it is the record's: the 2022-23
switching freeze, reproduced at about the published size. It is **not selection**. It is not the debt objection, which
is nearly inert, and inert by construction in the crisis because only SVT exits happened. The pounds a real supplier
lost in the crisis were on live accounts, and the BLOCKING finding's "leaver census" section already put the world's
remaining shortfall there: the **depth** of live arrears.

**The world change it implies: none for the step-up.** The nearest candidate is not crisis-shaped.
`simulation/payment_behaviour_source.py` gap 7 says a switcher's final bill recovers at the stayer's rate, where
Centrica provisions final bills at 71-86%. That moves the leaver-debt **level** in every year, and with only 9-17
switchers a year in 2022-23 it cannot make a step. It stays a named gap, not a build. Also noted, not built: SLC 14 is
recorded in `docs/market_research/domestic_debt_objection_rates_gb.md`, but the regulation commons
(`docs/domain_artefact_library/regulatory/`) holds no SLC 14 artefact.


## 2026-10-21 (night, last): depth graded. The world's missed bills cure in about two months; the record's arrears accumulate

The full table is in the BLOCKING finding, section "the depth graded". Same dump, no new run. Every year from 2016 to
2023, the world's live credit accounts in arrears (>91 days) carry **1.4-2.4 months** of their own bill. Ofgem's average
electricity arrears (£555 to £1,303) are about half a dual-fuel annual bill per single-fuel account. That puts the
world's depth at roughly x4-6 too shallow, the size of the provision volume gap. 556 of 648 failure runs are one bill.
A failed bill settles a median of 61 days after it falls due (p90 123).

**The build question this item now carries:** what sets a missed bill's cure time in
`simulation/household_budget.BudgetPaymentBook.settle_month` and the DD-failure re-presentation, and what published
evidence constrains it. K8 first: the knowledge page names Little's law on Ofgem's own flows ("average stay of about one
year", `debt_and_collections.md`) as the anchor, and names a cure-time distribution as a GAP. Decide it blind to company
results. The grade is the depth table against Ofgem's average-arrears column, not the bad-debt validator.
