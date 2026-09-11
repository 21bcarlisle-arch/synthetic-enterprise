# `blocked_on` cannot name an atom, and the map is 295 bytes from refusing every lane

**Date:** 2026-09-06
**Lane:** H_harness
**Severity:** LATENT — nothing is wrong today because no live atom uses the field; the next atom
that tries to record a real block cannot, and finds out only at the commit gate. Found under the
Lane 0 delivery claim `the-weather-cells-reach-the-world-or-w1-14-says-why-not`, while recording
W1_14's corrected blocker.
**Status:** RECORDED, not fixed. Worked around in W1_14 by using `depends_on`. Both halves are
one-line fixes in someone's lane; neither is this claim's.

## 1. Two gates demand opposite shapes, and no value satisfies both

`W1_14` needed to record that it waits on `W2_18_the_housing_joint_the_sample_and_the_ceiling`. Both
shapes of that statement are refused:

| value | `test_c_dependency_edges_are_lists_of_existing_ids` | `test_live_map_block_hygiene` |
|---|---|---|
| `blocked_on: W2_18_…` (string) | **FAIL** — "edges must be lists of atom ids" | pass |
| `blocked_on: [W2_18_…]` (list) | pass | **FAIL** — "resolves to no known releaser and no existing atom id" |

`check_edges` (`tests/design/test_maturity_map_contract.py:211`) requires a non-null `blocked_on` to
be a **list**. `_blocked_on_resolves` (`tests/design/test_maturity_map_facets.py:784`) does
`str(blocked_on)` and then `s in known_ids` — a list stringifies to `"['W2_18_…']"`, which is never
an atom id. So the only values that pass both are `null` and a string containing a releaser token —
and a releaser-token *string* is itself a scalar, so it fails `check_edges` too.

**Net: the only value of `blocked_on` that passes both gates is `null`.** The field's documented
purpose — naming the atom that must land first — is unreachable.

### Why it was never noticed

Measured, not assumed: across the live map at HEAD, atoms carrying a non-null `blocked_on` = **0**.
The field is universally null, so the two gates have never been asked about the same value at once.
Each is individually correct and individually well-tested; the contradiction lives *between* them,
which is the class of defect a bounded per-gate review cannot see.

`_blocked_on_resolves` is also the weaker of the two in a second way: it accepts a releaser token by
**substring** on `str(...)`, so a list whose *reason prose* happened to contain "watching_brief"
would resolve. It is checking text, not structure.

### The fix (not taken here)

Make `_blocked_on_resolves` handle the list case — resolve each member against `known_ids` — so the
list form passes both. One function, four lines. Left to the harness lane rather than done under a
weather claim, because it changes the meaning of a design gate that every commit runs.

### Workaround actually used

`W1_14` now carries `blocked_on: null` and
`depends_on: [W2_18_the_housing_joint_the_sample_and_the_ceiling]`. That is machine-readable, passes
both gates, and is arguably the more honest field: W1_14 does not merely *wait on* W2_18, its L2
depends on W2_18's output. **It is a real new edge in the graph and it will affect draw ordering** —
recorded here because that is a side effect of a workaround, not something the correction asked for.
Reverse by deleting the one list entry.

## 2. The map's size ratchet has 295 bytes of headroom

Found by hitting it four times in a row while trying to record the above.

- `MAP_SIZE_CEILING` = 409,600 bytes, measured across **both** halves
  (`tests/design/test_simplifications_store.py::_map_bytes`).
- At HEAD: `maturity_map.yaml` 171,149 + `maturity_map_closed.yaml` 238,156 = **409,305 bytes**.
- **Headroom: 295 bytes.**

Two hundred and ninety-five bytes is under three lines of YAML. The next lane to add an atom, or to
write two sentences of honest reason onto an existing one, reds a gate that **every commit runs**
and that names no owner — the failure text says "the register must live in the store, not the map",
which is advice about a refactor nobody has scheduled, not about the change in hand. This turn spent
four of its gate cycles compressing prose that was already the point of the edit.

This is not an argument for raising the ceiling: the ratchet is doing exactly what it was built to
do, and the closed half at 238 KB is 58% of the budget for atoms that are *finished*. The finding is
that it is about to become a **whole-tree wedge with no named owner**, and the cheap move is to
drain closed atoms into the store before it does, not to discover it as a commit refusal.

## What this claim did about it

Nothing to either, beyond the `depends_on` workaround and this record. Both are outside a weather
atom's scope and both are cheap for the lane that owns them. Recording them is the point: the first
is invisible until someone needs it, and the second is invisible until it stops every lane at once.
