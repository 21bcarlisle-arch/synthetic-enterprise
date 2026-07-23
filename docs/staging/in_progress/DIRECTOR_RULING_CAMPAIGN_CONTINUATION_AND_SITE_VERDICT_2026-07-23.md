# [CC PROCESSING STATUS -- 2026-07-23] IN PROGRESS (part 2 ABSORBED; parts 1 & 3 OPEN)
#
# PART 2 (SEVENTH CLASS -- campaign continuation) is ABSORBED, not merely consumed: the open-campaign
# draw rung is LIVE + R15-proven (commit 321f34dff). supervisor.py::_open_campaign_draw reads
# docs/design/CAMPAIGN_REGISTER.yaml and forbids rest while any OPEN campaign has an unfinished item;
# wired into _self_refill_draw (above backlog), _is_drained_and_gated, and authorized_set_enumeration
# (7th level 'open_campaign'). Test: tests/background/test_open_campaign_draw.py (must-not-rest
# reproduces the 14:03Z state; may-rest when all landed). Closes the "surface N -> rest until doorbell" class.
#
# OPEN sub-items (why parked in in_progress, not root):
#   PART 1 -- daily note must compute TURN-AWARE utilisation (spawn/turn logs, not commit gaps) alongside
#     the product/machinery split. Home: background/daily_self_note.py (NOT YET BUILT).
#   PART 3 -- SITE build continues: surfaces 2->5 (campaign rolls, now auto-drawn via CAMPAIGN_REGISTER.yaml);
#     iterate surface 1 (axis-1 FAIL recorded in director_axis_verdicts.jsonl) vs BRAND_CONSTITUTION +
#     Spec-005 rubric, next iteration AS SCORED RUBRIC ROWS. Unblocks per surface: land LIVE + Expert-Hour
#     + mark item `landed` in the register.
# -----------------------------------------------------------------------------------------------------

# [DIRECTOR-RULING] — Seventh class: campaigns must roll. Site verdict: front door FAILS. Utilisation truth. (2026-07-23)

**Type:** [DIRECTOR-RULING] via advisor bridge. Three parts.

## 1. The utilisation truth, on the record

Computed from today's ledger: 35 work commits over 9.3h with **6.6h idle across five >45-min windows** — ~29% by commit-gaps, ~40% turn-adjusted. Two of the idle windows (10:10–11:56Z; 14:03Z→) occurred **with the SITE_V5 campaign open and surfaces drawable.** The daily note must from tonight compute **turn-aware utilisation** (from spawn/turn logs, not commit gaps) alongside the product/machinery split.

## 2. The SEVENTH CLASS: campaign continuation (R10, mechanise today)

Landing campaign item N and then resting until a doorbell is the same disease as every rest-while-work-exists class before it. Rule: **an open campaign in PRIORITIES with unfinished items IS drawable work — finishing surface N rolls directly into surface N+1, no doorbell required.** R15 both ways: an open campaign with remaining items must FORBID rest (reproduce today's 14:03Z state as the failing test first); a campaign with all items landed permits rest per the normal whole-set proof. Per the standing console ruling, a seventh class is an R10 breach of R17 — treat it as such: the fix is to R17's enumeration, not a special case.

## 3. Site verdict recorded + the work continues NOW

**Axis-1, front-door MVP: FAIL — the director's verbatim: "It still looks awful."** Record the score. Do not wait for elaboration to act: (a) **build surfaces 2–5 now** — the campaign rolls; (b) **iterate surface 1 in parallel** strictly against BRAND_CONSTITUTION and the Spec-005 rubric rows (type-only wordmark, colour-as-information-never-decoration, the ten-second test, walk-any-claim-to-data), and present the next front-door iteration **as scored rubric rows** so the director's next verdict lands row-by-row instead of wholesale; (c) tonight's daily note answers in product terms: surfaces landed, rubric rows claimed-met with pixels, and turn-aware utilisation. A director one-line elaboration may follow via the bridge; it refines, it does not gate.

**Risk & proportionality:** draw-logic fix = failing test first, own commit, R15 before deploy; site work additive under the confirmed structure. Tag: **class fix contract-touching; site work proceed.**

— Advisor bridge, carrying the director's verdict and the ledger's numbers, 2026-07-23.
