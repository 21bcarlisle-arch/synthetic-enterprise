**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# bill validation: A DIFFERENCE LARGER THAN A PENNY: vat_gbp on C5 invoice 110, GBP +28.05 (validator 15.24, biller 43.29). Every difference on record until now was exactly 1p.

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 10 separate day(s)**, between **2026-11-02** and **2026-11-13**,
and **2 member(s)** of the family `bill_validation_delta` have fired. Both counts are DERIVED
from this document's own dated lines every time the alarm fires again, so they age with the
document rather than with its first firing.

Separately, the observer that last filed reported **32 consecutive firing(s) without a state
change**, over **31.0h**. That is `notify()`'s streak counter, which resets; it is not a total
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

_Template -- replace this paragraph with the check itself._ Read the canon (`docs/design/DIRECTOR_CANON*.md`, `docs/staging/DIRECTOR_CANON_*`, `docs/design/THE_MODEL_ON_A_PAGE.md`, `CLAUDE.md`), the logic, and the work and findings in question TOGETHER, as hypotheses under test, stated and unstated. For each surprise, list every explanation the evidence allows -- the world wrong, the maths wrong, the director wrong, it not being that simple, something none of us has thought of -- ranked by evidence, not convenience. Raise each resulting concern with `python3 -m background.director_concerns --raise --kind ... --what ... --proposal ...` and carry on; it never blocks the work.

- 

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
