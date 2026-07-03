[PROJECT] Priority 1 STILL OPEN -- PROJECT_STATE.txt sync did not take. Verify by fetch, not by claim.

Rule 2 catch: the commit "Priority 1 observability: PROJECT_STATE.txt auto-sync + shadow HTML fix" (18:50 BST) reported this done. It is NOT done. The live file at https://poesys.net/state/PROJECT_STATE.txt still reads:
  Generated: 2026-06-30T20:06:26Z | Phase HY | 9,290 tests
That is 3 days and ~60 phases stale. The auto-sync is not firing on push. A commit that touches the generator is not the same as a regenerated, deployed file. Done = the advisor fetches the live URL and sees today's phase and test count.

FIX, and verify each by actually fetching the live URL yourself (curl the poesys.net URL, confirm the bytes changed) before reporting done:

1. PROJECT_STATE.txt auto-sync
   - Find why the generator runs but the deployed file doesn't update (is it regenerating into the repo but not deploying to poesys.net? deploying to a path the URL doesn't map to? cached? not running in the post-run hook at all?).
   - Wire it so every run/push regenerates AND deploys it. Verify: fetch https://poesys.net/state/PROJECT_STATE.txt, confirm Generated timestamp is within the last hour and Phase matches the latest phase.

2. customer_sample.json
   - ~15-20 real segment-model customers with full behavioural trajectories (income_stress, life_events, payment_score, satisfaction, churn_estimate, basis_risk).
   - Publish to a stable URL. Verify by fetching it yourself. Add the URL to PROJECT_STATE.txt Key Files.

3. Shadow HTML site (all four sections: Supplier/Customers/Project/SIM)
   - Plain server-pre-rendered static HTML, NO client-side JS rendering. The advisor's fetch reads raw HTML only.
   - Verify by fetching each shadow URL yourself and confirming real data is present in the raw HTML (not an empty shell that needs JS).
   - Add the shadow URLs to PROJECT_STATE.txt Key Files.

Until the advisor confirms a live fetch of all three showing current data, Priority 1 is NOT done -- do not mark it done, do not move to a new board section, do not report completion. If something blocks the deploy (permissions, caching, path mapping), NTFY the specific blocker rather than reporting success.

Note: PROJECT_STATE.txt itself lists site/data/sim_data.json as "parseable without JS" -- if the shadow site is slow, publishing that same JSON for customers/supplier data at a stable fetchable URL is an acceptable faster first step, provided the advisor can actually fetch it.
