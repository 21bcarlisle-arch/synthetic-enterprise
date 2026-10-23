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

## 2026-10-20: the budget switches pass their second seed and default on

The exit from negative margin was built (78a36a84c), the shortfall is now shared (15a497992), and
both are now graded on two dice seeds:
`docs/staging/records/SEAT_RESULT_THE_SHARED_SHORTFALL_HOLDS_ON_A_SECOND_DICE_SEED_2026-10-20.md`.
`BUDGET_DECIDES_PAYMENT` and `ENERGY_SHARES_THE_SHORTFALL` default True in their own commit. So the
next published run is the first to carry the mechanism, and the switch-on run this finding waits
for comes from the weekly publish. It is not built in this lane.

**Prediction for the validator, filed before that run exists.** The level stays far under the real
1-3% of revenue band. World-only, the shared arm's pounds behind per account behind at Q4 2023 are
£302, against Ofgem's £1,303. The crisis shows in pounds, not in the share of heads: on seed 2 the
off world's Q4 2022 heads share falls. I expect the validator's headline basis to step up in 2022-23
for the first time, but to stay below the band. If it does not step up at all, the company's charge
is not reading the world's arrears, and the cause is on the company side.

**Status:** OPEN and BLOCKING until a published run with the switches on is graded by
`validate_run_output`.

## 2026-10-21: the first switch-on run, graded UNPUBLISHED. The 10-20 prediction is refuted on the basis it named

The switch-on run this finding waits for already exists, but it is not published. The shared tree's
plain `docs/reports/run_output_latest.json` names `producing_commit` **ec7fd9942** (resolved
2026-10-20T21:34Z). That commit has 768f41ed1 as an ancestor, and at it both
`BUDGET_DECIDES_PAYMENT` and `ENERGY_SHARES_THE_SHORTFALL` are `True`. The committed gz is still
the earlier run (ad8afadc5, published as 8b6fea024 on 2026-10-19). `validate_run_output` on each,
read through `tools/run_output_store`:

| run | basis | crisis 2022-23 | pre-crisis 2016-19 | step-up | verdict |
|---|---|---|---|---|---|
| published ad8afadc5 | headline | 0.0391% | 0.0559% | x0.70 | FAIL floor + step |
| published ad8afadc5 | ifrs9_charge | 0.1564% | 0.1133% | **x1.38** | FAIL floor |
| **unpublished ec7fd9942** | headline | 0.0606% | 0.2026% | x0.30 | FAIL floor + step |
| **unpublished ec7fd9942** | pnl_accrual | 2.0435% | 1.9940% | x1.02 | FAIL step (the seed 2%) |
| **unpublished ec7fd9942** | ifrs9_charge | **0.4000%** | 0.2184% | **x1.83** | FAIL floor only |

The IFRS 9 charge by year on ec7fd9942, in GBP (published ad8afadc5 in brackets): 2021 262 (83),
**2022 1,825 (537)**, **2023 1,529 (788)**, 2024 **-380** (540). Revenue barely moves between the
two runs (2022: 343,923 against 348,215).

**The 10-20 prediction, graded.**
- "The level stays far under the real 1-3% band": **held.** 0.40% is still 2.5x under the 1% floor.
- "The headline basis steps up in 2022-23 for the first time": **refuted.** It falls, x0.30. The
  prediction's fallback ("if it does not step up, the company's charge is not reading the world's
  arrears") is refuted as well, by the IFRS 9 basis. **Corrected beside the claim:** the prediction
  was aimed at the wrong basis. Headline grades the world's behavioural write-offs. On 10-15 this
  finding had already recorded that real write-offs do not step up in share either (Centrica:
  GBP 58m, 93m and 113m in 2021-23 while revenue doubled), and that an XPASS there would itself be a
  fidelity question. The basis that reads the company's charge is `ifrs9_charge`, and it now steps
  up x1.83, close to Centrica's ~x2. Its crisis level is 2.6x the published run's.
- **I cannot yet say how much of that move is the budget switches.** 30 commits touch `simulation/`
  or `sim/` between ad8afadc5 and ec7fd9942, including the shortfall order (15a497992), the B7
  job-loss scar (b1d3860b8) and the half-hourly read (254b4686a). The one-variable version is the
  same commit with the two switches off. Prediction, filed before that arm exists: with both off,
  the IFRS 9 crisis share falls back under 0.20% and the step-up under x1.5.
- **New, and unexplained:** 2024's charge is negative (-GBP 380, so the stock released). It is
  consistent with the 10-20 exit from negative margin letting arrears clear. Not traced.

**The strict xfails all still hold** (every basis fails at least one condition), so HEAD stays green.
The `_TENTH_OF_REAL` reason now under-states the level. It becomes about two-fifths of the floor
once this run is published, and the reason should be re-worded in the commit that publishes it, not
before.

**Status:** OPEN and BLOCKING. The company's charge now reads the world's crisis in shape and in
step. What still blocks is the level: 0.40% against 1%. The next grade is the published copy of
this run, plus the switches-off arm for attribution.

## 2026-10-21 (later): the switches-off arm is launched, queued

Drawn again as BLOCKING, worker tick. The one-variable arm the 10-21 grade owes is set up and launched:
- **The arm.** A detached worktree, `/var/tmp/se-baddebt-off`, at **ec7fd9942**. Its only change is `BUDGET_DECIDES_PAYMENT = False` and `ENERGY_SHARES_THE_SHORTFALL = False` in `simulation/household_budget.py`. Nothing else names either constant outside that module.
- **The run.** `python3 -m tools.run_annual_report --save-json /var/tmp/se-baddebt-off-out/off.json`, as long job `baddebt-switches-off-ec7fd9942`, with a peak of 7,000 MB and about 120 min expected.
- **The queue.** At launch it was queued behind `head_green_census` (11.2 GB) and the sim-runner's 9ca972774 run (7.1 GB). The queue log is `/var/tmp/se-baddebt-off-out/launcher.log`.
- **The prediction** is the one filed above, before this arm existed: with both switches off, the IFRS 9 crisis share falls back under 0.20% and the step-up under x1.5.
- **Grading.** Run `validate_run_output` on `off.json` on all three bases, through `tools/run_output_store.load_run_output`. Then remove the worktree.

**Status:** OPEN and BLOCKING, unchanged. The next tick grades the arm once its artefact exists. Do not re-launch: ask `.launch_records.json` for the job first.

## 2026-10-21 (05:36Z): that launch died queued; relaunched behind the per-customer-switch arms

The launch above never ran. At 05:35Z there was no `baddebt` process, no `longjob-baddebt-*` unit and
no `.launch_records.json` row, and the worktree `/var/tmp/se-baddebt-off` had gone too: it was never
locked, so it was pruned. The launcher was still queued for memory, so it had not yet made its own
unit. It ran inside the tick's cgroup and died when the tick ended. Its last words are the QUEUED
line in `/var/tmp/se-baddebt-off-out/launcher.log`. The relaunch went in at **05:36Z**:
- the worktree was rebuilt at ec7fd9942 with the same two constants set to `False`, and is now
  `git worktree lock`ed;
- a driver unit, `relaunch-driver-baddebt-1021.service`, runs `/var/tmp/se-relaunch-1021/driver2.sh
  baddebt` in its own cgroup;
- it waits while `longjob-per-customer-switch-arms-8fbb641d8` is active, writing a QUEUED line to
  `/var/tmp/se-relaunch-1021/baddebt.log` every 5 min, then calls `launch_long_job` for
  `baddebt-switches-off-ec7fd9942` with the same command, peak and artefact as above, logging to
  `/var/tmp/se-baddebt-off-out/off.log`.

When the job's follow ends, the driver hands off the grade as the continuation
`grade-the-baddebt-switches-off-arm-ec7fd9942`. It is filed then, not now, because a continuation
lives only 6h and this job ends later than that. The prediction and the grading are unchanged. If the job is missing, ask the driver unit
before relaunching anything.

## 2026-10-21 (evening): the switches-off arm, graded. The prediction holds, and the switches are the move

The arm finished (`off.json`, stamped `producing_commit` ec7fd9942, `imports_off_commit` naming only
`simulation/household_budget.py`; that file's diff is the two constants set to `False`, nothing else).
`validate_run_output` on it, read through `tools/run_output_store.load_run_output`, beside the
switch-on run at the same commit:

| basis | on (ec7fd9942) crisis / step-up | **off (ec7fd9942)** crisis / step-up | published ad8afadc5 |
|---|---|---|---|
| headline | 0.0606% / x0.30 | **0.0313% / x0.56** | 0.0391% / x0.70 |
| pnl_accrual | 2.0435% / x1.02 | **2.0436% / x1.02** | — |
| ifrs9_charge | 0.4000% / x1.83 | **0.1433% / x1.49** | 0.1564% / x1.38 |

The IFRS 9 charge by year, off arm, in GBP (on arm in brackets): 2021 158 (262), 2022 **420** (1,825),
2023 **781** (1,529), 2024 **494** (-380). Revenue matches to within 0.1% (2022: 343,663 against 343,923).

**The prediction, graded.** "With both off, the IFRS 9 crisis share falls back under 0.20% and the
step-up under x1.5": **held on both legs.** 0.143% is under 0.20%. The step-up, x1.49, is under x1.5
by a hair, so that leg is not evidence of much on its own. The level leg is the one that carries weight.

**What this decides.**
- **The budget switches are what raised the crisis charge.** Off, the IFRS 9 crisis share is 0.143%,
  within 0.013 points of the published ad8afadc5 run (0.156%). So the 30 other `sim/`/`simulation/`
  commits between the two runs move it by about a twentieth of what the switches move it (0.143% →
  0.400%). One variable, one commit, same revenue.
- **2024's negative charge is the switches too.** Off, 2024 charges +GBP 494; on, it releases
  GBP 380. That fits the 10-20 exit from negative margin letting arrears clear, and it is now
  attributed to the switches. The mechanism inside them is still not traced.
- **pnl_accrual does not move at all** (2.0435% against 2.0436%). That basis does not read the
  world's arrears, which agrees with the 10-15 trace (it is the seed's 2% accrual).
- **Headline halves with the switches off** but it falls in the crisis either way, so the
  switches do not explain why behavioural write-offs fail to step up.

**What still blocks** is unchanged: the level. Even with the switches on, 0.40% is 2.5x under the
1% floor. The switches explain the shape and roughly 2.8x of the level, not the rest of the gap.

The worktree `/var/tmp/se-baddebt-off` was unlocked and removed after grading. The artefact is
still in `/var/tmp/se-baddebt-off-out/`.

**Status:** OPEN and BLOCKING, on the level alone. Attribution is done. The next grade is the
published copy of the switch-on run, with the `_TENTH_OF_REAL` reason re-worded in that commit.

## 2026-10-21 (night): the 2.5x shortfall is arrears volume, not provision rate. The next step is the world's (W2_38)

Read only. Both arms are at ec7fd9942, read through `tools/run_output_store.load_run_output`. The switch-on
run is the archived copy `docs/reports/run_output_ec7fd9942_20261020T213420Z.json`. The shared tree's
plain `run_output_latest.json` has moved on to 8e99f83cd since the 10-21 grade. The switches-off arm
is `/var/tmp/se-baddebt-off-out/off.json`. The charge is `_ifrs9_charge_series`'s own: the movement in
year-end stock, plus write-offs, less recoveries.

**Quarter-ends are not readable.** `company_provision.by_date` publishes year-ends only (ten dates,
plus a closing at 2025-06-07). So everything below is at 31 December. A quarterly split needs the run
to publish the stock quarterly, and no published run does.

### (ii) The rate: the company applies one matrix in every year

On every date in both arms the company provides at Centrica's **2025** Note 17 rates. Live DD is
0/0/0%. Pay on receipt (PoR) is 4.5/15.1/50.3% for <30/30-90/>90 days. Final bill is 31.6/57.6/87.8%.
The published rates moved (`bad_debt_provisioning.md` §3.1). PoR >90 was 52.6% in 2021, **62.9%** in
2022 and **63.4%** in 2023. DD >90 was **34.8%** in 2022, an outlier that the page says not to read
as a matrix rate. Final >90 was 79.5% and then 85.8%. So the rate leg is a real defect: the crisis
years are provided at the post-crisis rates.

**How much it matters.** I re-provided the company's own balances, band by band, at each year's
published rates (2019-2025 columns), with write-offs unchanged:

| on arm | stock, own rates | stock, published rates | charge, own | charge, published rates | % revenue, own | % revenue, published |
|---|---|---|---|---|---|---|
| 2021 | 646 | 677 | 262 | 352 | 0.15% | 0.20% |
| 2022 | 2,380 | 2,316 | 1,825 | 1,729 | 0.53% | 0.50% |
| 2023 | 3,869 | 4,276 | 1,529 | 1,999 | 0.31% | 0.40% |
| 2024 | 2,931 | 2,994 | -380 | -723 | -0.12% | -0.23% |

**On the 2022-23 window this moves the charge from 0.400% to 0.445% of revenue, a factor of 1.11.**
2022's DD rate cannot bite, because no live DD balance in either arm is ever 30 days old (see (i)).
**Upper bound:** Centrica's macroeconomic overlay was 7%, 22% and 21% of its closing provision in
2021, 2022 and 2023 (§3.2: 30/426, 125/567, 175/850). Whether that overlay already sits inside the
band rates is not disclosed, which is the page's own GAP. If I add the whole overlay on top of the
published rates anyway, the window comes to **0.544%, a factor of 1.36**. Even that is still under
the 1% floor.

### (i) The volume: the arrears are the right size and the wrong age and kind

The company's book against Centrica's, both as a share of revenue. Centrica's denominator is
derived as charge divided by its published charge-%-of-revenue (234/2.1%, 396/2.7%), so it is UK
energy-supply revenue against a UK and Ireland residential roll-forward. These are derived,
indicative figures.

| 31 Dec | gross receivable / revenue | provision stock / revenue | final-bill (closed) balance / revenue | PoR >90d / PoR balance | live DD aged >=30d |
|---|---|---|---|---|---|
| Centrica 2022 | 8.9% | **5.1%** | **1.8%** | ~60% (implied by its 41.7% PoR coverage) | GBP 66m >90d, 20% of DD gross |
| company on, 2022 | 8.8% | 0.69% | **0.01%** | **8.8%** | **0** |
| Centrica 2023 | 11.3% | **5.8%** | **1.9%** | ~75% (50.9% coverage) | 4.1% coverage, GBP not split |
| company on, 2023 | 4.5% | 0.78% | **0.11%** | **30.6%** | **0** |
| company off, 2022 / 2023 | 5.9% / 3.2% | 0.26% / 0.33% | 0.01% / 0.07% | 2.1% / 15.8% | 0 / 0 |

The ~60% and ~75% PoR >90 shares come from Centrica's PoR coverage against its own band rates, with the two younger bands taken at about 8% between them.
Centrica does not print the GBP by age band, so these are derived. GAP: neither our pages nor
Note 17 publish an age-banded GBP split.

**Reading.** The switch-on run puts the right *amount* of money in the receivable in 2022: 8.8%
of revenue against 8.9%. What it lacks is debt that **stays unpaid and leaves with the customer**.
- The closed-account balance is a hundredth to a twentieth of Centrica's share, and that is the
  bucket provided at 75-90%.
- Live PoR debt is young. Centrica's live PoR book is mostly over 90 days.
- No DD account ever carries a balance aged 30 days or more. Whether that is the world (a failed DD
  is always re-presented and paid) or the company (the method register re-files a failed-DD account
  as PoR) is **not traced**.

The provision stock runs about 7x under Centrica's per pound of revenue. Rate explains 1.0x of
that: published rates on our balances give 0.67% and 0.86% against 0.69% and 0.78%. **Volume
explains the rest.**

### The split

| gap measured to | shortfall | rate factor (published band rates, up to whole overlay) | volume factor (the rest) |
|---|---|---|---|
| the 1% floor | x2.50 | x1.11, at most x1.36 | **x2.25, at least x1.84** |
| Centrica's 2022-23 charge, 2.44% of revenue (derived: 630 / 25.8bn) | x6.10 | x1.11, at most x1.36 | **x5.5, at least x4.5** |

In log share, volume is at least 66% of the floor gap and at least 83% of the gap to Centrica. On
the central reading, with no overlay double-count, those are 89% and 94%. **The side is the world
(W2_38).**

E6's D1-fixed roll rates can only re-weight balances that exist. Even at Centrica's 2022 rates plus
the whole overlay, no matrix lifts 0.40% past 0.54%. The rate leg is still owed: the frozen 2025
matrix should be dated or learned. But it is the smaller leg, and it is E6's.

### Why 2024's charge is negative: the switch-on world pays the old debt off

On the switch-on run, 2024's stock falls GBP 938 and write-offs add GBP 558, giving a charge of
-GBP 380. The fall is almost all the **live PoR >90-day balance, which drops from 4,589 to 1,942
(-2,647; x50.3% = -1,331 of stock)**. The 30-90 day band barely moves (5,676 to 5,252), and the
final-bill balance rises only 577. So aged live debt is *paid*. It is not written off and it does not
leave with the customer. The mechanism is `simulation/household_budget.BudgetPaymentBook.settle_month`
at ec7fd9942. It pays unpaid bills **whole, oldest first**, out of any month's surplus, and it holds
part-payments toward the oldest bill. In 2024 three of its inputs turn favourable together:
- the bill falls, because the cap comes off its 2023 level;
- the benefit-path deciles' income factor rises 0.867 to 0.932 (+7.5%, `_BENEFIT_PATH_FACTOR`);
- AWE rises 0.874 to 0.920;
- meanwhile the floor rises only about 2-3% (basket 0.926 to 0.943, CPIH 0.903 to 0.933);
- the 0.41-a-year income re-draw (78a36a84c) lifts some households out of negative margin.

Any household back in surplus clears its oldest bills first, and that empties the >90 bucket first.

**The record went the other way.** Centrica's 2024 charge was still +GBP 245m (2.6%), and its stock
rose from 850 to 984. Ofgem's arrears kept rising to GBP 4.43bn by June 2025 (`ASSUMPTIONS.md` row
78). Aged debt (>12 months) is 52-65% of the stock, and PPM repayment plans average 6.6-7 years
(`ASSUMPTIONS.md`, the 2026-10-04 arrears-prevalence row). **Which of the three 2024 inputs carries
the release I cannot yet say.** The one-variable arms are `BENEFIT_PATH_DECILES = ()` and
`INCOME_MOVE_PER_YEAR = 0`, each alone at ec7fd9942. Prediction, filed before either exists: the
release is mostly the falling bill and the rising benefit path acting through oldest-first whole-bill
clearance. With the income re-draw at 0, 2024 still releases (charge < 0). It is the same defect as
the volume leg: real debt, once old, is not paid off out of a margin that has just turned positive.

### Next step (world side)

Filed as `WORKER_FINDING_THE_WORLDS_ARREARS_CLEAR_OLDEST_FIRST_OUT_OF_ANY_SURPLUS_SO_DEBT_NEVER_AGES_OR_LEAVES_WITH_THE_CUSTOMER_2026-10-21.md`
on W2_38. It grades the world's arrears **age**, not only their prevalence, against the sourced 52-65%
aged >12 months, and it asks why so little debt leaves with a closing account. This finding is the
supplier result it unblocks. The rate leg (a dated or learned matrix in place of the 2025 one) stays
E6's and is second in order: on these numbers it is worth x1.11 to x1.36 at most.

**Status:** OPEN and BLOCKING. The split names the world. Nothing in `simulation/` changes in this
section.

## 2026-10-21 (late): the world's step 1 is graded, and it moves the side

*Correction beside the "night" section's claim that "the side is the world (W2_38)".* The world's own
truth was read on two existing switch-on captures (the world finding, section "step 1 graded"). The world's
>91-day stock is not young. A year-old share of 73% of bills and 47% of pounds in Q4 2023, against Energy UK's
52%, is at or above the record. And £1.9k-3.9k of it sits on closed accounts, nearly all of it over a year
old. The company books about £34-540 as final-bill debt (derived), and no aged DD debt, against £450-2,200 of
DD-method debt over 91 days in the world. Live pay-on-receipt debt roughly agrees. **So most of the volume
leg is what the company books, not what the world holds.** The world-side repayment-plan change is withdrawn.
The next step is the trace of where a leaver's and a failed-DD account's balance goes between the world's
settlement and `company_provision`. The world finding's steps 2-3 now carry that, and so does E6.

**Status:** OPEN and BLOCKING. The side is now the company or the seam, not the world.

## 2026-10-21 (late evening): the trace. No pound is lost between the world and the company; the side is the world's leaver-debt FLOW and an ageing convention

*Correction beside the "late" section's "the side is now the company or the seam". The trace below refutes it.*

**Instrument.** `/var/tmp/leaver_trace/probe.py` runs `run_phase2b.main` (the shared tree's disk at
2026-10-21 18:44Z, HEAD ce0640dd0, both budget switches on, default dice) and keeps the `LivePaymentTriad`. At each 31 December it reads the
world's own `PeriodRecord`s, joined to the company ledger's bill amounts by `invoice_ref`, beside the company's
`fifo_unpaid_bills` on the same ledger. "Closed" uses the company's rule (no bill in 62 days) on both sides. One
book and one dice seed. Unpublished.

**Predictions, filed before the run.** The world finding's prediction for step 3 was "most closed-account debt
never appears in `company_provision`". Mine was that it appears and is written off at the 365-day convention, and
that the DD zero is the bucketing rule.

| 31 Dec | world live, all ages | company live, all ages | world live >91d (per bill) | company live >91d (FIFO) | world closed >91d | company closed held | company closed written off to date |
|---|---|---|---|---|---|---|---|
| 2018 | 6,637.46 | 6,637.43 | 806 | 25 | 2,098.63 | 1,009.73 | 1,088.94 |
| 2019 | 9,161.37 | 9,161.33 | 1,287 | 186 | 2,400.69 | 438.71 | 1,962.01 |
| 2020 | 6,385.39 | 6,385.33 | 1,656 | 233 | 2,926.94 | 239.13 | 2,677.07 |
| 2021 | 8,110.46 | 8,110.45 | 1,605 | 149 | 3,051.30 | 303.81 | 2,778.30 |
| 2022 | 28,374.08 | 28,374.07 | 3,094 | 605 | 3,151.17 | 74.92 | 3,107.06 |
| 2023 | 20,748.55 | 20,748.52 | 5,825 | 2,580 | 3,474.87 | 206.49 | 3,299.19 |

**What it says.**
1. **Live money all reaches the company.** World and company live receivables agree to a few pence at every year
   end. Nothing is lost at the seam.
2. **Closed-account debt all reaches the company.** World closed debt equals company held plus company written
   off, to the penny in 2018-19 and within 1% after that (recoveries on reopened accounts). The world finding's
   step-3 prediction is **refuted**. Mine **held**: the company holds the debt, then writes it off at 365 days.
   The "final-bill balance 0.01% / 0.11% of revenue" in the "night" section left the write-offs out. The money is
   in `written_off_to_date_gbp`, and so in the charge, but in the year it was written off.
3. **The DD zero is the bucketing rule.** `provision_stock` files a DD bill unpaid at 30 days or more under the
   pay-on-receipt row (`_live_rate`, `DIRECT_DEBIT_REPRESENTATION_WINDOW_DAYS = 30`). So "no live DD balance
   aged 30 days" is true by construction, and the world's DD-method arrears are inside the PoR >90 bucket. It is
   a labelling choice. No pound is missing.
4. **Live age differs by convention.** The world grader ages each bill on its own. The company's rolling ledger
   allocates every payment oldest first, so a household that misses one bill and then pays each new one carries
   the same pounds, aged as the newest bill. On the same pounds the company's >91-day stock is 10-44% of the
   world's per-bill reading. Which convention Energy UK's 52% and Centrica's bands use is not published, which is
   a **GAP**. Oldest-first is the rolling-balance practice the company models. So this is not a defect in either
   side, but the W2_38 age grade (world "older than the record") was read on the per-bill convention, and that
   needs saying beside it.

**Why there is no step-up.** New closed-account debt in the world, year on year: about +1,040 (2017), +1,056
(2018), +302 (2019), +526 (2020), +124 (2021), **+100 (2022)**, **+324 (2023)**. The count of indebted closed
accounts goes 12, 30, 41, 50, 53, **55, 58**. The world makes most of its leaver debt in 2017-18. The company
writes it off a year later, so its charge lands in 2018-2021, the **pre-crisis** window. That raises the
denominator of the validator's ratio. The crisis then adds almost no new leaver debt. So the absent step-up is:
(a) the world's **flow** of indebted leavers falls through the decade, when the record has it rising (Ofgem's
arrears rose from 2021); and (b) the 365-day write-off clock moves early leaver debt into the baseline years.
Before (a) is called a defect, it needs reading as possibly a book-composition effect: indebted founders leave
early, and the payers stay.

**What I cannot yet say.** Whether (a) is selection on a closed 400-founder book (one cast) or a world rule that
stops indebted households leaving in 2022-23. Real switching froze in 2022, which would lower the flow there
legitimately, but moves did not. **Prediction, filed before it runs:** by year, leavers' count and share with
debt over 91 days. The share with debt falls from 2017 to 2021, independently of the crisis, i.e. selection.
Leavers with debt per 100 accounts on supply in 2022-23 is below 2017-18's.

**Next step.** That leaver census, read off the same probe: the triad's records and the run's churn log. It is
one cheap run. Then, depending on the answer, a W2 world question (indebted leavers' flow against Ofgem's
arrears series) or a statement that one founder book cannot show the step-up. The E6 rate leg (a dated matrix)
stays second, as before.

**Status:** OPEN and BLOCKING. The side moves back to the world, now named precisely: the leaver-debt **flow**,
not the stock's age and not the seam.

## 2026-10-21 (night, later): the leaver census. Not selection: the leavers stop leaving, and the debt stays live, where it is never more than about three bills deep

**Instrument.** `/var/tmp/leaver_trace/dump.py` is the same run configuration as "the trace", re-run to dump every
world `PeriodRecord` with its billed amount (45,555 records). `census.py` reads it.
**Definitions, stated first:**
- A *leaver in Y* is an account whose last bill was issued in Y, at least 62 days before the run's end.
- *Debt left* is the world's unpaid pounds on its bills 62 days after that last bill, which is the day the
  company files it closed.
- *On supply in Y* means billed in Y.

| year | on supply | leavers | leaver rate | indebted leavers | per 100 on supply | share of leavers indebted | debt left (GBP) | live accounts with world debt >91d at 1 Jan |
|---|---|---|---|---|---|---|---|---|
| 2017 | 798 | 201 | 25.2% | 11 | 1.38 | 5.5% | 1,070 | 1.1% |
| 2018 | 666 | 162 | 24.3% | 23 | 3.45 | 14.2% | 1,115 | 4.1% |
| 2019 | 572 | 131 | 22.9% | 20 | 3.50 | 15.3% | 828 | 4.0% |
| 2020 | 513 | 113 | 22.0% | 9 | 1.75 | 8.0% | 360 | 4.7% |
| 2021 | 463 | 66 | 14.3% | 8 | 1.73 | 12.1% | 378 | 6.5% |
| 2022 | 430 | 27 | **6.3%** | 3 | 0.70 | 11.1% | 192 | 7.4% |
| 2023 | 458 | 30 | **6.6%** | 3 | 0.66 | 10.0% | 332 | **10.0%** |

**Graded against the prediction filed in "the trace":**
- "The share of leavers with debt falls from 2017 to 2021, i.e. selection." **REFUTED.** It runs 5-15% with no
  trend.
- "Indebted leavers per 100 in 2022-23 are below 2017-18." **HELD**, but not for the predicted reason. The
  *leaver rate* collapses from 22-25% to 6-7%.

The direction matches the record: switching froze in 2022, and an indebted customer can be refused a switch. The
size of the real collapse is an unfetched GAP (`ASSUMPTIONS.md`, the "post-2022 switching collapse" row). So the
crisis debt **stays on live accounts**. The share of live accounts holding world debt over 91 days rises from 4%
to 7.4% and then 10%. That is where a real supplier's crisis charge sat as well: Centrica's live PoR >90 band.

**And on live accounts the company reads it young, and rightly by its convention.** A FIFO reconstruction from the
dump reproduces the company's >91-day live figures exactly (186, 605 and 2,580 in 2019, 2022 and 2023). On that
reading, the live balance billed more than 105 days ago is **2.0%** of the live receivable in 2019, **2.1%** in
2022 and **12.4%** in 2023. Centrica's implied PoR >90 share is ~60% and ~75%. So, cash-wise, the world's live
debtors are almost never more than about three bills behind. They miss bills, and then pay the later ones (or the
budget clears the oldest), so the overhang never deepens. Real crisis debtors' balances deepened.

**Where this leaves the split.**
- The seam loses nothing ("the trace").
- The leaver-debt flow falls for a reason the record shares, in direction.
- What is left is the **depth** of live arrears: how far behind an indebted household gets before it pays again.
  That is a world question (W2_38), and a fidelity one, decided blind to company results.
- The comparator has to be a published *balance-age* or *debt-per-indebted-customer* series, read on the
  oldest-first convention. Ofgem's average arrears per indebted account, rising through 2022-25, is the candidate
  in `ASSUMPTIONS.md`'s arrears rows. The knowledge page comes first (K8).
- No world change in this section.

**Status:** OPEN and BLOCKING. The next step is the world's: grade the depth of live arrears (pounds per indebted
live account, and its oldest-first age) against the published series, before any build.

## 2026-10-21 (night, last): the depth graded. The world's debtors are about two bills deep in every year; Ofgem's are most of a year's bill, and deepening

**Instrument.** `/var/tmp/leaver_trace/depth.py` reads the same world dump as the leaver census (45,555
`PeriodRecord`s, switch-on, one book, one seed, unpublished). No new run.
**Definitions, stated first, on Ofgem's (`debt_and_collections.md` §2.1):**
- *Live credit account:* a bill issued in the 62 days to 31 Dec, and the latest bill's method is not prepayment.
- *In arrears:* holds a bill unpaid more than 91 days after its due date.
- *Balance:* all of that account's unpaid bills at 31 Dec. Ofgem's "average arrears" is the account's arrears balance.
- *Months:* that balance over the account's own trailing-12-month mean monthly bill.
- Ofgem counts per fuel account. Ours are supply-point accounts. So compare months and growth, not raw pounds.

**Prediction.** None was filed for this table. The nearest one on record is the leaver census's "never more than about
three bills deep" (read on the FIFO age, not the balance). It is graded below, not used as a pre-registration.

| 31 Dec | live credit | in arrears | share | mean balance £ | median £ | mean £ >91d | mean months | median months | Ofgem avg elec arrears £ | Ofgem elec accounts in arrears |
|---|---|---|---|---|---|---|---|---|---|---|
| 2016 | 648 | 8 | 1.2% | 56 | 25 | 21 | 2.0 | 1.0 | 570 | 508k |
| 2017 | 570 | 27 | 4.7% | 54 | 34 | 34 | 1.6 | 1.0 | 555 | 602k |
| 2018 | 472 | 24 | 5.1% | 59 | 39 | 34 | 1.4 | 0.9 | 589 | 648k |
| 2019 | 404 | 28 | 6.9% | 74 | 71 | 46 | 1.9 | 1.9 | 654 | 694k |
| 2020 | 353 | 30 | 8.5% | 89 | 65 | 55 | 2.2 | 1.9 | 774 | 702k |
| 2021 | 352 | 32 | 9.1% | 92 | 65 | 50 | 2.2 | 1.8 | 905 | 776k |
| 2022 | 361 | 47 | 13.0% | 198 | 136 | 66 | 2.4 | 1.7 | 1,028 | 779k |
| 2023 | 380 | 51 | 13.4% | 198 | 122 | 114 | 1.6 | 1.3 | 1,303 | 1,005k |

**Graded.**
1. **Depth is flat in bills and short.** The world's indebted account carries 1.4-2.4 months of its own bill in every
   year, crisis included. Ofgem's average electricity arrears are £654 against a typical **dual-fuel** bill of
   £1,179-1,254 in 2019. In 2023 they are £1,303 against £1,923-2,500 (`ofgem_cap_windows.md`). That is about half a
   dual-fuel year's bill per *single-fuel* account, so most of a year of that fuel's bill (derived; no per-fuel typical
   bill is on our pages, a small GAP). The depth gap is **roughly x4-6**. That is the same order as the provision volume
   factor to Centrica (x4.5-5.5, "night" section). This is the first measured quantity that is the size of the shortfall.
2. **Incidence runs the other way.** 13% of live credit accounts are in arrears in 2022-23. Ofgem's no-plan arrears are
   about 3.6-4.0% of all domestic accounts (Q1 2025 to Q2 2026), and fewer before. The record's crisis is *"intensity,
   not incidence"*: average arrears x3.1 and heads x2.3, 2016-25. The world's is mostly incidence: heads x11 from a
   small base, and pounds x3.5 in nominal terms only, because months stay flat. The "about three bills deep" claim held.
3. **The mechanism.** On the same dump, 556 of 648 runs of failed bills are a single bill. A failed bill is settled at
   a median of **61 days** after its due date (p90 123; 1,357 of 1,553 settle before run end). The world's debtors are
   *late payers who cure*. They are not non-payers whose balance accumulates. Every published debt series the commons
   holds says the stock accumulates: PPM plans run 6.6-7 years, 52-65% of arrears are over 12 months old, and average
   arrears rise every year.

**Where this leaves the split.** No pound is lost at the seam ("the trace"). The leaver flow falls for the record's own
reason ("leaver census"). The provision rate is worth at most x1.36 ("night"). **What is left is the world's cure
time for a missed bill**, which is the depth. It is a W2 fidelity question, graded here against Ofgem's average-arrears
series, blind to company results. The world-side item now carries the build question:
`WORKER_FINDING_THE_WORLDS_ARREARS_CLEAR_OLDEST_FIRST_..._2026-10-21.md`, section "depth graded". K8 comes first. The knowledge page
must say what published evidence constrains time-to-cure, or name the GAP. Ofgem publishes the stock's average and
count, never a cure-time distribution. Little's law on Ofgem's own flows (`debt_and_collections.md`, "average stay of
about one year") is the candidate anchor.

**Status:** OPEN and BLOCKING. The cause is now named as one world quantity, the cure time of a missed bill (median
61 days, against a published average stay of about a year). The next step is K8's knowledge page on that quantity,
then a W2_38 build, then a published run graded by `validate_run_output`.

## 2026-10-21 (23:20): say what "cure time" is before the build. Pre-registration, filed before the count

*A correction to the "depth graded" section's framing, beside it.* That section set the world's median cure of **61 days**
against the record's "average stay of about one year". Those two figures count different things:
- **61 days** is measured over **every failed bill**. Most of those are transient lateness that cures before 91 days.
  Ofgem never counts that population (`gb_domestic_bill_payment_failure_and_arrears_prevalence.md`, l. 44, 283).
- **About one to two years** is a stay in Ofgem's **pool**. It counts accounts more than 91 days in arrears, or on an
  arrangement. Little's law on the 2018 stock and flow gives 1.99 years
  (`gb_domestic_bill_payment_failure_and_arrears_prevalence.md` §(f)). That agrees with the DRS IA's "more than 22
  months" to recover and the entry-weighted 95 weeks.

So the comparable world quantity is the **stay in the >91-day pool**: from the day an account first holds a bill unpaid
more than 91 days past due until the day it holds none. Comparing every failed bill's cure with the pool's stay would set
a build target from a ratio whose two sides count different populations.

**Instrument.** `/var/tmp/leaver_trace/stay.py`. It reads the same dump (switch-on, one book, one seed, unpublished),
with the same `unpaid` rule as `depth.py` and evaluated daily. A spell is closed when the account holds no bill >91 days
unpaid. Spells still open at the run's end, or at the account's last bill + 62 days, are censored. Two readings:
(a) Little's law, the mean pool over 2017-2023 divided by entries a year; (b) the Kaplan-Meier median stay.

**Prediction, filed before the script exists:**
1. The world's Little's-law stay in the >91-day pool is **under 0.5 years** in 2017-2023, i.e. at least **x4 shorter**
   than the record's 1.99 years.
2. The KM median spell is **under 90 days**.
3. The crisis years (spells entering 2022-23) are **not longer** than 2017-19's by more than 1.5x. The record's own
   intensity rose, and recovery of debt over 12 months old fell from 31% to 9% (Energy UK Fig. 5).

If (1) holds, the build target is the pool stay, graded on this instrument against 1.99 years. It is not the per-bill
cure.

### Graded (23:35): the stay is about x2-3 short, not x10. What is short is accumulation: 81% of spells hold one bill

`stay.py` and `accum.py` (same dump; 333 spells after the close stop: 243 cured, 39 closed, 51 censored):

| entry window | spells | KM median stay (days) | p75 | p90 | share >= 1 year | Little's law (years) |
|---|---|---|---|---|---|---|
| 2016-19 | 173 | 28 | 293 | 746 | 24% | 0.48 (2017-19) |
| 2020-21 | 66 | 28 | 605 | 1,067 | 29% | - |
| 2022-23 | 94 (30 censored) | 30 | 214 | 459 | 17% (censored short) | 0.91 |

At each 31 December, most of the world's pool is spells already **more than a year old**: 12 of 24 (2018), 21 of 32
(2021) and 25 of 47 (2022).

**Against the pre-registration:**
1. Little's-law stay under 0.5 years over 2017-23: **REFUTED.** It is 0.70 years. It was 0.48 in 2017-19 and is 0.91
   in 2022-23, against the record's 1.99. The pool grew over the window, so Little's law here reads high.
2. KM median under 90 days: **HELD.** It is 28-30 days.
3. Crisis spells not more than 1.5x longer: **HELD on the median** (30 against 28). On Little's law it is 1.9x. That
   ratio is carried by the stock of pre-crisis long spells, and 30 of the 94 crisis entries are censored.

**What the prediction did not name.** The pool is **bimodal**. Most spells cure in a month. A quarter persist past a
year, so the world does have the persistence population. What it lacks is accumulation. Bills crossing 91 days, per
spell: **mean 1.54 and median 1.** 81% of spells hold a single bill. So do 67% of spells lasting a year or more. A
world household in a long spell has **one old bill parked while it pays every later bill.** That explains why the
depth is about two months of bill however long the stay runs ("depth graded").

It is also partly the per-bill convention. A rolling balance allocates oldest-first, which is what the company models.
On that allocation the same household is one bill behind, aged as the newest bill, and never in the >91-day pool.
That accounts for the 10-44% FIFO-to-per-bill ratio in "the trace".

**So the build question changes from cure time to accumulation.** Once a household is in the pool, does it go on
missing bills? The record says yes: the average arrears are about half a dual-fuel year's bill per single-fuel account,
which is most of a year of that fuel, and that average rose every year 2016-25. The world says no. The knowledge
section is `debt_and_collections.md` §2.5a (this commit). What stops a world household going on missing bills is
**not traced**. The candidates are a budget margin that rarely stays negative for several months, and savings drawn
down to cover it. Tracing that is the next step. It is a world-side read, decided blind to company results, and the
grade is the depth column against Ofgem's average arrears.

**Status:** OPEN and BLOCKING.

## 2026-10-21 (late): which world path makes the pool. The budget's debt never passes a year; the per-bill draw's does

The table is in the world finding, section "the year-plus pool is the per-bill draw". It comes from records only, on
the same dump. Bills the **budget** fails (882, on 79 accounts) cure in a median 61 days, and **none** lasts more than
365. This is where the 61-day figure in "depth graded" comes from. Every bill unpaid for more than a year that sits
beside on-time later payments (99 of 101) comes from the **per-bill** draw: `later_settlement_date`'s 22-month lump
or never-repaid. It does not come from a household without money.

So the world has no household whose shortfall persists. The x4-6 depth gap is a **margin-distribution** question: does
the world draw any credit household whose margin stays below its energy bill for a year? It is no longer a
cure-time question. It is world-side, decided blind to company results, and graded on the depth column.

**Status:** OPEN and BLOCKING.

## 2026-10-21 (23:25): the depth is the shortfall rule's fixed point, about 1.7 bills. One design choice, already labelled GAP

`ENERGY_SHARES_THE_SHORTFALL` shares the money left after housing between the core basket and the whole arrears
**stock**, pro rata. Energy's share therefore grows as the debt grows, and the debt stops at `C/(A−B)` bills. Over the
256 credit account-years whose margin is below their bill (7-13% a year), that fixed point is a median of **1.67 bills**
(p90 3.49). It was predicted at 1-3 bills, and the prediction held. That is the depth table's 1.4-2.4 months. The
world does draw sustained deficits. Its rule caps how deep they go. The table and the build candidate (share on the
month's demand, not the stock; K8 amendment of `household_budget_w2_4.md` first; one variable; graded on the depth
column) are in the world finding.

**Status:** OPEN and BLOCKING. The cause is now a single named world rule.

## 2026-10-22: the demand reading is built behind a switch, and its paired world-only arms are running

K8 first: `household_budget_w2_4.md`, "2026-10-22: stock or demand". At real inputs, on the same 256
deficit account-years, the demand reading has no cap. The stock grows a median **0.34 bills a month**
(about 4 a year, p90 7.6), against the stock reading's fixed point of 1.67 bills. One correction to
the build candidate above: the literal swap (`owed_total` → this month's bill) would make a
household that can meet this month's basket and bill still go without food. The built form is
`basket = min(C, C·A/(C+B))`, with the rest to energy. A mutation pins that difference.
`THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND`, default False. Pre-registration:
`docs/staging/records/SEAT_PREREG_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_2026-10-22.md`.
Arms: `longjob-shortfall-stock-arm` and `longjob-shortfall-demand-arm`, about 45 minutes each.

**Status:** OPEN and BLOCKING. The next tick grades the two arms with `depth.py` against D1-D5. Do not
re-launch: ask `.launch_records.json` first.

## 2026-10-22 (00:55 BST): seed 1 graded. The stock reading was what held the depth down

All five bands hold (result record `SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_1_2026-10-22.md`).
Depth rises from 1.4-2.4 to 3.3-6.8 months. £ at Q4 2023 rises from £198 to £580 (record £1,303),
with no overshoot. That confirms the named cause on one seed. It does not clear this finding. The
pounds stay about 2.2x short, the median is unchanged, and depth falls after 2019 where the record's
rises. Seed 2 is queued (`longjob-shortfall-{stock,demand}-arm-s2`).

**Status:** OPEN and BLOCKING. Next: grade seed 2 against D1-D5. If it holds, default the switch on in
its own commit, beside both result records, then re-grade this finding's validator on the next
published run.

## 2026-10-22 (early): seed 2 held, and the switch is on by default

Seed 2 holds all five bands (`SEAT_RESULT_THE_SHORTFALL_SHARED_ON_THE_MONTHS_DEMAND_SEED_2_2026-10-22.md`).
Depth runs 2.8-6.0 months against 1.6-2.6, and £ at Q4 2023 is £710 against £250. The 2019-2020 fall
in depth repeats, so it belongs to the budget population, not the dice.
`THE_SHORTFALL_IS_SHARED_ON_THE_MONTHS_DEMAND` now defaults on, in its own commit. In the triad, it moves
only the ageing gap (0.354 to 0.240).

The flip also showed something the pre-registration did not name, in a unit control's partition. On the demand
reading, a household whose margin is below zero never clears a whole bill. The money it holds toward
the bill is shared with the basket again each month, so it levels off at `(m+C)·B/C`, below one bill
when `m < 0`. It pays nothing while it stays under water, where a real household part-pays. The depth
grade cannot see this, because it counts pounds owed and not payments made. It is a candidate for the
"part payments" question, and it is not changed here (one variable).

**Status:** OPEN and BLOCKING. Next: re-grade this finding's validator on the first published run with
the switch on. Two things stay open: pounds about 2x short of Ofgem, and depth falling after 2019.

## 2026-10-22 (02:30 BST): the zero-payment population is counted, and the fix is built behind a switch

**Counted (seed 2, demand arm):**
- **26 of 257** deficit credit account-years pay nothing in the whole year, and all 26 have `m < 0`.
- **22** accounts go 12 months or more with no payment while behind, and **5** go 24 months or more.
- The stock arm has none.

Replaying the budget rule alone reproduces them (28 and 24), so the rule is the cause. The build
also differs from the demand section's own arithmetic. The page printed growth of `1 − A/(C+B)` bills
a month. The code puts the held money back into the shared pot.

**Against the record:**
- The DRS working paper has about 90% of its phase-1 customers paying something towards their usage.
- The demand arm's accounts in arrears paid anything in the last 3 months at only **25-57%** before
  2022, and at 60% at 2023.
- Most of the pre-crisis pool, and part of the depth the demand reading gained, comes from households
  paying nothing.

The K8 page is `household_budget_w2_4.md`, "2026-10-22: held money is a part payment". The switch is
`HELD_MONEY_IS_A_PART_PAYMENT`, default off. The replay predicts unpaid bills at 31 December roughly
halve, so **pounds are expected to move further from Ofgem, not closer**.
Pre-registration: `docs/staging/records/SEAT_PREREG_HELD_MONEY_IS_A_PART_PAYMENT_2026-10-22.md`.
Arms: `longjob-held-{off,on}-arm`, about 50 minutes each.

**Status:** OPEN and BLOCKING. Next: grade both arms against H1-H5. Do not re-launch: ask
`.launch_records.json` first.

## 2026-10-22 (morning): the held-money arms were graded and the switch is on. Prediction for the 10-26 publish, filed first

**Correction to the status above.** The H1-H5 grade it asks for is done. Both seeds held, and
`HELD_MONEY_IS_A_PART_PAYMENT` defaults on in 6b81d3b25a (record
`SEAT_RESULT_HELD_MONEY_IS_A_PART_PAYMENT_SEED_2_2026-10-22.md`). So the world now carries three
changes that no company run has seen: the budget switches, the demand reading and part payments.
The arm outputs are world-only traces (`records/events`), not run outputs, so `validate_run_output`
cannot read them. The first run that can be graded is the weekly publish, which opens
2026-10-26 04:00 GMT (`.publish_gate_state.json`). It is not launched here: the publish produces it
anyway, four days later, at no cost.

**What the pools say, seed 2, accounts in arrears × mean £ at 31 Dec.** The stock column of the
demand record stands in for ec7fd9942's world. The held-on counts are the demand counts scaled by
the share ratio.

| | stock (≈ ec7fd9942) | held-on (HEAD) | ratio |
|---|---|---|---|
| pre-crisis pool, 2016-19 summed | ~£6,400 | ~£17,000 | ~x2.7 |
| crisis pool, 2022 + 2023 summed | ~£18,400 | ~£32,900 | ~x1.8 |

**Prediction (IFRS 9 charge basis, read through `run_output_store.load_run_output`):**
1. **Level: still FAIL.** The crisis share rises from 0.40% (ec7fd9942) to **0.50-0.80%** of revenue.
   It stays under the 1.0% floor. *Refuted if ≥ 1.0%.*
2. **Step-up: falls.** From x1.83 to **x1.1-1.5**. The new mechanisms deepen pre-crisis arrears more
   than crisis arrears. *Refuted if it rises above x1.83.* Below x1.2 it would fail the second
   leg for the first time, and that would be the expected direction, not a regression.
3. **2024 stays negative or near zero.** Part payments let the old debt clear, as the switches did.

Caveats, said now: the pools are one dice seed, the publish runs default dice, and a provision
charge is a flow, not a stock. So the ranges are wide on purpose. If (2) is refuted upward, the
charge is not tracking the arrears stock by year, and the next question is the matrix's
ageing buckets, not the world.

**Status:** OPEN and BLOCKING. Next: grade this prediction on the 2026-10-26 published run. Do not
launch a full run for it before then.

## 2026-10-22 (11:00 BST): a HEAD run is launched beside seed 2, and the run already in the shared tree moves the wrong way

**Correction to the status above** ("do not launch a full run for it before then"). The delivery
seat overruled it: one full-window run at HEAD now answers this grade, D48's held-bill prereg and
the post-departure gas count, and it runs beside `pcs-arms-s14-seed2` rather than after it.
- **The run.** Long job `head-crisis-989ce4f1c2`: `python3 -m tools.run_annual_report --save-json
  /var/tmp/se-head-crisis-out/run_output.json`, from the locked worktree
  `/var/tmp/se-head-crisis-989ce4f` at origin **989ce4f1c2**. That commit carries the budget switches,
  the demand reading (5c0eeeb48), part payments (6b81d3b25), the post-departure gas fix (2b81e1466)
  and the gas-PPM read instruction (c6c09641e). Peak 7,100 MB, about 150 min. At 09:52Z it was
  queued by admission behind a landing's commit gate, in its own unit, so it outlives the tick.
- **The grader** is `/var/tmp/se-head-crisis-out/grade.py`. It runs the three live bases of
  `validate_run_output`, recomputes `held_bills`, and counts gas billed on or after each household's
  departure. It was checked against the run below first.
- **It is not an attribution run.** It changes three world mechanisms and about 20 other commits
  against ec7fd9942 at once. Whatever it shows, the grade says what moved and not why.

**Graded meanwhile, UNPUBLISHED: the shared tree's plain run, `producing_commit` 76a29bd92.** That
run carries the budget switches (it descends from ec7fd9942) but not the demand reading or part
payments. So it is ec7fd9942's world plus 14 commits to the world and the company, read through
`run_output_store`:

| run | basis | crisis 2022-23 | pre-crisis 2016-19 | step-up | verdict |
|---|---|---|---|---|---|
| ec7fd9942 (10-21 grade) | ifrs9_charge | 0.4000% | 0.2184% | x1.83 | FAIL floor only |
| **76a29bd92** | headline | 0.0678% | 0.2363% | x0.29 | FAIL floor + step |
| **76a29bd92** | pnl_accrual | 2.0487% | 2.0038% | x1.02 | FAIL step |
| **76a29bd92** | ifrs9_charge | **0.2263%** | **0.2898%** | **x0.78** | FAIL floor + step |

The IFRS 9 charge by year on 76a29bd92, GBP: 2016 245, 2017 971, 2018 1,051, 2019 558, 2020 528,
2021 195, **2022 1,282, 2023 1,012**, 2024 -285. Revenue: 2022 421,868, 2023 591,570.

**What this says.** The x1.83 step-up of 10-21 did not survive the next 14 commits, before any of
the three new mechanisms. The crisis pounds fell (2022 1,825 to 1,282) while revenue rose (2022
343,923 to 421,868), and 2017-18 now charge about GBP 1,000 a year. Those are the years the book
fills. **I cannot yet say which commit moved it.** Two candidates lead on the evidence:
8927e9345 made the founders 400 households (a different book, so a different fill curve in
2016-18), and cda47a346 moved the E6 provision on early-warning signals before a miss. The order
effect on stayers from 2b81e1466 is not in this run. The one-variable test is ec7fd9942 against
8927e9345 with nothing else changed. It is not launched here. The HEAD run comes first, because if
its step-up is back over x1.2 the question changes.

**137cdb443's prediction is unchanged, and so is its base.** It was written against ec7fd9942, and
76a29bd92 now says that base was not stable. So the HEAD grade will read the prediction against
both bases: 0.50-0.80% and x1.1-1.5 against ec7fd9942's world, and the direction of move against
76a29bd92's.

**Status:** OPEN and BLOCKING. Next: grade `head-crisis-989ce4f1c2` when its artefact exists. Ask
`.launch_records.json` for the job before relaunching anything.

## 2026-10-22 (12:20 BST): the HEAD run, graded UNPUBLISHED. The level is in the predicted band; the step-up is not

`head-crisis-989ce4f1c2` ran 10:13-11:08Z (55 min, not 150), Result=success, exit 0. The artefact is
`/var/tmp/se-head-crisis-out/run_output.json`, with `producing_commit` **989ce4f1c2**. It **carries**
the post-departure gas fix 2b81e1466 and the gas-PPM read instruction c6c09641e (both are ancestors).
Seed 2 had ended before this run was admitted, so in the end the two did not run side by side. The
live legs of `test_crisis_bad_debt_validator.py` (all three bases: `validate_run_output` read
through `run_output_store`):

| run | basis | crisis 2022-23 | pre-crisis 2016-19 | step-up | verdict |
|---|---|---|---|---|---|
| ec7fd9942 | ifrs9_charge | 0.4000% | 0.2184% | x1.83 | FAIL floor only |
| 76a29bd92 | ifrs9_charge | 0.2263% | 0.2898% | x0.78 | FAIL floor + step |
| **989ce4f1c2** | headline | 0.0680% | 0.6248% | x0.11 | FAIL floor + step |
| **989ce4f1c2** | pnl_accrual | 2.0490% | 2.0034% | x1.02 | FAIL step |
| **989ce4f1c2** | ifrs9_charge | **0.6995%** | **0.7255%** | **x0.96** | FAIL floor (by 0.30 pt) + step (by 0.24) |

IFRS 9 charge by year, GBP (76a29bd92 in brackets): 2016 506 (245), 2017 **2,054** (971), 2018
**2,527** (1,051), 2019 **1,970** (558), 2020 732 (528), 2021 279 (195), 2022 1,297 (1,282), 2023
**5,784** (1,012), 2024 -1,678 (-285). Revenue is within 0.3% of 76a29bd92 in every year.

**137cdb443's prediction, graded.**
1. **Level 0.50-0.80%, under the 1% floor: HELD.** 0.6995%.
2. **Step-up x1.1-1.5: REFUTED, low side.** x0.96. The prediction's reasoning was right in direction
   (the new mechanisms deepen pre-crisis arrears more than crisis arrears) and wrong in size. The
   pre-crisis share went from 0.22% to 0.73%, x3.3, against the ~x2.7 the pools implied. The crisis
   share went from 0.40% to 0.70%, x1.75, close to the ~x1.8 implied. The miss is the pre-crisis
   side, and 2017-19 now charge GBP 2.0-2.5k a year. As said there, below x1.2 the second leg fails,
   and that is the expected direction, not a regression.
3. **2024 negative: HELD.** -GBP 1,678. The stock releases as the crisis debt clears.

**What the grade shows that the prediction did not ask.** The crisis charge is almost all 2023:
GBP 5,784 (0.98% of revenue) against 2022's 1,297 (0.31%). 2023 alone clears x1.2 on the pre-crisis
share (x1.35), and 2022 is under it. The real charge was 2.1% in 2022 and 2.7% in 2023 (Centrica), so
the real step came in 2022. Here it comes a year late. That is the same lag the P&L basis showed on
10-14. So two things now hold the leg, and they point at different fixes. (i) The 2017-19 charge is
high, and it is not credit: the book fills in those years, and the new world mechanisms build their
deepest pre-crisis arrears there. (ii) The 2022 charge stays flat although the price rise starts
then. Each could be the world, or the matrix's ageing (a debt reaches the high-loss buckets a year
after it forms). **I cannot yet say which.** The 10-22 caveat names the next question if (2) failed
upward. It failed downward, so the question is the pre-crisis level, and it should be read against
the world's pre-crisis arrears depth before any matrix change.

**Not an attribution run.** Against 76a29bd92 it changes the demand reading, part payments, the
post-departure gas fix and a handful of company commits at once. It says what moved, not why. The
76a29bd92 drop against ec7fd9942 (above) is still unattributed.

**Post-departure gas, full window** (households departed = churned `customer_events` plus
`svt_departures`, 354 in both runs; bills whose period starts on or after the household's departure):

| run | households | gas bills | kWh | GBP |
|---|---|---|---|---|
| 76a29bd92 (before 2b81e1466) | 20 | 147 | 128,550 | 4,715.70 |
| **989ce4f1c2** | **0** | **0** | **0** | **0.00** |

No gas bill straddles a departure on the HEAD run. Gas bills fell by 204 (24,123 to 23,919), and
electricity bills are unchanged at 29,191. 147 of the 204 are the post-departure bills. The other 57
are not traced. They are most likely the term splits that 2b81e1466 makes, but that is not measured.

**The strict xfails still hold on this run** (every basis fails at least one condition), so the
suite stays green when it is published. `_TENTH_OF_REAL` will under-state the level by then. As
already recorded, it is re-worded in the commit that publishes the run.

**Status:** OPEN and BLOCKING. The level is about 70% of the floor and the step-up is about 0.8 of
the requirement. Next: what makes the company's 2017-19 charge so high and its 2022 charge so flat,
read against the world's arrears by year on this run, before any change to the matrix.

## 2026-10-23: why 2016-19 is high and 2022 is flat. The matrix recognises loss in the year the debt forms; the world forms less 2022 debt per pound billed than 2017-19

Read-only, on the same HEAD run (`/var/tmp/se-head-crisis-out/run_output.json`, 989ce4f1c2,
unpublished). Instrument: `/var/tmp/crisis_age_probe/probe.py`, one process. No matrix or world
value was changed.

**What each series counts.**
- *World arrears* are counted per bill, each bill on its own, from the run's issued bills and the
  world's own payment truth (`per_customer_behavioral[*].world_payment_truth`: each month's outcome,
  part payments, crossed settlements and paid plan instalments). A bill is unpaid until the truth
  says it was paid. *Arrears* are bills unpaid for 30 days or more at 31 December. *New arrears
  formed in Y* are the bills issued in Y that the world records as failed.
- *Company debt by age* is `company_provision.by_date` as published: the company's own
  oldest-first (FIFO) ledger, across every footing.
- *The IFRS 9 charge* is the validator's own definition: the movement in year-end stock, plus
  write-offs, less recoveries. To split it, the probe rebuilds the company's book from the same
  bills and truth: per account, total unpaid, allocated to the newest bills (oldest first, as the
  company does), closed after 62 days unbilled, written off 365 days after the last bill, and rated
  on the matrix rows the company imports (`value_based_renewal`). Each bill's recognised loss at a
  year end is its provision, or its whole balance once written off. The *new-debt charge* is the
  loss recognised on bills issued that year. *Ageing* is the movement on bills issued earlier.

**The rebuild reproduces the published book closely enough to read, but not to the penny.**
Receivable is within 2-14% of the published figure in every year, write-offs within 6%, and the
charge within 10% except in 2022 (rebuild 746, published 1,297) and 2023 (5,103 against 5,784).
It pays a direct debit bill on its due date rather than modelling the company's level collections,
and it ignores back-billing write-offs and restatements. The gaps in 2022 and 2023 run in one
direction, so the rebuild understates the 2022 level and does not move its shape.

**A. The world, by year (31 Dec)**

| year | arrears >=30d GBP | households | of which >1y GBP | failed bills formed GBP | failed share of billed | households with a failed bill | households first failing |
|---|---|---|---|---|---|---|---|
| 2016 | 2,471 | 35 | 0 | 5,880 | 3.74% | 55 | 55 |
| 2017 | 6,462 | 71 | 1,053 | 10,145 | 3.39% | 85 | 66 |
| 2018 | 9,043 | 73 | 3,427 | 9,328 | 3.16% | 72 | 42 |
| 2019 | 11,928 | 82 | 6,041 | 9,046 | 3.33% | 69 | 34 |
| 2020 | 10,795 | 80 | 7,843 | 3,649 | 1.61% | 50 | 20 |
| 2021 | 11,681 | 86 | 8,446 | 3,905 | 1.70% | 53 | 21 |
| **2022** | 16,811 | 95 | 8,582 | 12,726 | **2.87%** | 49 | 14 |
| **2023** | 28,029 | 109 | 10,139 | 35,816 | **5.77%** | 58 | 16 |
| 2024 | 23,132 | 113 | 14,678 | 12,428 | 3.21% | 47 | 9 |

By month, the world's failed share is 1.3-3.4% through September 2022, then 2.6%, 3.3% and 4.0% in
October to December. It peaks at 6.7% in January 2023 and stays between 4.8% and 6.8% through all
of 2023. The pounds peak with the winter bills: January 2023 alone fails GBP 7,483 of 111,946 billed.

**B. The company's debt by age (published, 31 Dec, GBP)**

| year | <30d | 30-90d | >90d live | final bill held | written off to date | provision |
|---|---|---|---|---|---|---|
| 2016 | 4,589 | 1,338 | 464 | 4 | 0 | 506 |
| 2017 | 5,107 | 1,567 | 1,642 | 1,586 | 39 | 2,521 |
| 2018 | 5,264 | 1,861 | 1,980 | 2,368 | 1,671 | 3,417 |
| 2019 | 7,123 | 2,213 | 3,146 | 1,326 | 4,011 | 3,169 |
| 2020 | 4,544 | 1,671 | 662 | 358 | 6,996 | 975 |
| 2021 | 5,687 | 2,424 | 748 | 281 | 7,288 | 1,099 |
| 2022 | 21,266 | 6,807 | 1,202 | 75 | 7,609 | 2,091 |
| 2023 | 12,911 | 7,385 | 12,128 | 206 | 7,801 | 7,683 |
| 2024 | 12,643 | 5,399 | 8,142 | 773 | 8,008 | 5,798 |

**C. The IFRS 9 charge, split, and the one-variable ageing shift (GBP)**

The shift adds 365 days to every age the matrix is asked for, so each bill is rated as a year
older. Nothing else changes: not the write-off clock, not the closed rule, not the ledger. Two
scopes are printed. *Arrears only* shifts bills unpaid 30 days or more. *All unpaid* also shifts
bills still in their normal collection window.

| year | published | rebuild | new debt | ageing of earlier bills | % revenue | +1y, arrears only | +1y, all unpaid |
|---|---|---|---|---|---|---|---|
| 2016 | 506 | 504 | 504 | 0 | 0.34% | 935 | 3,250 |
| 2017 | 2,054 | 1,893 | 1,889 | +4 | 0.67% | 1,904 | 2,901 |
| 2018 | 2,527 | 2,389 | 2,500 | -111 | 0.85% | 2,433 | 2,242 |
| 2019 | 1,970 | 1,976 | 2,142 | -167 | 0.77% | 2,111 | 2,588 |
| 2020 | 732 | 763 | 801 | -38 | 0.35% | 654 | -435 |
| 2021 | 279 | 325 | 981 | -656 | 0.15% | 446 | 1,053 |
| **2022** | 1,297 | 746 | 1,430 | -683 | 0.18% | 1,821 | 8,343 |
| **2023** | 5,784 | 5,103 | 6,361 | -1,258 | 0.86% | 5,608 | 2,283 |
| 2024 | -1,678 | -1,657 | 2,990 | -4,646 | -0.45% | -2,276 | -2,843 |

The validator's ratio (2022-23 against 2016-19, as a share of revenue):

| reading | crisis | pre-crisis | step-up | 2022 alone |
|---|---|---|---|---|
| published | 0.700% | 0.726% | x0.96 | 0.31% |
| rebuild | 0.578% | 0.695% | x0.83 | 0.18% |
| +1y, arrears only | 0.734% | 0.759% | **x0.97** | 0.43% |
| +1y, all unpaid | 1.050% | 1.129% | x0.93 | 1.98% |

(The rebuild's 2025 row reads a 31 December the run never reached, since it ends on 2025-06-07, so it
is left out.)

**What the numbers say.**
1. **The matrix does not recognise loss a year late.** In every year almost all of the charge
   is on bills issued that year, and the ageing of earlier debt is negative: it releases as debt
   is paid or written off. A one-year shift on arrears leaves the step-up at x0.97 (from x0.83 on
   the same rebuild) and lifts 2022 only to 0.43%, still under the pre-crisis 0.76%. The
   all-unpaid shift does lift 2022 to 1.98%, but only by provisioning December 2022's
   GBP 21k of bills still inside their collection window at 50%. That charges the price rise, not
   debt, and its 2023 then falls to 0.39%. It is not a reading of credit, and it fails the step too.
2. **The 2022 charge is flat because the world's 2022 non-payment is flat.** The world fails 2.87%
   of 2022's billed pounds. That is lower than in any year from 2016 to 2019 (3.2-3.7%), and only
   the 2020-21 trough (1.6-1.7%) is lower. Its crisis response begins in October 2022 and lands in
   the winter bills of January to March 2023, at 5.77% for the year. So the charge lands in 2023
   because the world's failed pounds do.
3. **The 2016-19 charge is high because the world's pre-crisis non-payment is high,** at 3.2-3.7%
   of billed pounds with 18-20% of accounts failing a bill in a year. It is not the book filling:
   the rate is per pound billed, not a volume. Selection is part of it, since the households
   failing for the first time fall from 55 and 66 in 2016-17 to 14-16 in 2022-23. But the share of
   accounts with a failed bill holds at 18-22% throughout, so the falling count is not the whole
   story.

**Ruling.** The next change belongs to the **world**, not the matrix. Specifically, it belongs to
the world's failed share of billed pounds by year, which runs about 3.3% (2016-19), 1.65% (2020-21),
2.9% (2022) and 5.8% (2023). The real charge runs about 1.2% (2019), 1.1% (2021), 2.1% (2022) and
2.7-2.9% (2023) (Centrica, `bad_debt_provisioning.md` §3.2). Against that, the world's 2022 is too
low relative to its own 2016-19, its 2023 is too steep, and its 2016-19 is high relative to its 2021.
**What I cannot yet tell** is which end is wrong: whether the pre-crisis level is too high or the
2022 response too small and too late. That is not a run. It is a knowledge read: a published
annual series for the share of domestic accounts, or of billed pounds, falling into arrears from
2017 to 2023 (Ofgem's debt-and-arrears indicators are the first place to look), set against
column A's "failed share of billed". Then the W2 affordability cluster (W2_4.., W2_38) decides which
mechanism to move, blind to this charge. No matrix change is warranted on this evidence.

**Status:** OPEN and BLOCKING. The side is the world. The next step is the arrears-indicator read
against column A, before any world build.

## 2026-10-23 (later): the arrears-indicator read. The 2022 step is the overlay's, not the world's; the world's error is 2020-21 and persistence

The read the last section asked for, as a desk comparison. No fetch was needed: Ofgem's *Debt and
arrears indicators*, Q4 of each year, are already in `debt_and_collections.md` §2.1, and Centrica's
overlay by year is in `bad_debt_provisioning.md` §3.2. No run, world value or matrix value was changed.

**What each series counts.** Ofgem's figures are a **stock**: electricity accounts unpaid for more
than 91 days with no plan, at 31 December. They are counted per fuel account, not per household, and
written-off debt is excluded. The world's figures (table A above) are also a stock: bills unpaid for
30 days or more at 31 December, per household, with nothing written off. Neither the levels nor the
thresholds match, so no ratio between the two series is drawn. What is compared is each series'
**change on its own previous year, per indebted account**, which takes book size out of both.

| year | Ofgem avg arrears per account, GBP | change | world arrears per indebted household, GBP (A: pounds / households) | change |
|---|---|---|---|---|
| 2019 | 654 | | 145 | |
| 2020 | 774 | **+18%** | 135 | **-7%** |
| 2021 | 905 | **+17%** | 136 | **+1%** |
| 2022 | 1,028 | +14% | 177 | +30% |
| 2023 | 1,303 | +27% | 257 | +45% |
| 2024 | 1,617 | **+24%** | 205 | **-20%** |

Heads: Ofgem's accounts in arrears are flat from Q4 2021 to Q4 2022 (775,721 to 778,598), then rise
29% in 2023. Ofgem attributes the Q4 2022 to Q1 2023 dip to EBSS and EPG. Arrears pounds rise 18% in
2022 (GBP 1.11bn to 1.31bn), less than 2021's 28%, then 72% in 2023.

**What this says.**
1. **The published record has no 2022 step in formed debt. The step in the 2022 charge is the
   overlay.** Centrica's macroeconomic overlay rose GBP 95m in 2022 against a GBP 234m charge. Take
   it out and the 2022 charge is about 1.25% of revenue (derived: 2.1% x 139/234). 2021 was 1.1%. The
   overlay is Group-wide, covering billed and unbilled debt, so this is indicative only. The formed
   debt arrives in 2023, and so does the world's. **This refutes the last section's ruling that the
   2022 shortfall belongs to the world.** The world's late timing agrees with the record. The 2022
   step the validator asks for is a forward-looking provision that a real supplier booked on what it
   could see in 2022: the announced cap rise and its own collections. That is the company's question,
   and the wall allows it. `company/finance/bad_debt_provision.py` already carries the overlay
   at its two published ends. **How a supplier sizes its overlay against observables is GAP**, as that
   module says, and a K8 page must come before any build.
2. **The world's 2020-21 is wrong in direction.** Published arrears per account rose 18% and 17%,
   and Centrica's charge rose to 2.2% in 2020 (its COVID overlay). The world's per-household arrears
   fell, and its failed share of billed pounds halved (3.3% to 1.6%). Explanations, unranked because
   this evidence cannot separate them: (a) the COVID income shock is missing or too weak in the
   world; (b) the 2020 pause in supplier debt collection (no disconnections, no involuntary PPM
   installs), which is collection behaviour rather than household failure; (c) the sample, since 80
   to 86 households is small enough for a 7% move to be noise. The halving of the flow is large
   enough not to be noise. I cannot yet say which of (a) and (b) it is.
3. **The world's crisis debt clears, and the record's persists.** In 2024 the world's per-household
   arrears fall 20% while Ofgem's rise 24%. This is the 2026-10-15 worker finding
   (`WORKER_FINDING_THE_WORLDS_2021_23_ARREARS_STEP_UP_...`), now seen on this run.
4. **EBSS does not reach the world.** `household_budget_w2_4.md` said the GBP 400 "already reaches
   the world through the bill". It does not. `company/regulatory/energy_bill_support.py` and
   `ebss_register.py` are read only by tests and the dashboard generator, and no world or billing
   path nets the credit. That claim is corrected beside it, in this commit. Without EBSS, the world's
   October 2022 to March 2023 bills are GBP 66.67 a month too high per household. That lands in
   exactly the window where the world's failed share peaks (6.7% in January 2023). Its direction is
   to lower the world's too-steep 2023, but its size is not measured here. It is a fidelity item
   (W7: world first), decided blind to the charge.

**Status:** OPEN and BLOCKING, with the side now split. The 2022 step belongs to the **company**: an
overlay driven by observables, with a K8 page first on how suppliers size it. The 2020-21 direction
and the persistence belong to the **world**, along with EBSS, which is a plain fidelity omission.
Next, in order: (i) EBSS into the world's bill, which is the smallest and certain; (ii) the overlay
K8 page; (iii) the 2020-21 knowledge read, income shock against the collection pause. The validator's
`CRISIS_YEARS = (2021, 2022)` should be re-read in light of point 1. That is a question for the step
after (ii), not a change today.
