**Severity:** LATENT · **Lane:** D_billing_metering · **Atom:** `W2_21_the_premise_joint_is_fitted_not_drawn_independently`

# What the insulation change can move in the 16 Nov pre-registrations (2026-11-13)

e17ebc596 (13 Nov 19:08Z) changed the world's insulation draw: 72.1% of the fitted stock POOR became 15.2%. Six
grades on the 16 Nov 04:00 book were pre-registered before it. So that book carries the change each grade was written
for, plus this one. This record measures what the fabric change moves on its own, so that each grade can subtract it.
**It grades nothing.** Each pre-registration carries a dated amendment that points here and keeps its original
prediction.

## Method: one variable

Two worktrees, at `e17ebc596^` (f3e7962e82) and at `e17ebc596`. Between those two commits only
`simulation/premise_population.py` differs on any path a book reads. The comparison is against `e17ebc596`, not
origin/main, as direction asked. Origin/main also carries ceeefa5960 (the refund clock, `simulation/arrears_engine.py`),
which moves request days by design. Differencing against origin/main would put two changes in one delta, which is
the thing this record exists to prevent.

## Step 1, the population (run, 13 Nov 23:15Z)

`simulation.live_population.live_population(20260724)` and `live_drawn_households` at each commit, with seed 20260724
(the production default). Probe: `/var/tmp/fab-probe/probe.py`. Outputs: `/var/tmp/fab-probe/{old,new}.json`.

| | e17ebc596^ | e17ebc596 |
|---|---:|---:|
| accounts on the book | 1,046 | 1,049 |
| founders (SYN-*, drawn by `population_draw`), insulation | unchanged | unchanged, 0 of 675 move |
| hand-authored roster (C1…, incl. C5, SME) | present, no drawn home | present, no drawn home |
| campaign accounts (PROS-*) | 358 | 361 |
| PROS in both books | 192 | 192 |
| PROS leaving / joining | 166 leave | 169 join |
| drawn homes changing insulation level, among those in both | | 130 (128 PROS, plus SYN-2025-001 and its gas leg) |
| drawn homes POOR / PARTIAL / FULL | 326 / 679 / 28 | 142 / 780 / 114 |

**What this shows.** Fabric reaches the book by three routes:

1. **Which homes the campaign wins.** It wins on modelled saving, and modelled saving reads fabric. 166 of 358
   PROS accounts are replaced. Any pre-registered **count** taken over the whole book can move by this route
   alone, whatever the mechanism it was written for.
2. **The fabric of a PROS home that stays.** For example, PROS-2019-0318 goes from POOR to PARTIAL. This moves its
   heating demand and so every bill.
3. **A mover's destination.** `simulation/move_destination.draw_destination` draws the new home from the fitted joint.
   Any household that moves, founders included, has new fabric after the move.

The founders' own homes come from `population_draw`, not the fitted joint, and none of them changes. Before its
move, if it has one, a founder's consumption can move only through route 3 or through the company's book-level
decisions (pricing, hedge and cash all read the whole book, and the book changed).

**Named accounts, by route 1 or 2:**
- n29 cross-arm legs: **PROS-2021-0117 is not on the e17ebc596 book** (the campaign no longer wins it).
  PROS-2019-0318: POOR → PARTIAL. SYN-2016-047, SYN-2016-142g and SYN-2016-139: home unchanged.
- §9.8's 24 class-F accounts: **PROS-2016-0067, PROS-2017-0038g and PROS-2017-0249 are not on the e17ebc596 book.**
  PROS-2016-0349g, PROS-2017-0199 and PROS-2018-0359: POOR → PARTIAL. The 18 SYN accounts: home unchanged.
- §9.8 W2's five credit-bill accounts (SYN-2016-037, -225, -333, -444, -482) and W4's SYN-2016-244: home unchanged.
- C5: SME, hand-authored, no drawn home. It is on both books.

## Step 2, the book A/B (in flight)

Two full books, `python3 -m tools.run_annual_report`, one per worktree. Units `longjob-fabric-ab-old` (started
23:21Z) and `longjob-fabric-ab-new` (queued for memory behind the value test). Artefacts
`/var/tmp/fab-probe/run_{old,new}.json`. Each is put through the publisher's page chain
(`/var/tmp/n29/scripts/chain.py`) in its own worktree. It is then graded the way the publisher grades
(`runner.load_book` + `runner.run`), so each pre-registered figure is read at both commits and differenced.

*Prediction, filed before either book exists:* C5-INV113's lines do not move (C5 has no fabric, and Sep 2016 is
before most of the campaign's book exists). Every whole-book count does move, by more than its own pre-registered
band in at least one case, because 166 PROS accounts are replaced.

## C5-INV113: the pre-registration this record holds

C5's per-rate catch-up lines had no pre-registration record of their own. f0bca8e35 retired its staging finding by
deleting it. So the prediction is restated here from that commit and from the continuation
`catchup-vat-rows-on-the-16-nov-page`.

**Original (f0bca8e35, 13 Nov):** the 16 Nov `site/data/customers/C5.json` carries C5-INV113
`catchup_lines_by_rate`: 20% net −157.51, VAT −31.50; 5% net +112.49, VAT +5.62. These sum to −45.02 and −25.88,
and `catchup_corrects_invoices` is [C5-INV112].

**Amendment (2026-11-13, about e17ebc596 only):** C5 has no drawn home, so fabric cannot move its consumption
through route 2 or 3. Whether route 1 moves its bill is settled by the book A/B. The result goes in the table below.

**Amendment (2026-11-14, about e17ebc596 only, settled by the A/B):** fabric cannot move this. C5-INV113 reads
−157.51 / −31.50 and +112.49 / +5.62, correcting [C5-INV112], at both e17ebc596^ and e17ebc596. The original
prediction stands unchanged for the 16 Nov page.

## The A/B table

**Old arm read 14 Nov 01:25Z.** Book `run_old.json`, producing commit f3e7962e82 (= e17ebc596^). Neither arm carries
ceeefa5960 (the refund clock) or 69866925b (S6b). Both arms carry 3af02a2dd, 37d934286, b3ff041f0, c915067a8 and
f0bca8e35, so every grade's own change is on both sides. The 01:15Z auto-SALVAGE commits on both arm worktrees hold
observability JSON only, and no code.

**Correction to step 2's instrument, beside it.** `/var/tmp/n29/scripts/chain.py` omits
`generate_customer_reaction_chain`. That step is the publisher's last page step (`process_run_complete`, after the
payment ledger), and it writes the timeline's final bills. Without it, `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`
reads NOT_IN_EXPORT and the closing-refund row reads UNREACHED, 0 checked. The first old-arm grade read exactly that.
Both arms are graded with `/var/tmp/fab-ab2/chain_full.py` (the five steps in the publisher's order) and
`/var/tmp/fab-ab2/grade_arm.sh`, then read with `/var/tmp/fab-ab2/read_arm.py` (outputs `/var/tmp/fab-ab2/`).

| pre-registration | figure (its predicted value) | e17ebc596^ | e17ebc596 | fabric moves it? |
|---|---|---:|---:|---|
| C5-INV113 | 20% net / VAT (−157.51 / −31.50) | −157.51 / −31.50 | −157.51 / −31.50 | **no**: identical to the penny |
| C5-INV113 | 5% net / VAT (+112.49 / +5.62) | +112.49 / +5.62 | +112.49 / +5.62 | **no**; `corrects` [C5-INV112] on both |
| n29 P1 | `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` breached (only SYN-2016-139) | 0 of 1,668 (FLAGGED, 76) | 0 of 1,679 (FLAGGED) | breach count no; denominator +11 |
| n29 P2 | `INV_A_CLOSING_REFUND…` breached (29 ± 3) | 30 of 129 | 31 of 130 | yes, +1 |
| n29 P3 | refunds with a set-off (42 ± 5) | 45 of 184, GBP 1,400.40 | 43 of 187, GBP 1,469.38 | yes, −2 |
| §9.8 W1 | level leavers' final bills netted (170–215, GBP 4,200–5,200); proxy: an ever-level closed leg whose last bill carries `credit_applied_gbp` | 246 of 485, GBP 6,579.51 | 244 of 481, GBP 6,317.04 | yes, −2 legs, −GBP 262.47 (−4.0%) |
| §9.8 W2/W3 | R5 desk-written-off accounts printing owed (W3 0–3; W2 F 0–3) | 30, GBP 699.65 | 27, GBP 674.59 | yes, −3: 4 leave, 1 joins (below) |
| §9.8 W4 | SYN-2016-244 final bill asked (GBP 30–45) | 77.82 (face 77.82) | 77.82 (face 77.82) | **no** |
| n30 P1/P2 | s (0.22–0.36), row CLEAN | 0.2706, CLEAN | 0.2740, CLEAN | s +0.0034; verdict no |
| n30 P3/P4 | traditional pairs billed both (16,271 ± 15%); pairs with a read (3,000–5,000) | 16,244; 3,873 | 16,195; 3,843 | yes, −0.3%; −0.8% |
| n30 P5 | smart/smart one-only (near 12%, 5–20%) | 6.9% (214 of 3,098) | 6.2% (165 of 2,655) | yes, −0.7 pt; smart pairs −12% |
| c915067a8 | off-day openers in window (→ 0); off-day re-offers in window (→ 0) | 2; 0 | 2; 0 | **no**; other journey counts move up to −126 |
| baseline | publisher gate verdict line | 27 unexcepted breaches across 5 rows, 7 excepted: refused | 19 unexcepted across 5 rows, 7 excepted: refused | count yes (−8); verdict no |

These old-arm readings are the comparator only. They are not grades: the 16 Nov book also carries ceeefa5960 and
69866925b, which neither arm has.

**New arm read 14 Nov 03:30Z.** Book `run_new.json`, producing commit 01f3706d04. That is e17ebc596 plus one auto-SALVAGE
commit that touches only `docs/observability/book_growth_campaign.json` and `book_subset_verdict.json`, so no code
differs. Graded with the same scripts (`grade_new.json`, `grade_new.log`, `read_new.json` in `/var/tmp/fab-ab2/`),
then differenced by `/var/tmp/fab-ab2/figures.py`.

**R5's movers.** 4 leave: PROS-2016-0067, PROS-2017-0038 and PROS-2017-0249 (not on the new book, route 1) and
PROS-2019-0318 (POOR → PARTIAL, route 2). 1 joins: PROS-2019-0125. The founders' own accounts stay in the set.

**How far fabric reaches.** Of the accounts on both books, per-customer P&L is identical for 13 of 13 hand-authored
accounts, 427 of 673 SYN founders and 46 of 190 PROS. So 246 founders move without a home change, through route 3
or through book-level decisions. That fits step 1's routes.

**What I cannot say.** No same-commit replicate was run, so each delta is fabric plus any run-to-run noise. The
noise is zero on every figure that reads identically (C5, W4, c915067a8's two counts), and C5 is identical on all
13 hand-authored accounts. It is unmeasured on the rest.

**The prediction, graded against itself.** C5-INV113 does not move: **held**. "Every whole-book count moves, by more
than its own pre-registered band in at least one case": **refuted**. Every count moves, and none moves by as much
as its band. The largest relative moves are n30's smart pairs (−12%, a denominator, with no band) and W1's GBP
(−4.0%). Fabric replaces 166 PROS accounts, but the graded figures are dominated by founders, whose homes do not
change.

**What the 16 Nov grader subtracts.** Each pre-registration carries its own amendment (14 Nov) with the shifted
value: `SEAT_PREREG_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-12.md`, `LEVEL_DD_AREA_MAP_2026-11-11.md` §9.8,
`SEAT_PREREG_WHAT_THE_16_NOV_BOOK_GRADES_ON_DUAL_FUEL_READS_TAKEN_TOGETHER_2026-11-13.md`, the c915067a8 section
of `SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL_…_2026-11-07.md`, and the baseline record's
amendment A7. C5-INV113's amendment is the section above. Fabric cannot move it: C5's lines are identical on both
arms, so the original figures stand.

**Reverse.** Delete this file and the six amendments that cite it.
