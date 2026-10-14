**Severity:** BLOCKING · **Lane:** E_finance_treasury · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** none -- a control grading a published run against the bad-debt step-up already recorded in docs/market_research/ASSUMPTIONS.md (1.3% to 2.8% of revenue); no new domain claim

# The crisis bad-debt control has skipped since the run went gzip, and the published run shows no crisis step-up (2026-10-14)

**Fate (2026-10-14):** ATOM -- company-side, as printed below: the age-band provision lags the world's 2022 arrears; it is fixed by the forward-cash-forecast provision, and the reader fix lands with it, never alone.

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

## End-to-end check: the explanations the evidence allows, ranked

The validator's anchor is Centrica's **bad-debt charge**, "from 2.3 to 2.8% of revenue". That is a
P&L charge, and under IFRS 9 it is the expected credit loss, booked as arrears build, not when the
debt is written off.
1. **The supplier's provision lags by design (most likely).** company/finance/bad_debt_provision.py
   provisions on flat age bands (0.5/5/20/50/90%), so a 2022 arrears build is charged only as it
   ages, and the charge peaks in 2023. That matches the pounds above. The forward-cash-forecast
   engine (payment-plan design, section 9) already names these bands as what it replaces. If this
   ranks first, the defect is company-side, and the validator's window is right.
2. **The world under-builds 2022 arrears.** Its share peak of 2.35% is still short of 2.8% even in
   2023. The arrears stock by month through 2022 would separate this from (1); it is not printed
   yet.
3. **The validator's window (2021-22) is wrong.** This holds only if real charges lagged too,
   which IFRS 9 argues against.
Settle (1) against (2) with one print, before any change: the company's provision charge by month
against the world's arrears stock by month, for 2021-2023.

## Printed: (1) holds, the world builds the arrears and the provision lags them

Year-end, company_provision.by_date in the 6ab998ad7 run (GBP):

| year-end | receivable | 30-90 days | over 90 days | provision |
|---|---|---|---|---|
| 2021 | 6,515 | 1,716 | 868 | 978 |
| 2022 | 16,906 (x2.6) | 4,279 (x2.5) | 1,059 (x1.2) | 1,604 (x1.6) |
| 2023 | 13,970 | 3,928 | 1,978 | 2,090 |

The world builds the 2022 arrears: the receivable is 2.6x and the 30-90-day band 2.5x. The
age-band provision reserves little until debt passes 90 days, so it moves 1.6x in 2022, and the
over-90 band only arrives in 2023. **The defect is company-side: the provision is not
forward-looking.** The validator's window is right and the world does not under-build. The fix is
the forward-cash-forecast provision (payment-plan design, section 9), which charges expected loss
as arrears build, not a world change. Until it lands, this control stays red against the
published record, and that is correct. Its reader fix should land with the provision engine, or
with a recorded acceptance that the age-band provision is known to lag.

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
