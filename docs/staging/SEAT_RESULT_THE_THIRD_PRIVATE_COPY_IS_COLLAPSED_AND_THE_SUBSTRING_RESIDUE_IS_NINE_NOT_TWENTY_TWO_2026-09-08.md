**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The third private copy is collapsed, and the residue is nine controls, not twenty-two

Continues `SEAT_FINDING_A_SOURCE_SCANNING_CONTROL_THAT_MATCHES_BY_SUBSTRING_IS_WRONG_IN_BOTH_DIRECTIONS_AND_TWO_OF_THEM_ARE_WALLS_2026-09-08.md`,
whose **What is next** named two open items. Both are answered here.

## The shared tree did not have the work it was asked to build on

`tools/python_code_text.py` was at `origin/main` and **absent from the shared working tree**, which
was two commits behind. Every module the two skipped commits added was missing from disk while
being live in the record — the shape already filed as *a mixed reset onto a moved origin leaves
every file the skipped commits added absent from disk*. A plain `git merge --ff-only` refused: two
files another lane holds dirty, plus an untracked staging copy of a doc `origin` now tracks.

Imported via `surgical_land --merge origin/main` (`fe5c40f53`), which is the door for exactly this:
the merged tree is computed by plumbing, gated, and `merge_dispositions` moves only the paths the
working tree is clean on. The other lane's two dirty files were left alone. **This is worth naming
because the drawn work was unbuildable until it was done, and nothing in the doorbell said so.**

## Item one: the census had already given up its copy; the test had not

The finding said both `tools/launch_shape_census.py` and
`tests/background/test_the_seat_executor_stands_down.py` still carried private copies. **One was
already stale when written** — the census imports `prose_string_ids` at line 45 and its comment
records the collapse. Only the test's `_python_strings_and_argvs` was left.

It is now `code_strings(tree)` in `tools/python_code_text.py`, built from the same two primitives
the blob form uses (`prose_string_ids` + `_argv_joins`).

**The list form is NOT `searchable()` and must not be collapsed into it.** `_python_invokes`
searches each string separately and runs `_UNIT_START_RE` over it. Against one blob a pattern can
straddle two adjacent constructs and match text no running line emits — a false red on a wall, and
false reds are what got the invocation list widened three times.

One behaviour changed: the old copy dropped only a body's FIRST statement, `prose_string_ids` drops
every bare `Expr(Constant(str))`. A superset, and it costs no coverage — a discarded expression
cannot invoke, import or read anything.

**Reachability proved before the battery.** Poisoning `code_strings` reds the WALL, not just the
helper's own suite: dropping `_argv_joins` fires `test_the_documented_mutation_actually_fires` and
`test_naming_the_unit_and_starting_the_unit_are_told_apart`; keeping prose fires
`test_prose_about_the_executor_is_not_an_invocation_of_it` and
`test_the_only_thing_that_invokes_it_is_the_declared_schedule`. That is the wiring, not the
estimator — the catalogued trap the previous turn fell into on the arrears leg.

Three new legs on the helper, each killed by its own mutation (flatten → 2 legs; narrow prose back
to docstrings-only → exactly 1).

## Item two: the residue, and my first census was wrong the same way the class is

The finding left the tight/loose gap (12–31) unresolved. Screened at HEAD: **28 hits, of which 9
are candidate members.**

| | n | |
|---|---|---|
| Subject NAMES `*.py` | 5 | `test_no_committed_store_claims_an_unlanded_falsifier`, `test_env_constant_sync_guard`, `test_process_reconciler`, `test_substep4_exit`, `test_measure_publish_gate_subject_cost` |
| Subject is an UNFILTERED walk, so includes `.py` | 4 | `test_a_wait_is_written_one_way`, `test_pull_forward_proposal`, `test_brand_compliance`, `test_surgical_land` |
| Subject is not Python (`.md`/`.json`/`.yaml`/site output) — legitimate | 19 | left alone |

**The second row is the finding.** My first pass returned 5, because the classifier matched
`*.py` and was blind to `rglob("*")` — which walks Python source and three other kinds at once.
That is the *aimed-left* shape verbatim: a screen for the class, written as a substring over the
concept's usual spelling, missing the members spelled another way. It found itself.

`tests/architecture/test_a_wait_is_written_one_way.py` is the one to read first: it enforces a
CLAUDE.md-listed rule (*never hand-roll `pgrep`*) over an unfiltered `rglob("*")`. This turn hit
that rule's live hazard from the other side — `pgrep -af surgical_land` returned three sibling
Claude sessions whose PROMPT TEXT names the tool, and no running process. A control keyed to
`"pgrep" in text` cannot tell that apart from a call.

**None of the nine was read line by line and none is claimed clean.** The five fixed instances all
looked legitimate from the screen too.

## One of the nine, done (same turn)

`tests/architecture/test_a_wait_is_written_one_way.py` was a member, and its **allowlist was the
tell**. The single row excused `tools/wait_for.py` — *the mechanism this control points at* —
because its docstring quotes the broken form it replaces. That is the class wearing an exemption:
one row per accurate comment, until the allowlist is the control.

`_scan` now reads `.py` through `searchable` and `.sh` as raw text. **`ALLOWED` is empty and the row
was retired, not left behind**, and the whole-tree leg is still green without it — which is the
evidence the exemption was never needed, only the substring reading was.

`_scan` takes a `_root` so the new legs run the PRODUCTION scan over a planted tree rather than
calling `searchable` themselves. Mutations: drop `searchable` → 2 legs red (including the whole-tree
one, since the allowlist is gone); skip `.py` → the poison-round leg red; drop `.sh` → the shell leg
red.

**One mutation SURVIVED and it is an equivalence, established by running it.** Routing `.sh` through
`searchable` too changes nothing: `searchable` fails closed on unparseable source, and a shell
`until`/`while` line is never valid Python. So the suffix test is not what protects shell coverage —
fail-closed is. Recorded in the leg rather than left as a flattering silence.

## What is next

- **Eight left.** `test_pull_forward_proposal`, `test_brand_compliance`, `test_surgical_land`
  (unfiltered walks), and the five that name `*.py`. None read line by line.
- The screen is still a substring over test source and will keep being wrong in both directions.
  If a third sweep is needed, write it as an AST guard over the scan's SUBJECT expression — the
  census that beats the manual pass — rather than a fourth regex.
