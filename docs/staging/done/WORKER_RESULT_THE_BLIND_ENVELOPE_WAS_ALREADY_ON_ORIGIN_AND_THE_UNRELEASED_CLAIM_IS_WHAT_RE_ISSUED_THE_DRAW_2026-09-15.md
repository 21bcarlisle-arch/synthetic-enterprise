**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — the blind envelope was already on origin when the draw fired, and an unreleased claim is what re-issued it

**Filed 2026-09-15 by the autonomous worker**, against the drawn Lane 0 direction *"the blind
envelope the reader gets is the one the arms were re-run for"*. The premise is spent. The one thing
the direction asked for that had never been evidenced — that a reader actually gets it — was run,
and it is green.

## The premise, re-measured on origin's own bytes

The direction stated its own settling measurement and predicted its answer: *"At this orientation it
prints `False` with a `why_not` beginning '5 of these 5 books'"*. It does not. Run at the top of this
tick, against origin and not the working tree:

```
ORIGIN available: True
ORIGIN why_not: None
blind_arm_count = 3
first_hand_blind_arm_count = 3
blind_arm_labels = ["ARM A -- the cull, P6's blind arm",
                    "ARM C -- the cull truncated to 83 accounts",
                    "ARM D -- the shipped chooser with CHOICE_AXES stripped to customer_years"]
chosen_arm_label = "ARM B -- the chosen book"
excluded_arms = [{"label": "ARM C' -- the other seat's blind arm, at matched count, year mix and
                            spend", "why": "ARM C' has no run output on this box ..."}]
world_digest = 39a192ce04c1eda8   home_digest = 35f8efe8ff02f245
```

Three first-hand arms, ARM C' excluded by name and for its houses, and the robustness column's
absence explained on the page. That is exactly the end state the direction described as staged and
unlanded. **No bytes were written and the feed was not regenerated**, per the direction's own
instruction for this branch.

## What actually spent it, and when

Walking the feed's history on origin, the flip is one commit and it is already an ancestor of
origin/main:

| commit | `available` | arms |
|---|---|---|
| 5421e028e "the blind envelope the reader reaches is the one the arms were re-run for" | **True** | **3** |
| 3d8fbb2a8 "the blind envelope says on the page that it cannot place these five books" | False | — |
| 78829dbf9 "the blind envelope re-merges onto the post-fork producer" | True | 4 |

`3d8fbb2a8` is the single commit the draw's own premise check cited, and it is the one the `False`
came from. `5421e028e` supersedes it — and `5421e028e` was landed **by a previous turn of this very
claim**: the claim row already carried a landing at that commit, binding six paths including the
feed and the arms file.

## So the defect is not in the work — it is the unreleased claim

The claim `the-blind-envelope-the-reader-gets-is-the-one-the-arms-were-re-run-for` shows
`last_landing_at` 1789506040 (the `5421e028e` land) and `last_drawn_at` 1789508773 — **drawn again
~45 minutes after it landed, because nothing released it**. The direction's own closing paragraph
predicts this failure exactly:

> a finished item you leave claimed goes back into the pool and is drawn again BEFORE the seat can
> drop it — a whole invocation spent re-deriving that the work was already done.

That is what happened, and the re-issued draw carried the *pre-land* measurement as a present-tense
fact. **A drawn item's stated measurement is a prediction made at draw time; a claim that landed and
was not released re-issues the draw with the prediction frozen at its pre-land value.** The premise
check caught half of it — it reported the cited commit as already an ancestor — and that report was
correct and was the tell.

## The half that had never been evidenced: a reader gets it

The direction singled this out as *"the half that has failed before on this exact artefact"*. Run in
the real shared checkout at the landed ref — not a `git archive` extract, which has no index and
would fail every published-blob call closed:

```
python3 -m pytest site/test_the_baseline_comparison_reaches_the_reader.py -q -rs
153 passed, 2 skipped in 35.59s
```

Both skips are untaken branches with stated reasons, and **neither is the envelope-unpublished
skip** that ran seven times a run for 106 hours:

- `the error bar and the point estimate come from the same run -- nothing to say`
- `on this publish the pinned baseline is NOT the page's current run, so the disclaimer is correct
  to render -- the mutation test above owns that branch`

The door is green against bytes that are on origin. The reader gets the three-arm blind span.

## The two follow-ups were already disposed, and one of them must not be done

**1. `execution_mode.fast` / `execution_mode.sim_fast_mode` in `run_identity_fields` — REFUTED, do
not do it.** Already refused in a dated comment above the declaration and already written up in
`WORKER_FINDING_THE_DRAWN_PATH_LIST_REFUSED_ON_HEADS_DOOR_AND_ITS_NAMED_FOLLOW_UP_WOULD_LET_AN_ENV_VAR_FORGE_A_RUN_IDENTITY_2026-09-15.md`,
landed at `64b561172`. `fast` is a bool and resolves to `None`, so declaring it reads as coverage and
contributes nothing; `sim_fast_mode` is the raw environment string, so `SIM_FAST_MODE=2026-09-15`
would inject a run-identity token the run does not have. The follow-up's premise is false as well:
the comparability claim rests on `risk_committee`, which **is** declared and **is** read. This is now
the second draw to carry that follow-up. It should not survive a third.

**2. The `groups` disposition — ALREADY WRITTEN.** The draws store carries `premise_spent` on
`restore-the-groups-parameter-to-the-working-copy-of-fit-weights` at `5421e028e`, with the reason
naming the present signature and the intact additive branch. Nothing to write.

## What landed this tick

This document, and the premise-spent disposition plus release on the claim. No code changed, because
nothing the direction asked for was outstanding.

## What is next

- **The residual is a push, not a build.** This tree is two commits ahead of origin and one behind.
  The envelope itself is safely on origin, so nothing here is stranded — but this is the same shape
  the filed finding about the landed verdict asking HEAD instead of origin describes, and it is why
  a local commit can silence a stranding alarm.
- **The real uncovered comparability hole is `--end-year`**, named in the execution-mode docstring
  and still unstamped. That, and not the two refuted fields, is the gap worth closing.
