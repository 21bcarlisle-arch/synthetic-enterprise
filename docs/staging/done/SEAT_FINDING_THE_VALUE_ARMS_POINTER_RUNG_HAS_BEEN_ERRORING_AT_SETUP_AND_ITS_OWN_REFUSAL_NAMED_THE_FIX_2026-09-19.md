**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found under Lane 0
claim `a-generator-must-stamp-provenance-that-describes-what-it-read`

# The value_arms pointer rung has been erroring at setup, and its own refusal named the fix

Found 2026-09-19 while giving `value_arms.json` its reserved provenance key. Not repaired in that
landing, for the reason in the last section — the fix is two parts and only the first is mine.

---

## The state, measured

`tests/tools/test_the_value_arms_pages_undriven_pointers.py` is **red at a clean `HEAD` extract**,
and has been, as **four tests ERRORING AT SETUP**:

```
E  AssertionError: `build` reads 9 artefacts and this fixture supplies 6, so every recipe below
   would be driven over a payload the producer never builds
```

`generate_value_arms_data.build` has grown to nine artefact arguments. The fixture still lists six.
**The guard that catches this was written by the same file and it worked exactly as designed** —
its docstring says, verbatim, that the previous stale list *"raised `AttributeError` at SETUP, which
reports as four tests erroring rather than as one stale list — and a whole file erroring is how a
red gets attributed to whichever lane next touches it."* That is precisely what happened again, one
mechanism later, and the arity check turned it into a refusal that names itself.

This is why it is filed rather than left: **a whole-file setup error reds every lane that touches
`generate_value_arms_data.py`**, and it will be attributed to whoever that is.

## Part one of the fix, measured and in hand

The three missing paths are the ones `generate()` resolves after `DEPARTURE_TERM_RERUN_PATH`, in
that order. In `_real_inputs()`, the tuple becomes:

```python
paths = (gva.THREE_ARM_PATH, gva.NOISE_FLOOR_PATH, gva.DECOMPOSITION_PATH,
         gva.CURRENT_WORLD_THREE_ARM_PATH, gva.CURRENT_WORLD_NOISE_FLOOR_PATH,
         gva.DEPARTURE_TERM_RERUN_PATH, gva.DEPARTURE_TERM_BASELINE_PATH,
         gva.BLIND_ENVELOPE_ARMS_PATH, gva.AUC_FAMILY_FLOOR_PATH)
```

Measured with that applied: **4 errors → 3 passed, 1 failed.** The file starts measuring again.

## Part two, which is what the first part uncovers and is NOT a one-liner

With the fixture driving the real nine-artefact build, the surviving red is real coverage:

```
E  these symbols own an untied here-relative sentence and no recipe drives their branch, so the
   sentence is published-able and unjudged:
   ['_family_discrimination', '_population_repair_bias', '_skill_sample_size_explanation']
```

Three producer functions have arrived since the rung was last measuring, each owning here-relative
prose no recipe reaches. **None of the three takes the generic `_returns_string` recipe** — checked,
all three return dicts — so each needs a bespoke recipe that forces its untied branch while
preserving the branch's own return shape. That is the work the rung's own docstring calls "a recipe
rather than an exemption", and it is three separate readings of three branch structures.

`_population_repair_bias` is additionally **the subject of a live Lane 0 item of its own**
(2026-09-19, the director's item on which way the published `selection_gbp` is wrong). Writing its
recipe from outside that item risks pinning a control to the shape that item is about to change.

## Why this landed nothing, and the assumption that was wrong about it

**Part one cannot land on its own, and part two cannot land without it. They are one landing.**

I first wrote the opposite here — land part one alone, three recipes to follow — on the assumption
that a change to the producer selects this test. It does not. Read, rather than assumed,
`tools/pre_commit_test_gate.tests_for`:

* a changed **`.py` module** selects `tests/**/test_<stem>.py` and `tests/**/test_<stem>_*.py`.
  `generate_value_arms_data.py` therefore selects `test_generate_value_arms_data.py` and
  **not** `test_the_value_arms_pages_undriven_pointers.py` — the name matches neither glob.
* a changed **test file** selects **itself**.

Two consequences, and they invert what to do:

1. **The provenance repair to `generate_value_arms_data.py` is NOT blocked** by this red, and is
   landing in this turn after all. The rung is not selected by it.
2. **Part one alone IS blocked**, because touching the test file selects the test file, which then
   reds on part two. So the fixture arity fix and the three recipes must land together.

That also explains how `7b1895751` landed a change to this producer three commits ago with the rung
already erroring: nothing selected it. **This file is red at HEAD and invisible to the commit gate
of every lane that changes only the producer** — which is a sharper statement of the finding than
the one above, and the reason it is filed rather than left to be noticed.

So the next session's order is:

1. **One landing**: the fixture arity fix plus recipes for `_family_discrimination` and
   `_skill_sample_size_explanation`.
2. **Leave `_population_repair_bias` to its own item**, and say so in its row rather than skipping
   it — the rung refuses an unrecipe'd symbol on purpose and an exemption would be the hole. If
   that means step 1 cannot go green, it waits for that item; the rung stays red either way and the
   red is now named.

## What the value_arms provenance repair measured, so it is not re-derived

Kept here because the code is not landing with it. `generate()` resolves its nine sources once and
both reads and stamps that same list. Driven against the real artefacts:

```
BEFORE (no reserved key): (None, 'the feed records more than one commit of this repository, so
                           which of them is the publication standpoint and which is its subject
                           cannot be told apart from the bytes')

AFTER  (reserved key):    (None, "the feed records 78d99e276 but says the bytes it read were not
                           that commit's — ...")
```

A structural refusal nobody can act on became a refusal that names its cause and clears itself on a
clean-tree publish. All nine sources stamped `committed`. That is the whole of the value_arms half
of the Lane 0 item, and it is one edit away from landing once the red above is cleared.
