# REPO_PRIVATE_AND_IP — protect the IP, assert the copyright (P1)

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
