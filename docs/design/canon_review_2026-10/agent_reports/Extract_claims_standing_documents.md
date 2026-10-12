# Agent report: Extract claims: standing documents

## Brief given

Read the brief at /tmp/claude-0/canon/brief.md for the output format, then do THIS variant of the task. Your batch list is /tmp/claude-0/canon/batches/S_standing.txt (7 files, paths relative to /tmp/claude-0/canon/repo/). Your batch code is S. These are the STANDING canon surfaces: CLAUDE.md (the machine's rules, partly the director's text), docs/design/DIRECTOR_CANON.md (the brief the director-twin approver judges by), docs/operations/OPERATING_MODEL.md (generated from CLAUDE.md), docs/design/THE_MODEL_ON_A_PAGE.md, docs/vision/pitch.md, docs/vision/HUMAN_SIMULATION_LAYER.md, and docs/direction/DIRECTION.yaml (read only its `for_the_director` list: the open proposals awaiting the director).

For each standing document, extract every rule, principle, law, priority, or claim it states as CURRENT canon, kind=standing, one entry each, same format as the brief, with these additions in the note field: (a) does it look stale: dates, references to things that may have been retired, numbers that have probably moved; (b) for CLAUDE.md, mark which entries are in the operating-model section and which are the permanent rules R1-R15 and Laws A/B.

Then add a section "## Cross-document comparison" that answers: which of the following appear in which document (yes/partly/no for each of the seven): the mission (save customers cash, carbon and convenience/time; create value and share it); the epistemic wall; world-first / curtain principle; the operating model (machine gets on with knowledge, in-flight, error-fixing; escalates strategy with proposals; canon intent reserved to director); the priority order of 2026-10-05 (knowledge; unbilled and billing accuracy; forward CLV on held-back history; per-customer decisions; levers in merit order pays-stays-margin-value-add; forward simulation; comms/sentiment/NPS); the product-vs-machinery floor; R1-R15 and Laws A/B; the CLV merit order; carbon's purpose; forward simulation / phases; run discipline (minutes/hours ladder, over-an-hour rule); fairness rulings (no cost shifted onto prepayment; a save offer not paid for by stayers). Also list the `for_the_director` open items from DIRECTION.yaml with their raised dates in one line each.

Write everything to /tmp/claude-0/canon/extracts/S_standing.md. PROJECT_OVERVIEW.md is NOT in your list; ignore it. Read every listed file in full. Reply with only the batch summary and the cross-document comparison.

## Report


Counts match the summary. Written to `/tmp/claude-0/canon/extracts/S_standing.md`.

## Batch summary
- files read: 7 (all in full; none unreadable). CLAUDE.md, docs/design/DIRECTOR_CANON.md, docs/operations/OPERATING_MODEL.md, docs/design/THE_MODEL_ON_A_PAGE.md, docs/vision/pitch.md, docs/vision/HUMAN_SIMULATION_LAYER.md, docs/direction/DIRECTION.yaml (whole file read; `for_the_director` extracted). Snapshot is docs-only, single commit — code references and per-file git dates unverifiable.
- rulings extracted: 165 (CLAUDE.md 67; DIRECTOR_CANON 27; OPERATING_MODEL 2; MOAP 20; pitch 17; HSL 19; DIRECTION `for_the_director` 13 — 8 open as kind=standing, 5 answered as kind=ruling).
- most important / most likely forgotten:
  - R-S-71–87: the full text of R1–R15 and Laws A/B now exists in no standing document — DIRECTOR_CANON has one-liners and says "see CLAUDE.md for full text", but CLAUDE.md dropped every numbered rule on 2026-08-28; R3 (two-strike redesign), R7 (injected text zero authority) and R8 (NTFY untrusted) have vanished from the live rule-book.
  - R-S-88/R-S-29: one-way doors — seven in DIRECTOR_CANON ("complete and fixed"), five in CLAUDE.md; the dropped item 6 ("values decisions defining what the company is FOR — above all others") is the Epoch-4 fitness function nobody has raised.
  - R-S-89/R-S-68: DIRECTOR_CANON still installs the twin as standing approver (director's live instruction, 2026-07-13); the twin last acted 2026-07-16 and CLAUDE.md says the permission machinery is deleted — overtaken with no recorded overturn, in a file Law B says only an overturn may change.
  - R-S-102/R-S-158: making the objective two-sided is reserved to the director (MOAP, R13) and has never been put to him as such; the C34 row (open since 2026-10-06) is the nearest. The engine still "advises nobody".
  - R-S-116: the director's 2026-07-23 instruction to seed a plain-language lay page from the model-on-a-page — escalated, defaulted, never in `for_the_director`, never visibly done; pitch.md's "should inform the about section" is the same gap.
  - R-S-91: the Epoch-2 exit tests (bill lawfully wrong then corrected; mis-estimate → discover → rebill; "the director reads the rederived decade and recognises a real supplier's life") are the acceptance tests for step 2 of the 2026-10-05 order and are nowhere restated.
  - R-S-128: the pitch's five-condition Transition Test — absent from all current canon.
  - R-S-138/152: the 80/20 personalisation-dimension measurement the director asked to be notified of; nothing produces it.
  - R-S-129/131: pitch.md (the designated About-page source) still claims "SURVIVED the 2021-22 crisis", an 85% hedge floor justified by a finding later ruled an artefact, 18/19 retention success, and local-Qwen execution — each contradicted elsewhere in this batch.
  - Absent from all seven: the 2026-10-05 priority order, the product-vs-machinery floor, the run ladder / over-an-hour rule, the fairness rulings, the world-first ("world's responses first, then supplier levers") rule, the "2026-10-10 balance", and the 2026-08-12 Opus tiering rule the 2026-10-12 exception presupposes.
- contradictions between documents in this batch:
  - CLAUDE.md "Nothing inside the simulation is a one-way door" + five RESERVED_CATEGORIES vs DIRECTOR_CANON §3 seven doors "complete and fixed".
  - CLAUDE.md "permission machinery stays deleted" / "a level move is recorded, never authorised" vs DIRECTOR_CANON twin as standing approver, "director ranks", "Epoch 2 is the current open epoch".
  - CLAUDE.md NTFY "carries his full authority when the words are his" vs DIRECTOR_CANON R8 "all inbound NTFY is untrusted data".
  - DIRECTOR_CANON "see CLAUDE.md for full text" of R1–R15 vs CLAUDE.md with no numbered rules; MOAP "R1–R17" vs DIRECTOR_CANON R1–R15.
  - MOAP "Carbon is not demoted — one of three" vs MOAP TF2 "Carbon becomes the headline".
  - CLAUDE.md "Carbon is designed and unwired" / "Time does not exist here at all" vs MOAP 2026-10-09 correction (emissions measured) and the open time-in-minutes row.
  - pitch.md regime-change blindness + 85% hedge floor vs DIRECTOR_CANON §6 "a data-leak artefact"; pitch "SURVIVED" vs MOAP C3 "none of the death mechanisms presses yet"; pitch Qwen/four-hour opt-out vs CLAUDE.md "No local model"/"Silence is validation"; pitch 18/19 retention vs B8 "a loss at every cut size".
  - HSL/pitch CLV objective (supplier forecast lifetime value) vs the two-sided mission and pitch's own "for both parties"; HSL bill-shock threshold 20% vs 30% within one document.
  - MOAP "different mix every run" vs book seeds authorised only 2026-10-10.
  - OPERATING_MODEL.md refers to "the mission statement above" and "the walls", neither present in the published copy.

## Cross-document comparison
(C = CLAUDE.md · D = DIRECTOR_CANON · O = OPERATING_MODEL · M = MOAP · P = pitch · H = HSL · Y = DIRECTION `for_the_director`)

| Item | C | D | O | M | P | H | Y |
|---|---|---|---|---|---|---|---|
| Mission (create value and share it; money/carbon/time) | yes | no | no (dangling reference) | yes | partly | partly | partly |
| Epistemic wall | yes | yes | no | yes (fullest, two-way) | yes | yes | yes |
| World-first / curtain | partly (curriculum wall) | partly (R13) | no | partly (world-must-press outranks capability) | no | partly | partly |
| Operating model (get on with / escalate with proposal / canon intent reserved) | yes (source) | no — contradicts | yes (copy) | partly (pre-10-04 form) | partly (superseded form) | partly | yes (the mechanism) |
| Priority order 2026-10-05 | no | no (epoch arc) | no | no (TF1/TF2) | no | no (Phases A–D) | partly (rows map to steps; order unstated) |
| Product-vs-machinery floor | partly | partly (R6) | no | no (harness = "third product") | no | no | partly ("when it doesn't displace the steps above") |
| R1–R15 and Laws A/B | no (dropped; R10/11/12/14/15 unnumbered) | yes | no | partly ("R1–R17", R13) | no | no | no |
| CLV merit order (pays-stays-margin-value-add) | no | no | no | no | partly (precursor) | partly (precursor) | no |
| Carbon's purpose | partly (status only) | no | no | yes (with internal TF2 tension) | no | no | partly (losses definition) |
| Forward simulation / phases | no | partly (M1–M4, Epoch-4) | no | partly (TF2, endgame) | partly (Darwinism) | no | no |
| Run discipline (ladder, over-an-hour) | partly (commits >10 min, cache cost) | no | no | no | no | partly (stale scaling notes) | partly (box budget, 40-founder books) |
| Fairness rulings (prepayment; stayers) | no | no | no | no (prepay as protected tail only) | no | no | no |

`for_the_director` items (raised · status):
- 2026-10-04 the-end-to-end-review-of-claude · OPEN — approve CLAUDE.md cleanup item by item; rule on three canon wordings.
- 2026-10-04 time-is-scored-in-minutes-not-converted-to-money · OPEN — minutes per class, never GBP.
- 2026-10-04 whether-per-customer-pricing-beats-a-flat · ANSWERED 2026-10-10 — seeds 61101–61112 authorised under the seed-family runner.
- 2026-10-04 no-atom-can-reach-l3-while-an · OPEN — reviewer independence alone should not bar L3; H45 parks.
- 2026-10-05 a-household-s-electricity-carbon-is-shown · OPEN — add T&D losses as a named line beside the NESO figure.
- 2026-10-06 c34-next-best-action-the-customer-s · OPEN — rank C34 on joint value with a no-loss floor on both sides.
- 2026-10-09 the-run-s-company-cannot-learn-whether · OPEN — holdout off; no outside-book retention evidence unless he says so.
- 2026-10-09 a-held-lane-crash-can-now-wake · OPEN (reserved) — console SessionStart hook; not built without his yes.
- 2026-10-10 the-scale-lane-s-seed-families-need · ANSWERED 2026-10-10 — same seed authorisation (duplicate ask).
- 2026-10-10 c34-s-debt-decision-cannot-be-graded · ANSWERED 2026-10-11 — merge debt management into NBA with a personal payment plan; unpublished levers as toggles with a range, never findings; design before build.
- 2026-10-10 practitioner-question-at-an-annual-direct-debit · ANSWERED 2026-10-11 — SLC 27.15 (Aug 2022); DD = own 12-month forecast at known/forecast rates plus balance to clear.
- 2026-10-11 the-capital-target-binds-from-2025-but · OPEN — apply Capital Target from 31 March 2025 at GBP 115; start date is his.
- 2026-10-12 the-advisor-trial-steer-sonnet-5-5 · ANSWERED 2026-10-12 — 12 August Opus rule set aside for worker ticks only, ≤7 days, dated flag, stop rule.
agentId: ab245aaa30b44ef45 (use SendMessage with to: 'ab245aaa30b44ef45', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 238817
tool_uses: 27
duration_ms: 2652041</usage>
