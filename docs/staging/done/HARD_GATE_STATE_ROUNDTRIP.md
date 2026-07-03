[PROJECT] HARD GATE -- prove the state-file deploy round-trip. Do NOTHING else until this one loop closes.

STOP all other work. No billing, no customer_sample.json, no anchoring, no new phases, no report sections. This single round-trip is the only task until it is confirmed by advisor fetch.

THE PROBLEM: PROJECT_STATE.txt at https://poesys.net/state/PROJECT_STATE.txt has read "Generated 2026-06-30T20:06:26Z, Phase HY, 9,290 tests" for four days, across repeated "fixed" claims. Every fix has been reported done without the live URL being fetched to confirm. The instruction was never the problem -- the verify-by-fetch discipline is not landing. So this task IS the discipline, reduced to its smallest form.

THE ROUND-TRIP (do exactly this, in order):
1. Write the current UTC timestamp and current phase + test count into PROJECT_STATE.txt.
2. Commit and push through whatever path serves poesys.net/state/ (Cloudflare, per the deploy diagnosis).
3. Wait for deploy.
4. curl https://poesys.net/state/PROJECT_STATE.txt yourself.
5. Read the Generated timestamp in the returned bytes.
6. Paste that fetched timestamp into the NTFY, verbatim, as proof.

PASS = the timestamp you fetched in step 5 matches what you wrote in step 1, and it is today's date (2026-07-03), not June 30.

IF IT FAILS: do not retry silently and do not report success. Paste the EXACT error or the EXACT stale bytes you got back, and state which step broke:
- Did the commit land? (git log shows it)
- Did Cloudflare deploy run? (deploy log)
- Did the fetch return old bytes despite a successful deploy? (then it's caching or path-mapping -- report which path Cloudflare serves /state/ from vs where you wrote the file)

This is a diagnosis gate, not a feature. The entire observability layer -- and every "done" claim that depends on it -- is blocked until this one file proves it can go from write to served-and-fetched in a single confirmed cycle. Report back with the fetched timestamp or the exact broken step. Nothing else.
