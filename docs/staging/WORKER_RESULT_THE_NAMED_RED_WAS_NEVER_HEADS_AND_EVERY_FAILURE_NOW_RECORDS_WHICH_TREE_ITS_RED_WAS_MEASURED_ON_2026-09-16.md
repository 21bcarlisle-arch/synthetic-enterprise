**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the publisher has never recorded a clean publish in this episode)

# The named red was never HEAD's, and every recorded failure now says which tree its red was measured on

**2026-09-16, scheduled tick, worker seat.** The Lane 0 direction had two halves. The first is
spent — measured, not assumed. The second is built, landed and pushed.

## Half one: the premise is spent, and the way it was wrong is the finding

The item asked whether the red recorded against `3346182b6` —
`site/knowledge/test_index_reflects_the_record.py::test_the_card_copy_is_quoted_from_the_record` —
is red at HEAD or only on the tree the publish commit would create, and to repair it where it
actually is.

Measured in clean `git archive` extracts, three ways:

| tree | verdict |
|---|---|
| working tree | **passes** |
| clean extract of HEAD (`6a9ead27a`) | **passes** |
| clean extract of `3346182b6` itself | **passes** |

**There is nothing to repair.** That test was never HEAD's red. It was red only on the tree the
publish COMMIT would create — HEAD plus the publisher's own writes — and the RUNG-1 draw was sent
to repair it in a tree where it is green. The state file had also moved on by the time the item was
read: `blocking_tests` is now `[]`, `total_red` 0, and the most recent recorded cause is
`behind_origin`, not a test at all.

## Half two: the record already held the answer and dropped it

This is the same shape this module has paid for four times (R15 FAIL-SILENT — the diagnostic is
taken and thrown away at the record layer). The blocking record carries a `census` field, and that
field names the PRODUCER, whose SUBJECT is the whole question:

- the publisher's own scoped gate judges **a clean checkout of exactly one SHA**
  (DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09). Its red IS that SHA's red.
- the pre-commit **hook chain** judges **that SHA plus this publish's own writes**. Its red is not
  established as that SHA's.

Landed in `7a9e4c117`: `red_at_head_verdict` reads that subject and returns one of `yes` /
`commit_tree_subject` / `not_established`, each with its reason, written to both the failure entry
and the top level of `.publish_gate_state.json`. It is pure — it runs no git and no pytest, because
this is the ALARM path and a monitoring step that shells out can hang the pipeline it observes.

**Two claims it deliberately does not make.** A scoped green does not acquit a hook-chain red: the
two gates run different test selections, and reading one as the other's verdict is a claim over a
population it was never measured over. And `commit_tree_subject` is not "green at HEAD" — it says
the subject was a different tree, so HEAD is unproven either way.

Twenty controls, including the partition control (all three verdicts must be REACHABLE — a guard
that refuses everything passes every per-branch test) and the mutation: attributing by SHA alone
and ignoring the census is re-created and asserted to return `yes` for a hook-chain red. **That
mutant is exactly the defect that sent this turn's own draw at a green test.**

## What this does NOT finish, stated plainly

The director's finish condition is `episode_clean_publishes` non-zero. **It is still 0.** This turn
did not publish; it removed the reason every episode re-derives the same question from nothing.

Two things did move in the right direction:

- **The fork is closed and origin now carries this work.** `origin/main` was 4 commits ahead at the
  time of the last recorded failure, which is what `behind_origin` meant. `origin/main` and HEAD are
  both `7a9e4c117` as of this writing, so that specific cause is no longer standing.
- The next failure the publisher records will name its tree.

## The HEAD red this turn met, which is already on the register

Measured on HEAD-plus-this-turn's-two-files only — a shared-tree green measures several lanes —
365 passed and 1 failed:
`tests/background/test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`, on an
undispositioned `.launch_records.json`. It fails identically in a clean extract of HEAD with none
of this work applied, so it is pre-existing and was not caused here.

**It is not a new finding and no new document is minted for it.** It is already row 36 of
docs/staging/reference/HEAD_RED_REGISTER.md, red for 9 consecutive census runs since 2026-09-04,
one of 37 owed there. Minting a finding for a subject the register already carries is the
duplicate-atom shape, and the register's own header says how it is actioned: make the test green,
or name it in the baseline with a reason. Neither is this claim's work.

## Also spent, and worth recording

The shared tree's two other reds met this turn belong to another lane's live work, not to HEAD:
`test_every_disposition_row_still_has_a_live_subject` (on `.standing_red.json`) and the I001 row of
the static-quality ratchet are both **green in a clean extract of HEAD plus this turn's files** and
red only in the shared working tree. That is the ordinary mid-turn state of this tree, and
`surgical_land` gating a clean extract is what made the landing possible at all.

## Claim

**Not released.** `episode_clean_publishes` is still 0 and that is the stated test. The two landed
paths are bound to
`the-publisher-has-never-recorded-a-clean-publish-in-this-episode`.
