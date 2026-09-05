**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found while landing
Lane 0 delivery · **Class:** controls_that_cannot_fail

# The atom number is picked from ONE half of a two-file map and checked against BOTH

**Found:** 2026-09-05, delivery seat, while proving that a design red refusing nothing of mine was
pre-existing at HEAD. It is red on `origin/main` now, in a clean `git archive` extract, and
**nothing in `docs/staging/` names it.**

```
tests/design/test_maturity_map_contract.py::test_b_numeric_part_unique_per_lane_or_allowlisted
  (('H','31'), ['H31_secret_scrub_test_leaks_wake_key',
                'H31_the_consistency_gate_disagreement_before_the_next_publish'])
  (('H','32'), ['H32_map_size_ratchet_red_on_head',
                'H32_the_orientation_header_states_a_figure_it_computes'])
```

## Not two typos — one mechanism, and the map itself says which

The maturity map is **two files**, and the H numbers in each are almost disjoint:

| file | atoms | H numbers |
|---|---:|---|
| `docs/design/maturity_map.yaml` (open) | 88 | 8, **31**, **32**, 40, 41, 43, 45 |
| `docs/design/maturity_map_closed.yaml` | 227 | 1–7, 9–12, 14–16, 19, 23, 24, 26, 27, 30, **31**, **32**, 33–39, 42, 44 |

Before today's two writes the open half held H8, H40, H41, H43, H45. **To anything reading only
that half, 31 and 32 are free.** They are not: both are taken in the closed half, by
`H31_secret_scrub_test_leaks_wake_key` and `H32_map_size_ratchet_red_on_head`, each of which also
owns a `docs/design/simplifications/<id>.yaml`.

`check_number_collisions` reads `load_atoms()`, which is **both** halves. So the rule is checked
against the union and the number is picked from one side of it. That is not a bad guess by a lane;
it is a seam, and it produced **two collisions in one day** — the signature of a mechanism rather
than of carelessness. It would have produced a third the moment anyone reached 33.

## The rule exists nowhere but the test

There is no minting path. `grep` finds no `mint`/`next_id`/`add_atom` for the map: a lane writes an
atom by hand and the only thing that has ever objected is a whole-tree design test. **A rule
enforced solely at the gate and never at the point of writing is a rule that is discovered late,
by someone else, in a red that names no author** — which is exactly what happened here, and why it
reached `origin/main` unfiled.

**And this class has been closed before.** `docs/staging/done/WORKER_FINDING_ONE_NAME_ONE_NUMBER_2026-08-09.md`
fixed the instances and left the seam that generates them. The allowlist is called
`LEGACY_NUMBER_COLLISIONS` and the test's own message says *"renumber, do NOT extend the
allowlist"* — so the previous repair correctly refused to widen the exemption, and correctly did
not claim to have stopped the next one.

## What it blocks, and what it does not

The pre-commit pytest selection is path-scoped, so this did **not** refuse a `tools/` + `docs/staging/`
landing — mine went through with 405 tests green. It refuses any commit whose selection reaches
`tests/design/`, which is principally **the lane that mints atoms**: the writers of these two rows
will hit their own red on their next map edit and will have no reason to connect it to the
half-map read.

## What I did not do, and why

**I did not renumber.** Both new atoms were written today (`0b35f5781`), both are live, and both are
already named in `docs/direction/decisions.jsonl` and two generated `site/data/` artefacts.
Renumbering under a lane that is mid-turn is the two-lanes-one-defect merge this project has paid
for; the number is theirs to move. The instance is one line each. **The seam is the finding**, and
fixing the instance without it buys another fortnight.

## The repair this argues for

Whatever picks a new atom number must read the **union** the check reads, and the cheapest honest
version is not a new register: it is one function next to `load_atoms()` returning the next free
number over both halves, plus the one control that would have caught this — **a test that the
number source and the collision check are the same set**, keyed to the property and not to today's
free numbers, so it stays green as the map grows and reds if the two ever read different files
again. Nothing here needs a new document, and the existing contract test is where the second half
of it already lives.
