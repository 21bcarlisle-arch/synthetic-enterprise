**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Canon in one home, every page aligned (2026-10-12)

**Type:** STEER, canon alignment, with the director's rulings on the fourteen decisions in `DIRECTOR_CANON_V4_2026-10-12.md` §15: *[RULINGS: filled in from the director's answer before staging]*.

**When:** the install (step 1) now. It is one file and collides with nothing. The rest is machinery-class work, taken when it doesn't displace the payment-engine sequence (the four-principles audit, then the household payment world, then the supplier engine). The owed list (step 6) is ranked by the priority order like any other work.

---

## Why

The director's canon had spread across five standing pages and about 190 director documents, and they no longer agree.

- `docs/design/DIRECTOR_CANON.md` is the director twin's brief of 18 July. The twin last acted on 16 July. The brief still names it as the standing approver, lists seven one-way doors and says "Epoch 2 is the current open epoch".
- R1–R15 now exist in full on no standing page. The twin's brief says "see CLAUDE.md for full text", but CLAUDE.md dropped the numbered rules on 28 August.
- Three reserved-action lists disagree: the July seven, the director's four of 29 July, and the five in code.
- None of these is on any standing page: the 5 October priority order, the four principles of 11 October, the fairness rulings of 8 October, the run discipline of 8 October, carbon's purpose (5 October) and "knowledge before build" (11 October).
- The model on a page still says "Carbon becomes the headline". CLAUDE.md still says carbon is "designed and unwired" and that time "does not exist here at all".
- The pitch, which is the About page's source, still claims the company "survived the 2021-2022 energy crisis", an 85% hedge floor, 18/19 retention, a four-hour opt-out and local-model execution.

The director's own rule is that "a concept has one home". This steer applies it to canon.

## What to do

1. **Install canon version 4.** Copy the text of `docs/staging/DIRECTOR_CANON_V4_2026-10-12.md` below its staging header, verbatim, to `docs/design/DIRECTOR_CANON.md`. Move version 3 to `docs/design/archive/DIRECTOR_CANON_v3_TWIN_BRIEF_2026-07-18.md` under a one-line banner, "Retired 2026-10-12; superseded by DIRECTOR_CANON.md v4". Use the trailer `Director-doc: his-words -- canon v4, director rulings of 2026-10-12`.

2. **Align every standing page** to the list below. Each change either quotes a canon line verbatim or points to its id. A second wording of a canon line is the defect this steer exists to close. Where only facts change, it is a marked factual correction.

3. **Banner the sources, don't edit them.**
   - Every `DIRECTOR_*` document in `docs/staging/done/` and `docs/staging/in_progress/` that v4 consolidates gets a one-line banner: "Consolidated into DIRECTOR_CANON.md v4 on 2026-10-12. Kept verbatim as the record; the canon text governs."
   - Close the two canon documents in progress since July, `DIRECTOR_CANON_MODEL_ON_A_PAGE_2026-07-23.md` and `DIRECTOR_CANON_THE_STANDARD_2026-07-29.md`, as consolidated.
   - Do the parked-documents audit (owed item 11) in the same pass. For each parked director document, is the reason it was parked still true?

4. **Close the `for_the_director` rows the rulings answer:**
   - `the-end-to-end-review-of-claude`
   - `time-is-scored-in-minutes-not-converted-to-money`
   - `no-atom-can-reach-l3-while-an`
   - `a-household-s-electricity-carbon-is-shown`
   - `c34-next-best-action-the-customer-s`
   - `the-run-s-company-cannot-learn-whether`
   - `a-held-lane-crash-can-now-wake`
   - `the-capital-target-binds-from-2025-but`

5. **Keep it aligned, with the smallest mechanism that can fail.**
   - a. A canon-against-canon check, beside the existing canon-against-code check. Three conditions fail it:
     - a canon line quoted on a standing page that is not verbatim in `DIRECTOR_CANON.md`;
     - a cited canon id that does not exist;
     - a line that canon §16 marks superseded still presented as current.

     It runs in the Monday end-to-end step and is mutation-proven (R15).
   - b. Every new `DIRECTOR_CANON_*` staging document carries a `## Where this lands` section. The staging watcher flags one without it. The ruling is not done until each listed page is updated, or marked not applicable with a reason.
   - c. Add `docs/design/DIRECTOR_CANON.md` and `docs/design/THE_MODEL_ON_A_PAGE.md` to the startup anchors, so an advisor session orients from canon.

6. **The owed list.** For each of the twelve items in canon §15 "Owed to the director", either show the evidence that it is done or do it, ranked by the priority order. Report each in the stretch log.

7. **Report.** One stretch-log entry listing every page changed, every banner added, every row closed, and anything that could not be aligned, with the reason.

## Where this lands, page by page

**CLAUDE.md** (stay under 35,000 characters; prefer pointers to restated text)
- The mission: keep M1 verbatim. Replace the three lines that follow it with M2–M4 as canon words them. This retires two stale claims: "Carbon is designed and unwired" (CO4) and "Time does not exist here at all" (M3).
- Under the mission, add one line: "Canon lives in `docs/design/DIRECTOR_CANON.md`; this file quotes it and never rewords it."
- The walls: add the four principles (W7, one line each), no personal microdata (W11), and the harness clause of W6. Keep the existing walls.
- Knowledge:
  - Replace "When a reading is odd against how the industry actually works, say so and ask. Do not build on it" with K4.
  - Correct the knowledge-first paragraph with K2: omission is not neutrality.
  - Add K8, knowledge before build.
- The operating model: replace the reserved-actions sentence with G5. Replace the authority sentence with G8. Add G9.
- Habits: add F11's tie-breaker and R5, why we run.
- Who and what, and the Build line: apply the 4 October clean-up as approved, with the build figure derived at publish (decision 13).

**`docs/operations/OPERATING_MODEL.md`**: regenerated from CLAUDE.md, automatically.

**`docs/design/THE_MODEL_ON_A_PAGE.md`** (a director document; changes carry the his-words trailer)
- Mission section: add CO1 (carbon's job) and M3's wording on time. The three-currencies table's time row follows M3.
- Timeframe 2, "Carbon becomes the headline ... £/tCO₂e on the front page": follow decision 4.
- Endgame, "EV is fitness and mortality is selection": "open, the director's (decision 14)".
- Method, "R1–R17": "R1–R15" (H1).
- Add a pointer to canon §2, Phases.

**`docs/vision/pitch.md`**: a dated banner: "The June 2026 pitch, kept as written. Since superseded: 'survived the 2021-2022 energy crisis', the 85% hedge floor, 18/19 retention, the four-hour opt-out, local-model execution. Current canon: DIRECTOR_CANON.md." The About page draws from canon from now on, not from this file.

**`docs/vision/HUMAN_SIMULATION_LAYER.md`**: a dated banner naming its superseded parts:
- the one-sided CLV objective (now M2 and C7);
- the two bill-shock thresholds, 20% and 30% (now F20: the shock is the payment change);
- build phases A–D (now P1 and §2).

**`docs/design/DIRECTOR_AXES.md`**: a banner. The pricing law it cites no longer exists.

**`docs/PROJECT_OVERVIEW.md`**: point to `DIRECTOR_CANON.md` for canon, and remove restated canon that disagrees with it.

**`docs/status/STARTUP_ANCHORS.md`**: add the two anchors (step 5c).

**`docs/direction/priority_order.yaml`**: matches P1. Add the payment-engine sequence if the file carries notes per step.

**The site**: About and the front door take their claims from canon v4 at the next Monday publish.

## Evidence

The 12 October canon review is on branch `advisor/canon-review-2026-10-12`, under `advisor/canon_review_2026-10-12/`. It holds:
- fourteen reconciled theme chapters, citing each ruling by id and date;
- the theme extracts, which map each id to its source file;
- the quote check: 1,051 of 1,124 quotes in the chapters are verbatim in the repository, and all 257 in canon v4.

Copy it to `docs/design/canon_review_2026-10/` as the evidence base. It is not canon.

— Director steer, 2026-10-12, drafted by the advisor from the canon review.
