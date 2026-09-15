# [PREREG] Can the no-caller pattern set reach its own stranded instance without taking anything else?

**Severity:** RECORDED · **Lane:** H_harness

**Written:** 2026-09-15, BEFORE the corpus was scored. Subject:
`background/finding_classes.py`'s `no_caller_and_never_runs` pattern set, and the one named
exception carried by
`tests/background/test_finding_classes.py::test_no_archived_instance_is_stranded_in_a_class_it_no_longer_classifies_into`.

## The question

`WORKER_FINDING_THE_BILL_SHOCK_CHURN_CAP_CANNOT_BE_REACHED_BY_ANY_CALLER_2026-08-31.md` is
listed as one of the 14 instances of `no_caller_and_never_runs` and does not classify into it.
Its title states the class in plain English — *cannot be reached by any caller* — and the
pattern set matches `no caller` / `never called` / `never runs` / `unreachable` / `untested` /
`unimportable` / `dead code` / `inert`, none of which is that sentence.

Two outcomes are legitimate and the corpus decides which:

- **WIDEN** — a pattern exists that reaches this instance and whose other movements over the
  whole staged corpus are all documents that genuinely belong to this class.
- **REMOVE** — every pattern that reaches it also drags in documents that do not belong, in
  which case the honest act is to strike the instance from the register's list (it was
  consolidated under a classifier that could not put it there) rather than bend the classifier
  around one document.

## Why this is pre-registered

The immediately preceding claim on this module landed a *blind* narrowing — requiring a control
noun beside `blind` — and the corpus refuted it **in both directions**: it stranded archived
instances that did belong, and it did not move the documents it was aimed at. Nothing but
printing the corpus caught that. So the answer here is not known in advance and the predictions
below are filed before the scorer runs.

## Predictions, filed before the measurement

1. **A `cannot be reached` / `by any caller` pattern reaches the stranded instance.** Near
   certain — it is a literal substring match on the title. Filed so that its being trivially
   true is on the record, not claimed as a finding.
2. **The interesting number is the COLLATERAL, and I predict it is NOT zero.** A pattern built
   around the verb *reach* will move documents phrased *does not reach the reader* / *reaches no
   reader* / *never reached the leg*. I predict **between 3 and 30** such documents across the
   ~3,000-document archive plus the live root, and I predict that **a majority of them are
   genuinely no-caller/never-runs** — the class's own title is *"code and controls nothing
   reaches"*, so the verb is the class's own vocabulary and not a neighbouring family's.
3. **The narrowest candidate (`by any caller` alone) moves exactly one document.** If true,
   that is an over-fit to one filename and should be REJECTED on that ground even though it
   scores perfectly — a pattern that reaches exactly its motivating instance is the pattern
   equivalent of a control keyed to today's answer.
4. **No candidate steals a document from an earlier class in the precedence.** Widening the
   5th class can only take from `figures_on_a_superseded_clock` (6th) and from unclassified.
   I predict **0** moves out of `figures_on_a_superseded_clock`.
5. **Which way I will go:** I expect to WIDEN, on a pattern anchored to *reach* with a
   negation, not on `by any caller`. Recorded now so that choosing REMOVE afterwards is
   visible as the corpus refuting me and not as the plan all along.

## What the measurement is

`classify_file` re-run over every classifiable document in `docs/staging/` and every archived
document in `docs/staging/done/`, once with the pattern set at HEAD and once per candidate, with
every document whose `class_id` CHANGES printed by name. No sampling and no top-N: a silently
truncated corpus scan is how the last narrowing passed.

## What would refute the chosen answer

- WIDEN is refuted if any moved document is one a reader would not call *code or a control
  nothing reaches*.
- REMOVE is refuted if a pattern exists whose only movement is documents that do belong.
- Either is refuted by the stranded-archive control going red on a document other than the
  named one after the change lands.

---

# RESULT — measured 2026-09-15, same day, and prediction 2 is REFUTED

Seven candidates scored over **all 7,879 documents** under `docs/staging/` (root 133, `done/`
3,015, `records/`, `reference/`, `in_progress/`, `console/`). No sampling, no top-N. Every
document whose `class_id` changed was printed by name and read.

| candidate | reaches target | total moves | **live-root moves** |
|---|---|---|---|
| `by any caller` | yes | 1 | 0 |
| **`cannot\|can not\|could not be reached`** | **yes** | **2** | **0** |
| negated `reach` verb (`cannot/does not/never reach`) | yes | 12 | 5 |
| `reaches no <X>` | **no** | 5 | 1 |
| negated-reach + `reaches no X` | yes | 17 | 6 |
| `no <X> reaches/calls` | **no** | 1 | 0 |
| all three | yes | 18 | 6 |

**The decision is WIDEN, on `(cannot|can ?not|could not) be reached`** — the passive of
`unreachable`, which the set already matched.

## Predictions, scored

1. **HELD, and trivially so as filed.** Both `by any caller` and `cannot be reached` reach it.
2. **REFUTED — and this is the finding.** I predicted the wide candidate's collateral would be
   3–30 documents and that *a majority of them would genuinely belong*. The count held (11).
   The majority claim did not: of the five **live-root** documents the wide form would have
   consolidated and archived, **not one belongs to this class**, and three of them say so in
   their own header —
   `SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS` and
   `SEAT_RESULT_SIX_PAGES_ADVERTISED_A_CHECK_THAT_COVERED_A_BODY_THE_READER_CANNOT_REACH`
   both state `**Class:** controls_that_cannot_fail`, and
   `...FORTY_FIVE_FEEDS_REACH_NO_READER_AT_ALL` states `**Class:** measurements_that_mirror`.
   A fourth is another lane's (`A_strategy_governance`), and the fifth —
   `SEAT_FINDING_THE_STALE_COPY_CENSUS_CRASHES...ITS_OWN_SIBLING_MODULES_NEVER_REACHED_DISK` —
   is a **live BLOCKING** finding about modules that never reached disk, i.e.
   `uncommitted_and_orphaned_work`, which the wide form would have filed here and archived out
   of the root.
   **What I got wrong and why it matters:** I reasoned that because the class's own title is
   *"code and controls nothing reaches"*, the verb *reach* is this class's vocabulary. It is
   not — it is **every** class's vocabulary. A feed reaching no reader, a commit not reaching
   origin, a branch not reaching the page and a constant no caller can reach are four different
   families that share one English verb. Widening on the verb classifies on grammar and not on
   subject. Nothing but printing the corpus would have caught that, exactly as on the previous
   claim.
3. **HELD, and it did the work I filed it to do.** `by any caller` moves exactly one document
   in 7,879 — its own motivating filename spelled as a regex. Rejected on that ground despite a
   perfect score, per the criterion recorded above and not one invented afterwards.
4. **HELD.** Every move in every candidate was from `None`. Zero documents were taken from
   `figures_on_a_superseded_clock` or from any earlier class.
5. **HELD in direction, and by the narrow anchor rather than the one I named.** I predicted
   WIDEN "anchored to *reach* with a negation" — which is prediction 2's refuted form. The
   chosen pattern is anchored to *be reached*, the passive voice specifically, and the
   difference between those two is the whole result.

## Why the chosen pattern is not itself an over-fit

It moves two documents, and the second one belongs:
`SEAT_FINDING_THE_BRANCH_HALF_OF_THE_POINTER_SWEEP_CANNOT_BE_REACHED_FROM_THE_PUBLISHED_FEED_2026-09-08`
— LATENT, `H_harness`, and its own summary is *"it cannot be closed by any amount of reading
`site/data/*.json`… structural, not incidental"*. That is code nothing reaches. It is archived
and listed in no register, so classifying it correctly strands nothing and changes no count.

## Consequences, measured rather than asserted

- `python3 -m background.finding_classes --check` → **PASS (0 failures)**, and
  `no_caller_and_never_runs instances=14` — unchanged. **Zero live-root documents move, so no
  consolidation follows and no register is re-rendered by this change.**
- 170 of 170 carried archived instances now classify into the class that lists them (169 before).
- `_KNOWN_STRANDED_ARCHIVED_INSTANCES` is now **empty**, so the stranded-archive control asserts
  over the whole archive with nothing excepted.
- Mutation-proven by deletion: removing the one pattern line makes
  `test_no_archived_instance_is_stranded_in_a_class_it_no_longer_classifies_into` fail, naming
  the instance. Restoring it makes it pass. Run both ways, not reasoned about.

## What this scan turned up that was not its subject

`declared_class_of` reads **76** declarations. **280 further documents declare a class in a
`**Class:**` header field it cannot read**, 57 of them live in the staging root, and 53 of those
57 classify as `None` — invisible to the register they name. Filed separately as
`SEAT_FINDING_THE_CLASS_DECLARATION_CHANNEL_CANNOT_READ_THE_FORM_ITS_OWN_RENDERER_WRITES_2026-09-15.md`.
It is **not** fixed here: the repair would fold 53 live findings into five registers and archive
them in one step, which is not a thing to do as an afterthought at the end of another turn.
