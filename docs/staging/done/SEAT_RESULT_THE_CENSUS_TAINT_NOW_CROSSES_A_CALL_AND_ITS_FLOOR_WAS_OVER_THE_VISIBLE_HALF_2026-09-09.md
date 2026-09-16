**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The census taint now crosses a call, and the floor it held was over the visible half

Discharges the Lane 0 direction `census-taint-does-not-cross-a-call-boundary`. That direction asked
for one of two things — fix the interprocedural blind spot, or write it down as a named limit the
way the nested-function case already is. **It is fixed**, and the residue that remains is named.

## The two instances the direction pointed at, both live, both now correct

`tools/substring_source_scan_census.py` computed taint per SCOPE out of ASSIGNMENTS only. A
parameter is never assigned, so it could never be tainted, so nothing done to it was ever a match
site.

1. **False negative.** `capability_index._wire_edges` reads each module's source and hands it to
   `_path_references(text, ...)`, which regexes it. The census reported nothing. It now reports
   `_path_references` *and* `_dotted_invocations`, which is the same shape one line below.
2. **False positive.** `publisher_budget.declared_publisher_budget_seconds` was reported as reading
   Python by substring. What it holds is a dict of integers parsed by the module's own
   `_module_int_constants(source)` — but `ROUTERS` was matched against the call names in the
   caller's expression, which sees `_module_int_constants` and not the `ast.parse` inside it. The
   row is gone. `tests/saas/test_sourced_acquisition_costs.py::test_the_debt_register_cannot_
   outlive_its_debt` was the same shape and went with it.

## Call-site sensitivity is the whole mechanism, not a refinement

The obvious build is a per-function summary: seed every parameter, ask what comes back. **That
build keeps the false positive.** `_module_int_constants` calls `_evaluate_int(node.value, known)`,
and with both parameters seeded that helper returns something tainted, so `known` is tainted, so
the function reads as returning text and never launders. Seeded from the ACTUAL arguments,
`_evaluate_int` is reached with nothing tainted — because `node` came out of `ast.parse` — `known`
stays clean, and the helper reads as the parse it is. Recorded because the cheaper design is the
one you reach for first and it silently does not work.

## A second predicate was per-scope and crossing only one caught nothing

Built, measured, and found insufficient: with taint crossing but `_reaches_the_tree` still
per-scope, **the drawn instance stayed invisible.** `_wire_edges` is handed the repository root as
a parameter named `base` — not `root`, `tree`, `repo` or `project`, which is the four-name guess
`_root_parameter` makes — so every clause of "does this read the repository" answered no about the
one function that demonstrably does. The answer now comes from the call graph: a scope reaches the
tree if it says so itself, or if anything that reaches the tree calls it. `_root_parameter` stays
as the direct clause; it still answers for a function nothing in its own file calls.

**The mutation that removes this clause survived every other leg in the file.** That is what put
`test_a_scope_handed_the_ROOT_by_a_caller_is_reading_the_tree` in, and it is a missing test rather
than an equivalence: without the clause the real tree loses `_path_references` entirely.

## The number, and the one I refused to ship

Measured on a clean `HEAD` extract, never the shared tree, which holds another lane's rewrite of
`background/self_clearing_alarm_census.py` and is red on a stale row that does not exist at `HEAD`.

| | rows | gained | lost |
|---|---|---|---|
| `HEAD` (per-scope) | 187 | — | — |
| **shipped** | **352** | 165 | 2 |
| *also following text back OUT of a call* | *408* | *221* | *2* |

The third row was built and rejected. Letting raw text cross a call in the RETURN direction means a
helper that reads a file, parses JSON and returns a **dict** makes every `"key" in payload` in
every caller a substring match over file source — the container-membership false positive this
census's own docstring already records, multiplied by the helper's caller count.
`tests/tools/test_generate_value_arms_data.py` alone went from 2 rows to 57, and essentially none
of the 221 were this class. A floor that grows 2.2x in false positives is not a stricter floor, it
is a floor nobody reads, and the one row this turn was drawn for would have been shelved behind
221 others. **The return direction is shut and written down as a limit**, beside the
nested-function limit already pinned in the suite, and it is reachable again the day the
container false positive is separated from the text one.

An earlier draft was worse and is recorded for the same reason: attributing a helper's match to its
CALLER gave 152 rows in which every entry point that transitively reaches a grep was a member and
the function holding the match was named in none of them. A row is a specific control, so the
control is the function the match is in.

**The 165 are not new controls and not a regression.** They are what the per-scope rule could never
see. The floor was a floor over the visible half, and a green census meant less than it read as —
which is exactly what the direction said.

## Named limits, because a census that cannot state its coverage is the thing being fixed

Three, all in the module docstring: a call into ANOTHER module; a call spelled as an attribute
(`self._helper(text)`, `mod.helper(text)`), since only a bare `Name` resolves against this file's
defs; and a chain deeper than `_CALL_DEPTH` or one that recurses. The unknown summary is
**asymmetric on purpose** — an unresolved call never launders, so it can never excuse a member; it
can hide one, and that is the residue.

## What the fix cost the census about itself

The module docstring recorded a prior — that `tools/canon_drift_check.py` and
`tools/capability_index.py` are NOT members — as evidence the measurement was not fitted to a
guess. **That dismissal was wrong, and it was wrong by the blind spot being fixed here.** Both are
members. The measurement that refuted the original guess was taken with a rule that could not see
across a call, so what it established was that neither file scans by substring *in one scope*. All
three layers are kept beside each other in the file, because the point of the note is that a prior
survives its own refutation being refuted.

## Evidence

`tests/architecture/test_a_control_reads_python_as_code.py`, 11 legs, poison round first. Five
mutations, all killing after the fourth was found surviving:

| mutation | killed by |
|---|---|
| arguments seed no parameters | partition leg + `..._named_for_the_helper...` |
| a local laundering helper does not route | partition leg (`test_local_parse_helper.py` becomes a member) |
| seed every parameter regardless of the call site | `..._called_with_NOTHING_tainted...` |
| tree-reach direct clause only, no call graph | partition leg + `..._handed_the_ROOT_by_a_caller...` |
| helper sites attributed to the caller | `..._named_for_the_helper_and_not_for_its_caller` |

## What is next

Nothing blocking. The container-membership false positive is the thing standing between this census
and the return direction, and it is a separable piece of work: `key not in parsed_dict` and
`token not in source_text` are the same AST and different questions. Whoever takes it should read
the 408-row measurement above rather than re-taking it.
