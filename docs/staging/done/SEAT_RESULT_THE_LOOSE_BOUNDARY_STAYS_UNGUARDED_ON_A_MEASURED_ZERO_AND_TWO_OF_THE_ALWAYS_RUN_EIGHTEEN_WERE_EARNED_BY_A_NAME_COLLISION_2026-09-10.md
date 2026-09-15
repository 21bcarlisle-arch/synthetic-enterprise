**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `refuse-the-nineteenth-at-the-loose-boundary-or-say-why-not`) · **Class:** controls_that_cannot_fail

# The loose boundary stays unguarded on a measured zero, and two of the always-run eighteen were earned by a name collision

Answers the drawn Lane 0 item. Predictions were fixed in
`records/PREREG_HOW_MANY_LOOSE_CENSUS_MEMBERS_ARE_STRICT_IN_SUBSTANCE_AND_MISSED_BY_THE_ONE_HOP_RULE_2026-09-10.md`
before any of the numbers below were visible. **P1 is refuted and P2, the outcome I said I expected
to be refuted, is what happened.** Both are kept here beside the result.

## What the item asked, and why one of its two doors was already open

> *"either a cheaper predicate that promotes a loose member to strict when its walk becomes provably
> the counted population, or a stated decision that the loose pool is deliberately unguarded"*

The first door needs no predicate and never did. `test_the_strict_census_stays_discharged` re-runs
`wtsc.census()` over **every tracked test file**, not over a frozen list, and it is itself on
`CONTROL_TESTS`, so it runs whenever any code file is staged. A member edited from loose into strict
form is in the strict pool at that commit and is refused there.

That was a reading of the code, so it is now driven instead:
`test_editing_a_loose_member_into_strict_form_puts_it_back_in_the_refused_pool` edits the loose
fixture into one-expression form and follows it through `classify_source` **and** `unreachable()`,
composed on purpose because either leg alone passes while the pair does nothing. Mutation-proven:
`_strict_dataflow` stubbed to `False` reds it.

## The half nobody had measured, and it is empty

Every previous statement about this boundary — the census docstring, the control's docstring, the
drawn item — argues the same direction: *the loose predicate over-counts by construction, so a
control over 91 members would refuse honest work for a reason it could not defend.* True, and not
the dangerous direction.

`_strict_dataflow` is a **one-hop** rule. The shape this repo actually writes is often two:

```python
rows  = [p for p in DIR.glob("*.py") if _is_writer(p)]
names = {p.name for p in rows}
assert len(names) <= 56
```

That file is strict in substance — the walked population IS the counted one — and scores loose. So
the strict pool would **under**-count, and "deliberately unguarded" would be covering members that
belong on the guarded side. `_transitive_dataflow` is the fixpoint version of the identical rule.

| | count |
|---|---|
| loose pool (this tree, 9 commits behind origin; 91 at origin's base) | **109** |
| strict, one hop | 18 |
| transitive, any depth, scope-aware | 16 |
| **promoted loose → strict-in-substance** | **0** |
| strict but NOT transitive | 2 |

**P1 REFUTED: predicted 14, band 6–30; measured 0.** The two-hop shape I was confident was common
is essentially absent from this tree. **P2 HELD, and I named it as the flattering outcome I expected
to be refuted:** the one-hop rule already sees what it can, the over-count is the only error
direction of any size, and *the decision to leave the loose pool unguarded by a refusal now rests on
a number rather than an assertion.* **P3 never bound** — its ≤25 threshold has nothing to apply to.
**P4 held:** the loose total did not move, so the predicate re-labels and admits nothing.

The decision itself is written where the item asked for it — in the census module's own docstring,
in ONE home, because the reader who is about to propose a control over the loose pool opens that
file. It is not duplicated into the control, and the two-homes shape is why.

## The thing I did not predict: the instrument is scope-blind, and two of the eighteen ride on it

The first run of the transitive rule returned exactly one promotion, `site/test_ia_register.py`. The
prereg said three of any promoted set would be read by hand and the reading written down *including
any that fail*. There was one, it was read, and it failed:

- `victim = next(p for p in sorted(tree.rglob("index.html")) ...)` → `before = victim.read_text()` →
  `after = before.replace(...)`, all inside `test_MUTATION_a_hand_edited_nav_fires`;
- `assert len(after) >= 5` is in a **different** function,
  `test_MUTATION_moving_a_tab_in_the_register_makes_every_page_stale`, where `after =
  renderer.stale(tree)`.

Two unrelated variables that happen to share a name. My taint map merged every binding of a name
across the whole module, which is not a conservative over-approximation of Python — it is a
misreading of it. Fixed with a scope index, and the promotion count went 1 → 0.

**The same bug is in `_strict_dataflow`, which is the predicate that chose the always-run eighteen.**
Two of them are scope collisions:

- `tests/background/test_the_responder_refuses_to_guess_whose_a_message_is.py` — walk in the helper
  `_run` (lines 99–100), bounds in five separate test functions (120, 133, 156, 214, 228);
- `tests/company/policy/test_policy_field_consumption.py` — walk at line 467 in
  `test_mutation_restoring_the_pin_reds_the_scan`, bound at line **339** in
  `test_the_scan_has_a_population_to_scan`. The bound is textually *before* the assignment.

So the pre-registered claim that **strict ⊆ transitive holds by construction is FALSE**, and for a
reason I did not anticipate: it holds only if the two rules scope alike, and they do not.

## Why that is recorded and not repaired

Making `_strict_dataflow` scope-aware would put those two files outside the predicate, red
`test_every_member_still_earns_its_place_by_scanning_a_whole_directory`, and have the gate demand
their lines be **deleted from the always-run list** — on the strength of a rule with a known blind
spot pointing the other way. `_run` *returns* its walked population and the test functions count
what it returned: interprocedural taint, which the prereg named as unseeable before the count was
run. That first file is a true member of the class reached by a route neither rule can follow.

A narrowing that only ever hears the false-positive side is this project's own named failure. Two
files keep an always-run seat they may not strictly have earned; the cost is seconds on a hook, and
the alternative is deleting a real control's only selector. Recorded in the census docstring, in
`_walk_tainted_names`'s statement of its residual, and here.

## Controls added, all four mutation-proven

In `tests/tools/test_whole_tree_subject_census.py`, each red under exactly its own defect and green
under the other three:

| control | its named defect | mutation that reds it |
|---|---|---|
| `test_the_transitive_rule_can_say_yes` | the measured 0 is the predicate's own silence | `_transitive_dataflow` → `False` |
| `test_taint_does_not_cross_between_two_functions_binding_the_same_name` | scope-blind taint reports a subject that is not there | scope index reverted to module-wide |
| `test_scoping_the_taint_did_not_lose_module_level_bindings` | the scope fix as an asymmetric narrowing that drops `ROWS = DIR.glob(...)` | ancestor inheritance dropped |
| `test_editing_a_loose_member_into_strict_form_puts_it_back_in_the_refused_pool` | promotion-on-change asserted in prose and false | `_strict_dataflow` → `False` |

The reachability leg is first in the file, as it must be: `_transitive_dataflow` returning `False`
unconditionally would report the same 0 and pass every negative test here.

No live-tree count is asserted anywhere. There is deliberately **no** `strict ⊆ transitive`
assertion — it is false, and pinning it would make the instrument's defect a property.

## What is next, and what this turn did NOT do

1. **The prune is untouched and still live.** The drawn item's second half — the six expensive
   members carry 88% of the +32.0s on 88 of 392 tests, so cost does not track test count and a prune
   must take from the six — has had no work. Nothing here changes it.
2. **Nothing moved onto `CONTROL_TESTS`, and nothing needed to.** The promoted set is empty. The
   constant lives in `tools/pre_commit_test_gate.py`, which origin has rewritten under this tree
   (9 commits behind at the time of writing), so it was deliberately not touched.
3. **Interprocedural taint is the open residual.** At least one live member is reached only through
   a helper's return value. Whether that is one file or thirty is unmeasured, and it is the honest
   next question at this boundary — not the loose pool, which now has its zero.
