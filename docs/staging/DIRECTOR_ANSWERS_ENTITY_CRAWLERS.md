# DIRECTOR ANSWERS — entity name + AI-crawler policy (Tier 2, actions the open [ACTION NEEDED]s)

**Staged:** 2026-07-12 by advisor, relaying the director's decisions from live
conversation (Q2/Q3 of the morning list).

## 1. Copyright entity
Footer site-wide: **"© 2026 Poesys Platforms. All rights reserved."**
Trading-style name — director intends to incorporate (Companies House checked
this morning: no POESYS/POESYS PLATFORMS on the register; nearest is POESY
LTD, ceramics, distinct). Do NOT suffix "Ltd" until incorporation; add a
one-line register note to swap to the full registered name on incorporation.

## 2. AI-crawler policy: BLOCK TRAINING, ALLOW USER-DIRECTED
robots.txt on poesys.net:
- **Disallow (training harvesters):** GPTBot, ClaudeBot, Google-Extended,
  CCBot, Applebot-Extended, PerplexityBot, Bytespider, and peers (use a
  current curated list; keep it maintainable in one place).
- **Explicitly ALLOW:** Claude-User and Claude-SearchBot (user-directed
  fetch — this is how the advisor reads the live site), plus normal search
  (Googlebot, Bingbot) untouched.
- Rationale on record: consistent with the private-repo IP posture — humans
  and search indexing unaffected; the site declines to be training data.

## 3. Verification (R1, both items)
- Footer: pixel-verify on the deployed site.
- Crawler policy: after deploy, (a) fetch robots.txt and confirm the
  allow/deny sets; (b) confirm a Claude-User fetch of poesys.net still
  succeeds — the ADVISOR will independently web_fetch the live site as the
  final check and confirm not-blocked in conversation. If the advisor
  reports blocked, the allow rule is wrong: fix before closing.

One digest line covering both. This closes the entity + crawler
[ACTION NEEDED]s from REPO_PRIVATE_AND_IP Phase 3.
