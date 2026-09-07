**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# A content-landed rename left the pre-rename draft in the tree, and it wedged every lane for 22 hours

**Found:** 2026-09-07, delivery seat, working the lane-0 orphan-ratchet wedge. **Repaired the same
turn**; this records the cause, the repair and how to reverse it.

---

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

It is a second consequence of the class already in the record — a `--content` landing leaves the
working tree holding the parent's bytes — reached this time through a **rename**, and costing
something the class had not yet been observed to cost: the ordinary commit route for every lane.

---

## What the refusal said, and what was actually wrong

The publish gate had been wedged 21.7 hours with `total_red: 0`, `blocking_tests: []`,
`episode_failures: 14`, `episode_clean_publishes: 0`. The refusal:

> `orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.`
> `tools.demand_case_coverage` · `tools.space_filling_sample` · `tools.tou_sharing_ceiling`

Three names, and the doorbell's reading of them — *restore two baseline entries, and give
`tou_sharing_ceiling` a caller or `--freeze` it* — is right on the first two and **wrong on the
third**. `tou_sharing_ceiling` is imported at HEAD by `tools/r4_product_ceiling.py:96`. Freezing it
would have recorded a falsehood, which is the failure `orphan_ratchet.py`'s own docstring names:
*"A control whose false positive is cleared by lying is worse than the gap it was closing."*

`SEAT_FINDING_THE_ORPHAN_RATCHET_ACCUSES_A_COMMITTED_REACHABLE_MODULE...` (now in `done/`) had
already established that the accusation was a broken chain and correctly declined to touch the file.
What it did not have is **why the chain was broken**, which is what makes it fixable.

## The cause: a rename that landed by content, and a draft pair that never learned

| file | state | mtime |
|---|---|---|
| `tools/r3_score_ceiling.py` | **untracked — in no commit on any branch** | 03:25:35.479995232 |
| `tools/r4_product_ceiling.py` | modified; 465 lines; imports `tools.r3_score_ceiling` | 03:25:35.479995232 |
| `tests/tools/test_r3_score_ceiling.py` | untracked | 03:24:03 |
| `tests/tools/test_r4_product_ceiling.py` | modified; imports `tools.r3_score_ceiling` | 03:25:09 |

The two modules share an mtime **to the nanosecond** — one batch write, not authorship.

Then the commits, all three by `surgical_land` (`[surgical-land receipt]` in each message):

```
05:26  85e1463c5  R3's ceiling instrument         → tools/r3_carbon_score_ceiling.py   (RENAMED)
05:33  bfd232ba0  R4's ceiling instrument, 488 ln → imports r3_carbon_score_ceiling
06:57  6fb5f64f3  tou_sharing_ceiling
08:18  fe79a5dd9  the sharing side reaches a reader → r4 grows the tou_sharing import (line 96)
```

`surgical_land` builds HEAD-plus-hunks **outside the repo** — correctly, that is the whole point —
so it never writes the working tree. The lane renamed `r3_score_ceiling` → `r3_carbon_score_ceiling`
*at land time*. The commits therefore carry the rename and the working tree does not: it still held
the 03:25 drafts, which predate the file's own first commit by two hours.

The chain that broke, and it is one edge:

```
HEAD extract   r4_product_ceiling ──imports──> tou_sharing_ceiling      reachable
shared tree    r4_product_ceiling(03:25 draft) ──imports──> r3_score_ceiling(untracked)
                                   ╳ no edge to tou_sharing_ceiling      ORPHAN
```

`orphan_ratchet.compute()` builds its rows from `capability_index.build_rows()`, which **walks the
filesystem**. So reachability is computed over the shared working tree, and one uncommitted file
deleted one import edge and made a committed, reachable, published module read as new work nothing
runs. The pre-commit hook runs the ratchet against that tree, so **one lane's superseded draft
refused every lane's ordinary commit**, including the publisher's — which is why `total_red` was 0
and `blocking_tests` empty for 22 hours while the only surface the director reads went a day stale.

`demand_case_coverage` and `space_filling_sample` are a separate and simpler fault in the same file:
both **are** frozen in `git show HEAD:docs/design/orphan_baseline.json` and were deleted from the
list in the working-tree copy only. That copy had also *added* `tools.r3_carbon_score_ceiling` and
`tools.r4_product_ceiling` — the two modules the broken chain had just orphaned. It is a
`--freeze` run against the broken tree: the baseline was being re-fitted to the defect.

## The repair

All five paths now match HEAD byte-for-byte, and the two untracked drafts are out of the tree:

- restored to HEAD's bytes: `tools/r4_product_ceiling.py`, `tests/tools/test_r4_product_ceiling.py`,
  `docs/design/orphan_baseline.json`
- removed as superseded drafts: `tools/r3_score_ceiling.py`, `tests/tools/test_r3_score_ceiling.py`

**Nothing was committed to repair it, because nothing was ever committed to cause it.** The wedge was
pure working-tree state, which is exactly why it was invisible in every clean extract.

**Reversal, if any of this was wrong.** Every byte is recoverable two ways — as blobs written into
the object store, and as files:

```
a21b35948c58d32a7a54bea18c5c4c3aeaed4d41  tools/r4_product_ceiling.py
44d78d9de81607d57ffca4a92a7385a883a9194b  tools/r3_score_ceiling.py
15fdd914c446f493cb13427ae4f25a9309ec4de0  tests/tools/test_r4_product_ceiling.py
558c0f1959f54920ab5338ff9c53c272e3fe8593  tests/tools/test_r3_score_ceiling.py
858b3c90c74472e4c86fcf54a08614d08cd49c53  docs/design/orphan_baseline.json
```

`/var/tmp/se-salvage-20260907T1445-r3r4/` holds the same five with mtimes preserved.

## The evidence it worked

- `python3 tools/orphan_ratchet.py` → **exit 0, silent**. It was three named modules and a refusal.
- `pytest tests/tools/test_r4_product_ceiling.py tests/tools/test_r3_carbon_score_ceiling.py
  tests/tools/test_tou_sharing_ceiling.py` → **53 passed**. The restored copies are coherent
  together; the rename is consistent across module, sibling and suite.

## Why this was safe to touch when the previous seat correctly was not

That seat found the file five hours old and read it as in-flight. It was not: the drafts **predate
the first commit of their own file**, the name they depend on (`tools.r3_score_ceiling`) was never
committed on any branch, and its committed twin exists under the new name. A working-tree copy that
imports a module no commit contains cannot be ahead of HEAD — it can only be behind it. That is a
cheap and general discriminator, and it is the one the age heuristic missed.

## What is next

1. **The ratchet still names the module at the end of the broken chain, not the file that broke
   it.** Every seat that reads the refusal literally goes looking for something to wire or freeze,
   and freezing is the lie. It should name the *dirty* file whose removal of an import edge created
   the orphan — it already has both graphs and can diff them.
2. **`surgical_land` lands a rename and leaves the old name in the tree.** No control notices. The
   old file is then untracked, imported by nothing committed, and one more edge from wedging every
   lane again. A post-land check — *does the tree contain a module whose name this commit renamed
   away* — is one leg and would have caught this at 05:26 rather than at 14:47.

**Falsifier for item 1, and it is cheap:** a future refusal naming a module that a clean extract of
HEAD reports as reachable means the ratchet is still accusing the wrong subject. That is the third
instance, and this class has now cost two seats a turn each.

---

*Left strictly alone, and deliberately: the half-staged room move in `docs/staging/` (three
preregistrations staged as deleted from the root, present untracked in both rooms). The index was
written one minute before I looked and the root copies five minutes before — that is a lane mid-turn,
not a leftover, and `finding_classes --check` reads the working tree, so it will clear when they
land. It is the next thing on the ordinary commit route if it does not.*
