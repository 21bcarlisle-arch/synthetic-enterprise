**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The residue is five members, not eight, and two of the fixes were missing tests

Continues `SEAT_RESULT_THE_THIRD_PRIVATE_COPY_IS_COLLAPSED_AND_THE_SUBSTRING_RESIDUE_IS_NINE_NOT_TWENTY_TWO_2026-09-08.md`,
whose **What is next** left eight controls named and none read line by line. All eight are now read.
Five were members and are fixed; three were not members.

## The premise was half spent, and the doorbell did not know

The drawn item asked for two things. The first — collapse `_python_strings_and_argvs` in
`tests/background/test_the_seat_executor_stands_down.py` — **was already done at `50ce6ace2`**, the
commit the doorbell itself cited. The file imports `code_strings` from `tools/python_code_text.py`
at line 25 and the alias at line 447 is a one-line binding with the reasoning kept beside it. Only
the second half — reading the residue — was live.

## The census resolves, and the screen was wrong in both directions a third time

| Verdict | n | |
|---|---|---|
| Member, fixed this turn | 5 | see below |
| Not a member | 3 | `test_brand_compliance`, `test_surgical_land`, and the `rglob` the screen flagged in `test_pull_forward_proposal` |

- **`test_brand_compliance`** walks `.html`/`.css` only — `rglob("index.html")`, and a `glob("*")`
  filtered to `{".html", ".css"}`. Its subject is not Python. The screen's loose row caught it on
  the shape of the walk and not on what the walk reaches.
- **`test_surgical_land`** globs `surgical-land-*` under the temp dir and reads an owner marker,
  and elsewhere compares fixture-repo files for exact equality. No source scan.
- **`test_pull_forward_proposal`** IS a member — but not at the line the screen pointed at. The
  `tree.rglob("*")` at line 142 is `os.utime` over a tmp fixture, not a scan at all. The member is
  `test_the_draw_does_not_consult_this_module` sixty lines earlier in the file's tail, which the
  screen never looked at because the file had already been classified.

**That last one is the finding.** The screen classified a FILE and the class lives in a TEST. Two of
its three "unfiltered walk" rows were false positives and its one true positive was true for the
wrong reason. This is the third consecutive pass in which the screen for this class exhibited the
class — first `*.py` blind to `rglob("*")`, now a file-level verdict blind to which test inside it
does the scanning. The standing recommendation from the previous result holds and is now stronger:
**if a fourth sweep is wanted, write it as an AST guard over the scan's SUBJECT expression.** I did
not write one this turn — the population was small enough to read, and a guard whose census is five
rows does not yet pay for itself.

## The five, and what each was wrong about

1. **`test_process_reconciler::test_no_reaper_or_interactive_claude_kill_path_exists_anywhere`** and
   2. **`test_substep4_exit::test_reaper_absent_no_kill_path_in_background`** — verbatim twins, both
   scanning raw source for `os.kill(` / `signal.SIGTERM|SIGKILL` / `def reap_orphan`.

   **The live evidence is that this safety wall is green on punctuation.** Two background modules
   name `os.kill` in prose today, both to record that it is *not* used: `worker_seat.py` says *"NO
   reaping / process-killing (os.kill, signal, pkill)"* and `worker_tick.py` says *"NOT
   os.kill/signals"*. Neither fires only because the next character is `,` and `/` rather than `(`.
   Written the way a sentence naturally carries a parenthesis, each is a red on the control between
   this repository and an exit-143 console kill. The old docstring **conceded the hazard in prose**
   — *"the word may appear in docstrings/OOM-classification strings"* — instead of fixing it, which
   is the exemption-by-narration shape the wait-rule allowlist wore last turn.

   The scan now has **one home**, `kill_path_offenders(root)`, and `test_substep4_exit` imports it.
   Two verbatim copies contradicted that module's own docstring, which calls itself the end-to-end
   re-assertion of §9 and names `test_process_reconciler` as the piece-wise mechanism. A private
   copy is also how this class survived four instance fixes.

3. **`test_pull_forward_proposal::test_the_draw_does_not_consult_this_module`** — `"pull_forward_proposal"
   not in src`, a NEGATED substring, which is the dangerous half. A comment in `supervisor.py`
   saying *"the draw must never consult pull_forward_proposal"* — the most natural way to record
   this very rule beside the code it governs — was a red. **The rule punished its own
   documentation.** It was blind the other way too: `import_module("background.pull_forward" +
   "_proposal")` contains no such substring. "Must not consult" is a property of the import graph
   and is now asked of `imported_modules`.

4. **`test_env_constant_sync_guard::test_registry_covers_every_grep_visible_env_constant`** — a
   `^`-anchored regex per line. The anchor made this look safe and it does exclude comments, which
   are indented by their own `#`. **It does not exclude a docstring**, where a worked example sits
   at column zero exactly as real code does.

5. **`test_measure_publish_gate_subject_cost::test_any_test_module_that_enters_the_exclusion_redirects_the_lock`**
   — three substring legs, the third negated. A module that drove the measurement and did NOT
   redirect `RUN_LOCK_FILE` was excused outright if any comment in it mentioned `RUN_LOCK_FILE` —
   and the comment a careful author writes there is *"this does not touch RUN_LOCK_FILE
   because ..."*. **The explanation for the defect was also its cover.**

## Two of the five were MISSING TESTS, not equivalences, and I established which by running it

Reverting the fix on (4) and on (5)'s recruitment leg left the live suites **green**: no background
docstring happens to carry an unindented env-read example today, and no test module happens to
carry the excusing comment. The flattering read is "equivalence". It is not — the fix changes
behaviour on input the tree does not yet contain, which is a missing test. Both now plant that
input and run the PRODUCTION scan over it via a `root` parameter, rather than calling `searchable`
themselves — the catalogued trap of controlling the estimator and not the wiring.

**One mutation survived twice before it fired, and the second survival was my own fixture.** The leg
distinguishing `imported_modules` from `searchable` first used a module whose comment named
`_run_measurement` — but `searchable` blanks comments, so both readings agreed and the leg proved
nothing. Corrected, the input is a module that *shells out*: `searchable` rejoins argv literals by
design, so it reads as naming the measurement and gets recruited, while the import graph correctly
does not. It is genuinely not a member — the population is modules entering `_publisher_exclusion`
IN PROCESS, and a subprocess cannot inherit an in-process lock redirect anyway.

Battery: drop `searchable` from the kill scan → 1 red (the poison round; the whole-tree leg stays
green, which is the honest statement — today's tree has no prose that fires it). Flatten it → 2.
Break fail-closed on unparseable source → 1. Substring back in the draw check → 1. Drop `searchable`
from the env sweep → 1. From the driver scan → 1. Drop `imported_modules` → 1.

## The ratchet delta is one, not two, and the second is not mine

The dirty shared tree reads I001 **1308** against **1310** at clean HEAD. Banking 1308 would have
made the floor unreachable the moment this landed alone, reding every lane until a neighbour
committed. Measured in a clean `git worktree` extract of HEAD overlaid with exactly this commit's
files: **1309**. That is what is banked, with the attribution written beside it. The `-1` in the
shared tree is another lane's uncommitted fix and theirs to lower — the same disposition the
2026-09-07 CM-levy entry recorded four lines above it.

`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` is red in the shared
tree and **green in the commit's own tree**: another lane's staging record claims
`site/test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer.py`, which is
in no commit. Not mine, not fixed here, named so the next reader does not re-diagnose it.

## What is next

- **The class is closed on the enumerated population.** All nine screened members are read; five
  fixed this turn, one last turn, three were never members.
- The residue that remains is the SCREEN, not the controls. It has now been wrong in both
  directions three times running. An AST guard over the scan subject is the way to a fourth pass —
  but the honest next step is to stop sweeping unless a new instance appears, since the population
  it keeps re-deriving is now enumerated exactly.
