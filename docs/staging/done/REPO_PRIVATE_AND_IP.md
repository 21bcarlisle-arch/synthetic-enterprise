> **H48 PARKED-DOCUMENT AUDIT, 2026-11-18 -- DIRECTOR.** The repo is PUBLIC (gh, today). Phase 1's quota blocker is fixed: the Pages trigger is now derived from `tools/pages_publish_manifest`. Phase 2 (the flip) is his click. Phase 3 needs the entity name and a crawler decision. Raised in `for_the_director` as `the-github-repository-is-still-public-gh`, with a recommendation.

> **STATUS (2026-07-11):** Phase 1 pre-flight audit run --
> docs/design/REPO_PRIVATE_AND_IP_PHASE1_FINDINGS.md. Verdict: NO-GO as
> measured (deploy cadence ~206% of the private-repo Actions quota,
> root-caused to github-pages.yml having no path filter). Recommended fix
> not yet applied -- awaiting Rich's call since it changes site-freshness
> cadence. Phase 2 (the actual visibility flip) is Rich's own manual click
> either way. Phase 3 (site IP assertion) blocked on entity name +
> crawler-block decision. Move to done/ once Phase 2 flip + Phase 3 land.

# REPO_PRIVATE_AND_IP — protect the IP, assert the copyright (P1)

**Fate (2026-10-12, clear-the-decks):** ATOM -- Phase 2 (visibility flip) and Phase 3 (IP assertion/entity name) are explicitly the director's own manual actions per the doc; cannot be verified from inside the checkout (P3)

**Staged:** 2026-07-11 by advisor, director-decided. **Rationale on record:**
trade-secret posture requires demonstrable confidentiality steps — the public
repo undermined any proprietary claim over method/code. Site stays public
(product face + track-record principle); repo goes private.

## Phase 1 — pre-flight (agent, before the flip; report findings)
1. **Actions minutes audit**: private repos meter Actions. Measure our deploy
   cadence x run-minutes vs the 2,000/month free quota; if at risk, batch
   deploys (change-detection gate already helps) or move the deploy step to
   the cheapest compliant path. State the projected monthly usage.
2. **Auth continuity**: verify agent push/pull, advisor PAT (Contents API),
   staging watchers, and the Cloudflare Pages deploy all function against a
   private repo (they should — all authenticated — but verify, don't assume).
3. **Link migration**: replace every github.io URL (NTFY snapshot links,
   docs, CLAUDE.md protocols) with poesys.net equivalents; the github.io
   mirror dies with the flip on the current plan. Sweep and fix.
4. Confirm nothing else assumes public (badges, raw.githubusercontent links,
   the comments box path, discovery-agent fetches of our own site).

## Phase 2 — the flip (director, ~30 seconds, after phase-1 ntfy says GO)
GitHub → repo Settings → Danger Zone → Change visibility → Private.
(Reversible instantly if anything breaks; agent monitors first deploy after.)

## Phase 3 — IP assertion layer on the site (agent)
1. Footer copyright notice site-wide: "© 2026 [ENTITY — director to supply:
   legal/trading name]. All rights reserved." — BLOCKED on the name.
2. Terms page: ownership of content/method/data outputs; no reproduction,
   scraping, or dataset extraction without written permission; third-party
   data attributions as their licences require (check and honour Elexon/ONS
   attribution terms explicitly — we have obligations, not just rights).
3. robots.txt: standard crawl allowed (public face wants indexing); AI-
   training crawler blocks (GPTBot etc.) = DIRECTOR'S CALL, ask via
   [ACTION NEEDED] with a one-line pro/con.
4. Add a NOTICE line to the (now private) repo README asserting
   proprietary status, and record this instruction as the confidentiality-
   measures evidence trail (dated) — that trail IS part of the legal value.
5. Advisor note, verbatim, on the terms page footer: this is assertion, not
   legal advice — a solicitor review is registered on the P-5 backlog for
   the director.

## DoD
Phase-1 findings ntfy'd with GO/NO-GO; post-flip: deploy verified live
(pixel), all links resolving, © + terms live site-wide, attribution
obligations met, README notice in, [ACTION NEEDED] sent for entity name +
crawler decision. One digest line per phase.

## Done

Closed 2026-11-19, unbuilt, on the director's ruling of the same day (chat, 14:07: "Repo public. Website
password"; advisor file `docs/staging/advisor/DIRECTOR_RULING_REPO_STAYS_PUBLIC_AND_THE_WEBSITE_GOES_BEHIND_A_LOGIN_2026-11-19.md`).

- Phase 2, the flip to private, will not happen. The repository stays public.
- Phase 3.1, the footer copyright, will not happen in a company's name, because Poesys is not a company. A notice in
  his own name would be his call, if he asks for one.
- Phase 3.4, the README proprietary notice, is dropped: a public repository cannot claim confidentiality.
- Phase 3.3: `site/robots.txt` now refuses search crawlers as well as the AI-training ones, and the Pages copy is
  served `X-Robots-Tag: noindex, nofollow`. That landed with the site-login ruling, recorded in
  `docs/staging/records/SEAT_RECORD_THE_SITE_LOGIN_WHAT_LANDED_AND_WHAT_STAYS_PUBLIC_2026-11-19.md`.
- Phase 1's quota finding is moot, since there is no private repository to meter.
- Its `for_the_director` row, `the-github-repository-is-still-public-gh`, is answered `no` with his words.
- The site login that replaced this plan is followed in that record and in row `the-site-login-you-ruled-on-19`.
