**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** none -- a control grading a published run against the bad-debt step-up already recorded in docs/market_research/ASSUMPTIONS.md (1.3% to 2.8% of revenue); no new domain claim

# The crisis bad-debt control has skipped since the run went gzip, and the published run shows no crisis step-up (2026-10-14)

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
