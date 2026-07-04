[PROJECT] Advisor verification path: mirror shadow pages on the github.io host. poesys.net is confirmed unreliable for the advisor's fetches -- and only for the advisor's.

RESOLUTION OF TODAY'S DIVERGENCE (and the week's pattern): advisor cache-busted fetch of poesys.net/shadow/?v=1804 at ~18:04 STILL returned the 08:35Z generation (Phase OL, -8317 exec summary), while CC's 17:58 direct fetch of the same URL returned 16:40Z Phase QB, consistent, Cf-Cache-Status=DYNAMIC. A novel query string defeats normal CDN caching, so this is not simple staleness: the advisor's egress path to poesys.net persistently serves old content. Evidence across the week: poesys.net = advisor always stale; github.io = advisor always fresh (PROJECT_STATE.txt proved this same split before moving to github.io/status/).

CONCLUSIONS:
1. The website fix IS delivered at origin -- CC's 16:40Z evidence stands, incident hypothesis (CD stall) may explain part of the afternoon but the advisor-path staleness is now proven independent of it. The site is presumably correct for real visitors (Rich confirming in his browser).
2. poesys.net URLs are PERMANENTLY UNSUITABLE for advisor verification. github.io URLs are the advisor's reliable channel.

DO:
1. Publish the shadow pages (all five) and the state JSONs (customer_sample.json, billing_ledger.json, population_anchoring.json, sim_data.json equivalents) on the github.io host, same commit path that serves status/PROJECT_STATE.txt (proven fresh to the advisor). Likely trivial: ensure these files are in whatever the GitHub Pages deployment serves and list the exact github.io URLs in PROJECT_STATE.txt Key Files, replacing/alongside the poesys.net ones.
2. The consistency gate from WEBSITE_INTEGRITY applies to the github.io copies identically -- same generator pass, same run, same stamps.
3. Standing rule (CLAUDE.md observability section): every advisor-verification artifact ships on github.io; poesys.net is the human/visitor surface only. Advisor acceptance fetches always target github.io URLs.

CONFIRM with the list of live github.io URLs; advisor will fetch each to close. This ends the producer/consumer divergence class permanently by giving each consumer a channel that is reliable FOR THEM.
