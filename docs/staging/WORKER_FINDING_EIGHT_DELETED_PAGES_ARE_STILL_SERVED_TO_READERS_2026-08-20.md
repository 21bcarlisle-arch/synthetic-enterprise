**Severity:** BLOCKING · **Lane:** H_harness · **Status:** cause found, two fixes landed, one defect open

# The 504s were never real. What was underneath them is: eight deleted pages are still being served, and our own live checks were reading them

This REPLACES `WORKER_FINDING_THE_SITE_IS_FAILING_UP_TO_47_PERCENT_OF_PAGE_LOADS_2026-08-20.md`,
whose headline claim is **false** and whose filename repeated it. Retraction first, because
that document was filed BLOCKING and would otherwise be drawn on its own say-so.

## Retracted: the site was not failing 11–47% of page loads

No reader has seen a 504. Not one.

Cloudflare's analytics logs **every HTTP/2 request to this zone twice** — once truthfully,
and once as a phantom row with `edgeResponseStatus: 504` and
`clientRequestHTTPProtocol: UNK`. The "504 rate" was the share of traffic using HTTP/2.
It "quadrupled across the day" because my own HTTP/2 checks grew as a share of a small
sample.

Measured, not inferred:

| what was sent | what the client saw | what analytics recorded |
|---|---|---|
| 30 parallel `GET /proof/`, HTTP/2 | 30 × 404, all < 1s | 30 × `404 HTTP/2` **and** 30 × `504 UNK` |
| 20 × `curl --http1.1` | 20 × 404 | 20 × `404 HTTP/1.1`, **zero phantoms** |
| 5 clean HTTP/2 GETs | 5 × 404 | 5 × `404 HTTP/2` **and** 5 × `504 UNK` |

And the single decisive query: **in 24 hours, the number of 5xx rows carrying a real HTTP
protocol is zero.** All 419 are `UNK`. A genuine origin timeout logs the client's protocol
correctly, because the request was parsed before the origin was called. These were never
parsed, because they were never requests.

The earlier document's "every path that 504s is extensionless" was an artefact of a
smaller capture. `/swagger-ui.html`, `/actuator/health`, `/id_rsa` and `/.env.example` all
carry extensions and all appear as 504s — they are a scanner in SOF whose HTTP/2 probes
get phantoms like everything else. **The path-resolution-fallback theory is dead, and so
is the `site/404.html` 308 lead** (a 308 from `/404.html` to `/404` is Pages' ordinary
extension-stripping, present on every Pages site).

That is four theories wrong in one day on this incident: cache headers, zone purge,
local-curl-only, and path-resolution fallback. The one that held was the one that stopped
reasoning about mechanisms and partitioned the observations instead.

## The real defect, and it is worse than the phantom

**Eight pages deleted by the five-tab fold are still being served `200` to anyone who
visits them.** Cloudflare's own logs confirm it — the 200s are recorded server-side, so
this is not an artefact of the machine doing the checking.

    /proof/  /world/  /company/  /customers/  /now/  /glossary/  /director/  /evidence/

`age` climbs in real time (29012 → 29057 across a 45-second gap). The same URLs with
`?cb=<nonce>` return the true `404` every time. `/proof/` is the worst of them: a public
page presenting figures that are no longer verified.

What has been ruled out **by doing it, not by reading settings**:

| ruled out | how |
|---|---|
| zone cache | `purge_everything` and a targeted 8-URL purge, both `success: true`, `age` never reset |
| a stale deployment | 8 deployments landed today, all `success`, canonical is the newest and is aliased to `poesys.net` |
| the asset still being deployed | `poesys-net.pages.dev/proof/` and the canonical deployment's own URL both 404 |
| Always Online, dev mode, Page Rules, Worker routes, Cache Rules | all queried live: off / empty / only the three managed rulesets |
| a proxy on this machine | the 200 carries a fresh `cf-ray` and Cloudflare's own analytics record it |

The cache key includes the query string: `/proof/` and `/proof/?` return the ghost,
`/proof/?cb=99` returns 404. The objects are held by **Pages' own asset cache for the
custom domain**, which a zone purge does not reach and a redeployment does not evict.

## What this cost us, which is the part that generalises

Our live checks read the ghosts and reported the retired URLs correctly gone. They were
not. Every "verified live" absence claim made this week was made through a surface that
cannot distinguish absence from staleness.

> A copy cached in the past cannot contain something that did not exist yet. So a check
> that OBSERVES NEW CONTENT is sound. A check that concludes something is ABSENT, REMOVED
> or UNCHANGED is worthless without a cache-buster.

## Landed

1. **`site/live_pixel_verify.cache_bust()`** — every live fetch now carries a per-request
   nonce. Not per call site: deciding which checks are "absence shaped" is exactly the
   remembering that failed. The test double **asserts** the nonce, so removing it fails
   every test in that file at once; mutation-proven (`V.cache_bust = lambda u: u` →
   `fetch reached the edge with no cache-buster`).
2. **The deploy's zone purge is deleted**, replaced by
   `tools/assert_deployed_bytes_are_served.py`: after each deploy, fetch every changed
   asset cache-busted and compare sha256 against the checkout. The purge had **never
   worked once** — `secrets.CLOUDFLARE_ZONE_ID` is empty, so every call hit
   `/zones//purge_cache` and got code 7003, printed `Purge FAILED` and exited 0 — and it
   could not have fixed the ghosts anyway. 12 R15 tests, including one asserting that a
   deleted URL is *reported and never asserted*, because a deploy cannot prove absence.

## Open — needs a decision, and I have a recommendation

The eight ghosts. `site/_headers` now sets `no-cache, must-revalidate` on `/*/`, so nothing
new can join them — but **I do not know when the existing eight clear, and I am not going to
guess again.** What is measured: the oldest is 30 hours and the youngest 8, both still
climbing. What is documented: Cloudflare's default TTL for a 200 with no `cache-control` is
2 hours, which these have long passed, so the TTL in force is something else and not a
number I can read from outside.

So the honest position is that the expiry date is unknown, and the way to find out is to
watch rather than to predict.

Doing nothing is defensible: the director's ruling on the redirects was *"no one has ever
visited those URLs. There is no history to protect."* The traffic to them is my own checks
plus scanners.

**Recommendation: leave them, and let the hourly capture tell us when they clear** — the
ghosts appear in `docs/observability/edge_traffic.jsonl` as 200s on paths that no longer
exist, so the moment they stop is recorded without anyone remembering to look. The one thing
that would force them out is a zone Redirect Rule, and that means rebuilding the redirect
machinery the director deleted this morning, for URLs he ruled nobody visits. Acting
differently would need his word; not acting does not.

## Also outstanding, in the director's stated order

1. ~~The 504s~~ — retracted above.
2. **Re-run the absence-shaped verifications.** Now mechanised for
   `live_pixel_verify`; any claim made before today still needs redoing.
3. **Harness page content** — ships and renders real data; its written method account is
   thinner than the brief asks.
4. **PB3 growth path** — not started.

## Working mode, set by the director 2026-08-20

Act without checking in. Batch everything into one end-of-day report. Interrupt ONLY for
the four reserved classes: curriculum values, one-way doors, money, a real person. *"If you
find yourself waiting on me for anything else, that's a defect in how I've written the
rules — act, and tell me what rule needs changing."*
