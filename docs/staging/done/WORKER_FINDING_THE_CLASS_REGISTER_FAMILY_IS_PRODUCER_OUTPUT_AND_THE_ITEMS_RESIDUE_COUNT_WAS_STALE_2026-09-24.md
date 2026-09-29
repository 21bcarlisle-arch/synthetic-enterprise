**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0 delivery

# The CLASS_ register family is producer output classified as authored — and the item's own residue count was stale in both directions

**Discharged:** `tests/tools/test_a_producer_that_composes_its_filename_is_still_a_producer.py::test_the_CLASS_family_IS_CLASSIFIED_in_the_real_tree`, `tests/tools/test_a_producer_that_composes_its_filename_is_still_a_producer.py::test_MUTATION_a_CLASS_register_in_the_STAGING_ROOT_is_NOT_claimed`

Two of the six paths holding the shared tree behind `origin/main` were a producer's own output
graded as a lane's authored work, so `advance_shared_tree`'s all-or-nothing rule made them fatal to
the four beside them. Repaired in the commit this document lands in.

**Filed:** 2026-09-24, worker tick, on the shared tree at HEAD `61b67fa0d` (32 behind
`origin/main`, 3 ahead).

**Claim id:** `the-class-register-family-is-producer-output-classified-as-authored`

---

## Pre-registration, written BEFORE the change was made

The measurement below was taken first, so the before-number is not a prediction. What follows it is.

**Measured before touching anything** — the classification chain of
`background/origin_reconcile.advance_shared_tree` replayed read-only (blockers → untracked twins →
tracked twins → `stale_copy_verdicts` → `generated_output_verdicts` → `untracked_orphan_verdicts`),
against the live shared tree:

- `paths_blocking_fast_forward` returns **14** entries.
- After all five resolvable classes, **`held` is 6**:
  1. `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`
  2. `docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`
  3. `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py`
  4. `tests/background/test_publish_gate_wedge_draw.py`
  5. `tests/tools/test_refresh_to_head.py`
  6. `tools/refresh_to_head.py`

**PREDICTION.** Declaring `("background/finding_classes.py", "docs/staging/reference", "CLASS_")` in
`GENERATED_STEMS` moves rows 1 and 2 out of `held` and touches nothing else. Residue goes **6 → 4**,
and the four that remain are rows 3–6 — which belong to the *other* live claim
(`judge-the-advance-with-the-bases-rules-not-the-behind-checkouts`), not to this one.

Recorded before the change so it can refute me. The result is at the foot of this file.

---

## The item's count was wrong in both directions, and the coincidence hid it

The drawn item says the CLASS_ family *"clears one of the five residue paths"* and that done means
*"the residue set is four rather than five"*.

Neither number is the tree's. The residue is **six**, and this family holds **two** of them. The
item's arithmetic (5 − 1) and the tree's (6 − 2) land on the same answer, **4**, so the target the
item states is correct while both operands are wrong. A check keyed to the end state alone would
have passed and left the item's model of the tree unchallenged.

This is the ordinary shape: an item's claim about the tree is an un-re-asked prediction. It was
minted when the residue was five; two lanes have moved since. The item also says the producer
rewrites *"every one of those eight documents"* — there are **six** CLASS_ registers on disk, all in
`docs/staging/reference/`, none in the staging root.

## Why the family is producer output

`background/finding_classes.py:1434` `_write_class_documents` calls `doc.write_text(...)` over
every membership `derive_memberships(root)` returns, and `--check` re-derives that membership from
the filesystem rather than from a list. The destination comes from `_class_doc_path` →
`background.staging_rooms.class_document_path`. The name is composed, not spelled:

    finding_classes.py:139   CLASS_DOC_PREFIX = "CLASS_"
    finding_classes.py:201   return f"{CLASS_DOC_PREFIX}{self.id.upper()}_{self.registered}.md"

So no frame of the static write-site scan can resolve the destination — the identical shape the
landed `WORKER_FINDING_REPEATING_ALARM_` stem already fixed for the alarm family, from the same
module family. That is what `GENERATED_STEMS` exists for.

## The directory is declared NARROWLY, and that is the load-bearing decision

`class_document_path` has a **fallback**: reference room if the register is there, else the staging
**root**, else the reference room. So the producer *can* write to `docs/staging/` root — and the
staging root is where the seat files SEAT_FINDING and PLANNER_MINTED documents by hand.

Declaring the root would therefore offer the reconciler a **revert** on a seat's unlanded finding,
which is strictly worse than the wedge being fixed. Declaring `docs/staging/reference` only means a
CLASS_ register that ever lands in the root is graded *authored* — offered a landing, never a
revert. That is the direction that cannot destroy work, and it matches the safe-direction rule the
stem oracle already states for a dead producer.

It is also the direction the existing controls demand:
`test_an_AUTHORED_staging_document_in_the_real_tree_is_never_classified` globs the staging root and
asserts nothing there is classified. Declaring the root would have redded it.

---

## RESULT

**The prediction held, unmodified.** Same chain, same tree, re-run after the declaration landed in
the working copy:

- `generated_output_verdicts` now clears exactly two paths, and they are the two predicted:
  `CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` and `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`.
- **`held` is 4**, and the four are rows 3–6 verbatim:
  `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py`,
  `tests/background/test_publish_gate_wedge_draw.py`, `tests/tools/test_refresh_to_head.py`,
  `tools/refresh_to_head.py`.
- `stem_written_artefacts()` returns 20 paths — the 14 alarm documents it already held, plus all
  **six** CLASS registers.

Nothing else moved: no path left the classified set, and the two neighbouring oracles were not
touched (`test_the_stem_declaration_is_LOAD_BEARING_in_the_real_tree` proves the stem is the only
thing reaching these paths, and `test_the_stem_does_NOT_reach_the_COMMIT_GATE_or_the_frozen_census`
proves the commit gate's population did not).

**What this does NOT do.** The residue is four, not zero, so the shared tree still does not advance.
The four remaining are one lane's coherent `refresh_to_head` rework and belong to the other live
claim, `judge-the-advance-with-the-bases-rules-not-the-behind-checkouts`. This item was worth
landing separately because it is independent of that judgement, which is what the draw said and is
the one part of the item's reasoning that survives measurement.

### Mutation record

Both legs proven able to fail, on the live tree:

| Mutation | Caught by |
|---|---|
| Declaration deleted | `..._REFERENCE_ROOM_is_found`, `..._STOPS_SPELLING_IT`, `test_the_CLASS_family_IS_CLASSIFIED_in_the_real_tree` (named all six registers) |
| Directory widened to `docs/staging` | the three above **plus** `test_MUTATION_a_CLASS_register_in_the_STAGING_ROOT_is_NOT_claimed` |

**One leg did not fire and it is not an equivalence — it is vacuity, recorded in its own docstring.**
`test_the_CLASS_stem_claims_NOTHING_OUTSIDE_THE_REFERENCE_ROOM_in_the_real_tree` stayed green under
the widening mutation because the live staging root holds no CLASS_ document for it to find. It is a
standing guard for the day `class_document_path` writes one there, not a proof today; the widening
proof is the tmp-tree leg, which builds the population it needs.
