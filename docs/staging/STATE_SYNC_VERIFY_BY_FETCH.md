[PROJECT] PROJECT_STATE.txt STILL stale after "website fixed" claim -- the deploy pipeline for state files is broken, and "done" must mean verified-by-fetch

THIRD false-completion this session. The NTFY "Website fixed (92d65b66)... all deployed to poesys.net" was just checked against the live file:

  https://poesys.net/state/PROJECT_STATE.txt
  STILL reads: Generated 2026-06-30T20:06:26Z | Phase HY | 9,290 tests

That is 3 days and ~60 phases stale. It still lists /customers/, /project/, /sim/ as STUB. Whatever the commit fixed in the live SPA, the state-file deploy pipeline did NOT run. This is the same break open since June 30.

ROOT CAUSE (address this, not just the symptom):
"Done" is being defined as "committed" instead of "verified by fetching the live artifact." Three times this session a fix was reported complete while the live file stayed stale. The fix is a hard rule, not more diligence.

DO THIS:

1. DIAGNOSE THE STATE-FILE DEPLOY, don't just regenerate locally.
   PROJECT_STATE.txt regenerates into the repo but the deployed copy at poesys.net/state/ is stale. Find the actual break: is the generator writing to a path the deploy doesn't publish? Is the poesys.net/state/ route mapped to a different source than the GitHub Pages site? Is there a caching layer not being purged? Is the post-run hook that regenerates it not actually firing? Trace the full path from "run completes" to "bytes served at poesys.net/state/PROJECT_STATE.txt" and find where it stops.

2. FIX IT so every run regenerates AND deploys the file.

3. VERIFY BY FETCH -- curl https://poesys.net/state/PROJECT_STATE.txt yourself, confirm the Generated timestamp is within the last hour and Phase matches the current phase. Paste the fetched timestamp + phase into the completion NTFY. If you cannot fetch a fresh copy, it is NOT done -- report the specific blocker instead of success.

4. ENCODE THE RULE IN CLAUDE.md (permanent, applies to all observability artifacts):
   "An observability artifact (PROJECT_STATE.txt, customer_sample.json, shadow HTML, LATEST.md) is DONE only when its live published URL has been fetched and confirmed to show current data. 'Committed' is not 'done.' 'Deployed' is not 'done' until fetched. Completion NTFYs for these artifacts must quote the fetched live timestamp/phase as proof."

Same applies to customer_sample.json and the shadow HTML site from the earlier observability instruction -- none are done until the advisor can fetch them showing current data. Report each with its fetched live URL and timestamp.
