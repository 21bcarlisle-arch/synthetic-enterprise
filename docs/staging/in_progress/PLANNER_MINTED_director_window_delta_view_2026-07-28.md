<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: director_level_up -- director-window delta view; level move director-reserved (R16, no self-bump) -->
# [PLANNER-MINTED] — Director-window delta view (SPEC_005 §7.10 / Spec-005 §3) — SITE-lane (2026-07-28)

> **BUILT 2026-07-28: "Since you last looked" delta panel LIVE on `site/director/index.html`.**
> Client-only (localStorage `poesys_director_delta_v1` last-seen marker) over the already-published feeds
> (`decisions.json`, `director_reserved.json`, `agent_status.json`) — N new decisions / M reserved-queue changes /
> K daemons flipped STALE. NO new auth affordance (surface-5 ruling honoured). R11+R15 proven BOTH ways in
> `site/director/test_director_door.py` (mutation neutering the persistence → test REDS; restored → GREEN;
> honest-empty renders "nothing changed", not a fail-open blank). Full site suite green (357 passed, 7 skipped);
> site-lane gate rc=0. Marker flipped self-drawable→blocked; **`blocked_on: director_level_up`** (R16 — no self-bump).
>
> **STATUS 2026-07-28 (RUNG-7 planner mint): self-drawable NOW — SITE lane (L3, parallel-drawable).**
> Scope and build the "what changed since I last looked" delta view on the director window
> (`site/director/index.html`), a feature CONSCIOUSLY DEFERRED at the surface-5 close (2026-07-23:
> *"The deferred Spec-005 §3 delta-view / DO battery / stop control are NOT built and are named as
> deferred on-page"*) and now ranked back in as backlog by the published-gaps ruling.

**Source:** `docs/design/FIRST_RANKED_GAP_LIST.md` §2 machinery row **M3** ("Public challenge channel §7.8 +
**delta view §7.10**") + `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` §1 mint-source
*"registered follow-ons from prior steers"* (the surface-5 on-page deferral is exactly such a follow-on).
Note: the **challenge-channel half of M3 is already covered** (surface-4 Proof landed the server-side-checked
director-comments challenge channel) — this mint takes ONLY the un-covered delta-view half.

**Provenance:** RUNG-7 planner mint (autonomous — SITE lane is permanently parallel-drawable per THREE_LANES
L2; `mint` direction needs no ratification). grep-confirmed no existing `PLANNER_MINTED_*`/atom named
`delta_view`. Non-duplicate: the DO battery and stop control from the same surface-5 deferral are handled
elsewhere (stop control = its own mint this tick; DO battery remains deferred).

**Serves:** DIRECTOR_AXES **axis-1 Website** — *"Usefulness to him as an operational window — can he open the
site and understand the state of the company without asking."* A delta view ("since your last visit: N new
decisions, M reserved-queue items, K daemons flipped STALE") is the single highest-leverage upgrade to that
axis: it answers *what do I need to look at* without reading the whole window.

**Fidelity gained (one sentence):** no model change — an **operator-legibility** feature that makes the
director window answer "what changed" at a glance, directly moving the top ratified axis (site usefulness as
an operational window).

## Exit criterion
The director window renders a delta panel from published primary state (a last-seen marker + the live feeds
already on the page: `decisions.json`, `director_reserved.json`, `agent_status.json`), R11+R15-proven by the
site render harness (execute the page's real JS against published JSON; a mutation that changes a feed since
last-seen must flip the delta pixel; an empty/unchanged delta must render honestly, not fail-open). Full
site-lane gate green; Expert-Hour (phase-close-evaluator / cold-eyes-walk) PASS against the single job.

## Propose-then-proceed window
PROCEED autonomously — SITE lane (`site/**`, disjoint file_scope), reversible, no wall touched. The delta is a
read-only presentation over existing feeds; add NO new authenticated affordance (auth stays exactly as
surface-5 ruled — off-nav + noindex + the server-side comment box; a client-side gate is R15 theatre). If the
delta implies a new server/backend read-gate, that is the director's separate call — flag it, do not build it.

## Walls untouched
No new auth/safety surface (surface-5 auth ruling honoured). R16 (no level self-bump — land at L2/L3 quality,
leave `blocked_on: director_level_up`). R12 (the delta counts are a diagnostic, never a headline metric).
