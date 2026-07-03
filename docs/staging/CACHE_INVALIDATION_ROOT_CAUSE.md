[PROJECT] The hard gate passed for YOU but still fails for the advisor -- it's a CDN CACHE problem, not a regeneration problem. This is the real root cause.

CRITICAL EVIDENCE:
- CC fetched https://poesys.net/state/PROJECT_STATE.txt at 22:40 and got: Generated 2026-07-03T21:36:23Z, Phase PT, 15,290 tests. FRESH. Gate passed from your side.
- The advisor fetched the SAME URL minutes later and got: Generated 2026-06-30T20:06:26Z, Phase HY, 9,290 tests. STALE (4 days old).
- Same URL. Two different responses. The file IS regenerating and IS deploying -- CC proved that. But the public edge is serving a stale CACHED copy to external fetchers.

DIAGNOSIS: Cloudflare (or whatever CDN fronts poesys.net) is caching /state/PROJECT_STATE.txt with a long TTL and NOT purging on deploy. CC's fetch hits origin or a fresh-cache path; the advisor's fetch hits the stale edge cache. This is why 4 rounds of "regenerate the file" changed nothing the advisor could see -- the file was never the problem, the cache is.

THE FIX (cache invalidation -- do both):
1. Set Cache-Control on all /state/* files to no-cache or max-age=0 (or max-age=60 at most). These are status files that must always be fresh. Find where headers are set -- Cloudflare Pages _headers file in the site root, or a Cloudflare cache rule for /state/*. Add:
   /state/*
     Cache-Control: no-cache, max-age=0
2. Purge the Cloudflare cache for /state/* as the LAST step of the deploy hook (Cloudflare API purge, or purge-everything if scoped purge isn't wired). So every deploy evicts the old cached object.

VERIFY -- and this time verification MUST be an EXTERNAL fetch, not CC's own:
- After the fix + one deploy, the advisor will fetch https://poesys.net/state/PROJECT_STATE.txt and must see Phase PT+ / today's date.
- CC cannot self-certify this one -- the whole point is that CC's fetch and the advisor's fetch DIVERGE. CC seeing fresh bytes does NOT mean the advisor does. Report it as "cache fix deployed, awaiting external confirmation" and let the advisor confirm.

This same cache issue affects EVERY /state/ file: customer_sample.json, billing_ledger.json, shadow pages. Fixing the cache header for /state/* and /shadow/* fixes advisor visibility for ALL of them at once. This is the single highest-leverage fix in the whole observability effort.
