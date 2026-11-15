**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# delivery seat: the direction record did NOT reach origin, so origin's steer is the previous stretch's -- landing refused (LandingRefused): GATE RED on the resulting tree (rc=1). Th

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 1 separate day(s)**, on **2026-11-08**, and **1 member(s)** of
the family `auto:9cd1be5d90d8d339` have fired. Both counts are DERIVED from this document's own
dated lines every time the alarm fires again, so they age with the document rather than with
its first firing.

Separately, the observer that last filed reported **3 consecutive firing(s) without a state
change**, over **6.0h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

## The alarm, verbatim

```
delivery seat: the direction record did NOT reach origin, so origin's steer is the previous stretch's -- landing refused (LandingRefused): GATE RED on the resulting tree (rc=1). This is the tree the commit WOULD create, not the working tree -- a working tree that passes here means the unstaged half is what makes it pass. | ❌ SITE TESTS FAILED -- COMMIT REFUSED. | [site-lane] A red site/** test can neve
```

## What is known without diagnosing anything

- Signature: `auto:9cd1be5d90d8d339` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-11-08T03:48:41+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS` = 3, applied by `notify()`)
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

The loop was not the world, the maths or the canon: it was the page meeting the machine's own house
style. Explanations considered, ranked by evidence:

1. **The page prints a colon after its own label, and the concerns CLI asks for a colon in the value
   (confirmed).** `site/harness/index.html` drew each concern as `"Proposal: " + proposal`.
   `director_concerns --raise` asks for a proposal "or 'investigate: <what>'", and the row raised
   about the 5-7 Nov stop reads "Investigate first: did you shut the PC or WSL down...". The page
   printed "Proposal: Investigate first:", and `site/test_no_published_page_renders_an_empty_field.py`
   (shape "a label followed by another label") read it as an empty Proposal field. The seat must
   carry every open row until it is answered, so every orientation re-sent the same text and every
   landing was refused the same way.
2. A flaky render harness or the seat's systemd environment: ruled out. The refusal reproduced
   deterministically in an interactive worktree at origin/main a8252973fd plus the seat's
   WRITE_SCOPE bytes (1 failed, 1882 passed), and on the test alone.
3. The test is wrong: ruled out as the fix. "Proposal: Investigate first:" cannot be told from a hole
   by a reader either, and no lexical rule separates it from the 2 Nov hole "Source: Open question:
   a file". The test is keyed to the reader, which is the right key.

Nothing here is for the director: it was a page format, fixed as a class.

## Diagnosis and fix (2026-11-10, worker)

- **The red test:** `site/test_no_published_page_renders_an_empty_field.py::test_no_published_page_renders_an_empty_field`,
  on `harness/index.html`, through the full `pytest site/` run that `tools/site_lane_gate.py` triggers
  because `site/data/delivery.json` is in the seat's `WRITE_SCOPE`.
- **Why a direction-only change hit it:** delivery.json is the Harness page's feed, so the seat's own
  record is rendered by the page the sweep reads.
- **The fix:** the concern panel's labels take an em dash ("Proposal — ", "Resolution — "). Neither
  slot can be empty (the proposal falls back to "none recorded"; the resolution is drawn only when
  present), so the colon was the only thing making a hole. The control in
  `site/test_harness_delivery_record.py` renders a row in the seat's own form and asserts the sweep
  finds nothing; putting either colon back fires it.
- **Resolved when:** the seat's next orientation lands on origin by its own tick. Archive then, not
  before.

## Still live

## Instances seen
- `delivery seat: the direction record did not reach origin, so origin's steer is the previous stretch's -- landing refused` (first seen 2026-11-08)

## Re-asked
- **2026-11-08** — re-asked: **still_holds**. observed 2026-11-08, within the 3-day bar.
- **2026-11-09** — re-asked: **still_holds**. observed 2026-11-08, within the 3-day bar.
- **2026-11-10** — re-asked: **still_holds**. observed 2026-11-08, within the 3-day bar.
