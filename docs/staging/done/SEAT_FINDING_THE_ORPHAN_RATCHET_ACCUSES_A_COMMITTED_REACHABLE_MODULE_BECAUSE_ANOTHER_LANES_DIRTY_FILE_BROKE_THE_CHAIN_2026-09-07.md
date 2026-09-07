**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The orphan ratchet accuses a committed, reachable module because another lane's dirty file broke the chain

**Found:** 2026-09-07, delivery seat, working the lane-0 publish wedge. The instrument is
`tools/orphan_ratchet.py`; the accused is `tools.tou_sharing_ceiling`; the actual cause is an
uncommitted working-tree copy of a **different** file, `tools/r4_product_ceiling.py`.

---

## What the refusal says, and why every word of it is false here

The publish gate has been wedged since 2026-09-06T16:41 UTC with `total_red: 0` and
`blocking_tests: []`. The recorded cause is a `gate_refusal` whose text is:

> `orphan-ratchet: THIS COMMIT ADDS WORK THAT NOTHING RUNS.` — `tools.tou_sharing_ceiling`
> *"Nothing imports these, and no committed systemd unit, timer or git hook runs them."*

Three claims, measured:

| the refusal claims | measured |
|---|---|
| *this commit adds* the module | `tools/tou_sharing_ceiling.py` landed at `6fb5f64f3`, an ancestor of `origin/main`. No commit is adding it. |
| *nothing imports* it | `tools/r4_product_ceiling.py:96` at HEAD: `from tools.tou_sharing_ceiling import OUT_PATH as TOU_ARTEFACT`. |
| the tree is in this state | `tools/orphan_ratchet.py` in a **clean extract of HEAD** exits 0, silent. |

The ratchet is green at HEAD and red in the shared working tree, at the same commit.

## The actual mechanism

`compute()` builds its rows from `capability_index.build_rows(base)`, which **walks the
filesystem** — so reachability is computed over the shared working tree, not over the tree the
commit would create. Run in both roots, the graph is:

```
                     tools.tou_sharing_ceiling   callers
  HEAD extract   →   reachable=True              ['tools.r4_product_ceiling', '... (by path)']
  shared tree    →   reachable=False             []
```

`tools/r4_product_ceiling.py` is dirty in the shared tree (mtime 2026-09-07 03:25, matching **no**
commit — 11 symbols HEAD lacks, 9 of HEAD's absent). That copy does not carry line 96. Deleting one
import from one uncommitted file therefore made a *committed, reachable* module read as a new
orphan.

So the ratchet's subject is wrong in the way that matters: it names the module at the **end** of the
broken chain, not the file that broke it, and it names it as something "this commit adds" when no
commit adds anything. A seat reading the refusal literally goes looking for a module to wire or
freeze — and `--freeze` on a module that is already correctly wired at HEAD would record a
falsehood, which is precisely the failure this module's own docstring names: *"A control whose false
positive is cleared by lying is worse than the gap it was closing."*

## Why it is BLOCKING and not latent

It is not one lane's inconvenience. The pre-commit hook runs the ratchet against the shared working
tree, so **one lane's uncommitted refactor wedges the ordinary commit route for every lane** — which
is what the publish daemon has been failing on for 15+ hours while the only reader outside this
machine saw a site whose `delivery.json` reported `age_hours: 40.8` and `live: false`.

It is also the second instrument in a week to accuse the wrong subject from working-tree state no
commit contains, alongside the class already in the record
(`SEAT_FINDING_THREE_SHARED_TREE_FILES_CARRY_A_REWRITE_FROM_BEFORE_THE_STABILITY_RUNG...`).

## What I did, and deliberately did not do

**Did not** touch `tools/r4_product_ceiling.py`. Its uncommitted work is another lane's, it is five
hours old, and adding the one import line to green a gate would be the lie above. **Did not**
`--freeze`, for the same reason.

**Did** restore three files whose working-tree copies were provably superseded leftovers of a
`--content` landing — `tools/generate_delivery_page.py`, `tools/r1_inference_ceiling.py`,
`docs/observability/r1_inference_ceiling.json`. All three now match HEAD byte-for-byte and so
contribute nothing to any commit; the bytes they held are recoverable as blobs
`e76a4e04b`, `09b9d2e9a`, `5fa8065ea` and in `/var/tmp/se-salvage-20260907T0813/`. That copy of
`generate_delivery_page.py` was keyed to `honest_point_estimate`, an artefact field HEAD's
instrument **no longer writes** (it writes `magnitude_three_way_split`), so it would have published
`magnitude: null` over a real +0.2513.

**Did** land the publish surface by `tools.surgical_land`, which gates the tree the commit *would*
create — the legal route when the shared tree is dirty, and the one that was available throughout.

## What is owed

The ratchet should compute reachability over **the tree the commit would create**, as
`surgical_land` already does, not over the shared working tree. Until it does, its refusal text
should not assert "this commit adds" — it cannot know that from a filesystem walk.

**Falsifier, cheap:** with `tools/r4_product_ceiling.py` dirty in the shared tree,
`python3 tools/orphan_ratchet.py` must not name `tools.tou_sharing_ceiling`. If it still does, this
finding was right and unheeded.
