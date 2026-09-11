**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing`

# The opening DD estimate works, and nothing published can see it

*Delivery seat, 2026-09-03, lane-0. Grades
`SEAT_PREREGISTRATION_WHAT_GIVING_THE_DIRECT_DEBIT_AN_ESTIMATE_MUST_SHOW_2026-09-02.md` (P1–P5) and
`SEAT_PREREGISTRATION_WHETHER_THE_OPENING_DD_ESTIMATE_REACHES_ANY_PUBLISHED_NUMBER_2026-09-03.md`
(Q1–Q6). Both were filed before the arms were run. Evidence:
`tools/dd_opening_arms.py`, artefact `docs/reports/dd_opening_arms.json`.*

---

## 1. The question

Publish `1c4f64733` (run at `4013b1de1`, **before** `company/billing/annual_consumption_estimate.py`
landed at `9760fc7a5`) and publish `b6b3c3fa8` (run at `19f226e46`, **after**) carry **identical** net
margin, gross, capital, treasury start, treasury end, enterprise value, net after cost-to-serve and
bills issued. Either the organ does nothing, or we publish nothing that could tell.

**It is the second, and it is not close.** The organ moves a great deal. Not one figure it moves has
a reader.

## 2. Method, and the control that makes it trustworthy

`opening_dd` is computed at `simulation/run_phase4c_on_phase2b.py:319` — *after* `bills` exists —
and reaches exactly three call sites (`annual_dd_review_view` 320, `build_dd_balance_book` 332,
`build_dd_level_collection_book` 341). Nothing upstream of `bills` can see it. So both arms are pure
functions of one seed's issued bills, and re-running the ~100-minute Phase 2b twice would have added
nondeterminism rather than fidelity: the two runs would differ in committee decisions before they
differed in direct debits, and the diff would be unattributable.

* **Arm F (flat)** — the displaced rule: opening = `seq[0][1]`, the first issued bill.
* **Arm E (estimate)** — the live `_opening_dd_by_customer`, through the seam door. Not a copy of it.

**The control.** `docs/reports/run_output_latest.json` was produced 2026-09-01, before the organ
landed, so its own DD books **are** Arm F as the real run computed them. The reconstruction
reproduces `dd_balance_book` **byte-identically** and reproduces `annual_dd_review` on all 806
events and every summary field — differing only by the presence of the `unestimated_customers: 0`
key, which did not exist in the code when that run was made. The reconstruction is sound.

## 3. Act (a) — the whole-output diff: 3 of 104 keys move, and no headline is among them

| | |
|---|---|
| keys that moved | `annual_dd_review`, `dd_balance_book`, `dd_level_collection_book` |
| keys that did not | the other **101**, including all eight headline figures |

**Q1 CONFIRMED exactly.** Nothing outside the three predicted keys moved. And **`dd3_held_credit_balance_sheet` — the fourth key I predicted would move — is not in the substrate at all**, because it is computed inside `extract_report_data` from `dd_balance_book.summary.peak_held_credit_gbp`, which moves by 41.7% (below). So it moves too; it simply is not a key of this artefact.

**Q2 CONFIRMED, and it is structural, not a coincidence of this book.**
`simulation/run_phase2b.py:2618` is `treasury += rec["net_margin_gbp"]` followed by
`rec["treasury_cash_balance_gbp"] = treasury`. **The treasury is a running total of net margin.** It
is a P&L accumulator wearing a cash name. Empirically `final − starting − total_net = 6.2e-05` (float
rounding). So the published cash figure **cannot express payment timing under any direct-debit
arrangement whatsoever** — the two arms could not have differed on it even in principle, and neither
could any future one. That is the reason the repair is the surface and not the organ.

## 4. Act (b) — what actually separates the two arms

Every figure below is from one seed, 10,906 issued bills, substrate
`docs/reports/run_output_latest.json`. Intervals are 95% percentile bootstrap
(`_bootstrap_mean_interval`, 2,000 resamples).

**Opening amounts.** 178 accounts get an opening under Arm F, 142 under Arm E.
**0 of them agree to the penny** (Q4, P1 both confirmed — and a weak result, as pre-registered: two
continuous quantities rarely coincide). Arm F mean £36.31 (median £28.50, CI £30.53–£42.90); Arm E
mean £60.46 (median £56.44, CI £57.38–£63.65). The flat rule was systematically **under-sizing**.

**End-of-year-1 balance drift, matched population (the only attributable comparison).** 96 accounts
carried by both arms, credit and debit separate, never summed:

| | Arm F (flat) | Arm E (estimate) |
|---|---|---|
| ended year 1 **in credit** | 14 accts, mean **£193.19** (CI 58.67–396.36) | 40 accts, mean **£77.28** (CI 59.32–95.30) |
| ended year 1 **in debit** | 82 accts, mean **−£377.53** (CI −438.78–−316.82) | 56 accts, mean **−£199.74** (CI −262.92–−147.00) |
| worst single account | £1,459.60 credit / £1,346.46 debit | £278.14 credit / £1,108.68 debit |

Paired on the same household: **the estimate ends the year closer to zero for 80 of 96 accounts**,
and mean |drift| falls by **£201.93 (95% CI −£257.57 to −£143.50)**. The interval excludes zero.

The unmatched pair — what each arm would actually *publish* — is in the artefact beside this and is
deliberately not merged with it: Arm E's book is 96 accounts against Arm F's 178, and a difference
between those two is partly the refusal and partly the rule.

**First-year review variance (P2, the one designed to refute the organ).** Mean |variance| at window
0: **333.8% → 21.2%**; median **104.4% → 15.6%**. Large increases at window 0: **185 of 222 → 40 of
114**. **P2 CONFIRMED, by an order of magnitude.** The flat rule was not a baseline that took some
beating; it was an artefact of the join month that put five in six first-year households through a
>15% payment increase.

**The honest `None`s (P3, Q3 CONFIRMED).** Arm F refuses nobody. Arm E refuses **82** accounts in the
balance book and **110** in the review runner (the runner reads all bills, the book only direct-debit
ones — different populations, stated rather than reconciled away). **Every single refusal has the
same cause: no published rate.** `estimate_cause_no_consumption_basis = 0`. Not one account failed
for want of a consumption estimate; all 82 failed because this repository holds no published
GB rate before the price cap began in January 2019, so a pre-2019 acquisition has nothing to
annualise against. That is fail-closed working exactly as designed, and it is **46% of the DD book**.

**The basis split (Q6 CONFIRMED, and it is a finding of its own).**

| basis | accounts |
|---|---|
| `registry_eac` | **142** |
| `metered_history` | 0 |
| `customer_declared` | 0 |
| `tdcv_typical` | 0 |

`_opening_dd_by_customer` passes `registry_eac_kwh`, and `band="MEDIUM"` only when that is absent —
which never happens, because every account in this population carries an EAC/AQ. It never passes
metered history and never passes a declaration. **Three of the four rungs of `BASIS_ORDER` are built,
documented, tested and unreachable from the only live call site**, and the SLC 27.15 precedence the
module exists to implement is therefore exercised at exactly one value. Class
`no_caller_and_never_runs`.

**Held credit and collections (P4 CONFIRMED).** Peak held-credit liability **£3,394.32 → £1,980.45
(−41.7%)**, peak month 2025-06 → 2024-10. Portfolio final balance **−£38,046.14 → −£11,146.64**.
Level DD collections **7,835 → 2,820**, mean monthly level DD **£64.48 → £77.49**. P4 asked for
>5%; it got 41.7%.

## 5. Where a prediction was wrong

**Q5 is REFUTED, and in the direction opposite to the one I feared.** I predicted the estimate arm
would carry a *systematic* bias (registration EAC and cap rate both wrong in a consistent direction)
where the flat arm's error was scattered by join month, and said a systematic bias would be the worse
defect. The measurement says the **flat** rule is the systematic one — 82 of 96 matched accounts end
year 1 in debit, 85% one-sided — and the estimate arm is both closer to zero *and* less one-sided
(56/96, 58%). The prediction is kept here beside the result rather than revised.

## 6. The finding

**Every figure in §4 is invisible.** `annual_dd_review`, `dd_balance_book`,
`dd_level_collection_book` and `dd3_held_credit_balance_sheet` are run-output and report-data keys
with **no reader in `site/`**. Grep across `site/**.js`, `site/**.html` and the dashboard generator
returns nothing. The project already knew half of this and wrote it down inside `simplified.json`:

> *"TWO ARTEFACT KEYS HAVE NO BUSINESS READER and are deliberately unpinned
> (`dd3_held_credit_balance_sheet`, `enterprise_value_margin_basis`)."*

So the two publishes agreeing to the penny was never evidence about the organ. It was evidence about
the surface: **the eight headline figures a reader can see are, by construction, incapable of
registering a direct-debit change, because seven of them are P&L and the eighth is a P&L accumulator
named "treasury".** A supplier's opening direct debit is one of the few numbers a real customer can
quote back at you, and this company publishes no view in which it exists.

## 7. What follows

1. **Publish the per-account opening amount and the year-1 balance drift, both arms, with clocks and
   bounds.** That is the surface act (c) asks for, and it is the next increment.
2. **The `treasury` name is a defect of its own.** A figure that is arithmetically identical to
   cumulative net margin should not be called a cash balance on a page a reader can check. Filed
   here rather than minted separately because it is the same measurement.
3. **`BASIS_ORDER`'s three unreached rungs** need either a caller or an honest statement that the
   live population cannot exercise them.
