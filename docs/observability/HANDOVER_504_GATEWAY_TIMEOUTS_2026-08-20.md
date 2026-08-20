**Severity:** BLOCKING · **Lane:** H_harness · **Status:** RESOLVED — and the headline below is WRONG

> ## RETRACTED, 2026-08-20 15:30Z. Read this box before anything else in the file.
>
> **poesys.net was never returning 504s to visitors. No reader has seen one.** Cloudflare's
> analytics logs every HTTP/2 request to this zone **twice**: once truthfully, and once as a
> phantom row with status `504` and protocol `UNK`. Thirty parallel requests that all
> returned 404 in under a second produced thirty real rows *and* thirty phantom 504s; twenty
> `--http1.1` requests produced zero phantoms. In 24 hours, the count of 5xx rows carrying a
> real HTTP protocol is **zero** — all 419 are `UNK`, i.e. requests Cloudflare never parsed,
> because they were never requests.
>
> Everything below that reasons about *why the origin is slow* is reasoning about a
> measurement artefact. Kept verbatim, not tidied, because the sequence of four wrong
> theories is the useful part of the record.
>
> **The section below headed BREAKTHROUGH is also wrong** — see the second retraction there.
>
> What IS real, found underneath it: eight deleted pages are still being served `200` to
> readers. Current document:
> `docs/staging/WORKER_FINDING_EIGHT_DELETED_PAGES_ARE_STILL_SERVED_TO_READERS_2026-08-20.md`.

# Handover: poesys.net is returning 504s to real visitors

Written at the end of the 2026-08-20 session, at the director's instruction, so the next
session starts from evidence rather than from scratch. **Nothing here is fixed.**

---

## The finding, in one line

**29% of all requests to poesys.net returned 504 Gateway Timeout in the 24h to 2026-08-20
14:00Z** — 416 of 1,442 — and the rate roughly quadrupled across the day.

It was found by accident, while pulling analytics to answer a different question. Nothing in
this repo was watching for it, and nothing alarmed.

## What is ESTABLISHED (measured, not inferred)

**1. It hits HTML pages only. Never static assets.**

| path | requests | 504s |
|---|---|---|
| `/proof/` | 190 | 94 |
| `/` | 182 | 56 |
| `/knowledge/` | 97 | 45 |
| `/explore/` | 77 | 30 |
| `/capabilities/` | 74 | 37 |
| `/harness/` | 62 | 26 |
| `/world/` | 49 | 28 |
| **every `/data/*.json`** | 22–43 each | **0** |

Zero timeouts across every JSON asset. Whatever is slow is in the path that *routes* a
directory request, not in serving bytes.

**2. It is getting worse.** Hourly 504 rate, 2026-08-19 13:00Z → 2026-08-20 14:00Z:

```
19T13 12%   19T17 23%   19T21 28%   20T04 31%   20T08 37%   20T12 47%
19T15 21%   19T18 28%   19T23 26%   20T06 37%   20T10 45%   20T14 40%
19T16 28%   19T19 11%   20T01 20%   20T07 40%   20T11 14%
```

**3. It reaches real, external visitors — this is NOT an artefact of local curl traffic.**
An earlier reading of mine ("399 of 459 from LHR, so it's this machine") was **wrong** and is
corrected here. Timeouts also came from **SOF (49), ORD (3), MCI (2), VIE (1), AMS (2),
GRU (2)**. One GRU 504 was a Brazilian visitor on `/knowledge/electricity-wholesale/`.

**4. It predates the 2026-08-20 changes.** Already 12–28% on the afternoon of 08-19, before
`site/_headers` or `site/_redirects` were touched. Neither today's `/*/ ` cache rule nor the
redirect deletion caused it.

**5. It is not reproducible on demand.** Twelve consecutive HTML requests: 12 × 200, all under
300ms, TTFB ~0.11–0.26s. Intermittent under some load or timing condition not yet identified.

**6. IT EXPLAINS THE STALE PAGES.** Eight deleted pages (`/proof/`, `/world/`, `/company/`,
`/customers/`, `/now/`, `/glossary/`, `/director/`, `/evidence/`) were still being served 200 at
the edge while origin returned 404. Cause: **when the origin times out, Cloudflare serves
last-known-good.** Hence an `age` that climbs instead of resetting, immunity to `purge_everything`,
and `cf-cache-status: DYNAMIC` throughout. The stale pages are a SYMPTOM. Do not chase them
separately.

## What was RULED OUT (each checked, not assumed)

| ruled out | how |
|---|---|
| zone cache | `purge_everything` AND a targeted 24-URL purge, both `success:true`; `age` kept climbing (20560 → 20694) instead of resetting |
| `site/_headers` cache rule | 504s predate it; and it is correct now (`/*.html` never matched `/proof/`, `/*/ ` does) |
| `site/_redirects` | 504s predate the deletion and got worse after it |
| Page Rules | none exist |
| Cache Rules / rulesets | only the two managed ones (normalization, managed WAF) |
| Worker routes | none on the zone |
| Always Online | `off` |
| Development mode | `off` |
| Pages Functions | only `functions/api/query.js`, and `functions/` is **outside** the deployed `site/` directory, so it is not deployed at all |
| wrong/multiple Pages project | one project, `poesys-net` |
| stale deployment | canonical = latest = `29c4889f`; **all six recent deployments return 404 for `/proof/` on their own `*.pages.dev` URL**, including the live one |
| per-deployment domain pinning | none; `poesys.net` domain record active, `validation_data: active` |
| DNS misdirection | single proxied CNAME `poesys.net → poesys-net.pages.dev` (read only; nothing changed) |

## WHERE TO LOOK FIRST, and why

**1. `_routes.json` / the Pages routing manifest.** The signature — routed HTML slow, direct
assets never — points at whatever resolves a directory request to an asset. Check whether the
deployment carries a `_routes.json`, what it includes/excludes, and whether the asset manifest
has grown large enough to matter. `site/` was carrying ~35 pages and ~47 data files before
today's fold; it is now 15 pages.

**2. Deployment count.** The project has a long deployment history (every publish cycle creates
one). Worth checking whether an accumulating deployment list degrades custom-domain routing.

**3. Ask Cloudflare's own docs MCP** — `mcp__plugin_cloudflare_cloudflare-docs__search_cloudflare_documentation`
is authenticated and free to use. Query for Pages custom-domain 504s and asset-routing latency
before theorising further. **Three theories have already been wrong today** (cache headers, zone
purge, local-curl-only); the fourth should be checked against documentation first.

**4. `cloudflare-builds` MCP is installed but NOT yet authenticated.** It would show build and
deployment timing. Authenticating it is one OAuth round-trip and may be the fastest route to
whether deploys correlate with the timeout spikes.

## THE ABSENCE-VERSUS-STALENESS RULE

The director's framing, and it now governs every live check in this project:

> When the origin times out, the edge serves last-known-good. A stale copy can only ever be
> **older**, never newer.

Therefore:

- **A live check that OBSERVED NEW CONTENT still holds.** The five nav doors at 360px, the
  six-URL sitemap, Harness rendering "What we know is wrong", Explore's stage spine — a stale
  copy cannot contain something that did not exist when it was cached. These are sound.
- **A live check that concluded something was ABSENT, REMOVED, or UNCHANGED is UNSAFE.** Absence
  and staleness are indistinguishable through a timing-out origin. My claim of 2026-08-20 that
  "every retired URL lands somewhere real" fell into exactly this class and was wrong within
  hours.
- **The fix for an absence check is a cache-buster.** `?cb=<nonce>` returned the true 404 every
  time while the bare path returned a stale 200. That one technique isolated the whole problem.

**Re-verify after the 504s are fixed**, and only the absence-shaped claims need redoing.

## Ongoing visibility — built, blocked on one credential

Cloudflare's Free plan **refuses any analytics query wider than one day**:

    zone "f8261..." cannot request a time range wider than 1d, but your query time range spans 4w2d

So this shape exists for 24 hours and then does not. `tools/edge_traffic_capture.py` is written
and ready: it snapshots hour × path × status × colo into `docs/observability/edge_traffic.jsonl`,
deduplicates by key so re-runs cannot double-count a partial hour, and **exits non-zero on
failure** rather than writing an empty capture that reads as a quiet site.

**It needs `CLOUDFLARE_API_TOKEN` with Zone → Analytics → Read on poesys.net and nothing else.**
The director is minting it. The MCP grant is an OAuth session held by the interactive agent; an
unattended run has no access to it. Once the token exists, wire the collector into the tick — it
is cheap and the window is short, so run it often.

## Cloudflare access, and the one wall

Granted by the director 2026-08-20; recorded in
`docs/design/CLOUDFLARE_CAPABILITY_GRANT_2026-08-20.md`.

- **Free to use:** cache purge, analytics, build and deployment reads.
- **RESERVED — his word, every time: any DNS change.** `cloudflare-api` *can* change DNS. Nothing
  in this repo enforces the wall; it is prose honoured, not a capability lacked. Say so plainly
  rather than implying a mechanism exists.
- Zone id `f8261ea75d95ecb93867e7318f57766d` is discoverable via `GET /zones` — **do not add a
  `CLOUDFLARE_ZONE_ID` secret**, look it up. An empty secret is exactly how the deploy purge
  failed silently for its whole life.

## Also outstanding

- **Harness page content** — the page ships and renders real data, but its own written content
  (the method account) is thinner than the brief asks.
- **PB3 growth path** — not started.
- **The deploy purge step** now exits non-zero on failure (was printing `Purge FAILED` and
  exiting 0). It will RED the deploy until the zone id is resolved. That is the correct failure.
- **`docs/design/CLOUDFLARE_CAPABILITY_GRANT_2026-08-20.md`** and
  `tools/edge_traffic_capture.py` are uncommitted at handover.

---

## BREAKTHROUGH, 2026-08-20 15:40Z — measured against the capture, not guessed

**`_routes.json` and asset count are BOTH RULED OUT.** There is no `site/_routes.json`, and the
deployment is 219 files / 20 MB — far too small for manifest size to matter.

**The real pattern, from `docs/observability/edge_traffic.jsonl` (829 rows):**

> **Every path that has ever returned 504 is EXTENSIONLESS. Every path with a file extension
> has zero 504s.**

| 504s | never 504 (≥5 reqs) |
|---|---|
| `/proof/` 85, `/` 61, `/knowledge/` 53, `/capabilities/` 37, `/explore/` 30, `/world/` 27, `/harness/` 26 | `/data/*.json` (all of them), `/robots.txt` 28, `/favicon.svg` 28, `/brand/brand.css` 16, `/brand/tokens.css` 16, `/sitemap.xml` 17, `/wp-admin/install.php` 24 |
| …and `/Dockerfile`, `/Procfile`, `/graphql`, `/server-status`, `/actuator/health`, `/.ssh/id_dsa`, `/.env.production` — **bot probes for paths that never existed** | |

**The decisive observation: `/never-existed-xyz/` and `/definitely-not-a-page/` — my own test
requests for paths that have never existed — BOTH 504'd.** The timeout therefore has nothing to
do with serving content. It happens when a request **cannot be matched directly to a static
asset** and falls into Pages' path-resolution fallback (directory → `index.html`, or
missing → `404.html`).

Direct file hits never enter that path and never time out. Bot probes with extensions
(`/wp-admin/install.php`, 24 requests) never time out; bot probes without one always can.

**This reframes the whole incident.** It is not "the site is slow". It is: *the fallback that
resolves a path when it is not a literal file is intermittently hanging* — and every real page
on this site is reached through exactly that fallback, because every page is a directory URL.

### Where to look next, in order

1. **`site/404.html` served live returns HTTP 308 with 0 bytes**, while the file is a healthy
   961 bytes in the repo and in every deployment. A 308 on the fallback document is the single
   most suspicious thing found. Cloudflare's managed **Normalization Ruleset** (`http_request_sanitize`,
   confirmed present on the zone) is the likeliest source. If the 404 fallback redirects instead
   of serving, the resolution path may loop or stall — which would explain both the timeouts and
   their intermittency.
2. Re-check `site/_headers`. The `/*/ ` rule added 2026-08-20 matches directory URLs — exactly
   the set that 504s. **Note the trend was already 12–28% before that rule existed**, so it
   cannot be the cause, but it may compound it. Testing with it removed is cheap.
3. `cloudflare-builds` MCP is installed but **not authenticated** — one OAuth round-trip. It
   would show whether deploys correlate with the spikes.

### Confidence

The extensionless/extension split is **not a theory** — it is the observed partition of 829 rows
with no counter-example among high-volume paths. The 404.html-308 lead IS a theory, and the
fourth of the day; three have already been wrong. Test it before acting on it.

---

## SECOND RETRACTION, 2026-08-20 15:30Z — the breakthrough above is wrong too

Both halves of it.

**The extensionless partition was sampling, not structure.** It held across 829 rows and broke
at 1,442: `/swagger-ui.html`, `/actuator/health`, `/id_rsa`, `/.env.example` and
`/.git/packed-refs` all carry extensions and all appear as 504s. They come from one scanner in
SOF whose HTTP/2 probes get phantom rows like everyone else's traffic. What looked like a
partition was really "the high-volume paths on this site are all directory URLs, and the
low-volume ones are assets" — a fact about the site, restated.

I called it "not a theory — the observed partition, with no counter-example". It had a
counter-example; the capture was just too small to contain it. **An observed partition is still
a theory about the next observation.** That sentence is the one to remember from this file.

**The `404.html` → 308 lead was nothing.** Pages strips `.html` and redirects `/404.html` to
`/404`. Every Pages site does it. It was suspicious only because I was looking for something
suspicious.

**What actually settled it** was giving up on mechanisms and asking what the 504 rows had in
common with each other rather than with my theories. The answer was in a field I had not
queried: `clientRequestHTTPProtocol: UNK` on all of them, and on nothing else. Four theories
died to one extra dimension in a GraphQL query.

**Method note, and it is the reason this file is worth keeping.** Every wrong theory here was
about a *mechanism inside Cloudflare* — cache layers, routing manifests, redirect loops. The
right answer was about *the instrument*. When four mechanism theories die in a row, stop
proposing a fifth and go and check whether the measurement means what you think it means.
