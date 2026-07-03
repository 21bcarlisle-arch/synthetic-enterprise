[PROJECT] Priority 1 -- diagnose the poesys.net/state DEPLOY PATH specifically. Regenerating into the repo is not the same as bytes served at the URL.

STILL STALE ON LIVE FETCH: https://poesys.net/state/PROJECT_STATE.txt reads Generated 2026-06-30T20:06:26Z, Phase HY, 9,290 tests. Fourth stale check this session. The generator has been "fixed" in commits repeatedly; the served bytes never change. That means the break is NOT in the generator -- it is in the path between "file written in repo" and "bytes served at poesys.net/state/".

DIAGNOSE THAT PATH, END TO END:
- Where does poesys.net/state/PROJECT_STATE.txt actually serve from? Cloudflare Pages build output? A specific repo dir? A separate deploy step?
- Does the post-run hook regenerate the file into the repo but never trigger the Cloudflare deploy? Or deploy to a dir the /state/ route doesn't map to?
- Is Cloudflare caching it? (check cache headers / purge)
- Trace one full cycle: run completes -> file regenerated -> committed/pushed -> Cloudflare build -> served. Find the exact step where the June 30 version persists.
Report the specific broken step. Do not just regenerate locally again -- that has been done four times and changes nothing served.

FAST FIRST STEP FOR ADVISOR VISIBILITY (do this alongside):
PROJECT_STATE.txt already lists site/data/sim_data.json as "parseable without JS." The website tabs are JS and unreadable to the advisor, but JSON at a stable path is readable. So:
- Publish customer-level and supplier-level data as JSON at stable fetchable paths (e.g. site/data/customers.json, site/data/supplier.json), same mechanism as sim_data.json.
- customers.json: ~15-20 real segment customers incl. dual-fuel pairs (C4 + C4g), each showing elec leg and gas leg SEPARATELY -- separate revenue, consumption, margin, tariff per fuel, plus the combined roll-up. This directly answers the "gas and elec not split at every stage" problem and gives the advisor real data to audit.
- Confirm each by fetching its live poesys.net URL yourself and quoting the returned timestamp in the NTFY.

DONE MEANS: advisor fetches https://poesys.net/state/PROJECT_STATE.txt and sees current phase, AND fetches the customers.json URL and sees C4 with split gas/elec legs. Not "committed." Not "deployed." Fetched and confirmed. If a deploy step blocks you, NTFY the specific blocker.
