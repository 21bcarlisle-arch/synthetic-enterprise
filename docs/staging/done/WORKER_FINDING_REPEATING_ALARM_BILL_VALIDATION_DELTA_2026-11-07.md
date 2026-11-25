**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# bill validation: A DIFFERENCE LARGER THAN A PENNY: vat_gbp on C5 invoice 110, GBP +28.05 (validator 15.24, biller 43.29). Every difference on record until now was exactly 1p.

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 21 separate day(s)**, between **2026-11-02** and **2026-11-25**,
and **2 member(s)** of the family `bill_validation_delta` have fired. Both counts are DERIVED
from this document's own dated lines every time the alarm fires again, so they age with the
document rather than with its first firing.

Separately, the observer that last filed reported **45 consecutive firing(s) without a state
change**, over **44.1h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

## The alarm, verbatim

```
bill validation: A DIFFERENCE LARGER THAN A PENNY: vat_gbp on C5 invoice 110, GBP +28.05 (validator 15.24, biller 43.29). Every difference on record until now was exactly 1p.
```

## What is known without diagnosing anything

- Signature: `bill_validation_delta` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-11-03T04:05:02+00:00
- Repeats before escalation: 49 (threshold `ESCALATE_AFTER_REPEATS` = 3, applied by `notify()`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

A REPEATING FAILURE IS ONE OF THE THREE TRIGGERS FOR THE END-TO-END CHECK (director,
2026-10-04): before fixing the instance, write the section below -- the loop may be the world,
the maths, the canon or the frame, not the code that is alarming.

## End-to-end check

**Done 2026-11-25. The biller was right, and the validator's comparison was graded against the wrong rule.**

- **Re-measured first.** The full comparison on the f60d1d55a2 book, which is after 9739e7bad4, still filed C5/110 at +28.05 and C5/113 at −23.63. 9739e7bad4 did not clear it, because it never touched this claim.
- **What the bills say.** On 110 the VAT line is 5.88 (5% of the month's own 117.67 at 31.0 kWh/day, under the 33 kWh/day de minimis) plus 37.41 (20% of a 187.08 catch-up for Feb–May, months billed over the de minimis). The ledger's `catchup_lines_by_rate` confirms one line at 20%. On 113 it is 5.86 plus −25.88: August reversed at 20% (−157.51 / −31.50) and rebilled at 5% (+112.49 / +5.62).
- **The rule.** VAT Notice 700 §18.2.5 says a credit or debit note takes the rate of the original supply. The commons has this as `back_billing_and_liability.md` §15, read in the primary on 13 Nov. That page already named these two bills as correct on 3 Nov. `tools/bill_validation_comparison.compare_bill` was the one reader left that charged the catch-up at the carrying month's rate.
- **Ranked explanations.** (1) The comparison applies the wrong rule. This is confirmed: with the claim split, both bills agree. (2) The biller is wrong. Refuted, by the rule and by its per-rate lines. (3) The de minimis threshold is wrong. Not in play: both readers use the same 33 kWh/day. (4) Something deeper. One item is noted below. No concern is raised for the director, because this is a plain factual correction.
- **The fix.** `vat_gbp` now grades the month's own VAT (the VAT line less `catchup_vat_gbp`) against the month's own lines. A new `catchup_vat_gbp` claim grades the catch-up with `independent_bill_validator.catchup_vat_breach`, the run check §15 names. It reads BOUNDED inside the range, DISAGREED with the breach reason outside it, and UNCHECKABLE when no run check is available. Test: `tests/tools/test_a_catch_ups_vat_is_graded_at_the_corrected_months_rates.py`. Four mutations are killed: the old combined base, comparing the whole VAT line, an always-BOUNDED catch-up, and a dropped breach reason.
- **The book afterwards.** No difference over 1p remains. VAT disagreements fell from 2,993 to 1,445, all of them 1p. About 1,548 of the old penny rows were catch-up bills re-rounded at the wrong rate, a smaller instance of the same defect. 6,902 claims are BOUNDED, mostly domestic catch-ups, where the run check is exact.
- **Not done here.** For a domestic run `catchup_vat_breach` is exact, so its verdict could be AGREED rather than BOUNDED. I left it BOUNDED because that is the weaker claim. A reader wanting the stronger one should pass the segment through.

## Still live
- **2026-11-02** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-11-03** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-11-04** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
- **2026-11-05** — still live. The condition was observed to hold on this date. Restored from `.alarm_repetition_state.json` when this document was re-derived; the observation is that date's, not today's.
## Instances seen
- `bill validation: a difference larger than a penny: unit_charge_at_contract_gbp on pros-#-# invoice # gbp +# (validator -` (first seen 2026-11-02)
- `bill validation: a difference larger than a penny: vat_gbp on c# invoice # gbp +# (validator #, biller #). every differe` (first seen 2026-11-03)

## Re-asked
- **2026-11-07** — re-asked: **still_holds**. observed 2026-11-07, within the 3-day bar.
- **2026-11-08** — re-asked: **still_holds**. observed 2026-11-07, within the 3-day bar.
- **2026-11-09** — re-asked: **still_holds**. observed 2026-11-07, within the 3-day bar.
- **2026-11-10** — re-asked: **still_holds**. observed 2026-11-09, within the 3-day bar.
- **2026-11-11** — re-asked: **still_holds**. observed 2026-11-10, within the 3-day bar.
- **2026-11-12** — re-asked: **still_holds**. observed 2026-11-11, within the 3-day bar.
- **2026-11-13** — re-asked: **still_holds**. observed 2026-11-12, within the 3-day bar.
- **2026-11-14** — re-asked: **still_holds**. observed 2026-11-13, within the 3-day bar.
- **2026-11-15** — re-asked: **still_holds**. observed 2026-11-13, within the 3-day bar.

- **2026-11-15 (worker tick): the silence since 13 Nov is the validator going blind, not this delta clearing.** `bill-validation.service` has exited 1 on every run since 2026-11-13T02:01Z with `FileNotFoundError: docs/state/billing_ledger.json`. The publish has retired the plain ledger in favour of the gz (d7c214a392), and `bill_validation_comparison.compare_all` still read the plain file. It now goes through `ledger_store.load_ledger`, landed in the same commit as this line. Expect this alarm to resume on the next hourly run if the C5 invoice 110 VAT delta is still in the book. That would be the delta, still live and still undiagnosed, and not a new episode.
- **2026-11-16** — re-asked: **still_holds**. observed 2026-11-15, within the 3-day bar.
- **2026-11-17** — re-asked: **still_holds**. observed 2026-11-16, within the 3-day bar.
- **2026-11-18** — re-asked: **still_holds**. observed 2026-11-17, within the 3-day bar.
- **2026-11-19** — re-asked: **still_holds**. observed 2026-11-18, within the 3-day bar.
- **2026-11-20** — re-asked: **still_holds**. observed 2026-11-19, within the 3-day bar.
- **2026-11-21** — re-asked: **still_holds**. observed 2026-11-20, within the 3-day bar.
- **2026-11-22** — re-asked: **still_holds**. observed 2026-11-21, within the 3-day bar.
- **2026-11-23** — re-asked: **still_holds**. observed 2026-11-22, within the 3-day bar.
- **2026-11-24** — re-asked: **still_holds**. observed 2026-11-23, within the 3-day bar.
- **2026-11-25** — re-asked: **still_holds**. observed 2026-11-24, within the 3-day bar.
