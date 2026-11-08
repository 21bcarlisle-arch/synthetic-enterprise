**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Result: planting each no-evidence gate's own defect, and judging the rest of the stale-copy and site-lane refusals, for the 11 Nov gate review (2026-11-08)

*Delivery seat, 2026-11-08, claim `run-the-11-nov-two-reader-and-gate-review`. This scores the pre-registration
`SEAT_PREREG_PLANT_THE_DEFECT_ON_THE_NO_EVIDENCE_GATES_AND_THE_REST_OF_THE_STALE_COPY_AND_SITE_LANE_REFUSALS_2026-11-08.md`
(landed `e414e0538` before any plant ran). It sits beside the 7 Nov record
`SEAT_RESULT_WHAT_PREDICTS_A_DEFECT_AND_WHAT_EACH_COMMIT_GATE_HAS_CAUGHT_FOR_THE_11_NOV_REVIEW_2026-11-07.md`.
The review itself, which decides the selector and any retirement, is still due on or after 11 Nov.
No gate was changed.*

## The short answer

- **No gate is named for retirement.** Every gate that refused nothing in 30 days either refuses its own defect
  and is the only step that does, or is already non-blocking by an earlier decision.
- **One gate is dead on the route actually in use.** The ruling-archive-question gate watches only
  `docs/staging/done/`. Director rulings and steers have been archived to `docs/staging/advisor/done/` since
  October. The gate refuses an open-question ruling copied into `staging/done/` (rc 1) and passes the same bytes
  in `advisor/done/` (rc 0). **Six rulings and steers already in `advisor/done/` hold questions that the
  register counts as open.** Some of those are extractor noise ("Yes to all three."), so simply widening the
  prefix would block every advisor archive on false questions. I tried to raise this to `for_the_director`.
  `director_concerns` refused it: restoring a gate's reach changes no ruling, so it is an error fix and the
  seat's to make. It is handed on as `widen-the-ruling-archive-gate-to-advisor-done`.
- **The site-lane gate is not a candidate for narrowing.** In its remaining 32 refusals, 9 distinct events
  (10 verdicts, two of them the same event) were real page defects that the commit itself caused. Prediction 7
  is wrong, and so prediction 8's recommendation is withdrawn.
- **The stale-copy guard has no real catch in 58 judged refusals** (6 + 52). 31 were deliberate deletions
  that needed a `--drops` declaration, 22 are unclear, 4 were not refusals and 1 was a fault. Prediction 6 is
  wrong. Even so, this does not make it a retirement candidate: see Part B.

## Part A — the plants

The plants were run from `/var/tmp/gate_review/r2/plant.py` in a scratch worktree at base `008cd8e9af`. Each
chain step was run on its own, beside a control plant (a one-line change to a scratch doc). "Other step red"
counts only steps that were green on the control.

| gate | plant (its own defect) | own gate | other step red | reading |
|---|---|---|---|---|
| status-honesty | `LATEST.md` says a dark daemon is running | refuses | startup-anchor freshness | **sole line.** The anchor gate refused a *different* defect: the date sentence the plant left stale. |
| rulebook full (test gate) | CLAUDE.md over 35,000 characters | refuses | — | sole line |
| moap-coherence, site-data plant | an unknown atom in `site/data/moap_node_atoms.json` | refuses | site-lane gate (2 moap site tests) | redundant on this plant |
| moap-coherence, map-only plant | a closed atom's `level_current` set to 0 | refuses | level-promotion gate | **sole line** on the drift. The level gate refused the row's *placement*, not the drift. |
| ruling-archive-question | see "Correcting the run" below | refuses in `staging/done/`, **passes in `advisor/done/`** | — | **dead on the route in use** |
| consolidation-rhythm | four atoms lowered to target, closing epoch 5 | **passes**, and prints "reported, not refused: canon v4 decision 11 retired the gate" | level-promotion gate (placement) | already non-blocking by design |
| size-ratchet | 60 new functions in a sim module | **passes** (`rollout_state=warn`) | — | already non-blocking by design |
| company-network-isolation | `urllib.request.urlopen` added to a company module | refuses | — | sole line |
| file-scope-generated-paths | a generated `site/data` file put in an atom's `file_scope` | refuses | — | sole line |
| half-hourly-dependency | a settlement-period filter added to `saas/` | refuses | — | sole line |
| running-total-order | a treasury balance read from the last row after a sort | refuses | — | sole line |
| scope-evidence | a non-existent path put in an atom's `file_scope` | refuses | — | sole line |
| commons-source-supersession | a commons artefact's `fetched` set to `unknown` | refuses | — | sole line |
| commons-citation-provenance | a provenance value its own legend does not define | refuses | test gate | redundant on this plant. Re-run on HEAD `617a2181e`: the same plant turns 9 `tests/saas/reporting/test_annual_report.py` tests red, which are green without it. The test gate catches it only because the annual report *loads* this artefact. An artefact no code reads would get no second line. |

**Correcting the run.** The previous tick on this claim ran four ruling-archive plants and read all four as
"own gate passes". **All four plants were invalid.** Two moved the correctness ruling, which carries no question
the extractor finds. The other two copied a `DIRECTOR_QUESTION_*` file, a prefix the gate does not read. Today's
valid plant copies `DIRECTOR_RULING_THE_FOUR_RESERVED_QUESTIONS_2026-10-26.md` (1 open question in the register)
into each archive directory, and gives the result in the table. Separately, I ran one reset in my own worktree
by mistake, when a `cd` to a scratch worktree that no longer existed failed. It removed only the untracked owner
lease `.se_worktree_owner`, which I rewrote with the executor's pid. Nothing tracked was touched.

### Scoring Part A's predictions

| # | prediction | result |
|---|---|---|
| 1 | size-ratchet passes its own plant (warn mode) | **Held** |
| 2 | the other 12 all refuse their own plant | **Wrong.** Consolidation-rhythm passes, because it was made report-only by canon v4 decision 11. I had not read that. Ruling-archive refuses only on the route that is no longer used. |
| 3 | at most 4 of the 12 redundant; likeliest scope-evidence, file-scope, consolidation-rhythm, moap, network-isolation | **The count held** (2: moap on the site-data plant, citation-provenance). **The names were wrong.** None of scope-evidence, file-scope or network-isolation is redundant. |
| 4 | neither commons gate redundant | **Half wrong.** Citation-provenance was redundant on this plant, and only by accident: the loader breaks. |
| 5 | status-honesty and ruling-archive not redundant | **Held,** but the second half no longer matters: ruling-archive is dead on the route in use. |

## Part B — the remaining refusals

These were judged by the same rubric as the 7 Nov sample, from `/var/tmp/gate_review/r2/{stale,site}.json`. The
verdicts and their reasons are in `verdicts_stale.json` and `verdicts_site.json` beside them. I re-read every
REAL, RULE and FAULT reason. Site `#28` and `#29` come from one log, so they are counted as one event.

| gate | judged | real | rule | fault | not a refusal | unclear |
|---|---:|---:|---:|---:|---:|---:|
| stale-copy guard (remaining) | 52 | 0 | 28 | 1 | 4 | 19 |
| stale-copy guard (all, with 7 Nov's 6) | 58 | **0** (95% upper bound about 6%) | 31 | 1 | 4 | 22 |
| site-lane gate (remaining) | 32 | 10 verdicts, **9 distinct events** | 0 | 4 | 10 | 8 |
| site-lane gate (all) | 38 | 9 distinct | 0 | 8 | 12 | 8 |

**Site-lane: what it caught.** A new table without the `table-scroll` wrapper (twice). A door script writing
into elements that are not on the served page (twice). A front-door diagram hosted twice. Internal jargon
("open atom C31") on a public page. A node name that no longer matched the atoms file. Published-figure tests
broken by new markup. The map door throwing on boot. These are exactly the defects "done means the rendered
value changed" exists for. Its 8 faults are environment (`/tmp` full, DNS) and reds already on trunk. The fix
for those is the environment, not the gate.

**Stale-copy: why 0 of 58 is not a retirement.** Its catch is the one irreversible thing on this tree: a
landing that silently reverts another lane's commit. The judged events cannot show that catch, because every
"RULE" refusal was the guard correctly seeing a revert and asking for it to be declared. The intended revert and
the stale one look identical until the author says which. The cost is a re-launch with `--drops`, and the
guard itself takes 0.07 s. The isolated worktrees, which most landings now use, make stale copies rare. That
explains a low real rate without making the guard dead weight.

### Scoring Part B's predictions

| # | prediction | result |
|---|---|---|
| 6 | stale-copy: at least 5 of 52 real | **Wrong:** 0 (19 unclear) |
| 7 | site-lane: at most 3 of 32 real, at least half fault | **Wrong:** 9 distinct real, 4 fault |
| 8 | if 7 held, recommend narrowing the site-lane trigger | **Withdrawn:** 7 did not hold |

## What this hands the 11 Nov review

1. **Retirements: none recommended.** Two steps are already non-blocking by earlier decisions: consolidation-rhythm
   (canon v4 decision 11) and size-ratchet (warn since August). The review may choose to drop them from the chain
   (about 0.1 s together) or flip size-ratchet to gate. That is tidying, not a finding.
2. **The ruling-archive-question gate** is an error fix, not a review decision. It is handed on as
   `widen-the-ruling-archive-gate-to-advisor-done`: widen it to `advisor/done/`, narrow the extractor to
   sentences in his quoted words that end in "?", and close the six live rows in the register first.
3. **The selector** is still the review's to decide, using both of the 7 Nov tables and `trust_ledger`'s
   confirmed-findings rate over the full two weeks. This record does not change that evidence.
