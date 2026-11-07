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

## The two open questions answered: no double count; the registry, not the meter (2026-11-04, ~19:50 UTC)

The knowledge is in `docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md` §4 (K8).

**(a) Electric-heated homes.** On the a6b7a0fd47 book the 47 drawn storage or direct-electric homes meter
5-10 MWh/yr on full years, with a tail at 13-23 MWh: PROS-2017-0336 (EPC F, 5-bed detached), SYN-2016-355,
PROS-2019-0246, PROS-2024-0010 and SYN-2016-201. BEIS/Element Energy (2019/021) model a storage-heated
73 m² terrace at 12.8 MWh (9.7 MWh insulated) and a 174 m² detached house at 21.9 MWh (16.0 MWh insulated).
The DESNZ Economy 7 meter median is 3.3-4.1 MWh. The world's heated homes therefore sit where they should,
and the drawn band (a PC1 quartile range, defined by meter class and blind to the dwelling) works as their
appliance base. **There is no double count, and the 3 kWh/HDD coefficient is not changed.** Nothing
published refutes it.

**The cause is the registry.** All 15 breaching electric-heated homes (19 runs) are legacy premises still
registered at their drawn band. The 10 electric-heated fabric premises, registered on their own reads since
1 Oct, breach none. The fix carries the 1 Oct rule (BSCP504 §3.2.6.51) to every domestic legacy premise:
`run_phase2b.register_legacy_premises_on_their_own_reads`. The band moves to a world-side map
(`_WORLD_BASE_EAC_KWH`) that `_base_profile_eac` reads first. **The world's demand is therefore unchanged,
and only the roster's EAC moves.** Occupier legs take the premise's level, and a mover's new home drops it.
This is the "world-side true EAC and supplier-side declaration" split that `_base_profile_eac`'s
docstring named as owed, for legacy premises. The read error stays zero, a stated lag-only model.
Control: `tests/simulation/test_a_legacy_premise_is_registered_on_its_own_reads.py`, one partition. Three
mutations each turn it red: the map not read, legacy premises skipped, and a non-domestic point
re-registered.

**(b) Re-estimating after a read.** BSC Annex S-2 §4.3.7 (P40 text): every valid advance gives a new EAC
straight away, w × AA + (1 − w) × previous EAC, with w = min(FYC × SPAR, 1) and no minimum interval. SPAR's
value is a GAP. Whether a supplier's billing estimate follows the D0019 EAC or its own reads in the first
months is also a GAP. **The company's estimate rule is not changed.** SYN-2016-566's case was a registry
of 1,410.5 kWh on a home metering 13 MWh, and it was oil-heated, so c07e8ccce takes its meter down to its
band. With this change, the registry follows the meter for every domestic premise. If a first-year
estimate still sits far below a large read on the next book, that becomes the question.

**Predictions, filed before any run carries this change:**
- On a fresh book carrying c07e8ccce **but not this change** (if one is cut before this lands), the earlier
  prediction stands: est-run 54 → 15-30, carbon 12 → 10, revenue 4 → 3.
- On a book carrying **both**, est-run falls to **5-18**. The 12 first-year "below" runs on electric-heated
  legacy homes leave (PROS-2017-0336 twice, SYN-2016-118, -175, -225, -329, -409, -441, -541, -565 (2017),
  PROS-2017-0364 (2018), PROS-2018-0214). The 7 summer "above" runs stay, because they are the class shape
  spreading a heated year (exception (a)): SYN-2016-215 twice, -221, -565 (2019), -582, PROS-2017-0351 and
  -0364 (2022).
- Refutation: if more than 3 of those 12 remain, the registry is not what the estimates read. The next
  suspect is then `_company_eac_estimate`'s first-term basis.
- Carbon and revenue are as for c07e8ccce alone (12 → 10, 4 → 3). Their held bills are gated on the
  meter's monthly kWh (SLC 6.7), which this change does not touch.
- Each home's demand is unchanged, so the book's electricity volume moves only through who stays.
  Direct debits, quotes and EFFECTIVE_EAC_KWH rise for heated legacy homes, so the first-year catch-up on
  them shrinks. **I cannot yet say** by how much churn moves.

## Disposition of the redraw `the-seven-gate-rows-on-the-newest-book` (2026-11-04, ~21:05 UTC)

Drawn again at 21:00 with its three asks. All three are already answered above, at HEAD 75156811ef: (1) the
estimated-run row was traced to the world's heating label (c07e8ccce) and the legacy registry (75156811e), and its
predictions are filed; (2) carbon 14 -> 12 was checked row by row, and the held-bill explanation holds; (3) the
a6b7a0fd47 book is graded in the table above. The remainder is one job: grade a fresh book carrying 514e2015bf,
8befb331b, c07e8ccce and 75156811e against the filed predictions (est-run 5-18, carbon 10, revenue 3, overdue
without the 78 and SYN-2016-269's 39). The continuation `electric-heated-homes-eac-double-count-and-the-fresh-grade`
carries that job, so this id is released and not worked twice.

**Why no such book existed yet:** sim-runner had deferred every cycle since 20:55 because the shared tree's
`simulation/run_phase2b.py` was a copy from before 75156811e. I refreshed it to HEAD with `tools.refresh_to_head`,
which keeps the old bytes in a preserved commit, so the next sim-runner cycle can run at 75156811ef. Look for the
book as `docs/reports/run_output_75156811ef_*.json` (or a later origin head), and grade it with
`/var/tmp/b3ce-grade-scripts/`.

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

## The fresh 5200cd6239 book graded against the filed predictions (2026-11-05, claim `electric-heated-homes-eac-double-count-and-the-fresh-grade`)

The claim's two questions, (a) and (b), were already answered above at 75156811e, so only the grade was left
to do. The run `run_output_5200cd6239_20261104T211046Z.json` carries 514e2015bf, 8befb331b, c07e8ccce and
75156811e. It does **not** carry 9744dd436's in-loop settlement fix, though that fix's page half applies,
because the builder runs post-run. It was graded at origin 2f7a387b8b with the same chain
(`/var/tmp/b3ce-grade-scripts/`). Scratch is `/var/tmp/grade-5200/`, and every breach row is listed in
`/var/tmp/grade-5200/rows.txt`.

| Row | a6b7a0fd47 | 5200cd6239 | filed | held? |
|---|---:|---:|---|---|
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 54 | **8** | 5-18; refuted if more than 3 of the 12 named "below" runs stay | **yes**: 0 of the 12 stay, and all 7 named summer "above" runs stay |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 12 | **14** | 10 | **no** (see below) |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 4 | **0** | 3 | no, but on the good side. **I cannot yet say** why: four in-loop changes moved together |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 64 | **0** | 0 or at most 5, for a run with 9744dd436 | 0 without 9744dd436's engine half. Its 11 were the page half here, or this draw did not reach them |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 6 / 6 | 7 / 7 | none | one new account of the excepted class (below) |

**Est-run.** 7 of the 8 are the summer "above" runs named before the run. The eighth is PROS-2016-0263g, the
exception's class (c). **The filed reason "single-rate bills on a two-rate settlement" was wrong for five of the
seven.** Five of them print two registers, so the class average was not the cause there. A heated year spread
by the profile class's average shape over-estimates summer three to five times, on both meter types.
Exception (a) is re-based to 8, and its retirement is now the estimate following the home's own seasonal shape.
Whether a GB supplier does that is a GAP.

**Carbon 12 → 14.** As predicted, PROS-2020-0167 (oil, which c07e8ccce covers) left. As predicted, SYN-2016-355 and
PROS-2017-0233 stayed. SYN-2016-175 (2016 and 2017, 4 checks) was **not** predicted. It is one of the 12 heated
legacy homes, and its winter bills are now held. My reading is that the registry now follows its meter, so its
estimates rose into the gate's range, but I have not traced it.
All 14 checks are months missing from the carbon panel because the exception queue holds them on
`vat_by_segment` and `slc_6_7_billing_accuracy`: 16 bills on the three homes. **The root is company-side.**
`RESI_CONSUMPTION_ENVELOPE_ELEC_MONTHLY` (company/compliance/domain_invariants.py) is a flat 2,100 kWh/month,
sourced as "observed sim population + headroom". A storage-heated home metering 15-22 MWh a year, which BEIS/Element
Energy publish (how_far_a_settled_eac_sits_from_next_years_use.md §4), uses more than that in a winter month.
So the gate reads a heated home as a business. The fix is to scale that envelope, and the VAT-by-consumption
test, by the meter's own registered EAC, which since 75156811e follows its reads. That changes a company
billing gate, so the knowledge page comes first (K8). It is not done here. The exception is re-based to 14
with this cause.

**EBSS 6 → 7.** OCC-da79d3238e02's October 2022 bill carries `deemed_share_to: occupier`. The unnamed
occupier's deemed account held the 1st, which is the exception's guidance-5.4 case. Both rows are re-based to 7.

**After the re-base, the gate on this book reads 3 unexcepted breaches on 1 row:**
INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE. That is N19's row, not this finding's. Every
row this finding owns is 0 or carries a dated, traced exception on a fresh book, so its done-means is met.
The finding stays open for one more thing: the heated-home envelope above, the next item.

NEXT: none -- the remaining heated-home billing-gate envelope needs its knowledge page first and is filed above as the next item

## The fd91027799 book graded through the whole gate, against the filed predictions (2026-11-07, claim `grade-the-fd91027799-book-through-the-whole-invariant-gate`)

`run_output_fd91027799_20261105T004022Z.json` carries 9744dd436's in-loop settlement fix, every other
correctness fix to date, and N18's three pricing commits. It does **not** carry 26c891276. It was graded at origin
f6daa03a4f with the same chain (`/var/tmp/b3ce-grade-scripts/`), over 1,302 accounts. Scratch is
`/var/tmp/grade-fd91/` (`grade.txt`, `grade.json`). The two-day delay before the grade was the host outage
(`SEAT_FINDING_A_SIXTY_HOUR_HOST_OUTAGE_..._2026-11-07.md`).

| Row | 5200cd6239 | **fd91027799** | filed | held? |
|---|---:|---:|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 0 | **0** | 0 or at most 5, for a run with 9744dd436 | **yes** |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP_ALL_IN_FLOOR (N18) | — | **0** of 1,435 | 0 | **yes** |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP_ALL_IN_FLOOR (N18) | — | **0** of 2,204 | 0 | **yes** |
| INV_DEFAULT_DUAL_FUEL_COST_FOLLOWS_THE_PUBLISHED_DEFAULT_BILL (N18) | — | **0** of 3 | 0; ratios ≈1.04, 1.05, 1.03 | **yes**: 1.0431, 1.0518, 1.0284 (published +4.30%, +5.19%, +2.6%) |
| INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE | 3 | **3** | 0 apart from the 3 class B bills | **yes**, in count. Unexcepted, so it is the gate's only red (N19's row) |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 8 | **7** | 8 | **no**, by one, on the good side. Inside the exception's ceiling of 8. I have not traced which run left |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | **14** | 14 | **yes** |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 7 / 7 | **7 / 7** | 7 / 7 | **yes** |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 0 | **0** | — | stays 0 |

**The verdict:** 3 unexcepted breaches on 1 row (the cap-note row), and 7 rows excepted. The excepted rows include
`INV_UNIT_RATE_EPG_HOUSEHOLD` 336 and `INV_PPM_NOT_CREDIT_BILLED` 12, both on their own dated exceptions. Every row
this finding owns is 0 or inside its traced exception on this book.

**The miss this grade found is N20's, not this finding's.** `level_dd_collections` is absent from this book, and
from every saved book. `extract_report_data` dropped it, so N20's share test could only ever xfail. On this book,
34,888 of 36,139 successful DD collections (**96.5%**) equal their bill, against the 30% ceiling. The fix and its
control landed in the commit before this one. **The run at 8c7489e0d9 now in flight predates that fix**, so the
first book to carry the schedule is the runner's next one, and N20's test is graded there.

**The other three readings the item asked for:**
- **The billing ledger this book writes** is 86,052,705 bytes (82.1 MiB), against 100 MiB.
- **Explore slots:** 8 of 8 filled, rebuilt from this book through the publish pipeline's page generators in a
  scratch worktree. They are switch_in PROS-2025-0022, renewal SYN-2016-592, estimate_trap PROS-2017-0264,
  mover PROS-2017-0351, debt SYN-2016-217, ev PROS-2017-0183, storage_heating PROS-2020-0189 and shock_2022
  PROS-2019-0246. One book-level coverage flag: `above_cap`, 1 household of 757. The households were not
  cold-read here, so "filled" is not "valid to a reader".
- **26c891276's grade** (`grade-nil-ask-and-cleared-settlement-on-fresh-book`) is owed on the 8c7489e0d9 book.

## Pre-registration for the 8c7489e0d9 book and the first book carrying the level DD schedule (2026-11-07 16:35 GMT, before either book exists)

Claim `grade-the-first-book-carrying-the-level-dd-schedule`. Written while
`run_output_8c7489e0d9_20261107T154715Z.json` is still being built (runner PID 6294, started 15:47).
Between fd91027799 and 8c7489e0d9 exactly one commit touches `simulation/`, `sim/`, `company/`, `saas/`
or the triad: **26c891276**. So any movement between the two books, on any row, is 26c891276's or
noise, and nothing else's.

**26c891276's own prediction** (filed in `SEAT_FINDING_THE_WORLD_PRESENTS_A_NIL_DIRECT_DEBIT..._2026-11-05.md`)
is graded with its own script, `/var/tmp/settle-cleared-scripts/count.py`, plus one change, noted here
before running it: that script's replay prices each settlement at `asked[settles]`, the PRE-fix rule, so its
class (2) and (3) counters measure what the old engine *would* have done with the book's outcomes, not the
cash the world sent. A copy (`/var/tmp/se-grade-8c74-scripts/v2/`) reads the settlement row's own
`amount_gbp` instead. Both are reported; the v2 numbers are the grade.
- (1a) failed credit-bill months: **0** (fd91: 29). (1b) failed fully credited bills: **0** (fd91: 5).
- (2) settlements over the open balance, v2: **0** (fd91: 25, £1,497.46).
- (3) relabelled credit, v2: **0** (fd91: 3, £299.35).
- P&L bad debt rises by **£0–1,500** against fd91's.
- Outcomes not involving a £0 ask: identical, except through a desk contact, uncounted ("I cannot yet say").

**The rest of the gate on 8c7489e0d9**, against fd91027799's table above: every row the same count, except
that no row may rise. INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE stays at **3** (N19's
class B bills), still the only unexcepted red. INV_OVERDUE_WITHIN_PAGE_BALANCE stays 0.

**N20's share test on 8c7489e0d9:** the book predates 8178e24218, so `level_dd_collections` is **absent**,
the test xfails, and the share computed anyway is about **96.5%** again.

**N20's share test on the first book built at or after a66e97829:** `level_dd_collections` **present**, and
`share_equal_to_the_bill` at or below the 0.30 ceiling, near f874c6836b's **0.207** on an injected schedule
(range 0.15–0.30). If it reads above 0.30, the schedule reaches the book but not the ledger's payments, and
that is the next defect, not a tolerance to widen.

## The 8c7489e0d9 book graded through the whole gate, and 26c891276's own grade (2026-11-07 ~18:10 GMT)

`run_output_8c7489e0d9_20261107T154715Z.json` (finished 17:21Z), graded at origin 5b838d5960 with
`/var/tmp/b3ce-grade-scripts/` (ledger.py, then grade.py), over 1,302 accounts. Scratch: `/var/tmp/grade-8c74-seat/`.
**The gate grew between the two grades.** eafd683107 wired evaluators for INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR and
INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD, and INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE
now has its evaluator too. On fd91027799 they read UNCHECKABLE or NO_EVALUATOR. So, to keep one variable, **fd91027799 was
re-graded at the same origin** (`/var/tmp/grade-fd91-seat/`).

**Verdict, identical on both books:** 7 unexcepted breaches on 4 rows, and 7 rows excepted.

| Row (unexcepted) | fd91027799 at 5b838d5960 | **8c7489e0d9** | what it is |
|---|---:|---:|---|
| INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE | 3 | **3** | N19's 3 class B bills, as filed |
| INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD | 2 legs | **2 legs** | median abs(r-1) 0.0075 against a floor of 0.05; 29.3% of near pairs within 0.1 kWh against a bound of 16.9%. This is N17, the world side (W2_30 slice, eafd683107) |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 1 | **1** | SYN-2016-206g, 3 July repeats. The book leg passes: 10 of 3,743 pairs (0.27%, bound 1%) |
| INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE | 1 (Leg A 0.991) | **1 (Leg A 0.991)** | N20. This book has no schedule (below) |

The pre-registered row-by-row test (every row the same, and none may rise) **held**. Every breach and exception count
is equal. Only the denominators moved, which is what 26c891276 does: overdue steps went from 6,658 to 6,695, plan
re-offers from 1,272 to 1,289, SVT account-months from 32,593 to 32,603, and DD step-change flags from 1,561 to 1,562.
INV_OVERDUE_WITHIN_PAGE_BALANCE stays 0.

**Correction to the filed claim that the cap-note row is "still the only unexcepted red":** it is not, and it was not on
fd91027799 either once the new evaluators are counted. As the gate stands, three other rows are red without an
exception. The cap-note row's 3 class B bills are unchanged.

**N20 on 8c7489e0d9:** `level_dd_collections` is **absent**. The test xfails. `share_equal_to_the_bill` reads
34,888 of 36,143, or **96.5%**. Both are as filed.

**26c891276's own grade.** The v2 replay (`/var/tmp/se-grade-8c74-scripts/v2/`) prices the settlement at the old
engine's rule. So it was graded on the CURRENT engine's walk instead (`v3/count.py`, which probes
`balance_settlement_from_outcomes` at the point where it prices a settlement):

| | fd91027799 | filed for 8c7489e0d9 | **8c7489e0d9** | held? |
|---|---:|---:|---:|---|
| (1a) failed credit-bill months | 29 | 0 | **0** (405 DD, 103 standard credit, 39 PPM: no failures) | **yes** |
| (1b) failed fully credited bills (a nil ask) | 5 | 0 | **1** (OCC-cede70b10116) | **no**, by one |
| (2) settlements whose cash is over the open balance | 25, GBP 1,497.46 | 0 | **19, GBP 682.47** (18 legs; 5 also over the amount asked) | **no** |
| (3) relabelled credit | 3, GBP 299.35 | 0 | **0** | **yes** |

**(2) is refuted, and the cause is visible in the rows.** SYN-2016-047 is one example. Its Jul 2021 DD failed at GBP 64.38. A May 2023 credit
of GBP 43.67 (due 15 Jun 2023) then left GBP 20.71 open on that leg. Even so, the world sent GBP 64.38 on 20 Jul 2023. SYN-2016-255
(a GBP 125.18 credit, Oct 2020, before a 2022 settlement) and SYN-2016-329 have the same shape. So the triad's
`open_on_contract_gbp(leg_rows, settled_on)` does not see a credit that the engine's walk does see.
Two explanations fit the evidence, and I have not tested either.
- **(i)** The settlement crosses before the later credit row is appended to `_leg_rows`. That would happen through a `force` crossing by a reader, or through a record order that is not calendar order.
- **(ii)** `_leg_rows` for that leg is missing the credit, or carries a different amount. Its credit row is written from `credit_gbp`, but the engine's row comes from `_resolve_bills`.

Other legs have the same shape when the money in between is another settlement rather than a credit (SYN-2016-217 and -217g,
PROS-2018-0016g). The P&L effect is at most GBP 682.47 of cash that should not have been sent. It is no longer
GBP 1,497.46. Scratch for this: `count_v3.txt` and `classify.txt`.

**Correction (2026-11-07, same day, on reading the code): the 19 are not cash the world sent.** The count read each repayment
row's `amount_gbp`, and `world_payment_truth.repayment_rows` set that to the bill's FACE: the truth kept only the bill month of a
crossed settlement, never its cash. The 64.38 is the Jul 2021 bill's face. The triad's own cut (`_cross_settlement`) is tested to
send the rest only (`test_a_settlement_carries_only_what_a_credit_left_open`: GBP 70 of a GBP 100 bill after a GBP 30 credit),
and the engine cut the face to `min(asked, open)` again, so neither P&L carried the 682.47. So (2) was neither held nor refuted
by this count: it measured a face, and could reach 0 only on a book where no settlement was ever cut. Neither (i) nor (ii) is
shown. The book does not record the triad's cash, so I cannot yet say whether its walk agrees with the engine's.
The fix makes the claim measurable: the truth now records the cash on each settlement, and the engine's row carries it
(`tests/simulation/test_the_world_records_the_cash_a_settlement_carried.py`). **Prediction for the first book carrying it:**
the same count reads (2) = **0**, and no P&L figure moves from this change. Any residual is a real (ii) disagreement between
`_leg_rows` and `_resolve_bills`, and is the next item. The pre-registration below still holds for the 18:40Z book, which predates it.

**What this means for the 9 Nov publish.** Suppose the next book clears N20. It is still refused on the cap-note row (3), on N17's
electricity row (2 legs, a world fix that waits on the ERA5 pull), and on SYN-2016-206g's gas row (1). None of the three has a
dated exception. Each needs either a fix or a named, dated exception before a book can pass. Both are options under the
26 Oct ruling's step 4. That choice is the next item, not this one.

### Pre-registration for the next book (filed 18:10 GMT, before the runner starts it at about 18:40Z)

It is the first built at or after a66e97829, and the first that can carry the schedule.
- `level_dd_collections` **present**. The N20 test's `share_equal_to_the_bill` is at or below 0.30, near 0.207 (range 0.15 to 0.30), as filed.
- The gate row's Leg A (BILL-TRACKING, excluding x1 to x4) is also at or below 0.30, so the row is **CLEAN**, or at worst FLAG. Its Leg B (accounts that show a level amount) is at least 0.70.
- If either share reads above 0.30, the schedule reaches the book but not the ledger's payments. That is the next defect, and not a tolerance to widen.
- INV_ELEC 2 legs and INV_GAS 1 are unchanged, since nothing in between touches demand. The cap-note row stays at 3. Every other count is unchanged except denominators.
- 26c891276's (2) stays at 19 within plus or minus 3, because nothing in between touches the triad.

## One fate for each unexcepted red on 8c7489e0d9, before the 9 Nov window (delivery seat, 2026-11-07 ~20:00 GMT)

| Row | Fate | Where |
|---|---|---|
| INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE (3) | **Fixed in company/**. Under the EPG, a two-register bill is graded against the published multi-register cap, not the EPG scaled by the cap's ratio. A replay on this book takes the 3 excesses to 0, and nothing else moves. | `company/compliance/domain_invariants.py`; the E7 finding's 7 Nov progress |
| INV_ELEC_MONTHLY_USE_MOVES_YEAR_ON_YEAR_LIKE_A_HOUSEHOLD (2 legs) | **Dated exception**, world side (N17). Recheck by 2026-11-23. It is retired by the W2_30 slice `n17_year_on_year_slice_note` plus the ERA5 pull. | `DOMAIN_INVARIANT_EXCEPTIONS.yaml` |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR (1, SYN-2016-206g) | **Traced to the world; dated exception**. It is refused a fabric trace and settles on the 70/30 split, so every month with no heating degree days is aq x 0.30/365 a day with a constant AQ. That gives 421.4295 kWh in five Julys and two Augusts, and a register advance of 37.5584 m3 every time. Recheck by 2026-11-23. | `DOMAIN_INVARIANT_EXCEPTIONS.yaml` |
| INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE (1) | **Not re-graded here**. It is read from the first fresh book carrying the level DD schedule (continuation `grade-the-first-book-carrying-the-level-dd-schedule`). No such book existed at 19:42Z. If that book is still red, its fate is owed before 04:00Z on 9 Nov. | — |

The N15/N16 page rows (INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM, INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED) are
now on origin, so the next book is graded on them too. Their first readings were 0 and 0 (cast after 8d99f4d31c).
Neither has an exception. If either is red on the next book, it needs a fate as well.

`recheck_by` is a recorded commitment, not a control: `gate()` checks only the five required fields and the ceiling.
