**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `a-level-row-cannot-be-raised-before-its-evidence-is-at-head`) · **Class:** `publish_gate_and_wedge`

# The level gate read an absent path as clean, which is the generator behind two stretches of publisher wedge, and the refusal now prints the minimum landable unit

**2026-09-09, scheduled tick, LANE 0 DELIVERY.** The drawn direction named the class: *"W2_30 last
stretch, W2_28 this stretch, same shape: a level written in the working tree on evidence that is not
in the tree, discovered 36 hours later by a lane with no part in it, as a publisher refusal with no
path in the message. The instance keeps getting cured and the generator keeps producing."*

The generator is a fail-open in `tools/level_promotion_gate.py`'s SECOND CONTROL, and it is one
command wide.

---

## 1. The generator, measured

```
$ git --no-optional-locks status --porcelain -- sim/forecast_publication.py
$ echo $?
0
```

A path that exists **nowhere** — not at HEAD, not in the index, not in the working tree —
contributes no porcelain output. The RECORDED-BUT-UNBUILT control asks exactly that question and
refuses on the worktree column, so `dirty_source_paths("")` returns `[]` and the raise reads
**CLEAN**. The control was built to catch a program verified in the tree and never committed; it is
structurally blind to a program that was never written at all.

That is why both instances surfaced downstream. The gate whose subject the raise *is* said nothing,
and the publisher's level arm caught it 36 hours later, at whichever lane happened to commit next,
with no path in the message.

## 2. What landed

`tools/level_promotion_gate.py` gains a FIFTH CONTROL and both legs the direction asked for.

**(a) The raise is refused at its own write time, naming the path.** `absent_evidence_increases`
refuses any level increase whose `file_scope` names a path the tree *this commit would create* does
not contain. The index is the right subject and the module says so out loud — it covers both
"already at HEAD and untouched" and "landing in this very commit", which `absent from HEAD` alone
would get wrong for evidence the raise lands alongside itself.

**(b) The refusal prints the MINIMUM LANDABLE UNIT** — the explicit set of paths a commit must
contain for the claim to hold — computed from three sources: the row's `file_scope`, every repo path
its **prose** cites, and every path a control in that file_scope asserts `.exists()`. Each path is
marked `present` / `MISSING` / `?`. It is printed on the new refusal *and* on the existing
unbuilt one, which is the refusal the incident actually hit.

Driven end-to-end in a `git worktree add --detach HEAD` extract, raising `B3` 0→1:

```
[level-gate] ❌ COMMIT REFUSED (a level move's evidence must EXIST in the commit that declares it):
§0: level_current 0->1 on B3_published_forecast_error_horizons raises a level on evidence that is
NOT IN THE TREE THIS COMMIT WOULD CREATE. Absent:
    sim/forecast_publication.py
    tests/sim/test_forecast_publication.py
  MINIMUM LANDABLE UNIT -- what a commit must contain for B3_... at level 1 to hold:
    [MISSING] sim/forecast_publication.py
    [MISSING] tests/sim/test_forecast_publication.py
```

The direction's benchmark was *"tonight that set was four paths and recovering it took a hand-read
of a thirty-line YAML comment written by whoever hit it first."*

## 3. Three scoping decisions, each measured rather than assumed

**The refusal is keyed to `file_scope`; the printed unit is wider.** Prose legitimately names paths
that must NOT exist, and `KNIFE3_wall_crossing_paydown`'s prose cites
`sim/cache/elexon_ssp_full.json`, which is untracked — a refusal keyed to the wider unit would wedge
that atom permanently. A report cannot wedge anything; a predicate can. Measured: 31 of 348 atoms
get a wider unit than their file_scope, recovering **54 paths nothing else names**.

**Absence is scoped wider than dirt, deliberately.** `dirty_source_paths` is `.py`-only because this
shared tree holds `site/data/*.json` permanently dirty by design. Absence is the opposite case: a
regenerated output being dirty is ordinary, being absent from the tree entirely is not. Measured over
all 348 atoms at full suffix scope: **20 carry an absent file_scope path, every one at
`level_current` 0** (planned rows like `sim/product_ladder.py`). Zero atoms above level 0 are
affected — the control refuses nothing that stands today.

**The presence probe matches directory pathspecs.** 106 file_scope entries are directories
(`docs/design`, `tools`, `tests/sim`). An exact-match membership test reads all 106 as absent and the
control is unpassable; the prefix test reads 20, every one genuinely absent. The first draft of this
measurement returned 106 and would have shipped an unpassable control.

**A defect caught by writing the rule down:** `R / "saas" / "x.py"` is a left-leaning `BinOp` chain,
and `ast.walk`'s breadth-first order returns its components **reversed** — rejoining that yields
`x.py/saas`, which matches no path, silently turning the whole multi-component leg into a no-op that
still looks implemented. `_path_literals` recurses left-then-right; `test_the_rejoined_path_is_read_in_SOURCE_order`
holds it.

## 4. Controls

**Poison round first**, because *survived* means two opposite things. The refusing branch was proven
**reachable** against the live tree before any mutation was run, and the clean branch and the
fail-closed middle with it — `test_the_whole_partition_is_REACHABLE_not_only_the_refusing_leg` is one
control over all three outcomes, because a predicate that refuses everything passes every refusal
test and one that refuses nothing passes the clean one.

**8/8 mutants killed against a green 47-test baseline**, each run against a copy in a temp tree with
the anchor asserted present first (an anchor that does not match is a no-op mutation, and its
"survived" means nothing). The first battery reported *survived* for all eight — that was the
harness's own output parser going blind on a collection error, not eight fail-opens; it is recorded
here because that is precisely the shape that reads like a result.

| mutant | killed by |
|---|---|
| absence never refuses (fail-open) | `test_evidence_ABSENT_from_the_commit_tree_REFUSES_the_increase` |
| failed probe passes instead of refusing | `test_the_absence_probe_FAILING_is_a_refusal_not_a_pass` |
| negated `.exists()` no longer excluded | `test_a_NEGATED_exists_is_NOT_in_the_minimum_landable_unit` |
| module-level constants not resolved | `test_a_module_level_constant_path_is_recovered` |
| breadth-first (reversed) path literals | `test_the_rejoined_path_is_read_in_SOURCE_order` |
| directory pathspec: exact match only | `test_a_DIRECTORY_file_scope_entry_is_present_when_the_tree_holds_files_under_it` |
| unknown presence renders as `present` | `test_the_unit_says_UNKNOWN_when_the_probe_failed_rather_than_guessing` |
| prose citations dropped from the unit | `test_the_minimum_landable_unit_names_all_THREE_sources` |

**Not an equivalence of the SECOND control**, asserted directly rather than left to the reader:
`test_the_absent_path_is_INVISIBLE_to_the_dirty_check_so_this_is_not_an_equivalence` pins that the
dirty predicate reads the B3 raise clean and only the absence predicate refuses it. If a future edit
made `unbuilt_level_increases` catch this, the two would be one control wearing two names and one of
them should go.

**Both directions driven end-to-end through `main()`**, not only through the pure predicates — a
control that calls its estimator directly is blind to whether production wires it. Absent evidence →
exit 1 with the paths and the unit; evidence at HEAD → exit 0; a commit with no level increase →
exit 0, inert.

## 5. Declared control-set holes

- **Runtime-computed citations yield nothing.** `(project / path).exists()` over a loop variable
  contributes no rows, so the printed unit is a **floor** on what the commit needs and never a
  ceiling. Stated rather than hidden — and it is why the unit is a report, not a predicate.
- **An empty `file_scope` still passes**, for the same reason it passes the built-check: there is
  nothing to look for. That is the map's data gap, already reported on stderr, not a second silent
  hole opened here.
- **The write-time seat is the commit, not the map edit.** A level raised in the working tree and
  never staged is still invisible until someone stages the map. Closing that needs the same
  predicate called from `record_level_up_self_certified`, and it must be *called*, not copied —
  `tools.level_promotion_gate` already imports `background.gate_authorization`, so the shared
  predicate has to move somewhere neutral first. **Not built this turn; this is what is next.**

## 6. What is next

1. Reach the writer (§5 third bullet) so a raise cannot be *written* on absent evidence, not only
   not committed. One predicate, called twice, never copied.
2. The 20 level-0 atoms carrying absent file_scope paths are now each one refusal away from being
   visible at the moment someone tries to raise them. Nothing to do until one is drawn.
