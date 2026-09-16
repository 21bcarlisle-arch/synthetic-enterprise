**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — publish-once-cleanly-and-take-the-refusal-at-the-instant-it-fires) · **Class:** uncommitted_and_orphaned_work

# RESULT — the publish refusal was live, not spent, and the control it named is green only because `git ls-files` sees the index

The drawn item said the recorded cause in `docs/observability/.publish_gate_state.json` was spent,
as it had been the last two times, and instructed me to distrust the file and take the refusal at
the instant it fires. **The instruction was right about the method and wrong about the answer.** I
took my own readings and the recorded cause was live, at the current HEAD, and actionable.

---

## The premise the item cited is spent — but not in the direction it expected

The item states that HEAD, the cached `origin/main` and the real remote "all read `60bcdec35`".
Measured at draw time, read-only:

| | reading |
|---|---|
| `git rev-parse HEAD` | `3867ba3e647731883589148a723fe2cae706495c` |
| `git rev-parse origin/main` | `9d7cd5e4f621df70603edd1ba7aba5948c1d1caa` |
| `git ls-remote origin refs/heads/main` | `9d7cd5e4f621df70603edd1ba7aba5948c1d1caa` |

None is `60bcdec35`. HEAD is **two commits ahead** of a remote that agrees with its own cache. So
`behind_origin` is indeed not the live cause — but neither is the "all three agree" premise the item
reasoned from. Both were stale by the time the item was drawn.

## The live cause, taken at HEAD and reproduced independently

`.publish_gate_state.json` carried a refusal stamped `git_hash 3867ba3e6` — **the current HEAD** —
at ts `1788930708`, nine minutes before I read it. Not expired. Its text:

> `[scope-evidence] ❌ COMMIT REFUSED -- 1 atom(s) CLAIM A LEVEL on evidence that is not in the tree
> this commit would create.`
> `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over (level_current 1)`
> `NOT IN GIT: tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py`

I re-derived it rather than trusting it. `python3 -m tools.scope_evidence_ratchet` in the shared
tree exits **0**. The same control inside a HEAD-built extract refuses. Both are correct, and the
seam is one line:

```python
r = subprocess.run(["git", "ls-files"], ...)          # tools/scope_evidence_ratchet.py:103
```

`git ls-files` lists **index entries**. The file's status is `AM` — staged, modified, and never
committed:

```
AM tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py
git cat-file -e HEAD:<path>  →  exists on disk, but not in 'HEAD'
```

So in the shared tree the staged entry satisfies the check; in every extract built from git objects
it does not. **This is not a false positive and the control's own docstring predicted it** (lines
123–133). The map row bumping `level_current` 0 → 1 was uncommitted in the same tree, resting on
uncommitted evidence.

## The structural suspect the item named is REFUTED for this instance

The item's hypothesis: `episode_failures` (now **34**, not 31) counts refusals "expired before
anyone read it", so the count measures races lost rather than publishes prevented — and the proposed
fix was to re-test a refusal before counting it.

**That is false here.** The single recorded failure in the file is live at HEAD, reproducible on
demand, and names a real defect that no re-test would clear. Re-testing before counting would have
kept this refusal exactly where it is. The reason three previous diagnoses were wrong is not that
refusals expire — it is that `behind_origin` was read as the cause when the file's *newest* entry
had already moved on to a different one. **No mechanism is warranted.** A count of 34 with one live
entry is a count of one live entry.

## The second defect, which the refusal could not see

Landing the named file alone would still have failed. `test_every_outstanding_row_names_a_document_
that_still_exists` asserts `.exists()` on the document cited by the single `OUTSTANDING` row, and
that document — `docs/staging/done/SEAT_FINDING_TWO_LANES_BUILT_W1_14S_ARTEFACT_CUT_TWICE_AND_THE_
SHARED_TREE_HELD_THE_LOSING_ONE_IN_A_STATE_THAT_COULD_NOT_COLLECT_2026-09-07.md` — is `??`,
untracked. Measured in a `git worktree add --detach HEAD` extract:

| extract contents | result |
|---|---|
| HEAD + the four paths below | **16 passed** |
| the same, citation document removed | **1 failed, 15 passed** |

The citation is **load-bearing**, not incidental. The map comment claiming the control was "green in
the shared tree AND in a clean HEAD extract" was false on the word *clean*; it is corrected beside
itself in `docs/design/maturity_map.yaml`.

**The consequence is the landable unit, not the count.** W2_28's `file_scope` names two paths and a
two-path commit is red. The minimum unit is four: `tools/reduction_dimension.py`,
`tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py`, the
`docs/design/maturity_map.yaml` row, and the cited document. A control whose green depends on a file
no commit contains is `uncommitted_and_orphaned_work` wearing a passing suite — and the shared tree
structurally cannot notice, because `.exists()` is true there.

## What is next

- The publish wedge's live cause is cleared by this commit; `last_clean_publish` remains the
  acceptance test and is not asserted here.
- `file_scope` as a concept does not carry a control's *citations*, only its sources. Every
  citation-checked control in the tree has the same latent shape. Not measured — named.
