**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The b3ce2a4e73 book would be refused by the domain-invariant gate: 203 unexcepted breaches on seven rows (2026-11-04)

**Source.** `/var/tmp/fresh-grade-b3ce2a4e73/grade.txt`, the whole suite over 1,291 accounts, `enforce: true`. Full table
and the departures from the 85b044be54 chain in
`docs/staging/records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_AGAINST_ITS_FIXES_PREDICTIONS_2026-11-04.md`.
It is BLOCKING because the publisher would refuse this book when the window opens and the ruling's exit test is this gate.

| Row | Breached | Exception ceiling | First examples |
|---|---:|---:|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 128 | none | OCC-75d17c23c1da, 2022-07-16 to 2022-09-16: page prints 336.84 overdue against a balance of 273.62, on `arrangement_offered` and `repayment_plan_reoffer` steps |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 53 | 3 | OCC-00909e50a521 electricity 2020-02..06 (5 bills) ratio 0.235 against a band of 0.333-3.0; OCC-14d60fd5bb78, OCC-288aa561d534, OCC-2cf83688b2d2 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 6 | PROS-2017-0233 electricity 2019 and 2020 (10 and 5 months billed on the carbon panel), PROS-2020-0167 2024 |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 5 | 1 | OCC-bad56e8f97f9 (revenue 2595.34 against 857.08 billed), PROS-2020-0025, OCC-8c6b8bb21743, SYN-2016-264, SYN-2016-604g |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 1 | none | SYN-2016-110 electricity 2018-11 |
| INV_PERIODS_CONTIGUOUS | 1 | none | SYN-2016-604g gas, 2017-06-30 -> 2017-08-01, 32 days |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | 1 | none | SYN-2016-604g gas register 1, 2017-08-01, opening 253.6 kWh above the previous close |

**What it is not.** The four rows the 85b044be54 grade refused on (E7 two registers, read monotonic, ToU bands sum, estimate
after actual) are 0, 0, 0 and 1. The three supplier fixes' predictions hold except the cap edge (separate finding).

**Attribution: I cannot yet say.** More than one thing changed between the two books. Two cautions for whoever draws this:
- The revenue row compares page revenue (here from `per_customer_lifetime`, a substitution for summing `p2b__all_records`
  that the pickle chain used) against page bills. Re-grade it from the pickles, or from the pages built in
  `/var/tmp/fresh-grade-b3ce2a4e73/tree`, before treating the five as the book's.
- `INV_OVERDUE_WITHIN_PAGE_BALANCE` was CLEAN on the 85b044be54 grade (0), so 128 is a new regression, not a first
  count. The five examples the runner keeps are all one account, OCC-75d17c23c1da, on `arrangement_offered` and
  `repayment_plan_reoffer` steps printing 336.84, 316.80, 352.72 overdue against balances of 273.62, 253.58, 289.50.
  N15 (6a3da3e48) changed exactly when a re-offer step exists, and the commit's test names no print-side row. Candidate,
  not attribution: the steps that now survive are the ones where the standing arrear exceeds the page's balance.
  Related and older: `SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.

**Prediction, filed before any trace:** the 53 estimated-run breaches concentrate on the accounts N14's second pass
re-billed (`rebill_catchups_off_direct_debit`, 63 on the 0a6391d186 book), because that pass rewrites the estimated runs
this row bounds; if fewer than half of the 53 are on re-billed accounts, the cause is elsewhere (candidates: the world
change moving true use under the estimates, or the draw). Two accounts, SYN-2016-604g's pair, are one gap in a gas
leg's periods in 2017 and look like a single defect.

**Reverse:** delete this file.

## Prediction before tracing INV_OVERDUE_WITHIN_PAGE_BALANCE (filed 2026-11-04, before the 4669d77ddd re-grade was read)

The steps that 6a3da3e48 (N15) and ba868134c keep are the re-offers on days a bill was truly unpaid. Prediction: the
breaching steps are those where the desk's standing arrear (`undisputed_overdue_gbp`) is larger than the page balance,
and they are re-offer/arrangement steps that the calendar trigger used to fire on days the page balance had already
caught up. Before N15, the breach was there on these accounts too and was diluted, not absent: refuted if fewer than
half of the 4669d77ddd breaches are `arrangement_offered` or `repayment_plan_reoffer` steps.

## Re-graded on the 4669d77ddd book (2026-11-04)

`run_output_4669d77ddd_20261104T132452Z.json`, the same chain (`/var/tmp/b3ce-grade-scripts/`) at origin 61ddb41250,
scratch `/var/tmp/grade-4669/`. ba868134c and 4669d77dd moved none of the seven:

| Row | b3ce2a4e73 | 4669d77ddd |
|---|---:|---:|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 128 | 128 (6,391 checked, 13 households) |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 53 | 53 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 14 |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 5 | 5 |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 1 | 1 |
| INV_PERIODS_CONTIGUOUS | 1 | 1 |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | 1 | 1 |

An eighth row now reds the gate: `INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE` 147, N19's blind row
(0f1fe62b9f), which 61ddb41250 says waits on a household fix not yet on origin. Not this finding's.

## INV_OVERDUE_WITHIN_PAGE_BALANCE traced: the prediction is refuted

The prediction above named N15's re-offer steps. 110 of the 128 are `arrangement_offered`/`repayment_plan_reoffer`,
so the count it set to refute it does not fire. But the cause is not N15. Census
(`/var/tmp/grade-4669/overdue_census.py`), each breach's excess set beside the household's back-billing write-offs
on bills issued by the step:

- **78 of 128: the excess is exactly a back-billing write-off.** OCC-75d17c23c1da's GBP 63.22 is
  `catchup_written_off_gbp` on gas bill INV3866 (June 2022), on every step from July 2022. N14 (c6e1a29e1) caps a
  catch-up on a bill paid on receipt in a second pass after the run (`rebill_catchups_off_direct_debit`). The desk's
  bills come in-loop from `StopNoticeBoard.issued_bills_before`, which never re-billed, so the desk chased the
  uncapped first pass. The page was right; the desk was wrong. This is N14's regression, which landed after
  85b044be54 and before b3ce2a4e73.
  Fix: the board asks the same second pass when a bill carries a DD-basis catch-up. Control:
  `tests/simulation/test_the_desk_is_asked_the_capped_catchup_the_page_prints.py`. On origin's code it is red: the
  desk is asked 1034.31 against 857.36 printed. The uncapped arm still asks its whole bill.
  **Prediction for the next fresh run carrying it:** this row falls to the 50 below, on the same households, give
  or take the draw.
- **32: a credit bill the page nets and the desk does not.** SYN-2016-269 (credit bill INV36008 of -85.95, Aug 2023,
  27 steps; and 12 more from Nov 2024 at 85.95 + a 10.41 write-off) and OCC-81b87bae7bec (gas credit bill -4.84, of
  which 1.64 was netted, leaving 3.20; 5 steps in 2017). Not yet traced into the triad's credit-note path.
- **6: a standing credit on one fuel leg beside a missed bill on the other.** PROS-2016-0020 (electricity page at
  -10.00, gas DD returned 37.12), SYN-2016-291 (-20.42 vs 45.11). The row nets the two pages and the desk does not
  net across legs. That is a definition question (does a credit on one fuel's account reduce what is overdue on the
  other's?), to be answered from the knowledge layer before either side is changed.
  SYN-2016-380's 2 steps (desk 165.75 against one returned bill of 148.95, 16.80 over) are not yet explained.

## SYN-2016-604g's three rows traced: one held bill (2026-11-04)

The run has all 13 of the gas leg's bills, but the billing ledger issues 12. July 2017 sits in the exception queue:
"billed usage 253.5 kWh does not reconcile with the printed meter reads 5001.4 -> 5255.0". June closed the register
at 5001.45, which prints 5001.4. July's register opened at 5001.450000000001, and `generate_billing_ledger` started
the usage line there, which rounds to 5001.5. The 0.1 kWh went to a catch-up line that a bill with no true-up never
prints. The gate was right to hold the bill; the builder was wrong. Across the book this is the only such bill (1 of
8,030 actual bills with a register and no true-up whose opening rounds apart from the previous close).
Fix: a gap below print precision, with no true-up, is float noise, so the usage line opens on the printed close.
Control: `tests/tools/test_an_actual_bill_with_no_catch_up_opens_on_the_last_printed_close.py` (red on origin with
the same hold; the true-up arm still prints its 0.1 kWh catch-up).
**Prediction, filed before the re-grade of the 4669d77ddd book with this builder:** INV_PERIODS_CONTIGUOUS 1 -> 0,
INV_OPENING_IS_THE_PREVIOUS_CLOSING 1 -> 0, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 5 -> 4 (SYN-2016-604g leaves),
and no other row moves.

## INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER against its pre-registered split: refuted (2026-11-04)

On the 4669d77ddd book (census `/var/tmp/grade-4669/estrun_census.py`): **2 of 53** breaches are on N14-rebilled
accounts (66 such accounts in the book), against the "more than half" the prediction needed. N14's second pass is not
the cause. Split: electricity 52, gas 1; 41 below the band (the estimate is well under the meter's advance, ratios
0.10-0.33) and 12 above (3.1-5.3). Runs that start in 2016-17: 31 of 53. Runs of 2 bills: 20. 44 accounts, none with
more than 2. Gas is 1, so N13 (the gas-noise change) does not carry it. **I cannot yet say** which change does. The
electricity-side candidates between 85b044be54 (4) and b3ce2a4e73 (53): 7ec8b1030d (490 premises leave the climate
normal and read the weather store), 308a3f168e (an E7 meter's annualised estimate is per register) and 54f76662d1
(held opening estimates issued). Next: one-variable replays of a breaching account's leg, one candidate at a time.

**Result (the 4669d77ddd book re-graded with the fixed builder, `/var/tmp/grade-4669-fix/grade.txt`):**
INV_PERIODS_CONTIGUOUS 1 -> 0, INV_OPENING_IS_THE_PREVIOUS_CLOSING 1 -> 0, INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 5 -> 4:
as predicted. **"No other row moves" was wrong:** INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL also fell, 14 -> 12. I did not
predict it. The likely reading is that the held month was missing from one panel's year for this leg, but I have not
checked it row by row. Every other row reads as before.

## The 50 left after 514e2015bf, traced (2026-11-04)

Census re-run on `/var/tmp/grade-4669-fix/ledger.json`: 128 breaches, 78 the back-billing write-off 514e2015bf fixes,
50 left in six groups.

**39 (SYN-2016-269, 27 + 12): the world's settlement paid the bill's face, not what was left on it. Fixed.**
An 85.95 credit bill (INV36008, Aug 2023) netted INV36009 (276.73) to 190.78. The desk asked 190.78. On 18 Oct 2023
`world_payment_truth.repayment_rows` priced the triad's settlement of that bill at its issued face, 276.73, and the
engine put 190.78 on INV36009 and 85.95 on INV36010. From then on the page printed 85.95 less owed than the desk
chased (the 12 from Nov 2024 are the same 85.95 plus a 10.41 write-off). The desk is right. §7.3 of
`debt_and_collections.md` already says so from the PROS-2020-0191 trace ("a household settling a bill pays what is
left on it, not its face"), filed then and not fixed. Fix: a settlement row carries `settles_month`, and the engine
prices it at that bill's remainder while the bill is open. A settlement that arrives before its bill opens keeps
the face, which is PROS-2016-0263's path. Control: `test_balance_at_close_write_off.py::
test_a_settlement_pays_what_is_left_on_its_bill_not_its_face`. The mutation that drops the remainder fires it.
This is a world correction made for fidelity, blind to supplier results. It moves bad debt where a settled bill had
been netted: the household now pays less on that day, and the later bill keeps its debt.
**Prediction for the next fresh run carrying it, filed before it runs:** SYN-2016-269 leaves the row. The row falls
to at most 11 (the groups below) plus whatever the draw moves.

**9 (OCC-81b87bae7bec 5, PROS-2016-0020 2, SYN-2016-291 2): one class, and it is not a cross-fuel question at root.**
In each case a credit bill is larger than the bill it first meets:
- PROS-2016-0020 gas: -23.43 (Jun 2017), INV9316 13.43 netted in full, 10.00 left.
- SYN-2016-291 electricity: 42.62 (Mar 2023), 20.42 left.
- OCC-81b87bae7bec gas: -4.84, 1.64 netted, 3.20 left.

After that the household pays every later bill at face, so the page holds the remainder as a standing credit for
months or years. A later missed bill, on either fuel, is then chased by the desk at its face, while the row nets
the page credit. §7.3 lists this as not established ("a credit that meets an open bill smaller than itself. The
page holds the rest for the next bill. The triad leaves all of it to the desk's oldest-first allocation"). The
engine's own walk nets the remainder off the next paid bill (SLC 31H.12). The page's ledger never shows that second
netting, and the household is never asked the net amount. So the first question is single-fuel: what is the
household asked on the bill after a credit that was larger than the first bill it met? The cross-fuel question
(PROS-2016-0020, SYN-2016-291) only arises because the remainder is never used up. Next: trace the triad's ask on
INV9317 and the desk's allocation of the 10.00 before either side changes.

**2 (SYN-2016-380, Oct 2021): traced as far as the class, not the cause.** INV41230 is a PC2 (Economy 7) electricity
bill, estimated, single fuel, published at 148.95. The desk is asked 165.75, which is 16.80 more (16.00 ex VAT). Nothing is
open before it: the page balance had been 0 since 18 Oct. So the desk's in-loop bill and the published bill differ.
The desk's in-loop bill is built by `dd_collection_book.issued_bills_before` over the leg's records settled before
the cutoff. The published bill is built over the whole book. Two readings, and I cannot yet say which holds:
- The published PC2 estimate depends on records settled after the bill was issued. That would breach the epistemic
  wall, because a supplier cannot estimate October from November's reads. If so, the published bill is the wrong one.
- The in-loop build is missing part of the estimate's annualisation window (308a3f168e's per-register advance).
Next: rebuild this leg's October bill twice, through `build_monthly_bills`, once over records before 2021-11-01
and once over all of them, and diff the register estimates.

`INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER` (53): not started this turn. The one-variable replays named above
are still the next step.

## INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER: prediction before the candidate split (filed 2026-11-04 ~19:20 UTC, before any per-leg feature was read)

Of the three candidates, only 308a3f168e changes how an electricity estimate is built *after* an actual read, and it
does so only on a PC2 (Economy 7) meter. 54f76662d1 releases estimates *before* an account's first read, and those are
not graded here, because a run needs an actual read before it. 7ec8b1030d moves the world's use, and that moves the
meter, but on electricity it acts only through the heating share. **Prediction:** at least half of the 52 electricity
breaches are on PC2 legs, so 308a3f168e carries the row. This is refuted if fewer than 26 are PC2. In that case the
next candidate is 7ec8b1030d, and the test is whether more than half sit on the 490 premises that left the climate normal.

**Result: the prediction is refuted, and none of the three commits is the defect.** 15 of the 52 electricity breaches
are on two-register legs (fewer than 26), so 308a3f168e does not carry the row. Comparing the same legs across books
settled it without a full replay. The **estimates are identical** on the 85b044be54 and 4669d77ddd books, but the
**world's use is not**. SYN-2016-566's true electricity was 175 kWh in Jan 2017 on the earlier book and 2,085 on the
later one. In 2018 it metered 13,452 kWh against a registry EAC of 1,410.5. The estimates were right for the
declared home, and the meter moved under them.

The mechanism has two parts, both on the world side:
- `dwelling_records.build_properties` gave **every home without a gas account with us** `electric_storage`
  (`DEFAULT_HEATING_SYSTEM`), whatever the world drew. On today's draw that is 124 electricity-only homes. Only 36 of
  them were drawn storage-heated, and 11 direct electric. The other 77 were drawn with oil (28), gas bought elsewhere
  (36), communal heat (10) or a heat pump (3). `registered_profile_class`'s own docstring named this default and
  routed around it for the profile class only.
- The legacy shape adds 3 kWh per degree day for `electric_storage`, but only when the premise has a temperature
  (`if mean_temp is None: shape = list(base_shape)`). Before 7ec8b1030d, 263 of 575 electricity premises had no sky,
  so the wrong label added nothing. The rebuilt store gave them one, and the heating term fired on top of a LOW-band EAC.

So **7ec8b1030d revealed the defect; it did not create it.** The store fix was right. On the a6b7a0fd47 book, 28 of the
54 breaches are on homes the world drew non-electrically heated: gas 14, oil 8, communal 5, heat pump 1. The other 26 are
19 on drawn electric-heated homes, 6 occupier legs that copy their premise's record, and 1 gas.

**Fix (world, fidelity, decided blind to results):** `dwelling_record` carries the drawn household's
`drawn_heating_system`. `build_properties` maps it: storage and direct both become `electric_storage` (resistive heat;
the legacy shape has one coefficient for both); a gas boiler becomes `gas_boiler`; a heat pump, oil, communal heat or none
take no electric term. The heat pump's electricity is the ASHP overlay's (`Household.ashp_annual_kwh`), so a term here
would count it twice. The authored C-roster, with no drawn household, keeps the old rule. The key is
`drawn_heating_system`, not `heating_system`, so the mover path's `{**property, **dwelling_record(...)}` merge cannot
overwrite the mapped value with a raw one. Control: `tests/simulation/test_a_drawn_home_is_heated_by_what_the_world_drew.py`.
It is one partition control: a rule that heats nothing reds the storage leg, and the old rule reds the oil leg. Both
legs were red on the reverted line (measured).

**Prediction for the first fresh run carrying it, filed before that run:** INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER
falls from 54 to between 15 and 30. The non-electric 28 leave, along with any of the 6 occupier legs whose premise is
non-electric. INV_ANNUAL_USE_ELEC_ACCOUNT's 16 flags fall. The book's electricity revenue and settled volume fall,
because about 77 homes lose roughly 6-12 MWh a year of heating they never had.

**What it does not fix (named, not yet traced):**
- The 19 on genuinely electric-heated homes. Their EAC is drawn from a TDCV band, and the heating is added on top.
  Whether a storage home's drawn band already includes its heating (a double count) is the next question for the
  knowledge layer.
- The supplier's estimate does not follow the reads. SYN-2016-566 kept estimating about 150 kWh/month after a 1,639 kWh
  actual read, because with less than a year of reads it stays on the registry figure. Whether a real supplier
  re-estimates sooner (via the D0019 EAC/AA after each read) is the other question. INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS
  does not grade it.

**Separate, found on the way:** `tests/simulation/test_the_worlds_dwelling_is_drawn_not_believed.py::test_the_worlds_dwelling_never_crosses_the_wall`
is red on origin 5683caa403. Its text scan flags `company/interfaces/sim_interface.py:681`, where
`get_gas_charging_area` (3042023498) imports `live_drawn_households` to return only the home's LDZ. That is the seam
returning an observable, which looks like a scan too broad for the sanctioned crossing. It is the interface steward's
to rule on, not changed here.

## INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL 14 -> 12 and INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE 4, row by row (2026-11-04)

Full breach lists from the carbon evaluator on both 4669d77ddd ledgers
(`/var/tmp/grade-a6b7/carbon_grade-4669{,-fix}.json`). **The held-bill explanation holds.** The two rows that left
are `SYN-2016-604g gas 2017` and `SYN-2016-604g gas 2017 months` (7,670.0 against 7,844.3 kWh, 11 of 12 months). That is
the July bill 6f9976757d released. The other 12 rows are identical in value on both ledgers.

All 12 of those are **held bills too**, on three electricity legs. Every month missing from the carbon panel is in the
exception queue as `slc_6_7_billing_accuracy: 2,200-2,640 kWh over a month is implausible for a resi electricity account`:
SYN-2016-355 (7 bills, 2017-19), PROS-2017-0233 (5, 2019-20) and PROS-2020-0167 (1, Jan 2024). So the billing gate
is right, and these are the same over-heated homes as the estimated-run row. PROS-2020-0167 was drawn oil-heated,
so this fix covers it. SYN-2016-355 (direct electric, MEDIUM EAC 2,468.5) and PROS-2017-0233 (storage, HIGH EAC
3,634.6) are drawn electric-heated, and they meter 15-20 MWh a year. That is the open double-count question above.

Revenue's 4: PROS-2020-0025 was drawn with communal heat, so this fix covers it. SYN-2016-264 is storage-heated, and OCC-bad56e8f97f9 and
OCC-8c6b8bb21743 are occupier legs. Not traced further this turn.

**Prediction for the first fresh run carrying the heating fix:** carbon 12 -> 10 (PROS-2020-0167's two leave),
revenue 4 -> 3 (PROS-2020-0025 leaves), give or take the draw.

## The a6b7a0fd47 book graded (2026-11-04)

The run ended 19:06. Graded at origin 5683caa403 with the same chain (`/var/tmp/b3ce-grade-scripts/`), scratch
`/var/tmp/grade-a6b7/`. **The run is at a6b7a0fd47, which carries neither the desk fix (514e2015bf), the settlement fix
(8befb331b) nor the builder fix (6f9976757d).** The builder is post-run, so it applies; the other two are in-loop, so they do not.
The overdue prediction ("falls by the 78") therefore does not apply to this book.

| Row | 4669d77ddd | a6b7a0fd47 | pre-registered | held? |
|---|---:|---:|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 128 | 64 | -78 for a run carrying 514e2015bf | n/a: not carried. It still moved 64 for a reason not traced here; the holder of that row has it |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 53 | 54 | none for this book | traced above; the heating fix is predicted to bring it to 15-30 |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 12 | 12 with the builder fix | yes |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 5 | 4 | 4 with the builder fix | yes |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 1 | 1 | no move | yes |
| INV_PERIODS_CONTIGUOUS | 1 | 0 | 0 | yes |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING | 1 | 0 | 0 | yes |
| INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE | 147 | 3 | (N19's row, not this finding's) | |

The gate still refuses: 138 unexcepted breaches over 6 rows. **Not done:** by the done-means, every row reads 0 or
carries a dated, traced exception on a fresh book. That needs a fresh run carrying 514e2015bf, 8befb331b and this
heating fix, plus the three questions left open: the electric-heated double count, the supplier's re-estimate after
reads, and the overdue row's remaining classes.

## The overdue row's last 11, traced and fixed (2026-11-04, claim `overdue-row-credit-remainder-and-pc2-in-loop-estimate`)

**Both readings filed above were wrong in their frame.** The credit remainder is not held because
nothing carries it forward: the triad and the engine both net it off the next bill. And SYN-2016-380's
October bill is not two bills. The run's own DD book collected 148.96 for it in-loop, the same as the
published 148.95, so the wall question does not arise. Both groups are one engine defect, plus one
page defect:
- **The world's settlement of a bill was priced at the wrong figure.** The triad's settlement carries
  the cash the bill *asked*: its face less the credit waiting when it was collected. The engine
  priced it at the face, or at what was still left on the bill. PROS-2016-0020g's June 2017 bill was
  paid in full by a waiting credit (asked 0). Its settlement at face became a 13.43 phantom
  repayment, and the 10.00 credit remainder took the "repayment" label with it, so the page never
  netted it. SYN-2016-291 had the same shape (20.42). SYN-2016-380's Sep 2019 bill asked 84.32. A 2020
  credit cleared it, and its 2021 settlement carried 84.32 onto a later bill, leaving 16.80 the desk
  chased (165.75 = 148.95 + 16.80) while the page had netted the face.
  Fix: `balance_settlement_from_outcomes` records each bill's ask at collection and prices its
  settlement there. A settlement before its bill opens keeps the face.
  Control: `test_balance_at_close_write_off.py::test_a_settlement_carries_what_its_bill_asked_not_what_a_later_credit_left`
  (red on HEAD's engine, measured).
- **OCC-81b87bae7becg: a credit bill partly in the occupier window was printed whole on the payer.**
  The engine credits the payer (1 - share) = 1.64. The page printed -4.84, and 3.20 stood as credit
  for good. Fix: the credit branch of `generate_billing_ledger` takes the deemed share off as a
  charge's is. Control: `test_a_bill_inside_the_occupier_window_is_the_deemed_accounts.py::test_a_part_window_credit_bill_credits_the_payer_its_own_share_alone`
  (red on HEAD, measured).
- Knowledge: `debt_and_collections.md` s.7.3, the "not established" line answered beside its claim.

**Re-graded post-run on the 4669d77ddd book with both fixes** (`/var/tmp/grade-overdue-cr/`, same
chain): INV_OVERDUE_WITHIN_PAGE_BALANCE 128 -> **90**, and the census leaves **0 unexplained**. All 90
are the back-billing write-off class that 514e2015bf fixes in-loop (78 as before, plus SYN-2016-269's
12 steps from Nov 2024, whose 85.95 part this fixes and whose 10.41 part is a write-off). No other row
moved. The cap-note row reads 3 against 147 because this worktree is on newer origin code, not
because of this change.
**Engine side effect, measured:** the book's written-off total falls GBP 291.91 (13,574.18 ->
13,282.27, 280 -> 275 cases, 8 legs), because settlements now carry the triad's cash. The desk
agrees on the one leg checked: PROS-2020-0223g's journey cured on 2023-08-26, while the old engine
wrote off 141.33 of it.

**Prediction for the first fresh run carrying 514e2015bf, 8befb331b and this fix, filed before it
runs:** INV_OVERDUE_WITHIN_PAGE_BALANCE reads 0, or at most 5 from the draw. Refuted if any breach is
neither a back-billing write-off nor a new class. Bad debt is lower than an un-fixed engine would
give on the same book, by an amount of the order of GBP 300.
