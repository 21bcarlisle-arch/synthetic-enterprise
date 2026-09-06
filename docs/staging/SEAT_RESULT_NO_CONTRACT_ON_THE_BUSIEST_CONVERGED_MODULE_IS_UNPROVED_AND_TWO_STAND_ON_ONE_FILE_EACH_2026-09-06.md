**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: no contract on the busiest converged module is unproved, and two of the eight stand on one file each

> **CORRECTION, 2026-09-06 — the title is true of the ten-suite population and FALSE of the caller
> population, and the caller population is what the pre-registration asked about.** This battery's
> spec wrote `SUITES = DIRECT_SUITES + CALLER_SUITES`, so the three suites that IMPORT the module
> sat inside the verdict meant to answer *"did any CALLER prove this"* — the subject graded itself.
> **On the callers alone, three of the eight contracts are unproved: M3, M4 and M8**, each killed
> only by `W215` or `CASE`. M4 is the sharpest — three suites kill it and all three are the
> subject's own. The eight rows below are unchanged and correct; what changed is which of their
> killers count toward the question. Re-reduced from the same cells, no test re-run:
> `SEAT_RESULT_THREE_OF_SEGMENT_VOCABULARYS_CONTRACTS_ARE_PROVED_ONLY_BY_ITS_OWN_SUITE_AND_SO_WERE_BOTH_OF_FUEL_MIXS_2026-09-06.md`.
> The spec is repaired; `survived_all` here is now scored over six callers.
>
> A second correction to the same page: **`GUARD` is not the only miscount.**
> `tests/sim/test_segment_debt_obligation.py`, listed below among the suites that "reach it through
> a caller", imports `simulation.segment_vocabulary` directly at line 152 and is now declared a
> direct suite. It killed nothing in this run, so no row below moves.

**Measured 2026-09-06, delivery seat, isolated worktree at `e383c6328`. Claim id
`register-low-water-evidence-convergence-sweep`. Grades
`docs/staging/SEAT_PREREG_WHICH_SUITE_HOLDS_THE_SEGMENT_VOCABULARY_2026-09-06.md`, which was
landed in its own commit BEFORE the battery ran. Three of its five predictions hold, two are
wrong, and both wrong ones are the finding.**

Re-derivable: `python3 -m tools.segment_vocabulary_contract_battery`.

---

## The subject

`simulation/segment_vocabulary.py` — the top row of `tools/converged_contract_screen.py` by
caller count. 8 first-party callers, 3 test files that IMPORT it, 265 whose import closure
reaches it. Eight contracts, each mutated alone, each target asserted present exactly once before
the patch and asserted still present after the run, source restored byte-identical. Ten suites,
run separately. Baseline first, reds recorded (there were none).

## The reachability floor, run FIRST — P1 CONFIRMED

**All ten suites go red under an import-time raise**, in 0.6–0.7s each. **Both control suites —
`test_delivery_lane.py`, `test_atom_notes_store.py`, chosen for having no import path to the
subject — stayed GREEN under the same poison.** The floor discriminates: it is measuring the
subject and not the harness.

This matters more than it looks. Yesterday's subject produced a whole column of eight survivals
that turned out to be eight unreachable lines, and four turns of that column could not tell the
difference. Here every "survived" below is a real survival.

## The eight rows

`W215` = `tests/sim/test_w2_15_segment_vocabularies.py` · `CASE` =
`tests/simulation/test_segment_case_normalisation.py` · `SERVED` =
`tests/simulation/test_served_segments_curriculum.py` — the three DIRECT importers. The rest reach
it through a caller: `ARREARS`, `POPDRAW`, `LIVEPOP`, `W211`, `DEBTOBL`, `W26`, `GUARD`.

| contract | killers | which |
|---|---|---|
| M1 alias maps to its own canon (`"sme"` → SME) | 8 | W215 CASE SERVED ARREARS LIVEPOP W211 W26 GUARD |
| M2 lookup is case-insensitive (`casefold`) | 7 | W215 CASE SERVED ARREARS LIVEPOP W211 W26 |
| M3 a `CompanyBookLabel` (V2) is refused | **1** | **W215** |
| M4 a present-but-unknown segment RAISES | 3 | W215 CASE SERVED |
| M5 `is_business` is false for a household | 4 | W215 CASE W211 W26 |
| M6 `BUSINESS_SEGMENTS` contains SME | 4 | W215 CASE W211 W26 |
| M7 `CANONICAL_SEGMENTS` is all three | 2 | SERVED GUARD |
| M8 an absent segment defaults to RESIDENTIAL | **1** | **CASE** |

**Nothing survived all ten.** Every one of the eight contracts is proved by something. This is the
first subject in the sweep with no unproved contract, and it is the counter-example the sweep
needed.

## P2 CONFIRMED: the one-suite shape is a tendency, not a law

Eight distinct suites appear across the union of `killed_by`. `register_low_water` collapsed onto
one file and `run_phase3b_recalibration` onto one file; this module does not. **Three subjects
showing a shape and one refuting it is a tendency with a named exception, which is worth more than
a fourth confirmation would have been.**

## P3 WRONG, twice over — and the reason is worth more than the prediction

P3 said exactly one mutation would survive all ten suites, and named M8: changing what an ABSENT
segment defaults to. The reasoning was that every caller either passes `default=None`
(`live_population._norm`, `population_draw`) or passes a segment that is present.

**M8 died.** `CASE::test_the_corporate_rail_is_reached_via_the_bill_default` calls
`payment_method(None, 850.0)` and asserts `"direct_debit"`. The call sites read
`bill.get("segment", "resi")`, so an absent segment is a LIVE path through the module default, not
a defensive corner — and the test says so in its own comment. **I reasoned about the default from
the callers that override it and never asked which caller relies on it.** The prediction was made
from the two call sites I had read, and the answer was in a third.

## P4 WRONG, and it inverts yesterday's finding rather than repeating it

P4 said `GUARD` (`tests/tools/test_segment_case_guard.py`) would kill nothing. It kills **two**:
M1 and M7.

`GUARD` is the file that carries `segment_vocabulary` only inside fixture source strings and
assertion messages and does **not** import it — the grep-is-an-upper-bound case, which is exactly
why the screen scores it as reaching and not direct. It kills anyway, because
`tools/segment_case_guard.py` imports `_ALIASES` and `CANONICAL_SEGMENTS` and uses them as DATA to
decide which string literals are segment spellings. Change the alias table and the AST guard flags
a different set of lines.

Yesterday the caller whose docstring *advertised* reusing the shared code proved none of it. Today
the suite that never even imports the module proves two of its contracts. **The general statement
now has evidence on both sides and is stronger for it: a suite's apparent relationship to a shared
module — documented, textual, or absent — predicts nothing about whether it proves it, in EITHER
direction. Only mutating the contract answers it.**

Note what `GUARD` does NOT kill: M2, the casefold. The guard casefolds its own lookups
(`e.value.strip().casefold() in _ALIASES`) and so never depends on `normalise_segment` doing it.
A consumer of the alias table is not thereby a consumer of the normaliser.

## P5 CONFIRMED, and it is the sharpest thing here

**Every kill is also made by at least one of the three DIRECT suites. Not one mutation is killed
exclusively by a caller-dedicated suite.** Delete all seven reaching suites and this module loses
no evidence at all.

Two of those seven reach the subject — proved by the poison round, not assumed — and kill **nothing
across all eight mutations**: `POPDRAW` and `DEBTOBL`. `POPDRAW` costs ~39 seconds a pass and
contributed eight green cells, none of which was ever at risk. That is 5 minutes of this battery
spent measuring nothing, and it is the honest price of finding out.

`DEBTOBL` is the one that should trouble a reader: `simulation/segment_debt_obligation.py` is the
module that MINTS `CompanyBookLabel`, and its own dedicated suite does not kill M3 — the seal that
makes the type worth having.

## The finding inside the good news: two contracts stand on one file each

Module-level "well proved" hides contract-level single points, and this subject has two.

**M3 — the V2/V1 seal — is held by `tests/sim/test_w2_15_segment_vocabularies.py` and by nothing
else in the tree.** That contract is the refusal of a `CompanyBookLabel`, and the module's own
docstring calls the distinction it protects "the whole measurement": what the company RECORDED
about a customer is allowed to be wrong about them, and coercing the book label onto the canon
turns the belief-versus-truth gap into a silent identity function. Two of the three V2 labels
(`"resi"`, `"sme"`) are valid V1 aliases and would coerce silently; only `"iandc"` would raise. So
without that seal a pipe from the company's book into the canon works all the way through a
resi/SME population and blows up the first time an I&C customer appears — which is why the block
is on the TYPE and not on the string.

**M8 — the absent-segment default — is held by `tests/simulation/test_segment_case_normalisation.py`
and by nothing else.**

Both are one file away from being proved by nothing. That is the `register_low_water` shape at
CONTRACT granularity inside a module that looks healthy at MODULE granularity, and no count this
project keeps could distinguish the two.

## The repair, landed in this commit — and the table above is NOT edited to match

`tests/sim/test_segment_debt_obligation.py` gains
`test_what_this_module_mints_is_refused_by_the_world_true_canon`: every label `observed_segment`
mints is asserted to be refused by `normalise_segment`, at the MINTING site.

It was chosen over adding a second copy of the seal test somewhere convenient because this is the
one place the assertion belongs on its own merits — the module that creates the sealed type
should say what the seal is for — and because it simultaneously removes `DEBTOBL` from the list of
suites that reach the subject and prove nothing.

Mutation-proven, not asserted: under M3 the new test is now a second killer, and the previously
sole killer still fires.

```
M3 vs tests/sim/test_segment_debt_obligation.py:  rc=1  [test_what_this_module_mints_is_refused_by_the_world_true_canon]
M3 vs tests/sim/test_w2_15_segment_vocabularies.py: rc=1 [test_the_seal_holds_for_every_label_not_just_the_odd_one, test_the_refusal_survives_a_default]
```

It carries a partition control ahead of its refusal legs — `minted == {"resi", "sme", "iandc"}`
asserted before anything asserts what the refusal DOES — so it cannot pass by exercising one
label. And it asserts the refusal is about PROVENANCE and not spelling: the same characters as a
bare `str` still normalise. That is the leg a string-only block would fail, which is the trap the
type check exists to close.

**The table above is left as measured at `e383c6328`.** M3's row still reads `1` killer, because
that is what was true when the prediction was graded. A result table quietly updated to match its
own repair is no longer evidence that the repair was needed.

## A kill is not always evidence about the contract, and `-x` hides which

The battery runs each cell with `-x`, so a cell names the FIRST failing test, not the only one.
Read as a grade that is misleading, so the two cells where it mattered were re-run without `-x`:

* `W26` on M6 fails **12 tests**, including `test_insolvency_is_bad_debt_and_lost_supply_point`
  and `test_higher_shock_sector_fails_more_often`. Substantive proof about what the contract says.
* `W211` on M6 fails **exactly one**, and it is
  `test_advancing_pbs_leaves_sme_distress_byte_identical` — a cross-module byte-identity assertion
  that names no segment property at all. Re-measured on M1 and M2: **one failure each, the same
  test.**

So `W211` appears as a killer in three rows, and in all three its entire contribution is one
assertion that a sibling module's output is unperturbed. It proves the contract is load-bearing on
the RNG draw sequence; it proves nothing about what the contract SAYS, and it would go green the
day a mutation happened to be draw-count-neutral. **A byte-identity coupling test is a tripwire,
not a contract test, and a battery that reports only `died`/`survived` cannot tell them apart.**

## A second floor, added after this result and run against it: none of these kills is textual

Every battery in this family has assumed that `died` means "the suite executed the mutated line
and an assertion failed". Nothing established that. The next subject
(`tools/generate_grid_intensity_feed.py`) makes the gap concrete: **six of its callers read the
module's own source with `.read_text()` and walk it as an AST**, so a source mutation can redden
their suites without a line of it ever running.

So the engine gained the mirror image of the poison round — a **null round**: a source edit that
changes the bytes and adds an AST node and cannot change behaviour (`_NULL_ROUND_MARKER = None`).
A suite that reddens under it is grading TEXT.

Run against all ten suites of this subject, after the result above: **all ten are behaviour only.**
None of the kills in the table came from reading the file. `tests/tools/test_segment_case_guard.py`
was the candidate — it AST-scans `simulation/` for segment string literals — and it is indifferent,
which is the answer the marker was written to be able to get wrong (it deliberately contains no
string literal).

This is recorded here rather than in the next subject's finding because the claim it protects is
*this* result. A subject with no null round is now stamped UNKNOWN on the battery's own summary
line, never as a clean bill.

## The survivors are named, and none of them is left as "probably an equivalence"

There is no survivor to resolve: every contract died somewhere. The two suites that reach the
subject and never kill (`POPDRAW`, `DEBTOBL`) are a different question — not survivors, but eight
green cells each that were never at risk, and they are named above rather than left in the table
looking like agreement.

## What this does NOT establish

**The population is ten suites out of 265 that reach the module.** A contract killed by none of
these ten would be unproved *by the suites a reader would look in*, which is not the same claim as
unproved anywhere in the tree. No contract was in that position here, so the bound did not bind —
but it is stated because the next subject's might.

A kill says which suite holds a contract. It says nothing about whether the contract's VALUE is
right: that the alias table maps `"ic"` onto `"I&C"` is proved; that `"ic"` *should* be an alias is
a knowledge-layer question and not this measurement's subject.

And it does not generalise from four subjects. `register_low_water` and
`run_phase3b_recalibration` show the one-suite shape; `ops_repo` showed nothing proving the shared
code at all; this one shows eight suites and no unproved contract. The screen ranks 12 more rows,
and ranking is not grading.
