**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — clear-the-unrecorded-level-bump-then-publish-once-and-take-the-next-refusal-in-the-same-turn) · **Class:** publish_gate_and_wedge

# FINDING — the reconcile refusal told me to land a producer's output, and landing it would have restored a headline origin had just deleted

The shared tree had been behind origin long enough that the published figures were 35 hours old and
32 publish cycles had failed. One path was holding it. The refusal named that path correctly, and
then advised the single action that would have undone another lane's repair.

---

## The drawn premise was spent, and not in the direction the item expected

The item said `docs/design/maturity_map.yaml` was uncommitted with `W2_30` at `level_current: 2`
where HEAD said `0`, and that `gate_authorizations.jsonl` had no `LEVEL_UP` row for it. Measured
read-only at draw time:

| | reading |
|---|---|
| `git show HEAD:docs/design/maturity_map.yaml` → W2_30 | `level_current: 2` |
| working-tree copy → W2_30 | `level_current: 2` |
| `LEVEL_UP_SELF_CERTIFIED` row for W2_30 in the ledger | **present**, ts 1788922232 |
| `LIMITATION_ACCEPTED` row for the lane's blocking canon | **present**, ts 1788922220 |

Both landed in the previous turn's commit. **The level-promotion gate was not the live cause and
had not been for hours.** The item's method — take the refusal at the instant it fires rather than
reading the state file as a diagnosis — was right again, and again it was the item's own premise
that had expired.

## What was actually holding the tree

`python3 -m background.origin_reconcile`, run live:

> `NOT_ADVANCED: origin is 4 commit(s) ahead ... Refused by 4 path(s)` — one `FF_MODIFIED`
> (`site/data/value_arms.json`) and three `FF_UNTRACKED` staging documents.
> `advance: 1 of 4 blocking path(s) are NOT byte-identical to what origin brings, so clearing the
> 3 that are would delete files and still not advance. Nothing was removed.`

That advance-step refusal is **correct and well built** — it declined to delete three files when
deleting them could not have helped, and said so. The defect is one sentence upstream.

## The defect: a producer's output was described as a lane's work

For the one path that mattered, the refusal said:

> *"the 1 MODIFIED path(s) are this tree's uncommitted work and clear by LANDING or reverting them
> here — `python3 tools/isolate_hunks.py --survey <path>` lists the hunks and
> `python3 -m tools.surgical_land --content <path>=<isolated> <path>` lands your bytes"*

`site/data/value_arms.json` is the proof page's feed. **No person wrote those bytes.** Comparing
the three copies:

| copy | `generated_at` | `publishing_tree_commit` |
|---|---|---|
| working tree | `2026-09-09T04:25:38.755861Z` | `16f668451` (5 commits stale) |
| HEAD | `2026-09-09T03:31:39.323136Z` | `953db124f` |
| **origin** | **`2026-09-09T05:11:32.091226Z`** | `9d7cd5e4f` |

Origin's copy is 46 minutes later than the local one and carries real repair from commit
`77d92e0d1` — `is_the_later_run`, `superseded_generated_at`, and a `why_the_headline_omits_it`
block. Most of all it **deletes** the headline sentence beginning *"IN THE WORLD AS IT IS NOW…"*,
which was the very defect that commit was written to fix: the page was calling its older run "now".

The local copy still contained that sentence. **Following the refusal's first and most detailed
advice would have re-published a headline that another lane had just removed as false** — and it
would have looked like a successful landing.

## It is a class, not a file

`tools/file_scope_generated_paths.generated_artefacts()` already derives the set of paths a
producer writes — 176 members — for an unrelated gate. Measured against the live shared tree:

| | count |
|---|---|
| modified tracked paths | 658 |
| **of which the oracle calls GENERATED** | **71** |
| hand-written (the landing recipe is right for these) | 587 |

Any of those 71, on colliding with origin, draws the same wrong remedy. The map already states the
principle at `docs/design/maturity_map.yaml:1816` — *"that is the derived OUTPUT … Scope the
generator, not the generated"* — so the idea was in the tree; the refusal just never asked.

This is the third kind that `paths_blocking_fast_forward`'s docstring did not enumerate. Its two
kinds split on *tracked vs untracked*, and both assume the bytes are **work**. A generated path has
no owner, so "whose work is this" has no answer, and the question that does have one — which run is
later — is settled by the fast-forward plus the next regeneration. It also sits beside the open
`SEAT_FINDING_THE_STALE_COPY_REMEDY_HAS_NO_MOVE_FOR_A_RIVAL_COPY_HEAD_ALREADY_SUPERSEDES_2026-09-08`:
same shape, different control. Reverting is not a loss here, and that is exactly what makes it the
cheap move and exactly what the old text talked the reader out of.

## The fix

`background/origin_reconcile._split_generated` partitions modified blockers against the oracle, and
`_landing_clause` gives the generated side its own step: *do NOT land them … `git show HEAD:<path> >
<path>`, then let the fast-forward install origin's copy and the producer regenerate.*

**Fail-SOFT here, deliberately, against this repository's usual rule.** Everywhere else an oracle
that cannot answer must fail closed. This output is remedy *prose*, not a gate: raising would turn
"I cannot classify these paths" into "the tree may not advance", which is strictly worse than the
refusal already printed. So an unavailable oracle returns every path as authored **and prints that
it could not be asked** — an unsplit list that says it is unsplit, never one indistinguishable from
a clean split. `test_an_unavailable_oracle_says_so_rather_than_splitting_silently` holds that.

**Control:** `tests/background/test_a_generated_blocker_is_not_offered_a_landing.py`, 6 legs.
Mutation-proven: reverting `_split_generated` to the pre-fix behaviour (everything authored) turns
**3 of 6 red**, and the 3 that stay green are the authored leg, the fail-soft leg and the
unknown-kind leg — correctly insensitive to that mutation. A poison round runs FIRST
(`test_the_oracle_supplies_both_sides_so_neither_leg_below_is_vacuous`) because every other leg
asserts "X is on one side of a split", and an empty or total oracle set would leave all of them
passing while measuring nothing.

---

## What the turn landed

1. **Reverted** the generated copy (`git show HEAD:site/data/value_arms.json > …`), bytes salvaged
   first. This is the action the refusal advised against.
2. Reconcile then cleared the collision and hit a **different** cause: `.git/index.lock`, held by a
   live 28-minute `git commit` (PID 60941, the delivery seat's own direction commit, pre-commit
   hook still running). Waited on the named PID via `tools/wait_for.py --pid` — finished in 45s.
   *It was not a stale lock, and killing it would have destroyed another lane's turn.*
3. **Fast-forwarded 5 commits.** `behind_origin` cleared.
4. Verified the gate that refused the 05:04 and 05:11 **content** cycles — the scope-evidence
   ratchet on `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` — is now
   clean at HEAD: the file is tracked and `git cat-file -e HEAD:…` resolves.
5. Cleared a TWO ROOMS red (`finding_classes --check`): the 09-09 value-arms pre-registration
   existed tracked in `docs/staging/` **and** untracked, byte-identical, in `records/`. The root
   copy is the live one — its floor run is still in flight (PID 4064918) — so the `records/`
   duplicate was the stray. Removed; check went FAIL → PASS.
6. **Drove the publisher's own liveness path end-to-end** as the resident seat
   (`_refresh_published_liveness_on_skip`). It published. Verified against ground truth, not the
   log line: `git ls-remote origin main` → `c440337ad5f29c24804a51efa2d72efd63846e12`, equal to
   local HEAD, 0 ahead / 0 behind. **The first publish to reach origin this episode.**

## What is NOT done, and why

`last_clean_publish` is **still `null`**, and the item said done is that and nothing less. It is a
*content* publish and needs a `run_complete_*.md` marker; none exists. The sim runner restarted at
05:58 holding 194s, and its runs take ~55 minutes on a ~1h50m cadence, so the next marker is due
around 07:00Z — longer than this bounded tick.

I am claiming the two blockers are cleared, not that the content publish succeeded. The evidence
for the claim is that the same commit-and-push door (`_commit_and_push_paths`) the content path
uses **was driven end-to-end this turn and reached origin**, and that the scope-evidence gate which
refused the last two content cycles is green at HEAD. If the 07:00Z cycle still refuses, the cause
is a third one, and this record should be read as having predicted that rather than as having
covered it.
