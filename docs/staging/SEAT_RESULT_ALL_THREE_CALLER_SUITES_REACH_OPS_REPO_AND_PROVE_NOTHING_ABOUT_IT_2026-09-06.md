**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: all three caller suites reach `ops_repo` and prove nothing about it

**Measured 2026-09-06 00:50 BST, delivery seat, isolated worktree at `af958429e`, claim id
`converged-battery-next-subject`. Pre-registration:
`SEAT_PREREG_DOES_A_CALLER_SUITE_THAT_REACHES_OPS_REPO_PROVE_ANYTHING_ABOUT_IT_2026-09-06.md`,
landed at `af958429e` before the battery ran. Instrument:
`python3 -m tools.ops_repo_contract_battery`. Fourth subject of the convergence-evidence sweep.**

---

## THE FIRST RUN OF THIS BATTERY PRODUCED THIS RESULT WITHOUT RUNNING ANYTHING

It must be read before the table. At 00:47 the battery printed the pre-registered answer exactly —
`SURVIVED ALL 3 CALLER SUITES: ['M1'..'M8']` — having applied none of the eight mutations. It had
resumed a results file another lane wrote for a *different* eight contracts under the same ids at
the same default path. Cause, repair and its mutation proof:
`SEAT_FINDING_THE_BATTERY_ADOPTED_ANOTHER_LANES_RESULTS_AND_PUBLISHED_EIGHT_SURVIVALS_IT_NEVER_APPLIED_2026-09-06.md`.

Everything below is the 00:50 re-run on the repaired engine, results file
`/var/tmp/ops_repo_battery_0ef0e4ad7b86.json` (the fingerprint is now in the name). Its per-suite
timings are in the record — 1.2s to 11.6s per cell, forty-eight cells — and the first run's entire
wall clock was under thirty seconds for one pytest pass. **A run that reports nothing about how
long it took cannot be told from a run that did not happen.**

## The floors, which ran first and are what make the table mean anything

| round | result |
|---|---|
| BASELINE | all four suites green at HEAD, 0 reds to deselect |
| POISON (import-time raise) | **all three caller suites RED. The repair suite RED.** Both controls (`test_atom_notes_store`, `test_delivery_lane`) **stayed GREEN** |
| NULL (behaviour-preserving edit) | all four **behaviour only** — no suite grades this module's text |

**This is the first subject in the sweep where a whole surviving column is proved REACHABLE.**
`direction.py`'s fourth column was eight survivals in a suite that never reached the module —
UNREACHABLE, not UNPROVED, and four turns of that column could not tell the two apart. Here the
floor discriminates in both directions at once: the three caller suites go red for the subject, the
two controls do not, so the greens below were at risk and are not an artefact of a floor that
reddens everything.

## The eight contracts

| id | contract | 3 caller suites | repair suite | predicted? |
|---|---|---|---|---|
| M1 | the write REFUSES under a test process at all | all survived | **DIED** | yes |
| M2 | the refusal is the FIRST statement, before the `git add` | all survived | **DIED** | yes |
| M3 | the refusal carries its OWN TYPE | all survived | **DIED** | yes |
| M4 | ONLY a nothing-to-commit failure is swallowed | all survived | **DIED** | yes |
| M5 | a nonzero commit return code is inspected at all | all survived | **DIED** | yes |
| M6 | the push actually happens | all survived | **DIED** | yes |
| M7 | the lock is EXCLUSIVE | all survived | **DIED** | yes |
| M8 | the lock deadline is REACHABLE | all survived | **DIED** (11.6s) | yes |

**Every prediction in the pre-registration held: 8/8 survived all three callers, 8/8 caught by the
module's own suite, reachability true for all three callers and false for both controls, no
text-grading.** Nothing here refutes me and I am not going to dress that up — a uniform prediction
that comes true is a weak experiment on its own, and its value is entirely in the two floors that
say what the greens mean.

The two cells I named as genuinely uncertain — M7 and M8, the lock contracts the caller suites
really do execute, since nothing patches `ops_tree_lock` — came out as predicted too. Executing a
line is not observing it: all three callers take the lock uncontended, so neither a shared lock nor
an unreachable deadline changes anything they assert. **That is the mechanism of this whole class in
one cell.** Reaching the code, importing the module, even running the exact function is not
coverage; only asserting on the consequence is.

## What this establishes that the previous three subjects did not

`register_low_water` and `direction.py` established *convergence moves the code and does not move
the evidence*. `ops_repo` on 2026-09-05 established the harder sibling: *convergence left the
REPAIR at the call sites*. This run establishes the third thing, which is a statement about the
instrument rather than the subject:

**A converged module's entire caller population can reach it on every test and prove nothing about
it.** Three suites, three of three reaching, forty-eight cells at risk, zero kills. The reason is
one line repeated three times — `patch("background.<caller>.commit_and_push")` — and it is the
correct thing for each of those suites to do. No caller suite is at fault. There is no defect to
repair in any of them. **The evidence gap is a property of the convergence, not of anybody's
carelessness**, which is exactly why nothing anywhere was able to notice it.

Two subjects were a pair of accidents; four is beginning to look like the shape. But note what
carries the load in each of the four: in every case the answer came from the FLOOR, not the
mutations. Survivals are cheap and mean nothing until reachability is established.

## The one contract this subject has that no suite holds, and it is not on the table

`commit_and_push` returns early on "nothing to commit" **without pushing**, so a commit that landed
locally but whose push failed is never retried by a later identical write. The 2026-09-05 finding
filed this deliberately rather than fixing it in passing. It is not mutable as a one-line edit
against a stated contract — the module's prose does not claim the behaviour either way — so it is
absent from the eight above rather than scored as proved. **Eight green rows are eight contracts,
not a module.**

## What this does not establish

Three suites is the module's whole first-party caller population, so unlike `segment_vocabulary`
there is no sampling bound to declare. But the screen that selected the subject is a proxy, blind
to callers reached by subprocess or dynamic dispatch, and a green repair column proves the eight
contracts I chose to write down.

Both remaining ranked subjects have stale screen rows, in the same direction and for the same
reason — the sweep keeps repairing the thing it is measuring. `tools/generate_company_data.py` was
ranked `named by 0`; `tests/tools/test_generate_company_data.py` has imported two of its functions
since `cbd5f6298`. Whether the screen is now wrong, or the relocation landed after the screen ran,
is the first question for that subject and is **not** answered here.

## Next

`tools/generate_company_data.py` — 4 first-party callers, 194 reaching suites, and the screen's
`named by 0` to re-establish or refute before any battery is built for it.
