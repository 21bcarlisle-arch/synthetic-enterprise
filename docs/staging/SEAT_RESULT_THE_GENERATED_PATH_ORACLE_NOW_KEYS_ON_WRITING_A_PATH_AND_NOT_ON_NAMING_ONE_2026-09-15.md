**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
generated-path oracle

# The generated-path oracle now keys on WRITING a path, not on naming one

**Filed 2026-09-15 by the delivery seat**, holding
`teach-the-generated-path-oracle-that-writing-a-path-is-not-naming-one`. It executes what
`SEAT_RESULT_THE_FORK_IS_CLOSED_..._2026-09-15.md` left owed at item (2) and refused to do in the
tick that found it.

## What was wrong

`origin_reconcile._split_generated` exists to stop a refusal advising someone to LAND a producer's
output over what origin brings. It consulted one oracle,
`tools/file_scope_generated_paths.generated_artefacts()`, which is keyed to generated **trees** —
the `(parent, child)` segment pairs `site/data`, `docs/observability`, `docs/market_data`. A
producer's output living in an **authored** tree is invisible to it by construction.

`docs/design/orphan_baseline.json` is exactly that: written by `tools/orphan_ratchet.py --freeze`,
a photograph of a scan, and on 2026-09-15 the single path holding the shared tree behind origin.
The refusal called it this tree's uncommitted work and led with the `isolate_hunks` /
`surgical_land --content` recipe. Landing that photograph drops whatever rows origin's later freeze
recorded — the same defect `_split_generated` was written on 2026-09-09 to prevent on
`site/data/value_arms.json`, arriving through the one door the tree-keyed oracle cannot watch.

## What was built

`written_artefacts()` — a **third** function beside `generated_artefacts()`, not a widening of it,
and nothing in `violations()` / `gate_violations()` reads it. `GENERATED_TREES` is untouched, so
the fail-closed `file_scope` starvation gate that blocks commits and its ten-entry frozen debt list
stay keyed to exactly the set they were measured against;
`test_the_file_scope_GATE_does_not_consume_the_write_keyed_set` makes that a control rather than an
intention — it computes the gate's verdict with the new oracle replaced by a raiser.

The property is the **write site**, never the name. Authored paths are assigned as module constants
all over this repository, and the remedy a consumer applies to a generated path is REVERT, so a
naming-keyed classifier would quietly discard a lane's real work — a worse failure than the one
being fixed, because it destroys rather than over-warns. The evidence demanded is `.write_text` /
`.write_bytes`, an `open` in a rewriting mode, or an `os.replace`-shaped destination, reached by a
constant that statically resolves.

`_split_generated` then consults the **union**. Neither oracle subsumes the other: 180 paths are
tree-keyed, 144 are write-keyed, and the union is 226.

## Three things the measurement changed, each of which was a live false answer

Printed at real inputs before the formula was fixed, per the rule about printing the table first.
Every one of these was found by looking at the output, not by thinking about the code.

1. **Scope.** A module-wide name map read `Path(p).write_text(...)` inside
   `supervisor._record_harden_cooldown` — where `p` is the cooldown file — against a `p` bound to
   `DIRECTOR_AXES.md` in a different function, and reported **the director's axes** as a generated
   artefact. One-letter destination names are everywhere here, so a flat map does not blur: it
   manufactures the exact misclassification the oracle exists to avoid, on the most expensive paths
   in the repo. The map is now per-scope.
2. **Append is not a rewrite.** `"a"` was in the writing modes, which put
   `docs/direction/decisions.jsonl` — the director's own decisions, appended one line at a time —
   on the revert side. The reason a revert is cheap for a generated path is that a run makes it
   again; an accumulated record cannot be un-lost. Rewriting modes only.
3. **Written and still not reproducible.** Two paths survive the write test and are still nobody's
   photograph: `docs/design/maturity_map.yaml` (`pull_forward_proposal` edits one atom's
   `loop_stage` in place — a lane's uncommitted level move lives there) and
   `docs/design/DIRECTOR_CANON.md` (`director_twin` rewrites it to record an overturn; the words are
   the director's). Both are carved out by name with the reason attached, and
   `test_the_not_reproducible_carve_out_is_load_bearing_and_can_only_shrink` reds on a member
   nothing writes any more, so the carve-out cannot become a place exceptions go to be forgotten.

A fourth reading was a genuine agreement rather than a correction:
`background/derived_artefact_register.REGISTER` is a hand-curated list of three `docs/design/*.md`
files that are rendered rather than authored, built by a different lane for a different purpose.
All three are in the write-keyed set, and that is asserted as a control — an independent oracle
agreeing is evidence; my own fixture agreeing with itself is not.

## The verdict at the path this was filed for

```
the 1 GENERATED path(s) (docs/design/orphan_baseline.json) are a PRODUCER'S OUTPUT, not work --
do NOT land them: ... Clear them with `git show HEAD:<path> > <path>`, then let the fast-forward
install origin's copy and the producer regenerate
```

The landing recipe is absent from that clause, which is the whole point; the authored leg still
carries it, which is the partner that stops the fix being asymmetric.

## A third state the old note could not express

With two oracles there is now a half-answer: one oracle answers and one dies. The old note was
two-valued and would have said `UNSPLIT` about a list that was in fact half-split — a reader then
re-checks paths that were already classified and trusts the ones that were not. The note is
composed where which-half-failed is known, says `PARTIAL`, names the missing oracle, and keeps the
split the surviving one could still make. The fail-soft direction is unchanged and still
deliberate: this output is remedy prose, not a gate, so an oracle that cannot answer must not stop
the tree.

## What is NOT owed

Nothing on the shared tree. `docs/design/orphan_baseline.json` is uncommitted there and is the
orphan ratchet's to rewrite; reaching into it from this isolated worktree is the sweep the
isolation exists to prevent. What changes is that the next reader of that refusal — human or
daemon — is told to revert it rather than to land it.

## Gap named rather than papered over

A path handed to a helper (`_write_json(BASELINE_PATH, data)`) and written one frame down is not
found: that needs interprocedural reach this scan does not attempt. Such a path stays classified
**authored**, which is the safe direction — the consumer offers a landing where a revert would have
done, rather than a revert where work would be lost. Stated in the docstring so the next session
reads it as a bound and not as a complete answer.
