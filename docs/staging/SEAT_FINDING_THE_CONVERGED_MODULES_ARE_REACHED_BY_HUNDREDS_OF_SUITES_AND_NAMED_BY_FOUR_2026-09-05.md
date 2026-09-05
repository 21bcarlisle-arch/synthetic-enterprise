**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the converged modules are reached by hundreds of suites and named by four, and every count this project keeps reports the first number

**Measured 2026-09-05, delivery seat, from an isolated worktree at `5ab0af684`. Claim id
`register-low-water-evidence-convergence-sweep`. The screen is landed as
`tools/converged_contract_screen.py`, so every figure below is re-derivable by one command and
none of them is transcribed into this document as a standing claim.**

---

## The question this came from

Two turns established the shape at two subjects and neither asked whether it generalises.
`38871422b`: `background/register_low_water.py`, four callers, one contract proved by **no** suite
and two by one. `befe26b7e`: `background/ops_repo.py`, three callers, and **nothing in `tests/`
imported it at all** — every caller's suite patched the shared function by name in the caller's
namespace, so its body had never been executed by a test.

The drawn direction was to ask that of every *other* converged mechanism. Asking it properly is a
mutation battery per subject; the first thing needed is a population and a ranking.

## What the screen measures, and the column that carries the finding

`python3 -m tools.converged_contract_screen`. CONVERGED = ≥3 first-party callers. The two columns
that matter are not "is it tested":

* **direct** — suites that IMPORT the module. They can name its contracts.
* **reaching** — suites whose transitive import closure REACHES it. They execute its body as a
  side effect of testing something else.

`reaching` is the number every coverage-shaped count in this project reports. `direct` is the
number of suites that could possibly assert a contract. **Today they differ by two orders of
magnitude.**

| module | callers | named by | reached by |
|---|---|---|---|
| `background/direction.py` | 4 | **4** | **184** |
| `tools/generate_company_data.py` | 4 | **0** | **194** |
| `simulation/run_phase3b_recalibration.py` | 6 | **0** | 4 |
| `sim/risk_committee.py` | 4 | 1 | 250 |
| `simulation/segment_vocabulary.py` | 8 | 3 | 321 |

`tools/generate_company_data.py` is the sharpest instance and it is the `ops_repo` shape exactly:
**194 test files execute code that reaches it and not one names it.** A reader asking "is this
covered?" gets 194 and stops.

## The population

166 converged modules; **14** with no dedicated suite; **2** with no test importer at all. The
full ranked list is the tool's default output and is deliberately not copied here — a list pasted
into a document is a claim that starts rotting the moment it is written, and this one already did:
the same screen returned **15 and 3** one commit ago, and moved because `ops_repo` got its first
suite. **A screen that tracks its own repairs is worth more than the list it prints.**

The two remaining zero-importer modules are the ranked queue for the rest of this sweep.

## A number in the pre-registration is corrected here, beside the claim

`SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md` recorded
**161** converged modules from an ad-hoc screen. The landed screen says **166**. Neither is wrong:
the ad-hoc version analysed six roots and the landed one calls
`select_impacted_tests.build_graph`, whose `ANALYSED_ROOTS` is eight — it also counts `interface/`
and `functions/`. The 14/2 residue figures agree between the two. **Recorded rather than
silently adopted**, because the discrepancy is the only evidence that the hand-rolled first draft
was not measuring what the landed one measures, and it is the reason the tool calls the shared
graph builder instead of re-deriving it.

Two smaller corrections to the same pre-registration, both found by running the screen against it:

* It listed `tools/generate_delivery_page.py` as a caller with no suite ("no suite imports it *and*
  direction"). Two suites import both — `test_delivery_seat.py` and
  `test_the_self_audit_declared_a_correction_and_nothing_carried_it.py`. The row was wrong.
* It named four caller suites for `direction`; a `grep -rl` finds a fifth,
  `test_the_jsonl_carriers_claim_was_reasoned_from_a_sibling_and_one_of_five_was_wrong.py`. **That
  suite is not an importer.** It carries `("background.direction", "read_decisions")` inside a
  parameterised table of strings and cannot execute a line of the module. It was included in this
  turn's mutation battery before the screen caught it, where it correctly killed nothing.

## The general statement, and why a grep cannot answer this question

The two bounds run in opposite directions and must never be mixed:

* **static imports are a LOWER bound on callers** — a caller reached by subprocess or dynamic
  dispatch is invisible to the screen;
* **a grep for the module name is an UPPER bound on evidence** — it counts a name in a string
  table as a test importer.

The pre-registration's fifth suite is the second failure, live. Both are asserted as controls in
`tests/tools/test_the_converged_contract_screen_separates_naming_a_module_from_reaching_it.py`
rather than promised in a docstring.

## What this does NOT establish

**The screen ranks; it does not grade, and it must never be read as a grade.** "Has a dedicated
suite" does not mean each contract is proved — the low-water case had four caller suites and
still a contract proved by nothing, which is the whole reason this sweep exists. "No dedicated
suite" does not mean unproved. Only a mutation battery, run per caller suite separately, answers
the drawn question for a given module, and that is one subject at a time.

The tool is therefore an instrument and not a gate: no exit code, no register, no residue, and
nothing calls it on a diff. An exit code here would be a control keyed to today's answer, which is
the failure this project has filed more times than any other.

## Controls

Five source mutations on `tools/converged_contract_screen.py`, each applied alone with its target
asserted present exactly once, **all five caught, each by its own named test**: `reaching`
collapsed onto `direct`; test files counted as callers; the convergence threshold loosened by one;
`dedicated` forced empty; the transitive walk stopped after one hop. Every leg builds a synthetic
tree and never reads the real repository, so these controls cannot go green or red because another
lane landed a module. The partition control asserts a dedicated row, an undedicated row, a
reached-but-unnamed row and a below-threshold exclusion all exist **at once**, before any leg
asserts what a branch does.

No simulation output, gap value or financial figure passes through this instrument — it parses
Python imports and nothing else.
