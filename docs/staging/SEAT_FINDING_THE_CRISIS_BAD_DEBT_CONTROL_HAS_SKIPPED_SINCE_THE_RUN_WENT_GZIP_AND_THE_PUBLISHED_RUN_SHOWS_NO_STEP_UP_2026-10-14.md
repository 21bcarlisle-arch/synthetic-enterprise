**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build`
**Knowledge:** none -- a control grading a published run against the bad-debt step-up already recorded in docs/market_research/ASSUMPTIONS.md (1.3% to 2.8% of revenue); no new domain claim

# The crisis bad-debt control has skipped since the run went gzip, and the published run shows no crisis step-up (2026-10-14)

**Fate (2026-10-15):** ATOM -- folds into `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-14):** ATOM -- world fidelity, the affordability cluster's question (W2_4..); the control's reader fix lands with the cause's fix, never alone.
**Fate (2026-10-15):** stays OPEN. The roll-rate matrix and the reader fix land together (shipped off). The leg that still fails is the validator: 2021-22 does not step up on either basis, and the roll-rate matrix's own charge also peaks in 2023. See the last section.

## What was found

`tests/company/compliance/test_crisis_bad_debt_validator.py` reads `docs/reports/run_output_latest.json` by
its plain path and **skips** when it is absent. Since 2026-10-10 the publish commits only
`run_output_latest.json.gz` (tools/run_output_store.py). So in every worktree and every gate extract
both live legs have skipped and passed silently. Only the shared tree, which keeps the plain file,
could still run them. Found while fixing red #7, which read the plain path the same way and failed
outright rather than skipping.

## Read through the store, the control fails on both published runs

`validate_run_output`, run on both runs and both bases:

| run | basis | crisis-years rate | pre-crisis rate | verdict |
|---|---|---|---|---|
| committed gz, 2248e3baf (13:44Z) | headline | 0.0988% | 0.1534% | FAIL |
| committed gz, 2248e3baf | pnl_accrual | 1.7566% | 2.0055% | FAIL |
| shared plain, 6ab998ad7 (22:05Z) | headline | 0.0988% | 0.1535% | FAIL |
| shared plain, 6ab998ad7 | pnl_accrual | 1.7568% | 2.0058% | FAIL |

Bad debt as a share of revenue **falls** in the crisis years on both bases. The published record
has it rising from 1.3% to 2.8% of revenue. 2022 is a fact, not a scenario.

## Measured since: the pounds DO step up, late and short (corrected beside the headline)

The table above grades the SHARE. On the accrual basis the pounds rise: GBP 3,531 (2021) to
GBP 5,698 (2022) and GBP 11,342 (2023), against GBP 3,758-4,126 a year in 2017-2020. 2023 is
about 3.2x 2021. The 2022 share falls because revenue doubled (GBP 177k to 348k) while
write-offs lag into 2023. So "no step-up" is too strong. **The world's step-up arrives a year late
(2023) and stays short in share (2.35% at peak against 2.8% published)**, and the validator's window
(CRISIS_YEARS = 2021, 2022) misses the year it lands in. Before the world changes, decide which is
wrong: the lag (when a real supplier writes 2022 debt off) or the window. That is a knowledge
question first.

## What I cannot yet say

A share can fall while pounds rise, because revenue roughly doubled with prices in 2022. Whether
the **pounds** of bad debt step up, and by how much, is not measured here. That is the first
number to print, before any change. The test's own comment already marks the cause as not
established: whether the step-up emerges from a household budget meeting the price shock is the
affordability cluster's question. The book is now the 774-household founder book. Whether the
control passed on the 127-household book is not checked either.

## The reader fix, held back on purpose

The change, as a diff (it applies to origin at 3476f2398):

```diff
diff --git a/tests/company/compliance/test_crisis_bad_debt_validator.py b/tests/company/compliance/test_crisis_bad_debt_validator.py
index e4e18f6c5..ee968d144 100644
--- a/tests/company/compliance/test_crisis_bad_debt_validator.py
+++ b/tests/company/compliance/test_crisis_bad_debt_validator.py
@@ -31,6 +31,7 @@ from company.compliance.crisis_bad_debt_validator import (
     validate_crisis_bad_debt,
     validate_run_output,
 )
+from tools.run_output_store import load_run_output, resolve_run_output
 
 _RUN_OUTPUT = Path(__file__).resolve().parents[3] / "docs" / "reports" / "run_output_latest.json"
 
@@ -82,9 +83,9 @@ def test_zero_revenue_year_does_not_crash():
 
 
 def test_extract_both_bases_from_run_output():
-    if not _RUN_OUTPUT.exists():
-        pytest.skip("no run_output_latest.json present")
-    run = json.loads(_RUN_OUTPUT.read_text())
+    if resolve_run_output(_RUN_OUTPUT) is None:
+        pytest.skip("no run_output_latest.json present, plain or gzipped")
+    run = load_run_output(_RUN_OUTPUT)
     head_bd, head_rev = extract_series_from_run_output(run, "headline")
     pnl_bd, pnl_rev = extract_series_from_run_output(run, "pnl_accrual")
     # Both bases must yield the crisis years.
@@ -106,8 +107,8 @@ def test_extract_both_bases_from_run_output():
 # meeting the price shock rather than from a tuned propensity -- R12's condition for closing the
 # gap. That question is the W2_4.. affordability cluster's and is not answered by this pass.
 def test_live_run_output_shows_crisis_step_up_headline():
-    if not _RUN_OUTPUT.exists():
-        pytest.skip("no run_output_latest.json present")
-    run = json.loads(_RUN_OUTPUT.read_text())
+    if resolve_run_output(_RUN_OUTPUT) is None:
+        pytest.skip("no run_output_latest.json present, plain or gzipped")
+    run = load_run_output(_RUN_OUTPUT)
     result = validate_run_output(run, "headline")
     assert result.passed, result.summary()
```

In short: resolve_run_output and load_run_output in
place of `.exists()` and `json.loads`. Landing it alone would put a red at HEAD that every gate
refuses. Landing nothing leaves the control silent, which is what this finding records. **The
patch lands in the same commit as the fix to the cause, or with a recorded acceptance of the red.**

## A sibling, noted

`tests/tools/test_a_published_rate_says_which_rate_it_is.py` reads the plain path the same way and
skips in gz-only checkouts. Its conversion was withdrawn on 2026-10-10 (34aa44858) only because the
shared tree held an uncommitted edit of it. That edit is gone (the shared copy is clean,
2026-10-14), so the conversion can land again. The stale-copy gate reads it as re-creating a
deliberate deletion, so it lands through that gate's own door with this note as its reason.

## 2026-10-14 (evening): the reader fix landed with the first leg of the cause's fix

Worked as `the-bad-debt-provision-charges-expected-loss-as-arrears-build`.

- **The reader.** Both live legs now read the published run through `tools/run_output_store`, and a
  new control fails (not skips) if a gz-only checkout cannot load it; mutation-proven (the plain-path
  reader turns it red). The live legs are re-armed as **strict xfails on both bases**, the module's
  own convention: both published runs fail on both bases, so HEAD stays green and the day a published
  run steps up on a basis, that leg XPASSes and reds the suite.
- **The validator's verdict, on both bases, is unchanged: 2021-22 does not step up in share.** Nothing
  in the run moved, because the build below ships off.
- **A premise of the item was wrong and is corrected here.** The flat age bands with no origin
  (`company/finance/bad_debt_provision._PROVISION_RATES`) reach no production code. The provision the
  run publishes is `default_belief.provision_stock`, on Centrica's Note 17 rates, and it does move most
  in 2022: the stock rises GBP 977 -> 1,604 (+627, against +34 to +317 in 2017-2021) as the receivable
  goes GBP 6,507 -> 16,905 (2248e3baf). What lags into 2023 is the P&L accrual line, which is the
  world's write-offs. The validator grades the world's write-offs and the P&L accrual, never the
  company's provision.
- **Built, off:** `bad_debt_provision.roll_rate_provision_stock`, a matrix learned from the company's
  own monthly roll rates, point in time, with the overlay at its two ends (0 and 0.134). Knowledge
  first: `docs/market_research/bad_debt_provisioning.md`, section "A provision matrix whose loss rates
  come from the company's own roll rates" (2026-10-14).

**Still open: the printed charge by year.** The roll rates need the run's ledger, which the published
run does not carry, so the 6ab998ad7 book cannot be re-read; a 40-founder run with the switch on
in-process is the measurement (`/var/tmp/rollrate/member.py`, seed 61109).

## 2026-10-15: the matrix lands, and its charge by year also peaks in 2023

Landed from the stranded `/home/rich/wt-baddebt-rollrate` (owner pid gone) as
`the-roll-rate-provision-lands-from-wt-baddebt-rollrate`. No subject path had moved on origin since
its base f4df6adb5, so the files were carried over whole. `ROLL_RATE_PROVISION` ships `False`.

**The charge by year**, from `/var/tmp/rollrate/out/provision_61109.json` (40 founders, 453 homes,
seed 61109, run at f4df6adb5 with the switch on in-process). The company ledger records **no
write-offs to date at any year end** (`written_off_to_date_gbp` = 0.0 throughout), so the charge is
the change in the stock. GBP:

| year | receivable | Note 17 stock | charge | roll-rate, no overlay: stock | charge | roll-rate, overlay 0.134: stock | charge |
|---|---|---|---|---|---|---|---|
| 2017 | 999 | 93.20 | +59.11 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2018 | 2,572 | 178.06 | +84.86 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2019 | 2,338 | 234.92 | +56.86 | 137.11 | +137.11 | 158.32 | +158.32 |
| 2020 | 3,324 | 434.45 | +199.53 | 355.31 | +218.20 | 410.29 | +251.97 |
| 2021 | 4,759 | 565.27 | +130.82 | 389.55 | +34.24 | 449.82 | +39.53 |
| 2022 | 12,967 | 990.48 | +425.21 | 574.41 | +184.86 | 663.29 | +213.47 |
| 2023 | 10,807 | 1,247.21 | +256.73 | 901.81 | +327.40 | 1,041.35 | +378.06 |

- **The learned matrix lags the shock, as the knowledge page predicted.** The receivable nearly
  triples in 2022 (4,759 to 12,967), but the roll-rate stock covers only 4.4% of it at end-2022,
  against 8.2% at end-2021. The charge peaks in 2023. The published-rate (Note 17) stock charges
  most in 2022. At the high end the overlay is a fixed share, so it scales the lag and does not move
  it. That is the gap Centrica's 2022-23 overlay filled.
- **2017-2018 read 0.00 with `reason: None`.** Before the 24-month window fills there are 320 and
  517 transitions but no rate that reaches the terminal age. That zero should be a `None` with a
  reason (K2), not a provision. It is noted here and not fixed in this landing.
- **The validator, read through `tools/run_output_store`:** unchanged. 2021-22 **does not step up**
  on either basis (both strict xfails hold; 801 passed, 2 xfailed across `tests/company/finance/` and
  the validator module). The validator grades the world's write-offs and the P&L accrual, never the
  company's provision, so no provision switch can turn it. The open leg is the world's write-off
  timing against `CRISIS_YEARS`: the knowledge question above, still unasked.

## 2026-10-15 (morning): pre-registration, written before re-grading the published run on a moved window

The knowledge page already answers the timing question (`bad_debt_provisioning.md` §3.2, §2.3):
Centrica's UK charge ran 1.2% (2019), 2.2% (2020), **1.1% (2021, the low)**, 2.1% (2022), **2.7-3.1%
(2023, the high)** of revenue; Ofgem's industry debt-cost series peaked in summer 2023. So in the
real record the charge's step-up is 2022-2023, and 2021 is the trough. Predictions, filed before
the validator is run on a (2022, 2023) window against the committed gz run:
- **pnl_accrual: still FAIL**, step-up about x1.02 (crisis about 2.05% against about 2.01%
  pre-crisis), because 2022's share dips while revenue doubles.
- **headline: still FAIL**, the behavioural write-off share stays near 0.1%, far under the 1% floor.
- So both strict xfails hold, and moving the window cannot be read as tuning the control to pass.

## 2026-10-15: graded, and decided

**The predictions held.** On the committed run, with the window at 2022-23: P&L accrual x1.02 (2.0497%
against 2.0055%), headline x0.57. Both legs fail, both strict xfails hold.

**Decided** (`bad_debt_provisioning.md`, section "When a GB supplier charged and wrote off 2022-era
arrears"):
- **The window was wrong.** Centrica's charge was 1.1% of revenue in 2021, its low, then 2.1% in 2022
  and 2.7-2.9% in 2023. Ofgem's series peaks in 2023. `CRISIS_YEARS` is now (2022, 2023).
  **Corrected beside the claim:** the anchor this finding and the validator quoted, "2.3% to 2.8%", is
  Centrica's FY2025 Q&A, a 2025 movement and not the crisis. A new control feeds Centrica's published
  series through the validator and requires a pass. It is mutation-proven: reverting the window reds it.
- **The world's write-off lag is not the defect.** Real write-offs did not step up in share either
  (GBP 58m, 93m, 113m in 2021-23 as revenue doubled). The headline leg grades write-offs against a
  charge anchor. Its xfail now says that, and an XPASS there would itself be a fidelity question.
- **The leg still open is the P&L charge.** The real charge is the movement in provisions plus
  write-offs, less recoveries (Ofgem App. 2 §3.14). This finding's 2026-10-14 reading is that our
  accrual line follows the world's write-offs. That reading was not re-traced this turn. The
  company's Note 17 stock already moves most in 2022. The next build: make the published P&L
  bad-debt line the IFRS 9 charge, then re-grade. Its prediction will be filed before the run.
- **Done:** `roll_rate_provision_stock` returns `None` with a named reason, and the whole receivable
  unrated, while no debt in the window has reached the last age before terminal (11 months). A zero
  roll followed by an unobserved age had multiplied out to 0.00. The control is mutation-proven, and
  it asserts the branch can be left: the same book at 30 months provides.

## 2026-10-15 (afternoon): the P&L line traced. It is neither the write-offs nor the IFRS 9 charge

Worked as `the-published-pnl-bad-debt-line-is-the-ifrs9-charge-not-the-write-offs`.

**Corrected beside the 2026-10-14 reading** ("our accrual line follows the world's write-offs"):
it does not. `management_accounts[*].income_statement.bad_debt_gbp` is account 6001
(`company/finance/double_entry.py`), and the only thing that posts to 6001 is `bad_debt_event`
(`saas/ledger.build_ledger`). `close_the_books` passes no payment model, so the default,
`saas/payment_behaviour`, is used: **every issued bill books `total_amount_gbp x rate` as a write-off**,
dated 30 days after its expected payment date, debit 6001, credit 1100. The rate is read from
`CREDIT_RISK_BY_CUSTOMER`, a seed table naming four toy ids (C1-C4), so every real account takes the
`medium` default, 2%. Because the bill is VAT-inclusive, that is about 2.1% of ex-VAT revenue. The
validator's own docstring already said this ("a broadly FLAT ~2% rate every year -- it tracks
revenue"); the finding did not. On the committed run, by year, as a share of revenue: 2.12, 2.11,
2.15, 2.20, 1.99, **1.64 (2022)**, **2.35 (2023)**, 2.14. 2022 dips and 2023 rises only because a
bill's charge is booked 30+ days after its period, so the expensive winter of 2022-23 lands in 2023.
The pattern is timing, not credit.

The real thing (Ofgem, Debt-related costs, App. 2, May 2025, para 3.14) is the IFRS 9 charge: the
movement in the provision plus write-offs, less recoveries. The company's own pieces are in the
published run: `company_provision.by_date` (the Note 17 stock at each year end), and its ledger's
write-offs. The 40-founder roll-rate run recorded no write-offs at any year end
(`written_off_to_date_gbp` = 0.0), and nothing in the run posts a `WRITE_OFF_CREDIT` to the triad's
ledger. So the company's IFRS 9 charge is the movement in its stock.

### Pre-registration (before the validator is run on that series)

The stock figures were printed before this was written (end-2016 to end-2024, GBP 96.96, 363.25,
680.49, 803.13, 837.10, 976.59, 1,603.95, 2,089.66, 2,384.10), so the charge itself is arithmetic,
not a prediction. The test is what the validator makes of it, with 2016's charge taken from a zero
opening stock (the company opened in 2016):
- **level: FAIL.** The crisis-years charge is about 0.13% of revenue, far under the 1% floor.
- **step-up: FAIL**, about x1.1 against the 1.2x bar: about 0.13% in 2022-23 against about 0.12% in 2016-19.
- **So the IFRS 9 basis fails on both conditions, as the accrual and headline bases do.** It fails
  for a reason neither of them shows: it is about ten times under the real band.
- If the company's charge is about a tenth of a real supplier's, the P&L line cannot simply be
  swapped. Swapping it would cut published opex by about GBP 45k over the run, so every margin
  would rise. That errs FOR the thesis (F11). Prediction for the decision: the line is not swapped
  in this turn. The IFRS 9 charge is graded and published as its own basis.

### Graded: the predictions held

The validator has a third basis now, `ifrs9_charge` (`company/compliance/crisis_bad_debt_validator.py`).
It is the movement in `company_provision.by_date`'s year-end stock, plus the movement in
`written_off_to_date_gbp` once a stock carries it, against management-accounts revenue. A year whose
prior stock is missing is left out rather than charged from zero. On the committed run:

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| charge GBP | 96.96 | 266.29 | 317.24 | 122.64 | 33.97 | 139.49 | **627.36** | 485.71 | 294.44 |
| % revenue | 0.097 | 0.141 | 0.162 | 0.066 | 0.020 | **0.079** | **0.180** | 0.101 | 0.092 |

The crisis years come to 0.1339%, against 0.1200% for 2016-19: **x1.12, FAIL on both the floor and
the step-up**, as predicted. A third strict xfail holds it. A new control fails if the basis yields
no crisis years, because an empty series would otherwise hold that xfail trivially.

**What this says that the other bases did not.** The company's own charge has **the real shape**:
2021 is the low, 2022 the high, and 2022/2021 is x2.3, against Centrica's 1.1% to 2.1% (x1.9).
What it lacks is **the real level**, which is about a tenth of the real one. The 2016-19 baseline is
inflated because the stock fills from zero as the book is built (2017-18). That is book growth, not
credit, and it is why the step-up test reads x1.12 while the 2021-to-2022 move is x2.3.

### Decided: the published P&L line is not swapped in this turn

Swapping `bad_debt_gbp` to the IFRS 9 charge would take the published bad-debt cost from about 2.1%
to about 0.13% of revenue. That is about GBP 45k off opex over the run, and every published margin
would rise. The direction errs for the thesis (F11), and the level sits 8-20x under the real 1-3%
band (`domain_invariants.BAD_DEBT_RATE_RESI`). Each line is wrong in its own way:
- The **P&L line** is in band only because a seed rate puts it there. The 2% is
  `saas/payment_behaviour.DEFAULT_PROBABILITY_BY_CREDIT_RISK["medium"]`, and its keying table
  names four toy ids. It is a number picked to fill a slot, applied to every bill whether paid or not.
- The **IFRS 9 charge** is the right definition, read off what the company actually saw. It is a
  tenth of the real level because the company's receivable rarely goes bad. Two reasons:
  (a) **the company never writes anything off.** No production caller posts a `WRITE_OFF_CREDIT` to
  the triad's ledger (`company/billing/arrears_engine.build_write_off_event` has no caller), so
  unpaid debt ages forever at the oldest band's rate and is never charged in full. (b) How much the
  world's households fail to pay is the W2_4.. affordability cluster's question.

So the swap waits until at least (a) is built, and the two are graded side by side until then.
Handed on as the continuation `the-company-writes-off-what-its-own-ledger-says-is-gone`.

**Status:** OPEN. The window is right and all three bases are graded. None of them steps up at the
real level.

## 2026-10-15 (evening): the company writes off its own closed-account debt. Pre-registration first

Worked as `the-company-writes-off-what-its-own-ledger-says-is-gone`. Knowledge first:
`docs/market_research/bad_debt_provisioning.md`, section "When the company writes off its own
closed-account debt, and what the recoveries line counts".

**Built.** `arrears_engine.closed_balance_write_offs` writes off a closed account's unpaid balance
365 days after its final bill. The 365 days is a labelled convention, because C4 is not published.
Live arrears are never written off on a clock. Each month-end sweep reads the ledger as it stood
that day, by valid time and by transaction time. The sweeps run once the run is over
(`LivePaymentTriad.write_off_closed_balances`), because bills post in term order and not date
order. Each stock now carries `written_off_to_date_gbp` and `recovered_to_date_gbp`, and the
`ifrs9_charge` basis subtracts the recoveries' movement.

**What the premise got wrong, measured before any run.** "With no write-offs, unpaid debt ages
forever at the oldest band's rate", so it is never charged in full. That much is true. But the
final-bill row over 90 days is already 87.8%, so a write-off adds only the other 12.2% of its face.
On the committed run the year-end final-bill receivable is GBP 241 to 1,723, so writing off all of
it could move the decade's charge by about GBP 200, against about GBP 2.2m of revenue. **A
write-off cannot close a tenfold level gap.** The gap is the size and age of the receivable
(year-end final-bill debt at most about 0.5% of revenue, pay-on-receipt debt over 90 days at most
about 0.2%), and that is the world's non-payment.

**Pre-registration, filed before the run** (40 founders, seed 61109, `all_wins`, as the roll-rate
run). Two arms on one ledger: (A) the year-end stocks read before the sweep, and (B) after it.
1. Write-offs posted: more than 0. Recoveries at every year end: exactly 0.00, because the world's
   final-bill model has "no later lump".
2. Arm B's charge over the decade exceeds arm A's by less than GBP 300, and in every year by about
   0.122 of what was written off that year.
3. On the `ifrs9_charge` basis both arms FAIL both conditions. The crisis-years share stays
   between 0.10% and 0.20% of revenue, and the step-up stays under x1.2.
4. So the published P&L line is still not swapped. The level gap goes back to the world's
   affordability cluster.

### Graded (2026-10-15, late): predictions 1 and 2 held; prediction 3 did not grade on the first run

Worked as `the-write-off-two-arm-run-graded-against-its-pre-registration`. The run (unit
`longjob-writeoff-two-arm-61109`, worktree at 7e7c59779, seed 61109, `all_wins`) used **12 founders,
not the 40 pre-registered**. The launch record says why ("shares are scale-free"). The book was 279
homes. Both arms were read from one ledger (`provision_61109.json`) and put through the validator's
own `_ifrs9_charge_series`:

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| A charge GBP (before sweep) | 20.25 | -0.33 | 91.55 | 48.23 | 61.23 | 59.10 | 171.43 | 156.91 | 134.63 |
| B charge GBP (after sweep) | 20.25 | -0.33 | 91.55 | 48.23 | 78.10 | 59.10 | 179.60 | 156.91 | 156.96 |
| written off in year, GBP | 0 | 0 | 0 | 0 | 138.29 | 0 | 66.95 | 0 | 183.05 |
| B - A / written off | | | | | 0.1220 | | 0.1220 | | 0.1220 |

1. **Held.** Nine write-offs were posted, with a face value of GBP 388.29 by end-2024. Recoveries are
   0.00 at every year end.
2. **Held.** Over the decade, B exceeds A by GBP 47.37, under the GBP 300 bound. In each year with a
   write-off, the excess is 0.1220 of the face written off, which is exactly the un-provided 12.2%. The
   stock itself falls much further (end-2024: A 743.00, B 402.08), because the provided 87.8% leaves
   the stock and re-enters as a write-off. The prose estimate "about GBP 200" was scaled to the
   40-founder book; this book is about a third of that size.
3. **Not graded on this run.** The first grader read `run_output["management_accounts"]`, which is
   empty at the point it is called. That gave zero revenue, and the validator's "no crisis-year data"
   FAIL in `graded_61109.json` is vacuous. It is not a result. The corrected grader
   (`member2.py`, which builds the accounts from `ledger_events` and refuses if they are empty) was
   relaunched as `-r2`. A user-manager teardown stopped that run at 09:29, along with every other
   service, at 2020-07 simulated. It is relaunched as `-r3`.
   It runs detached (`/var/tmp/writeoff/launcher3.log`) and is queued behind an 11.2 GB resident.
   **I cannot yet say** whether the crisis-years share falls inside 0.10% to 0.20%. The pounds alone
   step up from GBP 39.9 a year in 2016-19 to GBP 164.2 (A) or 168.3 (B) in 2022-23, which is x4.1. On
   this book that is mostly book growth and price, and the share needs this run's own revenue.
4. **Not graded yet.** It rests on 3. Prediction 2's GBP 47 does bound how far the write-off can move
   the decision: it is 6% of the decade's charge on either arm. A swap that was wrong without the
   write-off is still wrong with it, whatever the shares turn out to be.

Handed on as `the-write-off-run-r3-grades-prediction-3-and-removes-the-worktree`. The worktree
`/var/tmp/writeoff/wt` stays locked until r3 has run, because r3 runs in it.

### Graded (2026-10-15, r3): predictions 3 and 4 held. The share is only just inside, for a reason the prediction did not name

Worked as `the-write-off-run-r3-grades-prediction-3-and-removes-the-worktree`. The r3 launcher queued
behind the 11.2 GB heldgrade run and died with its tick before it was admitted. It was relaunched
detached (`/var/tmp/writeoff/launch3.sh`, `--wait-for-pid` on the heldgrade python), ran when that
run exited, and wrote `graded2_61109.json`. It ran in the same worktree as r1, with the same seed and
12 founders. The per-year charges are identical to r1's table to the penny, so the replay is
deterministic and the two runs can be read as one. Revenue is built from the run's own
`ledger_events`, and the grader refuses if they are empty. It did not refuse.

| year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| revenue GBP | 10,147 | 17,047 | 22,569 | 30,524 | 36,120 | 49,846 | 110,167 | 204,518 | 208,137 |
| A charge % revenue | 0.200 | -0.002 | 0.406 | 0.158 | 0.170 | 0.119 | 0.156 | 0.077 | 0.065 |
| B charge % revenue | 0.200 | -0.002 | 0.406 | 0.158 | 0.216 | 0.119 | 0.163 | 0.077 | 0.075 |

3. **Held, on all three parts.** Crisis-years share: A **0.1043%**, B **0.1069%**, inside 0.10% to 0.20%.
   Step-up: A **x0.52**, B **x0.54**, under x1.2. Both arms FAIL both the 1% floor and the step-up.
   **Beside the claim:** the step-up sits under x1.2 for a different reason from the one the
   prediction carried over from the committed run (x1.12 there). Here it falls, x0.5, because the
   2016-19 baseline is 0.199% against 0.120% on the committed run: on a 12-founder book the stock
   fills from zero against a tiny revenue (2018: GBP 91.55 on GBP 22,569, 0.41%). That is book growth,
   as already noted for the committed run, but larger on a smaller book. The crisis share passes the
   0.10% lower bound by 0.004 points (A), so "held" is narrow. The pre-registered 40-founder run might
   not have held it. Shares are not scale-free while the stock is still filling, so the launch
   record's reason for cutting to 12 founders was wrong for prediction 3. It was right for
   prediction 2, which is a ratio per write-off.
4. **Held.** The published P&L bad-debt line is **not swapped**. On either arm the IFRS 9 charge is
   about a tenth of the 1% floor in the crisis years. The write-off moves the crisis share by 0.003
   points (A to B), so it does not decide the swap either way. The level gap goes back to the world's
   non-payment (the W2_4.. affordability cluster) and, inside the company, to a receivable that
   rarely ages into debt. Swapping now would raise every published margin, which errs for the thesis
   (F11).

The worktree `/var/tmp/writeoff/wt` is unlocked and removed. Before removal it was checked against
origin: its eight modified source, test and knowledge files were byte-identical to origin/main. Its
untracked `test_closed_balance_write_off.py` was an earlier prefix of origin's longer copy. The rest
were run-written observability files and an older copy of this finding. r1-r3's outputs stay in
`/var/tmp/writeoff/out/`.

**Status:** OPEN, the same as before r3. All three bases fail at the real level. The P&L line stays
on the seed rate until the world's non-payment is grounded.

## 2026-10-16: the provision charge beside the company's own arrears, by year, from the committed run

Worked as `when-a-gb-supplier-charged-2022s-bad-debt`. The knowledge question was already answered
on 10-15 (`bad_debt_provisioning.md`, "When a GB supplier charged and wrote off 2022-era arrears"):
**the published step-up is a provision charge, not a write-off.** Centrica's charge rose 1.1% (2021)
to 2.1% (2022) and 2.7-2.9% (2023) of revenue, while write-offs stayed flat in share (GBP 58m, 93m,
113m). GB suppliers recognised 2022's arrears in 2022 and 2023 through the provision, and most of
that debt was still held, not written off, through 2025. The window was corrected to (2022, 2023)
on that basis. This section prints the table that was still owed.

**What each column counts.** *Arrears* is receivable aged 30 days or more, across every bucket
(live DD, live pay-on-receipt, final bill, no published row). *Stock* is `company_provision.by_date`,
meaning `default_belief.provision_stock` on Centrica's Note 17 rates, which is what the run publishes.
*Charge* is the year's movement in stock. The ledger records no write-offs in this run, so the
charge is the IFRS 9 charge as the `ifrs9_charge` basis grades it. *Revenue* and the *P&L line*
come from the validator's own `extract_series_from_run_output`. Source: the committed
`run_output_latest.json.gz`, producing commit 2248e3baf.

| year | receivable | arrears >=30d | of which >90d | stock | stock / arrears | charge | change in arrears | charge % revenue | P&L line (seed 2%) |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 3,217 | 466 | 0 | 96.96 | 20.8% | +96.96 | +466 | 0.097% | 1,316 |
| 2017 | 4,222 | 976 | 293 | 363.25 | 37.2% | +266.29 | +511 | 0.141% | 3,982 |
| 2018 | 5,034 | 1,716 | 599 | 680.49 | 39.7% | +317.24 | +739 | 0.162% | 4,126 |
| 2019 | 6,206 | 1,896 | 686 | 803.13 | 42.4% | +122.64 | +180 | 0.066% | 4,002 |
| 2020 | 4,537 | 1,656 | 846 | 837.10 | 50.6% | +33.97 | -240 | 0.020% | 3,758 |
| 2021 | 6,507 | 2,579 | 867 | 976.59 | 37.9% | +139.49 | +924 | 0.079% | 3,531 |
| **2022** | 16,905 | 5,337 | 1,058 | 1,603.95 | 30.1% | **+627.36** | **+2,758** | **0.180%** | 5,698 |
| 2023 | 13,962 | 5,905 | 1,978 | 2,089.66 | 35.4% | +485.71 | +568 | 0.101% | 11,342 |
| 2024 | 14,445 | 6,023 | 2,116 | 2,384.10 | 39.6% | +294.44 | +118 | 0.092% | 6,867 |
| 2025 | 10,444 | 5,606 | 2,228 | 2,360.07 | 42.1% | -24.03 | -417 | -0.015% | 4,717 |

**Ruling.**
- **The published provision does not lag.** Arrears build most in 2022 (+GBP 2,758, three times any
  other year), and the charge is largest in 2022 (+GBP 627). In 2023 arrears grow only +568, yet the
  charge is still +486, because the 2022 debt ages: the over-90-day balance nearly doubles, from 1,058
  to 1,978. That is the Centrica shape, with the step in 2022 and the peak carried into 2023. Coverage
  dips to 30.1% in 2022 because new arrears are young, which is the age-banded method working as
  designed and not a lag.
- **The learned provision does lag, and that is already filed.** E6's own roll-rate matrix trails the
  run's arrears by three quarters. It is filed as
  `WORKER_FINDING_THE_ROLL_RATE_PROVISION_TRAILS_THE_RUNS_ARREARS_BY_THREE_QUARTERS_2026-10-15.md`,
  pre-registered (lag 0 was predicted and refuted), held by a strict xfail in
  `tests/company/finance/test_the_provision_charges_expected_loss_as_arrears_build.py`, and ships
  off. No second filing is needed.
- **The window was the timing defect, and it is fixed.** `CRISIS_YEARS = (2022, 2023)`, cited to
  Centrica and Ofgem (10-15). No further window change is warranted.
- **So what keeps this finding BLOCKING is level, not timing.** The company's charge has the real
  shape, but at 0.10-0.18% of revenue it sits about a tenth of the way to the real 1-3% band. The P&L
  line sits inside the band only because of the seed 2% rate, and its 2023 peak is booking delay, not
  credit. Both are already recorded above and go back to the world's non-payment (the W2_4..
  affordability cluster).

**Corrected beside the claim:** E6's map row says "the crisis control is red because the age bands
lag 2022's arrears a year". The table above refutes that: the age-band stock charges most in 2022.
The comment is corrected in the same commit. This finding's header also cites "1.3% to 2.8%" as
recorded in `ASSUMPTIONS.md`. No 1.3% figure is recorded there. The 2.3-to-2.8% figure that is
recorded is Centrica's FY2025 movement, as corrected on 10-15. The crisis anchor is the 1.1% (2021)
to 2.1-2.9% (2022-23) series in `bad_debt_provisioning.md` §3.2.

## 2026-10-17: drawn again as BLOCKING; the cause's build waits for the publish, and its one GAP is researched

**Why nothing in the world moved this turn.** The level gap goes back to the world's non-payment.
Its fix (the budget decides how much of the bill is paid, month after month) is filed in
`WORKER_FINDING_THE_WORLDS_PAYMENT_DRAW_HAS_NO_PRICE_INPUT_..._2026-10-16.md` as the first world
change **after the 2026-10-19 publish**, with R1-R4 pre-registered. That is a world change, so it
is not started before the publish. The one thing left to do before it was its named GAP: which
deflator brings the 2026/27 essentials floor and income ladder to each run year.

**Researched**, in `docs/market_research/household_budget_w2_4.md`, section "The price level,
researched (2026-10-17)". Two results bear on this finding:
- **The floor already holds the energy bill.** JRF's £120/£205 a week includes £24/£33 of
  electricity and gas. A build that pays the bill out of income minus that floor counts energy
  twice. The build's floor is the basket without energy, deflated line by line on CPIH divisions:
  £300 a month single in 2016, £363 in 2022 and £425 at 2026/27.
- **The bottom of the ladder has a crisis of its own.** Benefits rise by the previous September's
  CPI, so April 2022's 3.1% put a benefit household's real non-energy purchasing power **6.5% under
  2021** in both 2022 and 2023, before any bill. That is the 2022-23 window this control grades.
  A single deflator on the ladder (AWE or CPIH) would hide it.

**Prediction for the build, filed now:** with the bottom deciles on the uprating path, the share of
households under water rises in 2022-23 by more than the bill alone gives (the 2026-10-16 probe:
+1.7 points under the EPG), and falls back by 2024. If the uprating path adds less than 0.5 points
at Q4 2022, the bottom deciles are mostly not benefit-led in the ladder's shape, and the HBAI
income-by-source cut (still a GAP) decides it.

**Status:** OPEN and BLOCKING, unchanged. The next move is the post-publish build, not this lane's
next tick.

## 2026-10-19: the post-publish build is graded, and it does not clear this finding

The cause's build landed as 718a631a1 and f8fdb99cc: the budget decides how much of the bill is
paid, behind `BUDGET_DECIDES_PAYMENT`, which ships False. The reader fix this finding asked to land
with it was already on origin (2026-10-14 evening, above), so nothing was owed there. The grade
is in the payment-draw finding, section "2026-10-19: R1-R4 graded on the paired run". It is one
seed, world-only. R2 and R4 hold. R1 (£1,200 at Q4 2023, predicted £200-400) and R3 (+4.6 points
at Q4 2022, refutation line +3) are refuted on the high side, because a household the budget puts
under water never leaves it.

**The 10-17 prediction (the uprating path adds at least 0.5 points at Q4 2022): cannot yet say.**
Separating it needs an arm with the uprating path off. The on arm's whole move over Q4 2021 to
Q4 2022 is only +0.8 points beyond the off arm's.

**The validator: not re-graded.** The capture is world-only and the switch ships off, so no
published run carries the mechanism. The switch stays off until the no-exit defect is fixed
(`the-under-water-household-has-no-exit-so-the-budget-switch-stays-off`).

**Status:** OPEN and BLOCKING. The cause's first layer is built and graded. What still blocks is
the exit from negative margin, then a switch-on run graded by this validator.
