**Severity:** LATENT · **Lane:** H_harness

# The discharge-citation control NEVER RUNS on the commit that renames a falsifier, so a rename lands green and freezes a lane hours later

**Found:** 2026-08-27, worker tick, while discharging the rung-1c BLOCKING draw on
`CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`.
**Class:** `no_caller_and_never_runs` — the control exists, is correct, and is unreachable from
the commit that creates the defect it owns.
**Measured at:** HEAD `34aad1380`. §1 and §2 are `observed-with-evidence` (R9); §4 is inferred and
labelled.
**Intended rank (P-1):** H_harness backlog, below the live BLOCKING band. It costs hours of lane
freeze per occurrence, not a wrong published figure.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): this tick's drawn work was the blocker
in `34aad1380`, and the repair here is a gate-cost decision that deserves its own measurement pass.

## Class registration

Belongs to `no_caller_and_never_runs`.

---

## 1. What happened, with the commit that did it

`71cdda78a` (2026-08-27, 08:26 BST) re-based an R15 mutation and renamed one node:

    tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py
      test_MUTATION_the_word_only_predicate_fires_this_contradiction_on_the_real_corpus
      -> test_MUTATION_the_word_only_predicate_MISREADS_the_spelling_this_control_was_built_for

The rename was correct and is not in dispute — the old assertion keyed on EP1's outstanding debt
and went red when that debt was PAID, which is R15 evidence with an expiry date.

What the rename also did, invisibly, was falsify a `**Discharged:**` citation in a committed
record that the commit never touched
(`docs/staging/done/WORKER_FINDING_THE_SAME_TRUE_SENTENCE_IS_HONEST_SPELLED_OUT_AND_A_VIOLATION_ABBREVIATED_2026-08-19.md`).
Every artefact a discharge names must exist or the whole release voids — fail-closed by design —
so that finding reverted BLOCKING, and `class_severity` propagated it to the class document, which
refuses level-raises across all of `H_harness`. A correct rename froze a lane on a defect that had
been repaired eight days earlier in `830c47d9c`.

## 2. The mechanism: per-file selection maps the rename to itself

Measured directly against the gate at HEAD:

    >>> tools.pre_commit_test_gate.tests_for(
    ...     'tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py')
    ['tests/architecture/test_no_committed_store_claims_an_unlanded_falsifier.py']

    citation control selected on that rename? False
    'tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py'
        named anywhere in tools/pre_commit_test_gate.py source? False

The renamed file's own tests are selected and they PASS — the store control does not read its own
node names, so nothing in the selected set can see the breakage. The control that does see it lives
in the SIBLING file, is reachable only by editing that sibling, and is named nowhere in the gate.

The failure is therefore silent in the exact direction that matters: the commit that CREATES the
stale citation is green, and the red appears later, on a full run, attributed to whoever is holding
the tick at the time.

## 3. This is the sixth instance of a shape `pre_commit_test_gate.py` already names five times

The file's own comments describe this shape for LEVEL_SURFACE, MINT_MARKER, CANON_SURFACE,
STORE_SURFACE and SITE_SURFACE, each added after an instance. `STORE_SURFACE_PREFIX`'s note is
almost verbatim this defect one surface over:

> removing or renaming one silently falsifies a declaration that lives in a file this commit
> never touched.

`SITE_SURFACE_TESTS` states the general rule the repair needs: *"Per-file selection would fire on
tools/site_reachability.py and stay silent on the exact commit that strands a section."* Substitute
the citation control and the sentence is unchanged. The surface that has no trigger is the one the
staging RECORDS sit on, and its declarations are test NODE IDS rather than paths — which is why
neither the store-surface nor the site-surface prefix catches it.

## 4. Why LATENT and not BLOCKING (inferred)

The control is not untrustworthy: its verdict is correct whenever it runs, it caught this instance
unaided, and its failure message named the exact node. No published figure depends on it. What is
defective is its REACHABILITY at commit time. Filing it BLOCKING would also re-freeze the lane that
`34aad1380` just released, for a defect strictly weaker than the one released — which would be the
severity inflation clause 2 warns about, not caution.

**Population unmeasured, and deliberately not asserted:** I did not count how many other committed
records cite test NODES that a future rename would void. The corpus is ~195 node-bearing citations
across ~82 records by the figure `finding_severity.py` records for 2026-08-18, so the exposure is
plausibly wide, but I have not re-counted it at HEAD and the number is not claimed here.

## 5. Recommendation, recorded not asked (`NEVER_ASK_WITHOUT_RECOMMENDING`)

1. **Add a surface trigger, not a per-file mapping.** The sixth sibling: any commit touching
   `tests/**` runs `tests/architecture/test_no_committed_discharge_cites_an_unlanded_falsifier.py`.
   A citation is voided by editing a TEST, never by editing the record, so that is the trigger
   direction with the evidence behind it.
2. **Measure the cost before wiring it, the way the five siblings each did.** That control read the
   corpus in ~5.5s standalone in this tick — an order of magnitude above the ~0.2s the site-surface
   entries justify, and `tests/**` is a broad trigger. If the cost does not survive measurement,
   the narrower honest trigger is `tests/architecture/**`, which covers this instance and admits in
   the comment what it does not cover.
3. **Then ask the R10 question, because a sixth instance of a five-times-named shape is the
   finding.** Each surface trigger has been added reactively after its own outage. The invariant
   worth extending is that a DECLARATION whose subject lives in another file must have a trigger on
   the subject's surface — which points at deriving the trigger set from the declaration registers
   themselves rather than hand-maintaining a sixth constant that the seventh instance will not be
   in.

## 6. Reversal

Nothing to reverse — this document is a queued finding and changes no behaviour. The instance it
came from is repaired and pushed in `34aad1380`.
