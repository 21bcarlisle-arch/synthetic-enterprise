# [WORKER-FINDING] Re-freezing a finding as "not the cause" makes it a better-scoring suspect

**Severity:** BLOCKING · **Lane:** H_harness
**Not-a-suspect-for:** `tests/background/test_staging_archive_policy.py` — §"Not the cause of this episode" below: that test passes at HEAD and every recorded red predates its own repair. This document analyses the citation instrument, so it names the whole trail and scored as its own best suspect.
**Discharged:** `tests/background/test_publish_gate_alert.py::test_an_exonerated_finding_is_dropped_from_the_citation_for_that_red`, `tests/background/test_publish_gate_alert.py::test_an_exoneration_for_another_red_still_leaves_the_finding_cited`, `background/finding_severity.py` — the recommended field is built as parse_exoneration, both named mutations run, and the live citation for the 20th wedge's own suspects is now empty while a different red still cites the same two documents.

**Found:** 2026-08-12 22:10 UTC, drawing the 20th publish wedge (RUNG 1, priority zero).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE — the machine is not blocked, the repair for
this episode's red had already landed. Filed, not fixed on sight.
**Rank:** top of the H_harness backlog. It has now cost two consecutive priority-zero draws.

## Observed, with evidence

`background/process_run_complete.py::linked_findings` (line 3685) ranks staged findings by how many
tokens of the red's blame trail their **text** contains:

```python
hits = sum(1 for n in needles if n in text)
```

The needles are the suspect test files and modules, each in three forms (full path, basename, stem).

The RUNG-1 draw's own instruction is *"dispose of each (fix, or **re-freeze with provenance**)"*.
Yesterday's tick did exactly that: commit `b74357282` appended a "checked against the 19th wedge and
NOT its cause" section to `WORKER_FINDING_A_REPO_WIDE_CENSUS_IS_NOT_DECOMPOSABLE_BY_PATHSPEC_2026-08-12.md`.
To *say* it was not the cause, that section had to *name* the cause.

Needle-hit count for that document, before and after the re-freeze (**observed** — counted against
the live `suspects` in `docs/observability/.publish_gate_state.json`, pre-image via
`git show 83f80e0ce:<path>`):

| | hits | which |
|---|---|---|
| before re-freeze (`83f80e0ce`) | **2** | `process_run_complete`, `process_run_complete.py` — both incidental prose |
| after re-freeze (`b74357282`) | **7** | the two above, plus `test_staging_archive_policy` ×3 and `staging_archive_policy` ×2 |

The disclaimer raised the document's suspect score by 5. It was re-cited to this tick's doorbell,
verbatim, as a finding "ALREADY HOLDING THE SUSPECTS" — the second consecutive priority-zero draw
spent on a document whose own text says, in terms, that it is not the cause.

## The property that breaks

The link is **lexical co-occurrence**, and an accusation and a refutation are the same tokens.
The instrument cannot distinguish "this document explains the red" from "this document denies
explaining the red", so the act of answering it correctly is scored as stronger evidence of guilt.
Answering the draw as instructed makes the next draw worse. That is a positive feedback loop on a
priority-zero channel.

The docstring names the only disposition it can observe: *"Only the scanned staging ROOT counts — a
finding in `done/` has been dispositioned."* So of the two dispositions the draw text offers, the
citation can see exactly one. **Fix-and-archive** clears the citation; **re-freeze with provenance**
is by definition a document that stays in the root (it is still an open backlog item — here LATENT,
QUEUED, rank backlog), and therefore can never clear it. That is R11's orphan transition in its
purest form: a release whose effect is nothing, on a channel that has no other release.

## Why the two obvious diagnoses are wrong

- **Not "the re-freeze was written badly".** Any correct refutation must name what it refutes.
  A re-freeze that avoided the trail's tokens would be unreadable to the human it is written for,
  and would still not clear the citation — it would merely score 2 instead of 7 and be cited later.
- **Not "move it to `done/`".** That would be false. The census finding is a real, open, LATENT
  backlog item whose promote condition has not been met. Archiving it to silence a citation is the
  bulk-archive-to-silence-a-doorbell defect this project has already filed against itself.

## Recommendation

**Give the citation the one thing it cannot currently read: the finding's own answer.** `OPS9`
already put a machine-readable header on every finding (`background/finding_severity.py`). Extend
that same parsed header with an explicit exoneration field the ranker subtracts on, e.g.

```
**Not-a-suspect-for:** tests/background/test_staging_archive_policy.py
```

and have `linked_findings` drop (not merely down-rank) any document whose header exonerates it for
the *current* blocking test. Two properties make it R15-shaped rather than cosmetic: the field names
a specific test, so it cannot become a blanket opt-out of ever being cited; and it lives in the
parsed header block, so a claim buried in prose does not silently suppress a real suspect.

The mutation that must fail: exonerate a document for test A, red on test B, assert it is **still**
cited. And the second: exonerate for test A, red on test A, assert it is gone — run today, both
directions, before the fix, per R15.

Cheaper interim, if the above is not drawn: have the draw text stop asserting that cited findings
"ALREADY HOLD THE SUSPECTS". They are lexical matches, not established causes, and the payload's
own wording is what makes a reader spend a priority-zero draw before checking.

## Not the cause of this episode

**Observed:** the 20th wedge's recorded blocking test,
`tests/background/test_staging_archive_policy.py::test_process_run_complete_still_sees_a_duplicate_after_the_sweep`,
passes at HEAD `90213ebb5` (29 passed, 0.14s; the file is identical to HEAD, no working-tree diff).
All five in-window failures carry timestamps at or before 21:59 UTC; HEAD was authored 22:07 UTC.
Every recorded red predates its own repair.

## Related, already recorded

- `feedback_named_blocking_test_passes_when_you_run_it`
- `feedback_the_wedge_doorbells_cited_test_may_not_exist_anymore`
- `feedback_a_rendered_documents_derived_severity_is_a_snapshot_nothing_re_reads` — same shape one
  layer up: a verdict written once that nothing re-reads against the thing it describes.
- `WORKER_FINDING_A_REPO_WIDE_CENSUS_IS_NOT_DECOMPOSABLE_BY_PATHSPEC_2026-08-12.md` — the document
  this was found on. Its disposition is unchanged and is deliberately **not** re-annotated here:
  adding a third "not the cause" section would raise its score again.
