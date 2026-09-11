**Severity:** RECORDED · **Lane:** H_harness (parked-backlog hygiene) + W2_customer_generator · **Priority:** P1 for §1–§2 (small, immediate); §3 sequenced AFTER the HadUK pull lands · **Proportionality:** reversible / narrow — just do it

# [DIRECTOR-RULING][ADVISOR-STAGED] Three July segmentation steers reconciled, one amendment, and the parked-documents audit (2026-09-05)

**Decided by the director in the advisor channel, 2026-09-05.** His instruction, verbatim: *"I don't want to ignore prior steers or stages that are out of date."* The three dispositions in §1 were checked against the repository by the advisor this afternoon, not against the documents' own headers; the evidence lines are given so they can be re-verified in one command each.

## 1. Three parked steers — dispositions

### 1a. `docs/staging/in_progress/FROM_AGENT_SEGMENTATION_INTEGRATION_FOLLOWON_2026-07-22.md` — DONE, close it

All four items landed and the document was never moved:
1. W1_6→C13 pair wired — `background/coupled_triad.py` carries `"W1_6": "C13"` in the authoritative coupling.
2. Per-asset tenure→adoption gates — `simulation/population_draw.py` reads `tenure_adoption_gating_strength.per_asset[asset][tenure]` from the director curriculum, per-asset, director-confirmed 2026-07-22 (solar 0.10 / 0.25, EV 0.55 / 0.55, heat pump 0.14 / 0.35 for private / social renters).
3. Sensitivity study — `docs/market_research/tenure_adoption_sensitivity.md`, `tools/tenure_adoption_sensitivity.py`, `tests/tools/test_tenure_adoption_sensitivity.py` exist.
4. Hypothesis register — `docs/market_research/population_fusion_assumptions_register.json` exists.

Move to `done/`. **Carry forward:** the per-asset tenure factors are R13 director values already given; people phase 3 (uptake) consumes them from the curriculum and must not re-derive or re-assert them.

### 1b. `docs/staging/in_progress/DIRECTOR_STEER_TRIANGULATION_SITE_SEGMENTATION_2026-07-22.md` — blocking condition met weeks ago, close it

Parked "until either board spec lands". Both landed: `docs/staging/done/BOARD_SPEC_005_WEBSITE_2026-07-22.md` and `BOARD_SPEC_006_SEGMENTATION_2026-07-22.md`, each with its reconciliation (`docs/design/BOARD_SPEC_005_RECONCILIATION.md`, `BOARD_SPEC_006_RECONCILIATION.md`). This is the idle-hole class the harness has already named twice (a correct park with no mechanism to notice its condition changing). Move to `done/`. **Carry forward:** the Spec-006 coverage test — see §2.

### 1c. `docs/staging/in_progress/DIRECTOR_STEER_LEGIBILITY_AND_SEGMENTATION_2026-07-20.md` — Part 2 superseded, Part 1 stays open under its own name

- **Part 2** (segmentation too thin; cohorts as combinations across need, attitudes and engagement; derived from data; independence; score the worst cell) is superseded in full by the three phase-1 rulings staged today (`DIRECTOR_RULING_WEATHER_CELLS_…`, `DIRECTOR_RULING_HOUSING_…`, `DIRECTOR_RULING_PEOPLE_…`), which carry every requirement it states and more. Record the supersession in the document's header.
- **Part 1** (the site must let the director follow, as running state, four things: what the world is doing; what the supplier is doing; what it is like for one customer — consumption, bill, payments, products, arrears; and their CO₂) is **not** superseded by anything today. The director has not yet re-judged it: *"Not sure — I'll look later."* Re-home Part 1 as its own open item with its own name (the four-things window), so it is not lost under a July header whose other half is dead. It is **not** a build authorisation; it waits for his verdict.

## 2. Amendment to `DIRECTOR_RULING_PEOPLE_MONEY_AND_WHO_THEY_ARE_PHASE1_2026-09-05.md` §3.4

Add to the crossed-coverage deliverable: **the Spec-006 coverage test.** When the three phase-1 samples exist, check the board's blind list of segments a GB-domestic veteran insists exist (from `BOARD_SPEC_006_SEGMENTATION_2026-07-22.md` and its reconciliation) against the data-derived structure. A board-named segment absent from the derived structure, or a derived corner no practitioner named, is a first-class finding either way — report both honestly. The learning-value objective is not to be leaked to the board via any channel (the original steer's rule stands).

This amendment is recorded here rather than by editing the staged ruling, so the staged file stays byte-stable for the bridge.

## 3. The parked-documents audit — commissioned, sequenced after the HadUK pull

`docs/staging/in_progress/` holds **121** documents. Three sampled this afternoon were stale in three different ways (done-but-not-moved; parked-on-a-condition-since-met; half-superseded). The director's decision: **run the audit, after the HadUK-Grid pull commissioned by the weather ruling has landed** — the 72-hour token clock outranks this, and the audit must not compete with it.

**The question for every parked document is the idle-hole question:** *is the reason this was parked still true?* Dispose each into exactly one of:
- **DONE** — the work landed; move to `done/` with the evidence line.
- **SUPERSEDED** — a later ruling carries it; record which, move to `done/`.
- **UNBLOCKED** — its stated condition has been met; it becomes live work (re-stage or mint) and is not left parked.
- **STILL PARKED** — the condition is genuinely unmet; re-state the condition in the header with today's date, so the next audit has a checkable claim.
- **DIRECTOR** — needs his verdict; batch these into ONE plain-English list for him, not 121 messages.

Report back in plain English: counts per disposition, the UNBLOCKED work that came out of it, and the DIRECTOR list. Housekeeping never outranks a blocker (FINDING SEVERITY AND INTERLEAVE stands).

**The mothball ruling** (`DIRECTOR_RULING_MOTHBALL_THE_APPARATUS_2026-07-29.md`, with its three 2026-08-12 addenda: the coverage-based test, the three imports from a peer harness, the deterministic-before-judgement test) is one of the 121 and is disposed inside this audit like any other — its open item is "execute the MOTHBALL-verdict rows". Under its own text (*"do not send a proposal and wait… if he disagrees he will say so"*), execute or close on your judgement and tell him which.

## 4. Risk

**Touches:** document moves and headers in `docs/staging/`; nothing in `simulation/`, `company/` or `site/`. **Blast radius:** nil on published figures. **Failure modes:** (a) a parked document closed as DONE on its own header rather than on evidence — every DONE carries an evidence line; (b) UNBLOCKED work minted without a home — it goes onto the map, not into a new parking place; (c) the audit starting before the HadUK pull — §3 sequencing.

## 5. WORK THIS CREATES

- Three document dispositions (§1), one re-homed open item (Part 1, awaiting the director).
- One amendment recorded against the people ruling (§2).
- The parked-documents audit (§3), after the HadUK pull lands; one report and one DIRECTOR list.
