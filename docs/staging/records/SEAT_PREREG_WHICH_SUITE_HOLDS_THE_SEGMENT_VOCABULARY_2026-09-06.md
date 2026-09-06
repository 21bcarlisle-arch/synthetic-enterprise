**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: which suite is each `segment_vocabulary` contract standing on?

**Written 2026-09-06, delivery seat, isolated worktree at `fa80a1361`, claim id
`register-low-water-evidence-convergence-sweep`. Every prediction below is fixed BEFORE the
battery runs, and this file is landed in its own commit ahead of any result so that the ordering
is in the record and not in a claim about the record.**

---

## The subject and why it is next

`tools/converged_contract_screen.py` at `fa80a1361` reports 167 converged modules, 13 with no
dedicated suite, 1 with no test importer at all. Its top row by caller count is
`simulation/segment_vocabulary.py`: **8 first-party callers, 3 direct test importers, 265
reaching suites.** The drawn direction names it as the sweep's next subject.

It is the sharpest subject the screen offers for the drawn question, because the module exists to
be the *single* place a segment is normalised. If a converged mechanism's contracts stand on one
borrowed suite anywhere, this is where it costs the most: the defect the module closes is C5 and
C6 — two microbusiness accounts billed as households for the whole history, silently.

The eight callers: `arrears_engine`, `live_population`, `payment_behaviour_source`,
`population_draw`, `segment_debt_obligation`, `sme_distress`, `sme_payment_behaviour`,
`tools/segment_case_guard`.

## The suite set, and why it is these ten

Three DIRECT importers — the only suites that can *name* a contract:

* `D1 tests/sim/test_w2_15_segment_vocabularies.py` (13 tests, 0.7s)
* `D2 tests/simulation/test_segment_case_normalisation.py` (49 tests, 1.1s)
* `D3 tests/simulation/test_served_segments_curriculum.py` (32 tests, 6.9s)

Seven CALLER-DEDICATED suites, one per caller that has one — they execute the body as a side
effect of testing something else:

* `R1 tests/simulation/test_arrears_engine.py`
* `R2 tests/simulation/test_population_draw.py`
* `R3 tests/simulation/test_live_population_seam.py`
* `R4 tests/sim/test_w2_11_payment_behaviour_source.py`
* `R5 tests/sim/test_segment_debt_obligation.py`
* `R6 tests/sim/test_w2_6_sme_distress.py`
* `R7 tests/tools/test_segment_case_guard.py`

`sme_payment_behaviour` has no dedicated suite of its own; its only test importer is D2, already
in the set. 265 reaching suites cannot all be run and this is stated as a bound, not hidden: the
battery grades ten suites and **a contract killed by none of these ten is not thereby proved
unheld anywhere in the tree** — it is unproved *by the suites any reader would look in*.

`grep -rl segment_vocabulary tests/` returns FOUR files; the screen says three. The fourth is R7,
which carries the module's name in fixture strings and assertion messages and never imports it.
That is the grep-is-an-upper-bound failure from the screen's own finding, live again, and it is
why R7 is scored as a reaching suite and not a direct one.

## The eight contracts

Taken from the callers' own attribute accesses, each mutated alone, each target asserted present
exactly once.

| id | the contract as the module states it |
|---|---|
| M1 | an alias maps to its OWN canon — `"sme"` is SME and never RESIDENTIAL |
| M2 | lookup is case-INSENSITIVE by construction (`casefold`) — the whole reason the module exists |
| M3 | a `CompanyBookLabel` (V2) is refused whatever it spells |
| M4 | a PRESENT-but-unknown segment RAISES; it never falls back to the default |
| M5 | `is_business` is true for SME and I&C and FALSE for a household |
| M6 | `BUSINESS_SEGMENTS` contains SME — dropping it is the C5/C6 defect itself |
| M7 | `CANONICAL_SEGMENTS` is all three segments |
| M8 | an ABSENT segment defaults to RESIDENTIAL |

## THE REACHABILITY FLOOR RUNS FIRST

Yesterday's rule, earned on `direction.py`'s fourth column: when a battery pre-registers survival,
run the poison round FIRST, because *survived* means two opposite things — the contract held, or
the line was never reached — and the flattering reading is the one that gets written down. An
import-time raise, target asserted present exactly once, every suite run under it.

**P1 — all ten suites go red under the poison.** Unlike `direction.py`, every one of the eight
callers imports the vocabulary at MODULE level (checked by reading the import lines, not
inferred), and R7 reaches it through `tools/segment_case_guard.py`'s own module-level
`from simulation.segment_vocabulary import _ALIASES, CANONICAL_SEGMENTS`. There is no
monkeypatched path here of the kind that made `test_supervisor.py`'s eight cells unreachable. If
any suite stays green, its whole column is stamped `survived_but_unreachable` and proves nothing.

## The predictions

**P2 — this subject does NOT show the one-suite shape.** The union of `killed_by` across the
eight mutations contains **at least three distinct suites**. `register_low_water` and
`run_phase3b_recalibration` both collapsed onto one file; this module has three suites that name
it and a docstring that points at a specific one by name, so if the one-suite shape is a law
rather than a tendency, this is where it should break.

**P3 — exactly one mutation survives all ten suites: M8**, the absent-segment default. Every
caller that could exercise it passes `default=None` (`live_population._norm`,
`population_draw`) or passes a segment that is present, so changing what an absent segment
defaults TO should be invisible. The other seven are each on the direct path of at least one
caller's own behaviour.

**P4 — R7 kills nothing.** `tests/tools/test_segment_case_guard.py` reaches the subject and
writes synthetic fixture trees to test the AST guard; it never asserts a vocabulary behaviour.
This is the same shape as `sim/ssp_tail_model.py` yesterday — the file that *documents* the
relationship proving none of it — and predicting it again is the only way to find out whether
that was a coincidence.

**P5 — every kill is also made by at least one DIRECT suite.** No mutation is killed exclusively
by a caller-dedicated suite. If P5 is wrong, the direct/reaching distinction the screen ranks on
loses a piece of its justification, and that is worth more than being right.

## What a survivor will and will not mean

A survivor is a missing test or an equivalence and it is never assumed to be the flattering one.
Each survivor is resolved to one of those two before the result is written, with the reason
stated. A kill says which suite holds the contract; it says nothing about whether the constant's
VALUE is right — that is a knowledge-layer question and not this measurement's subject.

## The instrument

`tools/direction_contract_battery.py` already implements this exact procedure — baseline with
reds deselected, poison floor, one mutation at a time with the target counted, restore from a
pristine copy outside the tree. Writing a second copy of it for this subject would be the precise
defect this whole sweep exists to find, so the engine is extracted to `tools/contract_battery.py`
and both subjects become specs. That refactor lands with this file, before any result.
