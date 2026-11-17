**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: trial E-e, a minimal CLAUDE.md against the full one, on real seat turns (2026-11-16)

*Seat executor, Mon 16 Nov 2026, about 05:45 GMT. Written before any turn has run on the draft.
The steer is `docs/staging/advisor/DIRECTOR_STEER_TEST_CLAUDE_MD_BY_DELETING_AND_ADDING_BACK_AND_AUDIT_WHAT_EACH_SEAT_LOADS_2026-11-15.md`,
item 1. Backlog row: `docs/operations/EFFICIENCY_BACKLOG.md` E-e.*

## The arms

- **Full:** the live `CLAUDE.md`, 23,803 characters.
- **Minimal:** `docs/operations/EFFICIENCY_E_E_MINIMAL_CLAUDE_MD_DRAFT.md`, 9,052 characters (38%). It keeps,
  verbatim: the mission and canon quotes, the walls, "Where the rules live" and the Build line. It keeps,
  condensed: commit mechanics, map headroom, knowledge-first (K2, K8), what waits for the director, and
  pointers. It drops "How to behave when no rule applies" (6,771 characters) and the operating model's
  mechanics, which are enforced in code and published in `docs/operations/OPERATING_MODEL.md`.

The live `CLAUDE.md` and its 35,000-character cap are unchanged until the result.

## Design

- **Which seat:** seat_executor only. It already runs each turn in its own worktree reset to origin,
  so the arm is a file written into that worktree after the reset, never committed, and the base's
  bytes are written back after the turn. Assignment is a salted hash of the work id
  (`seat_executor.claude_md_arm`), so both arms draw from the same queue in the same hours, a re-drawn
  item keeps its arm, and the buckets are independent of the P2 model pilot's. **Opus turns only**,
  so the model is not a second variable. Window: 21 Nov to 28 Nov, UTC, after the Friday read of E-f; the first 25 per arm count.
  *(Corrected before any turn ran: the first draft of this paragraph said "alternates by turn".)*
- **Sample:** 25 turns per arm (about two days at 25 turns a day). Named turns: the session ids of the
  50 turns, listed in the result.
- **Confounds:** E-f (plugins off, 9554dcf49f) is live in both arms equally, and its after-window is read
  on Friday 20 Nov, before this trial opens, so neither trial moves the other's measure.
- **Guard:** a session cannot land the draft as `CLAUDE.md`. Staging CLAUDE.md runs
  `tests/tools/test_claude_md_integrity.py` in the pre-commit gate, and the draft fails three of its
  tests (it has no operating-model section). Measured 16 Nov by writing the draft over CLAUDE.md.

## Measures, and the predictions

| Measure | Source | Prediction (minimal against full) |
|---|---|---|
| Tokens per turn, first call | `tools.tick_burn_rate` per session | **Lower by 5,000–7,200** (14,751 characters at 0.416 tokens each is 6,100) |
| Context tokens per turn, whole turn | same | Lower by 5–15%; turn length may change, so this is the uncertain one |
| Gate refusals per turn (pre-commit and commit-msg) | surgical_land logs | No difference the sample can see |
| Wall-hook denials (`.claude/hooks`) | hook logs | 0–2 per arm; no difference |
| G5 and one-way-door refusals | `background/one_way_door.py` log | 0 in both arms |
| Landed share (turns with a promoted landing) | executor ledger | Within 15 points of the full arm |
| Reverts or corrections of landed work within 7 days | git log on bound paths | 0–1 per arm; no difference |

**Direction I expect:** cheaper, with no measurable loss in these measures. **What would refute it:** the
minimal arm shows more gate refusals or wall denials by 3 or more, or lands 15 or more points less, or
any landed commit from it is reverted for a reason a dropped line names.

## The bound the sample earns

At 25 turns per arm, an event that never occurs bounds its rate below 12% per turn at 95% (rule of
three). Only a large difference in refusals or landing (about double) would show. **What this sample
cannot see:** the dropped habits are mostly about method: pre-registering, printing numbers before
shipping, naming what a divisor counts, keying a control to the property. Their failures show weeks
later as a wrong published figure, not as a refusal in the turn. So a "no difference" result licenses
dropping those lines only from the always-loaded file, not from the project: each dropped habit tied to
a named past incident moves to a pointed-at file, and the result names the evidence for each line kept.

## Built with this pre-registration

- `background/seat_executor.py`: `claude_md_arm`, the write and the restore, and the arm on the
  `RUNNING` log line. Reverse by emptying `CLAUDE_MD_TRIAL_WINDOW`.
- `tests/background/test_the_claude_md_trial_never_lands_its_draft.py`: both arms reachable and off
  outside the window or on Sonnet; the draft written and the base restored; and the draft fails
  `claude_md_integrity.check`, which is what keeps it off origin.

## Amendment, 17 Nov, before any turn ran: a golden set decides; real turns are the secondary check

*Director steer, 17 Nov ("Yes", 17:57 GMT):
`docs/staging/advisor/done/DIRECTOR_STEER_THE_CLAUDE_MD_TRIAL_USES_A_GOLDEN_SET_RUN_TWICE_AND_EACH_HANDOFF_EARNS_ITS_PLACE_2026-11-17.md`.*

- **The decider is now the golden set**, `docs/operations/EFFICIENCY_E_E_GOLDEN_SET.yaml`: ten seat
  tasks with inputs and pass criteria fixed on 17 Nov (a staging draw, a fidelity change at the wall,
  a commit through the gates, a knowledge-first build, an escalation to `for_the_director`, a G5
  refusal, an interconnection review, and three of the dropped method habits). Each runs **twice on
  each arm**, in a sealed clone of `18f201c5bf` with no remote, via `python3 -m tools.claude_md_golden_set`.
- **The rule:** a dropped line is added back if its absence fails a task in **either** run. A task
  that fails on the full file too is a finding about the task or the file, not evidence for the cut.
  Every run is reported, not only the totals (`--report`).
- **The real-turn split above stays**, 21–28 Nov, as the secondary check; it no longer decides.
- **What the set cannot see**, said before it runs: 20 runs per arm bound a never-seen failure below
  about 15% per run at 95% (rule of three), pooled across tasks; two runs per task catch a flaky failure, not a rare one. Several
  checks read words (a refusal, an escalation), so a run whose grade looks wrong is re-read from its
  kept transcript and corrected beside its row.
- **My prediction**, written before any minimal-arm run: the minimal arm fails g08 (print the numbers
  before the test) or g09 (two changes, one move) in at least one run, because those habits live
  only in the dropped section; it passes g02, g03, g05 and g06, whose rules it keeps.

## Amendment, 17 Nov, before any golden run: each dropped line's lineage predicts what breaks

*Director steer, 17 Nov ("Yes", 19:16 GMT):
`docs/staging/advisor/done/DIRECTOR_STEER_EVERY_CLAUDE_MD_RULE_CARRIES_ITS_LINEAGE_AND_EVERY_TRIAL_ITS_MODEL_2026-11-17.md`.
Written before any counted golden run: `docs/operations/efficiency_e_e_golden_runs.jsonl` does not yet exist.*

The lineage of every CLAUDE.md rule is in `docs/operations/EFFICIENCY_E_E_CLAUDE_MD_LINEAGE.md`, one line
each. Its numbers are used below. Each golden run row now records the model and CLI version **that ran**,
read from the transcript's init event (`tools/claude_md_golden_set.py::run_identity`). The result reports
"observed" per line against these predictions, on Opus 5.5 with the CLI version from the rows.

**The 34 dropped lines and what their lineage predicts.** "Case" is the golden task that can show the
break. Where a named incident has no case, the reason why not is given.

| # | Dropped line | Lineage predicts, on the minimal arm | Case |
|---|---|---|---|
| 8 | Finishing is not the end of the turn | A turn that ends on an offer ("say go and I start") | g05 (its `shall I` check); g01 for an early stop after archiving |
| 9 | Prefer measuring | Nothing a task can see. GAP origin | none: no incident to cast |
| 13 | The 30 Aug "why" paragraph | Nothing, if rule 10's condensed form holds | g04 |
| 14 | Smallest mechanism | A register or watcher built where one leg would do | none. The 28 Aug register needed a multi-hour build to show. A sealed 45-minute task cannot reproduce it |
| 15 | Say what it is before measuring | An undefined quantity differenced and published | none. Bill shock took weeks of published runs to show. A sealed task has no publish loop |
| 16 | Knowledge has three sides | Nothing a task can see. The practitioner is the director, absent from a sealed run | none: the incident's input is his correction |
| 17 | K4: search Ofgem before asking | A regulatory question escalated that the commons answers | g05 in part (escalation content). No dedicated case: no fixed regulatory question was chosen on 17 Nov |
| 19 | F11 err against the thesis | Nothing a task can see | none: no named incident |
| 20 | R5 a run answers a stated question | A run launched with no question | none: sealed tasks launch no runs |
| 21 | Print the numbers first | **Test written before any table at real inputs** | g08 |
| 22 | Two changes, one move | **A cause attributed to one of two changes** | g09 |
| 23 | A mutation that does not fire | Nothing, unless the turn writes a control | none: no task asks for a mutation test |
| 24 | A rarely-taken branch, assert it can be taken | A guard tested only for refusal | none. The 4 Sept case (`1b98c83609`) needs a guard module the base does not carry. Candidate for a later set |
| 25 | Key a control to the property | A control pinned to today's value | g07 in part. Its 35,000 assumption is a property test |
| 26 | Say what each number counts before dividing | A count over a different count | none. The 28 Aug case (`7bb9daa465`) needs the A/B artefact, which is not in the base. Candidate |
| 27 | Refusals name their reason | Nothing a task can see. GAP origin | none |
| 28 | Fail closed, on the surface | Nothing in these tasks: none publishes | none |
| 29 | Look for the parked atom | A new atom minted beside an existing one | none. No task mints. g01 is a staging draw only |
| 30 | Finish the file before committing | A commit refused for an unfiled finding | g03 |
| 31 | Correct yourself beside the claim | Nothing a task can see | g09 in part |
| 32 | Write for the next session | Nothing a task can see. GAP origin | none |
| 35 | Never ask without recommending (guard) | Nothing: `recommendation_guard.py` refuses a bare ask in code | g05 |
| 39 | End-to-end check | Nothing in these tasks. It is mechanised in the Monday close | none: weekly, not per turn |
| 40 | Transparency (stretch log, `for_the_director`) | An escalation written somewhere other than `for_the_director` | g05 (`director_concerns --raise`) |
| 41 | G8 his words; yes and go | Nothing: no task carries his words | none: a sealed task cannot carry his authority |
| 42 | NTFY mothballed | A `send_ntfy` call, which is harmless: mothballed in code | g05 would show it in the calls. Not graded |
| 43 | Silence is validation | A hold awaiting approval | g05 |
| 44 | No new gate on his path | Nothing a task can see | none: no task asks for a new channel |
| 45 | Escalate in `for_the_director`, never in the window | **A question in the final text** (the 16 Jul P0 wall) | g05 |
| 70 | Interconnection review | **The CLAUDE.md size assumption missed** (the VAT shape) | g07 |
| 77 | Cache reads are the bill; serial; never poll | More forks or polls: cost, not a failed task | none in the set. The real-turn split's tokens-per-turn measure covers it |
| 78 | Route spawned agents by model | Search agents on Opus: cost only | none: the same tokens measure |
| 80 | Roster of daemons and timers | Nothing a task can see | none |
| 81 | No local model | Nothing: there is no endpoint left to call | none |

**What this says, before the runs.** Lineage predicts a visible break on four cases: g08 (21), g09 (22), g05
(8, 45) and g07 (70). That is wider than the 17 Nov prediction above, which named only g08 and g09. Both stand, and each is graded.
Twenty dropped lines have no case:
- six because a sealed turn cannot reproduce the incident, which took weeks, a publish loop, a run or
  the director (14, 15, 16, 20, 39, 41);
- four with no named incident (9, 19, 27, 32);
- two that are cost only, which the real-turn tokens measure covers (77, 78);
- six that no task exercises (23, 28, 29, 44, 80, 81);
- two named incidents with a feasible case the set does not carry (24, 26).

**So a clean golden result licenses dropping those twenty from the always-loaded file, and not from the
project.** That repeats the bound already written above. Cases for 24 (`1b98c83609`) and 26
(`7bb9daa465`) would change the decider after its 17 Nov fix, so they are listed as candidates, not added.
