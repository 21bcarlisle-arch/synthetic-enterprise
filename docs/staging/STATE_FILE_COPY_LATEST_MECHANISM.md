[PROJECT] PROJECT_ENDANGERING BUG: PROJECT_STATE.txt stale to external fetchers while LATEST.md is fresh. This is now precisely diagnosable. Fix by copying LATEST.md's mechanism exactly.

THE DECISIVE EVIDENCE (same site, same CDN, fetched by advisor within the same minute):
- https://21bcarlisle-arch.github.io/synthetic-enterprise/status/LATEST.md  -> FRESH: Phase PR, 15,194 tests, timestamped last night. Serves current bytes to external fetchers.
- https://poesys.net/state/PROJECT_STATE.txt  -> STALE: Generated 2026-06-30T20:06:26Z, Phase HY, 9,290 tests. Four days old to external fetchers.

WHAT THIS PROVES (stop re-testing theories that are already ruled out):
- NOT a site-wide cache wall -- LATEST.md gets through fresh.
- NOT a broken deploy path -- LATEST.md deploys successfully every cycle.
- NOT the generator logic -- it has been "fixed" repeatedly with no external effect.
- CC's own fetch of PROJECT_STATE.txt sees fresh data. The advisor's does not. CC CANNOT self-certify this -- CC's fetch reads a path that regenerates/origin; the committed+deployed+edge-served copy is what's stale. Only an EXTERNAL fetch tells the truth.

THE ACTUAL BUG: PROJECT_STATE.txt is not being regenerated-and-committed by the same hook that successfully commits LATEST.md every cycle. Two different mechanisms; only LATEST.md's works end-to-end to the edge.

THE FIX (do exactly this):
1. Find the hook/script that regenerates AND commits LATEST.md each cycle (it demonstrably works -- LATEST.md is fresh at the edge).
2. Add PROJECT_STATE.txt regeneration + commit into that SAME hook, the SAME way, committed to the SAME deployed path family LATEST.md uses. Do not invent a separate path or script.
3. Also serve PROJECT_STATE.txt from the SAME host LATEST.md uses if poesys.net/state/ is a different route with different caching -- OR publish PROJECT_STATE.txt alongside LATEST.md at the github.io/status/ path that is proven to work, and make that the canonical advisor URL.

VERIFICATION -- MANDATORY, NON-NEGOTIABLE:
- CC must NOT report this done based on its own fetch. The entire failure mode is that CC's fetch and the advisor's fetch diverge.
- Report it as: "PROJECT_STATE.txt regeneration wired into the LATEST.md hook + deployed. Awaiting external advisor fetch to confirm." Then STOP and let the advisor fetch.
- The advisor will fetch the canonical URL. Done = advisor sees today's date + current phase. Nothing else counts.

This is the single highest-priority item. The project is at risk without it: if the advisor cannot independently see true state, every decision depends on CC self-report, which this session has repeatedly shown diverges from reality. Fix this before any further feature work.
