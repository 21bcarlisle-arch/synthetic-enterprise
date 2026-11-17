**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Every CLAUDE.md rule carries its lineage, and every trial its model (2026-11-17)

**Type:** STEER, through the advisor channel. It amends the CLAUDE.md delete-and-add-back trial (`DIRECTOR_STEER_TEST_CLAUDE_MD_BY_DELETING_AND_ADDING_BACK_AND_AUDIT_WHAT_EACH_SEAT_LOADS_2026-11-15.md`, as amended by `DIRECTOR_STEER_THE_CLAUDE_MD_TRIAL_USES_A_GOLDEN_SET_RUN_TWICE_AND_EACH_HANDOFF_EARNS_ITS_PLACE_2026-11-17.md`) before it starts on 21 Nov. The director's words, from chat on Tue 17 Nov:

- 19:14 GMT, sharing a summary of a paper with no comment.
- 19:16 GMT, on the advisor's recommendation below: "Yes"

## What the advisor found (check it)

- **The source, unverified.** The summary he shared describes Yu et al. (Google Cloud AI, Google DeepMind, Penn State), "Self-Improvement Memory Enables Continual Recursive Self-Improvement", arXiv 2611.18856, 13 Nov 2026.
  - The advisor could not fetch the arXiv page, and search did not find it. Adjacent work exists: arXiv 2608.24876 and 2609.24972. The summary reads as AI-written, so treat its numbers as unconfirmed.
  - **Claim:** when a self-improved harness moves to a new model or task, carrying only the final harness loses why each rule exists. The optimiser then overwrites scaffolding that mattered or repeats rejected experiments.
  - **Fix:** carry a structured changelog with the harness. Per edit, record the recurring problem, the rationale, predicted against observed outcome, and the evaluation context (model, data, conditions).
  - **Claimed results:** +2.36 on coding (p = 0.003); 68.41 → 84.75 with the changelog against 73.42 without, on a harness moved from Claude Opus to Gemini.
- **We already hold most of it.** `docs/operations/EFFICIENCY_BACKLOG.md` records idea, source, expected saving, trial and result, and keep or drop. Pre-registered predictions in `docs/staging/records/` record predicted against observed. CLAUDE.md cites some incidents inline, and `docs/retrospectives/` holds 19 retros.
- **Two gaps:**
  1. **Most CLAUDE.md rules have no recorded lineage.** `docs/design/CLAUDE_MD_REWRITE_NOTES_2026-08-28.md` records what was kept, dropped and added in the rewrite, not per rule why it exists or what it prevents. The delete-and-add-back trial is the paper's exact hazard: cutting scaffolding without knowing what it guarded.
  2. **Nothing records the model a rule was written under or a trial was run on.** Rules written to correct older models (Cherny, YC, 27 Jul) and new models (Fable 5.2; CLI 2.1.323) make this the dimension most likely to go stale.

## The outcome wanted

1. **A lineage per CLAUDE.md rule, before 21 Nov.** One line each, in one file beside the trial, not in CLAUDE.md itself:
   - the rule (its heading or first words);
   - the recurring problem it targets;
   - the incident, finding or ruling that introduced it, with a path and date;
   - the model in use then;
   - what it was predicted to prevent.

   Where git history and the records cannot establish a rule's origin, write **GAP: origin unknown**. Never reconstruct a plausible story. An unknown origin is itself evidence for the trial.
2. **The trial records predicted against observed, per rule.** For each line dropped in the minimal file, write before the golden-set runs what its lineage predicts will break. After the runs, record what did break, on Opus 5.5 with the CLI version used. Rules with a named past incident need that incident's case in the golden set, or a stated reason why not.
3. **A model and CLI-version column** in `EFFICIENCY_BACKLOG.md` and in every trial record from now on. Backfill only where the record already says.
4. **Carry it forward.** The lineage file is appended to, not rewritten, as rules change. A rule added later carries its lineage line in the same commit.

## Reading-log entry to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-17 | Summary of Yu et al., "Self-Improvement Memory Enables Continual Recursive Self-Improvement" (arXiv 2611.18856, 13 Nov), unverified by the advisor | Director | A harness should carry the why, prediction, outcome and model of each change, or a model change strips what mattered. We already have most of it in the efficiency backlog and pre-registered records. Gaps: per-rule lineage for CLAUDE.md, and the model on every trial. | ADOPT (amends the CLAUDE.md trial) |

## Rules

- **The lineage is evidence, not decoration.** Write it from git history and records only.
- **No new gate.** The trial uses it. A gate on future rules is not proposed here.

## Risk

Touches: one new lineage file, the trial design, a column in the backlog.
Blast radius: none to runs.
Probable failure modes:
- **Invented lineage:** a plausible origin written where history is silent. Mitigated by GAP and by the paths cited.
- **Lineage used to keep everything** ("it had a reason once"). The trial still decides. A reason that no longer reproduces on Opus 5.5 is a reason to drop.

Proportionality: harness, reversible. Implement directly.

— Director steer, 17 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

*Seat, 17 Nov 2026, the evening after his "Yes".*

1. **Lineage per rule:** `docs/operations/EFFICIENCY_E_E_CLAUDE_MD_LINEAGE.md` has 83 lines, one per CLAUDE.md rule.
   - Each line gives the rule, the problem, the introducing incident, finding or ruling with a commit and date, the model on that commit's `Co-Authored-By` trailer, what it was predicted to prevent, and whether the minimal arm keeps, condenses or drops it.
   - Written from `git log -S` on CLAUDE.md, the pre-rewrite file's own dated stamps (`3d83edffb6^`), and the commits and retros those name.
   - Ten lines carry **GAP: origin unknown**: nine habits the 28 Aug rewrite notes call "taught by hand in the console", W7's history in this file, and the REUSE gate. On 49 lines the cited commit has no model trailer. The file says so, and gives that day's other trailers only as labelled context.
   - Finding from the history: on 24 Sept the prompt audit (`f325485b4f`) already recorded the paper's hazard. A rule deleted without its reason gets re-added, which is how the 200-line limit outlived its deletion.
2. **Predicted against observed, per rule:** amendment to `docs/staging/records/SEAT_PREREG_TRIAL_E_E_MINIMAL_CLAUDE_MD_AGAINST_THE_FULL_ONE_2026-11-16.md`, written before any counted golden run (none has run).
   - Each of the 34 dropped lines gets what its lineage predicts will break, and the golden task that can show it.
   - Where a named incident has no case, the reason is given. Lineage predicts visible breaks on g05, g07, g08 and g09.
   - Twenty dropped lines have no case, so a clean golden result licenses dropping them from the always-loaded file, not from the project.
   - Two named incidents with feasible cases (`1b98c83609`, `7bb9daa465`) are listed as candidates and not added, since adding them would change the decider after its 17 Nov fix.
3. **Model and CLI version:**
   - `EFFICIENCY_BACKLOG.md` has the column, with a rule line. It is backfilled only where the row already said: E-e Opus with the golden set's `claude-opus-5-5`, E-f Haiku at CLI 2.1.319, E-f2 Haiku. Other rows say "not in the record".
   - Every golden run row now records the model and CLI version **that ran**, read from the transcript's init event (`tools/claude_md_golden_set.py::run_identity`). A new test covers it, with both legs (present, absent).
4. **Carry forward:** the lineage file ends with an "Appended lines" section, and its header says a rule added later carries its line in the same commit. No gate was added, as the steer says.
5. **Reading log:** row appended to `docs/institutional/reading_log.md` (Agents and models), marked unverified as the advisor found it. `site/data/reading_log.json` regenerated.

Decision: outside_source yes
