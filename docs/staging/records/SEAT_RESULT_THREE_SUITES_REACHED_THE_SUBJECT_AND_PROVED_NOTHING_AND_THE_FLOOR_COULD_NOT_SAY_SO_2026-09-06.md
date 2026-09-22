**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: three suites reached the subject, proved nothing, and the floor could not say so

**Run 2026-09-06 by the delivery seat. Subject 6 of the convergence sweep,
`background/ops_repo.py`. Pre-registration, unrevised:
`SEAT_PREREG_WHETHER_REACHING_A_MODULE_IS_REACHING_ITS_CONTRACT_OPS_REPO_2026-09-06.md`.
Claim id `converged-battery-next-subject`. Raw: `/var/tmp/ops_repo_battery_results.json`.**

---

## The table

Eight contracts, four rooms, thirty-two cells, plus a control room and a null round.

| | ntfy_mirror | director_input_log | backup_company_data | **repair suite** | control |
|---|---|---|---|---|---|
| **poison — reaches subject?** | **yes** | **yes** | **yes** | yes | green ✓ |
| **null round — grades text?** | no | no | no | no | — |
| M1 refusal raises, not silent | survived | survived | survived | **DIED** | — |
| M2 refusal before the `git add` | survived | survived | survived | **DIED** | — |
| M3 refusal names the repo | survived | survived | survived | **DIED** | — |
| M4 identical rewrite is a clean no-op | survived | survived | survived | **DIED** | — |
| M5 a real failure is not swallowed | survived | survived | survived | **DIED** | — |
| M6 the ops lock is exclusive | survived | survived | survived | **DIED** | — |
| M7 the timeout names the lock file | survived | survived | survived | **DIED** | — |
| M8 the guard is stronger than the copies | survived | survived | survived | **DIED** | — |
| **contracts proved** | **0 / 8** | **0 / 8** | **0 / 8** | **8 / 8** | — |

All six predictions held, including P5 (no equivalences) and P6 (poison round 5.3s). The control
room stayed green, so the floor discriminates rather than grading the harness; the null round says
all four rooms are behaviour-only, so the repair's eight kills are execution evidence and not a
suite reading the subject's bytes.

## The finding, and it is about the instrument rather than this module

**Every caller suite reddened under the reachability floor and not one of them was ever at risk.**
The three callers each do `from background.ops_repo import commit_and_push` at module scope — so an
import-time raise takes them all down — and each then patches `commit_and_push` *by name in its own
namespace*, so the shared body is executed by none of them. The floor answered "this suite imports
the subject". The sweep has been reading that answer as "this suite reaches the subject", and until
this subject those were the same sentence.

They are not. There are **three** states, and the summary could print two:

1. **never imports it** — green under poison; every survivor means *unreachable*. This is
   `direction.py`'s fourth column, and finding it is what the poison round was built for.
2. **imports it and never executes the contract** — red under poison, survives everything. This is
   all three of `ops_repo`'s callers, and the battery had no word for it.
3. **executes it** — the only state in which a green cell is evidence.

State 2 is the more dangerous of the two failures, because it reads as the *good* answer. A blind
column at least announces itself as blind.

## It was already in the record, twice, unreported

Re-reading the sweep's own stored results through the new lens, without re-running anything:

| subject | suite | reaches | cells | kills |
|---|---|---|---|---|
| `simulation/segment_vocabulary.py` | `tests/simulation/test_population_draw.py` | yes | 8 | **0** |
| `simulation/segment_vocabulary.py` | `tests/sim/test_segment_debt_obligation.py` | yes | 8 | **0** |

Subject 4 carried two suites in state 2 and reported neither, because the summary only ever printed
the blind column. So this is not an `ops_repo` peculiarity — it is a reporting gap that has been
live for the whole sweep, and the evidence to catch it was sitting in `/var/tmp` since 2026-09-05.

## The repair

`tools/contract_battery.py` now computes, after the mutations and over the cells a suite actually
has, which reaching suites killed nothing — printed beside the survivors and **stamped into the
JSON** per suite (`imports_but_proves_nothing`), because a caveat kept only in a summary line stops
travelling the moment anyone reads the file. A suite with no graded cell is left out entirely: *not
yet asked* is not *answered no*, and a partial run is exactly when that conflation would be
believed. Control suites are excluded, since a control that never reaches the subject is the
control working.

This sits beside `survived_but_unreachable` (state 1) and `died_but_grades_text` (a different axis
— whether a kill came from reading the text). It is a third question and neither of those two
answers it.

## The collision, and why the spec was re-homed rather than landed beside

This lane wrote its spec as a third `SubjectSpec` in `tools/direction_contract_battery.py`, which
is what the pre-registration says. **While it ran, another lane converged that battery into
`tools/contract_battery.py`** — a shared runner plus one spec module per subject — and added the
null round. Three commits, landed to origin, invisible to this lane until the pre-land orient.

The pre-registration is left unrevised, including its now-wrong sentence about where the spec would
land. A plan corrected after the fact stops being evidence that it was written first.

The spec is re-homed as `tools/ops_repo_contract_battery.py` on the new runner. Landing it beside
the old shape would have made a second copy of a runner whose value is entirely in the repairs it
has absorbed — the exactly-once target assertion, the deselected baseline reds, the poison round,
the control room and now the null round — which is the recorded shape where a new branch that
hand-rolls what a helper centralises regresses every repair the helper holds. Re-homing also
bought the two rounds this lane had not built: the control room and the null round both ran on this
subject because they came with the runner.

**Every mutation in the table is fail-closed by construction**, and that constrained the table
rather than decorating it. The obvious M1 — delete the guard — would have left a test process with
nothing between it and `git push origin main` on the real private ops repo. M1 keeps the guard and
makes it silent, which is the exact shape two callers hand-rolled; M8 inlines a guard that still
fires inside any test body. No cell in this run could reach `origin`.

## What this does and does not say about `ops_repo`

It does **not** say its contracts are unproved. The 2026-09-05 repair suite killed all eight, and
it has now been graded rather than trusted — including its own non-vacuity leg, since a
`commit_and_push` that raised unconditionally would have survived M4 and M5 and did not.

It says the three callers prove nothing about the shared body, which was the pre-registered
question, and that **a converged module whose callers all patch it by name inherits no proof at
all** — not weak proof, none. That is a different failure from `direction.py`'s borrowed suites,
where the proof existed and belonged to somebody else.

## Next

`tools/generate_company_data.py` (4 callers) is the drawn next subject and is not run here. Its
caller columns must be read as state 2 until a mutation kills something in them, and the sibling
finding on subject 5 already warns that its converged surface may be mostly re-exports — a contract
taken from a name the callers import can belong to another module entirely.
