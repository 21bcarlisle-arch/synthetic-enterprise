# Campaign A — cross-door honesty audit (finding + queued debt)

**Date:** 2026-07-18 · **Lane:** SITE (product) · **Provenance:** director console ruling
2026-07-18 ("Campaign A — site rebuild per the reconciled site specs"). Audit run by a
scoped `site/**` fork; verified + landed by the orchestrator.

## What was checked
Every public door's static HTML scanned (visible text nodes outside `<script>`/`<style>`)
for hardcoded metric literals, nav integrity, evidence links, and passport terms, against
the live `site/data/*.json`. Rules from `docs/design/SITE_CONSTITUTION.md`:
R1 claim→evidence · R2 number-passport (basis + freshness + PROVISIONAL) · R3 render-not-author
(values from `site/data`, nothing hardcoded) · R4 honesty featured · R5 progressive disclosure.

## Result — 5 of 7 doors clean, verified with evidence
| Door | Verdict | Evidence |
|---|---|---|
| Home `index.html` | **PASS** | 0 hardcoded metric figures; `PROVISIONAL` badges + basis/settled/billed/banked + `generated` stamp from `dashboard.meta.generated_at`; dual-ledger gap featured |
| Company | **PASS** | 6 evidence links; 17 billed / 15 settled / 6 provisional terms rendered; 0 hardcoded; 5 render fns off `company.json` |
| World | **PASS** | 6 links; `basis`/`generated_at`; R12 "diagnostic not verdict" band; 0 hardcoded |
| Proof | **PASS** | 6 links; banked/basis/generated_at/provisional; 0 hardcoded; open-work + kill-list + retros featured |
| Method | **PASS** | 6 links; basis/freshness/generated_at; 0 hardcoded; renders `method.json`+`activity_cost.json` |
| **Journey** `project/` | **PARTIAL** | JS sections all data-driven + passported, BUT the **Regulatory tab is fully static HTML** (debt A below) + Key Discoveries prose has unlinked figures (debt B) |
| Simplified | **PASS (minor)** | qualitative register from `simplified.json`, 0 hardcoded; no financial figures; **register lacks its own freshness stamp** (debt C) |

**Nav (all 7):** canonical `Home/Company/World/Proof/Method/Journey/Simplified` present on every
door; **Director absent from every public nav** (auth-gated). Verified programmatically.

This VERIFIES (not merely asserts) the standing claim that the JS-rendered doors comply with
rule 3 — the audit found zero hardcoded metric figures on the five, with evidence.

## Landed this pass
- **Journey door test gap CLOSED** — `site/project/test_project_door.py` + `_render_harness.mjs`
  (11 tests: R11 render-tracks-source, R15 3× mutation-independence, canonical-nav-present +
  Director-absent, ≥1 claim→evidence). Commit on origin (`de1e9aef9`). Every other public door
  had a render test; Journey was the only gap — now closed.
- **Proof-panel 8th-pair regression fixed** — the W2_11↔D5 payment coupling (director-authorized,
  wired earlier this session) took the coupled-gaps panel to 8 pairs; `site/proof/test_coupled_gaps_panel.py`
  still asserted 7. Fixed to track the live pair count (was red on the Proof door; missed because
  `site/**` tests are outside the publish gate's `tests/` scope — a coverage seam noted below).

## Queued debt (next Campaign A increments — NOT hand-patched, per DON'T-ACCRETE + R10)
**A — Journey Regulatory tab data backing (`site/project/index.html` ~lines 298–324).**
Entirely static HTML. The published levy **rates + legal basis** are defensible commons
(regulation-commons doctrine) and cite their basis — keep. But the **build-status claims are
unbacked company metrics that can silently drift**: "62 regulatory modules wired" (line 298),
"10 SLC domains" (SLC row), "90% HH portfolio = GREEN RAG" (settlement row), and every
`WIRED/EXEMPT/NEXT` badge. Proper fix (rule 3 + R14 freshness): a `regulatory.json` generator
emitting scheme statuses + the module count + a freshness stamp, then convert the tab to a render.
Partial seed already exists — `dashboard.json.regulatory` carries `obligations` (SLC codes +
domain + RAG), `overall_rag`, `latest_year` — enough to back the SLC scorecard row + overall RAG;
the scheme table (RO/FiT/CCL/…) needs its own status source. Sized: fork-scale build, not inline.

**B — Journey Key Discoveries (~lines 136–158).** Narrative figures without per-claim R1/R2:
hedge cover `0.80–0.90`, `~30 real UK suppliers`, avg `£3,549`, `3–4%` switching. Add evidence
links / passports or render from data.

**C — Simplified door (minor R2).** The honesty register shows no `generated_at`/freshness stamp
for itself. Add one.

**D — Home + Proof lack a full `test_*_door.py`** (Proof has only panel-specific tests). Parity
gap for two canonical doors; add render tests mirroring the others.

**E — Coverage seam (meta).** `site/**` tests are NOT in the publish gate (`pytest tests/ …`), so a
red site-door test does not wedge the gate and can go unnoticed (how the 8th-pair regression above
slipped). Options: add `site/` to a site-lane CI check, or a lightweight pre-push site-test run.
Queued as a harness finding; now FRAMED (build-ready design: `docs/design/SITE_TEST_COVERAGE_SEAM_FRAME.md`, recommended mechanism B+C, R15-failable) — off-front, opens on a harness front / director BUILD_OPEN.
