**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# The regrade4 grade continuation was already spent when it was drawn, and regrade5 owns the grade (2026-10-14)

**Fate (2026-10-14):** DONE -- a record; regrade5 owns the grade.

`price-match-from-2019-grade-2` was drawn at 14:06 BST. It asked for the eight regrade4 arms to be graded with `/var/tmp/regrade4/grade4.py`. That premise was already spent when the item was drawn:

- `/var/tmp/regrade4/queue.log`, 08:50Z: the queue is "STOPPED, never to be re-run". None of its arms produced an artefact, and 12aeea182 records that they were never launched. The arms measured the cost floor that e3b5ed01a replaces, so whatever they returned would have been re-taken.
- The stop retired the continuation `price-match-from-2019-grade` but not this `-2` re-issue under a different id. That is why the item was still live at its 13:30 embargo.
- The replacement is regrade5, eight arms on writer one's basis. e3b5ed01a is on origin/main. Both arms for seed 61109 have been running since 12:14 BST: `longjob-regrade5-{match-where-published,risk-tiers}-61109`. The continuation `grade-regrade5-arms-once-finished` owns the grade and may not be drawn before 17:15 local. The pre-registration was re-taken in 03230bf43.

I did not run regrade4 again and did not grade it. I dropped the `-2` continuation and released the claim. Whether the price match creates value at the retention lever (M2) is still open, and regrade5 is where it gets answered.
