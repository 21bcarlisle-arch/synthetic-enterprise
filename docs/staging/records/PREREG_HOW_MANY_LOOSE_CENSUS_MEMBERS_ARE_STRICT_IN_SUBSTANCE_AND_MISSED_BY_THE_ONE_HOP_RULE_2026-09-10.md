**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `refuse-the-nineteenth-at-the-loose-boundary-or-say-why-not`) · **Class:** controls_that_cannot_fail

# PREREG — how many LOOSE census members are strict in substance, and invisible to the one-hop rule?

Written BEFORE the transitive predicate is run over the tree. The drawn item asks me to decide what
guards the strict/loose boundary of `tools/whole_tree_subject_census.py`, and offers two doors: a
cheaper predicate that promotes a loose member when its walk becomes provably the counted
population, or a stated decision that the loose pool is deliberately unguarded.

## The first door is already open, and that is not the question

`test_the_strict_census_stays_discharged` (origin `a613d5dce`) re-runs `wtsc.census()` over **every
tracked test file**, not over a frozen list. So a member that is loose today and is EDITED into
strict form tomorrow reappears in the strict pool at that commit, and the control — itself on
`CONTROL_TESTS`, so it runs whenever any code file is staged — refuses it there. Promotion-on-change
needs no new predicate. I will prove that by mutation rather than assert it, because a mechanism
nobody poisoned is a mechanism nobody has tested.

## The question whose answer I do not know

The drawn item, the census docstring and the control's own docstring all say the same thing about
the loose pool: *the predicate over-counts by construction, so a control over it would refuse honest
work.* That is true of the direction they all name. **Nobody has measured the other direction.**

`_strict_dataflow` is a **one-hop** rule: `len(X)` vs an integer, where `X` is a name assigned
directly from a walk call, or is the walk call itself. The shape this repo actually writes is often
two hops —

```python
rows   = [p for p in DIR.glob("*.py") if _is_writer(p)]
names  = {p.name for p in rows}
assert len(names) <= 56
```

— and the one-hop rule cannot see it. Every such file is **strict in substance**: the walked
population IS the counted one, the bound IS a claim about a directory that grows behind it. It is
sitting in the loose pool, and the "deliberately unguarded" decision would be covering it.

**How many of the loose members are strict in substance?**

## The predicate I will count (fixed now, so it cannot be tuned to the answer)

`_transitive_dataflow` — the fixpoint version of the same rule, and nothing else changes:

1. A name is WALK-TAINTED if the value assigned to it contains a walk call
   (`glob`/`rglob`/`iterdir`/`walk`), **or** contains a `Name` that is already walk-tainted.
   Iterate to a fixpoint over the whole module, flow-insensitively.
2. The file is transitive when some `len(X) <op> <int literal>` has `X` a walk-tainted name, or `X`
   contains a walk-tainted name or a walk call anywhere inside it.

One-hop is the depth-1 case of this, so **strict ⊆ transitive ⊆ loose holds by construction** and I
will assert it as a control rather than claim it in prose.

**What it will still not see, stated before the count so it cannot be quietly dropped later:**
accumulation through `append`/`add` inside a `for` loop over a walk, and taint through a helper
function's return value. Both are real shapes. So the number below is a LOWER bound on strict-in-
substance, not the answer.

**Reported, not enforced, in this change.** No member moves onto `CONTROL_TESTS` this turn — the
constant lives in a file origin has rewritten under me and my tree is 9 commits behind it. A false
positive therefore costs nothing yet, which is the right time to look at one.

## Predictions, fixed now

- **P1 — the count.** Transitive promotes **14** loose members. Band **6–30**.
- **P2 — the flattering outcome, named as such.** If it promotes **0**, the one-hop rule already
  sees everything it can, the over-count is the only error direction, and the "loose pool is
  deliberately unguarded" decision stands unqualified. I expect this to be refuted.
- **P3 — the decision threshold, fixed before the number is visible.** If transitive promotes **≤
  25**, the boundary is guardable in principle and the next turn's work is to promote that set onto
  the always-run list, conditional on a measured cost under **30s** for the whole set. If it
  promotes **> 25**, the loose pool stays unguarded by refusal and the decision is recorded as a
  decision, with this number as its price.
- **P4 — what will NOT move.** The loose pool's headline (109 here, 91 at origin's base) does not
  change: transitive re-labels members, it admits none. If the total moves, the predicate leaked
  and the run is void.

## What would refute the whole frame

If every promoted member turns out to be a false positive on inspection — the counted expression
merely *mentions* a walked name while counting something else — then transitive taint is too
promiscuous and the one-hop rule was right to be narrow. Three of the promoted set will be read by
hand and the reading written down beside the count, including any that fail.
