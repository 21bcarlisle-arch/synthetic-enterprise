**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — confirm the first clean publish after the split pair landed)

# PRE-REGISTRATION — is the copy test red at HEAD now that the split pair has landed?

**Written:** 2026-09-16 ~06:10Z, BEFORE any of the three measurements below were run.
**Seat:** Lane 0 delivery, claim
`publish-wedge-confirm-the-first-clean-publish-after-the-split-pair-landed`

## Why this is being written before the answer is known

The drawn item's done-condition is "read `docs/observability/.publish_gate_state.json` for
`last_clean_publish != null` and `episode_failures == 0`". Read live in the shared tree at
05:48:24Z — seven minutes AFTER `d9f9ef69b` landed — it says `last_clean_publish: null` and
`episode_failures: 34`, and `blocking_tests` still names
`site/knowledge/test_index_reflects_the_record.py::test_the_card_copy_is_quoted_from_the_record`.

That does NOT establish the fix failed. The same record carries
`red_at_head: "not_established"` with the reason *"the red was measured at git=dbd92cedc and HEAD
is now git=c2d8ac167"* — both of those commits precede `d9f9ef69b`. So the record is a photograph
of a tree that no longer exists, which is this project's most-repeated reading error on this exact
file. The question has to be re-measured, and the prediction written down before it is.

## The prediction

Measured three ways, as the item itself instructs, because only the third construction is the one
the publisher actually builds:

1. **Clean `HEAD` extract** (`origin/main` = `84bebe197`, nothing uncommitted):
   **PREDICT PASS.** `d9f9ef69b` landed both halves of the authored pair, so the feed and
   `site/knowledge/index.html` agree at HEAD.

2. **HEAD + the shared tree's working-copy `site/data/`** — the construction that showed the
   defect: **PREDICT PASS**, and this is the weaker prediction of the three. It fails if any lane
   has regenerated `site/data/` in the shared tree since `d9f9ef69b`, because that re-creates the
   original split — a newer feed against HEAD's now-stale `index.html`.

3. **Shared tree as it stands:** **NO PREDICTION.** It holds several lanes' uncommitted work and a
   green or red there is not attributable to this fix (green-in-shared-tree measures several lanes).
   Recorded for completeness only; it is not evidence either way.

## What each outcome would mean

- **1 PASS, 2 PASS** → the repair holds at HEAD and in the publisher's own construction. The wedge's
  named cause is cured and the only thing standing between here and `last_clean_publish` is the
  publisher's next cycle. The claim releases on that and nothing else.
- **1 PASS, 2 FAIL** → the repair is correct but the *generator* is not fixed: the publish pathspec
  can still split an authored pair the next time the feed is regenerated. That is the finding, and
  it is a bigger one than the instance.
- **1 FAIL** → the repair did not do what `d9f9ef69b`'s message claims, and that claim needs
  correcting beside itself.

## RESULT — appended after measuring, beside the prediction and not instead of it

Run 2026-09-16 ~06:15Z, `site/knowledge/test_index_reflects_the_record.py`, 12 tests:

| tree | result |
|---|---|
| 1. clean `origin/main` (`84bebe197`) extract | **12 passed** — as predicted |
| 2. HEAD + shared tree's working-copy feed | **12 passed** — as predicted |
| 3. shared tree as it stands | 12 passed — no prediction was made, and none is claimed |

**Prediction 1 and 2 both held.** `d9f9ef69b`'s claim is confirmed: the copy test named in the
live record's `blocking_tests` is green at HEAD and green in the construction the publisher
actually builds.

**One thing I predicted badly, and it is worth writing down.** Prediction 2 was framed as the
weaker of the two, on the grounds that a lane regenerating `site/data/` in the shared tree would
re-split the pair. The shared tree *had* regenerated a large part of `site/data/` — but
`knowledge_wholesale.json` was byte-identical to `origin/main`'s (`b8cd7146b78d` both sides), so
constructions 1 and 2 collapsed into the same test and construction 2 never independently
graded anything. It was a weaker prediction than I thought, for a reason I had not considered:
the two trees agreeing is not the same evidence as the second tree being checked.

**What this does NOT establish.** The live record still reads `last_clean_publish: null` and
`episode_failures: 34`. A green test is not a clean publish. The item's done-condition is
unmet, the claim is NOT released, and the reason is now known to be separable: the named cause
is cured, and the gate state is stale for a different reason entirely (see the finding below).
The live `liveness_surface_refusal` names `behind_origin`, and the shared tree sat at
`d9f9ef69b` while `origin/main` was `84bebe197` — one commit behind.

## The separate thing already established without measurement

`docs/observability/.publish_gate_state.json` is a **tracked** file whose committed content is
`{"alerted_at": null, "failures": []}` from `f534b9f3d`, **2026-07-17** — its only commit. Every
fresh worktree therefore checks out a two-month-old placeholder that reads as green (no alert, no
failures, and neither `last_clean_publish` nor `episode_failures` present at all) while the live
episode is 34 failures deep. This needed no measurement — `git log` on the path establishes it —
so it is filed as its own finding rather than predicted here.
