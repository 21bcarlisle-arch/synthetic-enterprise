# [IN PROGRESS] Site campaign continuation — WORDS → DIAGRAM → EVIDENCE + financials reframe + R11 link integrity (2026-07-23)

**BLOCKING OPEN SUB-ITEM (why this is parked here, not the scanned root):** §A — the
canonical-door decision (which SITE_V5 doors survive vs fold/redirect) is
director-pixel-gated (ruling #3 requires the master diagram back as pixels before
nav adoption). §B/§C/§D below cannot land canonically until §A resolves the
`/method`-vs-`_redirects` contradiction. This file consolidates three overlapping
director rulings into one running campaign; do NOT re-scan the sources as new work.

**Consolidates three staged rulings (moved alongside this file):**
- `DIRECTOR_RULING_WORDS_DIAGRAM_EVIDENCE_2026-07-23.md`
- `DIRECTOR_RULING_SITE_MODEL_SPINE_2026-07-23.md`  (near-duplicate of the above)
- `DIRECTOR_ADDENDUM_MODEL_ON_A_PAGE_DIAGRAM_2026-07-23.md`  (the diagram asset)

**Campaign framing (director):** "a bit better" — progress acknowledged, structure of
information still wrong. These REFINE the running SITE_V5 campaign; they do not
restart it. Rung-1 publish-gate rule + claim==pixel (R11) discipline apply.

---

## Context — the publish-gate wedge is CLEARED (unblocks consumption)
The addendum explicitly gated all of this BEHIND the live publish-gate wedge
("the wedge is the crisis; this is content"). Verified cleared this tick: HEAD
`92ae6cc04` and its parent `1a29fe3b0` are both successful auto-process completions
past the failure lineage (last gate failure was `eb94267b1`; both subsequent
commits processed green). So the campaign may now proceed.

## DONE this tick — R11 link-walk DIAGNOSTIC (serves rulings #2/#3)
- `site/link_walk.py` — crawls every internal page-nav href across all doors,
  classifies each as OK / DEAD / REDIRECTED (points at a `_redirects` SOURCE = a
  legacy/backward link). Complements `test_evidence_links_resolve.py` (which covers
  data/state JSON links; this covers page-to-page nav, which it does not).
- `site/test_link_walk.py` — R15 mechanism self-test (synthetic fixtures): proves
  the walker fires on a dead link AND on a redirect-source link, and stays silent
  on a clean tree. Passes green regardless of the live findings → does NOT wedge.
- **Finding (authoritative, reproducible via `python3 site/link_walk.py`):**
  **22 non-canonical internal links, 0 dead.** ALL 22 point at SITE_V5 legacy
  redirect-sources — `/method` (incl. the FRONT DOOR `index.html → ./method/` and
  `../method/#track-record`), `/project`, `/simplified` — from pages: index (home),
  customers, glossary, now, wip-flow, and the legacy doors themselves (method,
  simplified, project, tours). This is exactly the director's complaint made
  precise: "links route back to legacy versions/formats."

## THE BLOCKING CONTRADICTION (surfaced by the diagnostic — needs §A)
`/method`, `/simplified`, `/project`, `/tours` are SIMULTANEOUSLY:
  (a) live nav doors the front door links AND that `test_nav_story_platform_method_rq`
      REQUIRES reachable (Method reachability was *restored* this morning at
      `dd45de549` precisely to un-wedge that gate); and
  (b) redirect SOURCES in `site/_redirects` (SITE_V5 block: `/method → /proof/ 301`).
"Canonical" is therefore undefined until the IA cutover decides which doors survive.
**Fixing the 22 links or gating the walk NOW would either be wrong (if /method is
canonical) or re-wedge the just-cleared gate (if it is not).** Do not act on the
link findings before §A.

---

## OPEN sub-items (sequenced)

### §A — WORDS → DIAGRAM → EVIDENCE IA decision  [BLOCKS §D; director-pixel-gated]
Derive the master diagram from `docs/design/THE_MODEL_ON_A_PAGE.md` (world → wall →
company → score; actual-vs-forecast weather; prices/demand; tariffs/hedging; three
clocks; carbon). Decide the CANONICAL DOOR SET — which doors survive, which fold to
redirects — resolving the `/method` contradiction above. Per ruling #3 the rendered
diagram returns to the director as pixels ([ACT]) BEFORE it becomes the nav spine.
The v4 SVG (see §B) is the approved content; the NAV-SPINE adoption is the gated part.

### §B — Embed the director-APPROVED model-on-a-page diagram (F-MOAP-1)  [LANDED 2026-07-23 tick]
**DONE this tick.** Hosted ONCE on the front-door fold (`site/index.html`, new `.moap` section
placed as the bridge from the thesis into "Three ways in" — the diagram's world→company→score maps
onto the three doors). Form shipped: **native SVG asset** `site/assets/model-on-a-page.svg`
(byte-identical to the approved v4, sha `be3c407044…f7cd0f`), referenced as `<img>` scaled to the
column (`width:100%`) — crisp on mobile, no HTML bloat, glyph grammar + BRAG colour preserved intact.
Real alt text (names governance/world/wall/company/score). R11 (published-tree pixel: `<img>` present
+ asset resolves) and R15 (guard fails when the asset is hidden) proven by
`site/test_home_door.py::test_model_on_a_page_diagram_hosted_and_resolves`; full front-door lane green
(70 passed). **Live-site pixel verify (R11 on poesys.net, mobile viewport) is POST-DEPLOY** — the
change is committed, not yet published; verify on the next auto-process publish. No /simplified door
resurrected. **F-MOAP-2 registered** on `THE_MODEL_ON_A_PAGE.md` (wall made two-way; bills OUTBOUND;
inbound observable = the payment/complaint answering a bill; settlement-late a first-class inbound gate).
"lives rerun across worlds" chip left as director-approved (asset is sha-pinned, 4 rounds approved;
softening an approved pixel is riskier than leaving it — my call, not escalated). §A/§C/§D still open.

<details><summary>original §B brief</summary>
Asset: `docs/staging/assets/poesys_model_on_a_page_v4.svg`
(SHA-256 `be3c407044fc28799a1419a415ca55bb915493bd3e7c9c5b81d74b0049f7cd0f`) — already
director-approved (four rounds). Host: front-door fold on the next surface-1
iteration, ONE host, no resurrected /simplified door (director saw & did not override
this default). Implementation free: embed as-is or rebuild responsive per
`BRAND_CONSTITUTION.md` (SVG is fixed 880-wide portrait — native likely better on
mobile); BRAG semantics + glyph grammar (`.` `_` `~`) are information, keep them.
Alt text required. **Verify R11-to-pixel on the LIVE site (mobile viewport too);
NTFY which form shipped.** Register findings: **F-MOAP-2** on `THE_MODEL_ON_A_PAGE.md`
— the wall is TWO-WAY and bills are OUTBOUND (amend the canon's wall sentence when
touched: inbound observable is the payment/complaint answering a bill, never the
bill; settlement-late is a first-class inbound gate). Borderline "lives rerun across
worlds" chip: soften to "designed to rerun" if the claim-status rubric reads it as
present-tense TF2 (my call, do not escalate).
</details>

### §C — Financials reframe (RC6): unit economics, never bare totals  [COMPANY DOOR LANDED 2026-07-23 tick; /now + /project OPEN]
**DONE this tick — The Company finance panel (`site/company/index.html::renderFinance`).**
The director's exact complaint ("totals from a random sample of customers") made concrete: the
book is a **drawn sample of N=19 customers** (from `company.json::stress_bands.total`, the same
sample the totals are earned by), now STATED on the panel with the draw ("curriculum-weighted
historical replay, 2016–2025"). The grid now **leads with unit economics** — Net margin/customer
(£26,909.56, 2025) and Revenue/customer (£67,578.98, 2025), each with its **denominator stated
inline** (`÷ 19 sampled customers`, same clock/year — no hidden division) — plus the Collection
rate (a book-size-invariant RATE). Every cumulative total is **demoted and caveated** (`10-yr
cumulative · scales with drawn book`), with a small-print footnote: totals "scale with the book and
are not meaningful in isolation." R11 render (against live `company.json`) + R15 failable tests in
`site/company/test_company_door.py` (per-customer value+denominator FOLLOW N — a hardcoded ratio
FAILS; totals carry the caveat) — 13 pass; full site suite 274 pass. `finance-unit-note` added to
the render harness whitelist so it is R11-observable. **Live-site pixel verify (poesys.net, mobile)
is POST-DEPLOY** — committed, not yet published; confirm on the next auto-process publish.
**STILL OPEN:** the same reframe on **/now panel 2** and **/project (investor summary)**; plus
cost-to-serve/arrears £-per-customer and DISTRIBUTIONS across coverage cells (needs the generator to
emit an authoritative per-customer denominator + distribution — company.json currently carries only
the aggregate N; a follow-on data-plumbing step, logged here not faked).

<details><summary>original §C brief</summary>
Convert every financial surface to £-per-customer (margin, cost-to-serve, arrears),
RATES (collection %, hedge cover, complaint rate), DISTRIBUTIONS across coverage
cells, £/tCO₂e when instrumented — with **N and the draw stated on every panel**
("this run's cohort: N=…, curriculum-weighted"). Totals appear only as small-print
footnotes marked "scales with drawn book; not meaningful in isolation." Belief-vs-truth
gaps are first-class financial exhibits. Apply across /company, /now panel 2, /project
(investor summary). Director verbatim: "I don't take financials as useful at all.
Certainly not totals from a random sample of customers."
</details>

### §D — Fix the 22 links + flip link_walk into a GATING test  [BLOCKED on §A]
Once §A fixes the canonical door set: correct the 22 non-canonical links to point at
their canonical targets, then convert `link_walk.classify()` into a gating assertion
(zero DEAD, zero REDIRECTED) wired into BOTH the publish-gate content set AND the
site-lane pre-commit set (per the parked UNWEDGE §3 class fix: a nav/link invariant
must be in the site-lane pre-commit subset so a site edit cannot green-locally-but-
wedge-publish). R15 mutation-proof both directions (the self-test already locks the
mechanism). Then it is the director's R11 "publish fails on any non-canonical link."

---
**Sequencing / risk:** presentation + IA within ratified structure; no sim/company/saas
code. Do NOT consume §B/§C ahead of a green publish gate, and do NOT act on §D before §A.
— Worker tick, 2026-07-23, carrying the director's round-2 site verdicts.
