**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

**Discharged:** `tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_brand_new_module_selects_every_member_of_the_batch`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_staging_record_on_its_own_selects_the_discharge_control`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_an_atom_store_on_its_own_selects_the_store_falsifier_control`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_new_test_file_selects_the_ratchet_over_the_whole_test_CORPUS`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_the_module_subject_guard_is_selected_by_its_SUBJECT_and_not_by_a_stem`,
`tests/tools/test_the_gate_reaches_the_git_oracled_controls.py::test_a_commit_that_can_break_nothing_still_selects_nothing`
— the selection half. The census blindness this uncovered is NOT discharged and is filed separately.

# The seven reds are green, the gate now reaches all of them, and three of the seven were detectors over-matching rather than defects in their subjects

Closes the Lane 0 item `origin-main-carries-seven-reds-that-no-commits-gate-selection-reaches`.
Landed in three commits: `943b9b4f9`, `b305119b1`, and the commit carrying this document.

## The premise was NOT spent, and that is worth stating first

The draw reported `eff979da5` as already an ancestor of `origin/main` and flagged all three named
paths as "already landed". Both readings were true and neither meant the work was done: `eff979da5`
is where the **defect entered**, not where a repair landed. All seven reds reproduced at
`HEAD == origin/main` in this worktree before any edit. The pointer red had also **grown** since the
finding was written — one offending phrase at census time, two by the time it was drawn.

## What the seven actually were

| # | control | verdict |
|---|---|---|
| 1 | value-arms tied-pointer rung | REAL — two here-relative pointers in published prose |
| 2 | commons supersession, `[superseded]` | REAL, in the CONTROL — refusal reason was false |
| 3 | commons supersession, `[cannot_tell]` | same defect, second leg |
| 4 | empty-population ratchet | **FALSE POSITIVE ×5** — `ast.walk` read as a tree walk |
| 5 | committed-discharge citations | REAL — two stale citations, both renames |
| 6 | committed-store credits | **FALSE POSITIVE** — store says "not yet existing" |
| 7 | coverage-claim declarations | **one FALSE POSITIVE, one REAL** |

**Three of the seven were the detector reading its own subject too widely.** The finding's census
could not have known that — it ran the tests and read the failures, which is the right thing to do
and is exactly as far as running them gets you. Each is repaired at the detector, because in every
case the alternative was to add a guard that cannot fail in order to satisfy a guard that should not
have fired:

- **`ast.walk` is not a tree derivation.** `walk` is in the vocabulary for `os.walk`/`Path.walk`;
  matching the bare attribute name swept in the AST module's node walker. All five offenders matched
  on `ast.walk` and nothing else, and four of the five loop over a literal tuple written in the test
  — the shape the control's own `test_a_loop_over_a_FIXTURE_is_not_in_scope` already declares out of
  scope. Its printed remedy would have put a population floor under `('income', 'arrears', ...)`.
- **"not yet existing" is the same statement as "not yet written".** The latter was already in
  `_DISCLAIMS`; the former was not, so A51's store was judged an over-claim for choosing the second
  true wording. Identical to the failure the `_DISCLAIMS_SYMBOL` note beside it already records.
  Checked against the map, not read off the prose: `level_current: 0`, `loop_stage: build`.
- **A private constant holding a filename is not a claim.** `_claim_symbols`'s `FunctionDef` leg
  applies the public-symbol rule the module's own docstring declares; its `Assign` leg omitted it,
  and `str.isupper()` is True for a leading-underscore name because `_` is uncased. One rule, two
  spellings, and the asymmetry was invisible because only one had an instance.

## The real one that was worth having

`tools.validate_weather_world::check_era5_coverage` genuinely declared nothing, and writing the
declaration **surfaced a live conflation rather than tidying a red away**: the leg is named "every
cell carries the ERA5 columns" and computes `any(field non-empty, over any row, over any field)`, so
a cell holding wind and no cloud passes — while the module's own header says the fabric path reads
cloud cover and "a cell with temperature and no cloud cannot drive it". Both collapses are now
declared, and the field one as a derived dimension so the banner states it as arithmetic:

    collapses any_era5_column_present = wind_speed_mean_ms + cloud_cover_pct + precipitation_mm

Whether `any` should be `all` is **not decided here** — filed for the weather lane. This is the
canon's own class: it "flatters in a consistent direction, always making the coverage look better".

## The load-bearing half: the gate now reaches all seven

Measured before, over eight subject-bearing paths — the value-arms producer, the commons checker,
the reduction census, the weather validator, the A51 store, a discharge record, the weather writer,
the gap-ledger reconciler. **Every one of them reached zero of the seven.** A discharge record
selected zero tests of any kind.

Measured after, by commit shape:

| commit shape | selects | of the seven |
|---|---|---|
| a brand-new module | 44 | all five whole-index/corpus controls |
| the value-arms producer | 46 | all six |
| an atom store alone | 4 | the store-credit control |
| a staging record alone | 1 | the discharge control |
| a new test file alone | 45 | all five |
| a pure regenerated-output commit | **0** | none — fast path intact |

Four mechanisms, and the choice of each was priced rather than assumed:

1. **`GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS`** — five always-run entries, ~31s total (0.7 / 1.6 / 7.1
   / 8.7 / 13.4), about 5% of the 600s the gate budgets against.
2. **`DISCHARGE_SURFACE_PREFIX`** — a staged `docs/staging/**.md`. Always-run catches a citation
   falsified by a code commit renaming the test; only this catches the commoner direction, a closure
   claimed in a pure-docs commit.
3. **One `STORE_CONTRACT_TESTS` entry** — the same two-sided argument for atom stores.
4. **`SUBJECT_TESTS`** — the 43s pointer rung, selected by its subject module only. Not always-run
   (7% of the budget for a subject ~1 commit in 50 touches); not a rename (its path is cited by
   three producer comments, a site door, two findings and an alarm log, and a record citing the old
   path would red the discharge control this same commit adds); not a derived
   "tests naming this module's path" rule — that was **measured over ten real modules**, costs a
   median of +2 files, and **does not reach this rung**, which imports the module as `gva`.

**Subject-selection as a general derivation was not re-litigated.** It was built, modelled over 40
real commits and refuted on 2026-09-10 (`SEAT_RESULT_SELECTING_A_CONTROL_BY_WHAT_IT_SCANS_IS_THE_
ALWAYS_RUN_LIST_SPELLED_DIFFERENTLY`). A list with priced reasons is what this repository already
chose for this class.

## Two corrections to my own work, kept beside the claim

1. **My null control could not fail in the direction its docstring advertised.** It asserted a pure
   output commit selects nothing and claimed that caught widening `DISCHARGE_SURFACE_PREFIX` to
   `docs/`. Running the mutation: **it stayed green.** The trigger is a conjunction of prefix and
   extension, and a `.json` probe isolates neither. Now three probes, one per clause.
2. **A mutation that did not fire was not an equivalence.** Dropping the `.endswith(".md")` clause
   also stayed green. Rather than assume the flattering reading, I counted: **six non-`.md` files are
   tracked under `docs/staging/`**, so the clause is a real narrowing with no test. Third probe added.

Nine mutation rounds in total, each reddening the leg that names its defect and green returning on
restore.

## One pre-existing control was re-keyed, and it had this repo's named defect

`test_non_mint_staging_doc_is_still_pure_data` asserted `select_targets(...) == []`. Its subject is
the MINT trigger's narrowness; the literal it asserted was a description of the tree. It **reddened
because the gate became more honest** — precisely the backwards direction CLAUDE.md names. Re-keyed
to the property it owns (a non-mint doc must not run the mint hygiene set) and mutation-proven:
widening `MINT_MARKER_PREFIX` now fires it, where before that widening was the one thing it missed.

## What is NOT claimed

- The seven are green **at this base**. Nothing here claims the tree has no other standing reds; the
  census that found these seven was scoped to one landing's wider suite run, not to the whole tree.
- The gate's selection is verified for the six commit shapes tabled above. Those are the shapes that
  falsify these seven controls; they are not an exhaustive partition of commits.
- I have not measured how many other controls sit in the class the census cannot see. That is the
  separate finding, and its first step is counting, not fixing.

## Where the census finding lives

`SEAT_FINDING_THE_WHOLE_TREE_SUBJECT_CENSUS_IS_BLIND_TO_A_GIT_ORACLED_POPULATION_AND_TO_THE_TEST_CORPUS_2026-09-22.md`,
consolidated by `background/finding_classes.py` into
`docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` and archived to
`docs/staging/done/` in the same commit — **the class document is its live home and the drawable
unit**, per that class's own disposition ("OPEN is the drawable state"). Named without a directory
prefix on purpose: an archival is what last falsified a pointer of exactly this shape, three commits
ago, and repeating the mistake in the document that reports fixing it would be poor form.

It carries a **pre-registered prediction** about what the widened predicate will return. That
prediction is written before the measurement and is there to be refuted.
