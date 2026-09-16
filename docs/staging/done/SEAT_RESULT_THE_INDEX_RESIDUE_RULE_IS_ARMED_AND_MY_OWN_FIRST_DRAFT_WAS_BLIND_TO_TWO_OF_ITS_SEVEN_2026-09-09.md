**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — clear-the-unrecorded-level-bump-then-publish-once-and-take-the-next-refusal-in-the-same-turn) · **Class:** uncommitted_and_orphaned_work

# RESULT — the index-residue rule is armed, and my own first draft was blind to two of its seven

The previous turn banked
`SEAT_FINDING_THE_SHARED_INDEX_STILL_HELD_THE_FAILED_CYCLES_PRE_LANDING_BLOBS…` and named the work
in its *what is next*: **a one-leg check — index-behind-HEAD on any path is residue, not work — and
it belongs beside the existing stale-copy census rather than in a new register.** That is what
landed. It is `tools/stale_copy_refusal.index_residue`, reached by `--index-residue`, and it is a
third rule in a module that already had two, not a new module and not a new register.

---

## The drawn premise was spent, and saying so is the first result

The item said `docs/design/maturity_map.yaml` is uncommitted in the shared tree with `W2_30` at
`level_current: 2` where HEAD says `0`, and that `gate_authorizations.jsonl` has no `LEVEL_UP` row
for it in 271 rows, so the level-promotion gate refuses every publish commit. Measured on real
disk/git state at draw:

| | reading at draw |
|---|---|
| `W2_30.level_current` at HEAD | **2** — and the working tree is byte-identical, `git diff HEAD` on the map is empty |
| `LEVEL_UP_SELF_CERTIFIED` row for `W2_30` in the ledger | **present**, with a `LIMITATION_ACCEPTED` row beside it |
| ledger row count | **277**, not 271 |
| `HEAD` vs `origin/main` | **equal** (`a10da2a48`) |
| `.publish_gate_state.json` | `wedge_since: null`, `episode_failures: 0` — *recovered*, not wedged |

Both halves of the named cause were already false, and the log records `Publish gate recovered --
queue drained to zero, episode CLOSED` at 06:42 UTC with heartbeats reaching origin at 06:00 and
07:32. `last_clean_publish: null` is the episode-scoped trap, not a wedge: grade on `wedge_since`.

So the question became what is holding the tree *now*, and — as last turn — the answer was in the
index.

## What was there: seven paths, and the ledger row was one of them

`git diff --cached` reported the index **behind** HEAD on `docs/observability/gate_authorizations.jsonl`
— 274 rows against HEAD's 277. **The three rows missing are the `W2_30` block**: the
`LIMITATION_ACCEPTED` row, the `LEVEL_UP_SELF_CERTIFIED` row, and its neighbour. A plain commit
taken from that index would have un-recorded the level bump and rebuilt *precisely the
level-promotion-gate refusal this item was drawn to clear* — with the map, the working tree and
every gate green, because disk agreed with HEAD throughout.

The other six were the same mechanism on documents: two pre-archive ROOT copies whose archived
twins are already at HEAD under `done/` and `records/` and **byte-identical** to the staged blob
(so committing them recreates the duplicate that reds the staging gate), two staged deletions of
documents still on disk, and `site/data/knowledge_how_many_synthetic_households.json` — a staged
ADD of the per-page feed that
`site/test_the_sampling_page_reaches_the_reader.py` exists to say *was not being published*. That
page was rewired to the consolidated `knowledge_topics.json`; the slug is in it, and the door test
is green at 7 passed. Committing that index entry resurrects the file the fix deleted.

## The measurement that refuted my own first draft

I specified the leg as set arithmetic — `git diff --cached` minus `git diff HEAD`, "staged but the
working tree does not ask for it". It reads as the same question as the property and it is not.
**`git rm --cached` leaves the file untracked, and git then reports an untracked path as *deleted in
the working tree* even though its bytes sit on disk unchanged.** The proxy scored those paths as
"the working tree disagrees with HEAD" and dropped them.

| | paths found on the shared tree |
|---|---|
| draft 1 — set arithmetic (proxy) | **5** |
| draft 2 — HEAD blob vs `hash-object` on disk (property) | **7** |

The two it was blind to are `D ` beside `??` — the banked half-staged-archive-move class that reds
two rooms at once. Both were byte-identical to HEAD on disk. **The gap was found by the test, not by
thinking**: `test_a_staged_deletion_with_the_file_still_on_disk_is_residue` failed against draft 1,
and that is the whole reason draft 2 exists. Keyed to the property, not to the proxy that agreed
with it on today's tree.

## Reachability, proved with a poison round before any claim of coverage

"Survived" means two opposite things, so the battery ran against a known-poisoned rule first. Only
the `-k residue` tests are counted:

| mutation | result |
|---|---|
| always-clean (`if False`) | **3 failed** — the positive legs bite |
| always-refuse (`if True`, flag every staged path) | **2 failed** — the false-positive guards bite |
| revert to the set-arithmetic proxy | **3 failed** — the regression is caught |

The middle row is the one that matters. **A guard that refuses everything passes every positive test
in this file**, and would fire on the ordinary staging that three concurrent lanes always have —
which is the pressure toward bypass that the one legal landing door exists to remove. Suite: 36
passed. `test_the_whole_partition_is_reachable_in_one_tree` asserts both answers in a single tree
and that residue is a **strict** subset of what is staged, so neither "always" can pass it.

## The repair has TWO doors, and naming only one would have been wrong

The finding's stated remedy was `git reset HEAD -- <paths>` — path-limited and mixed, so it rewrites
only those index entries and never touches the working tree (`git checkout` and `git stash` both
overwrite the only copy that is *correct*). That is right for six of the seven. It is **not** right
for a `D ` beside `??` whose twin already exists:

- `SEAT_PREREG_RECONCILING_THE_TWO_VALUE_ARMS…` has a `records/` copy on disk, byte-identical. The
  staged deletion is a *half-finished archive move*, and the completion is to remove the root copy
  from disk and land the move. Resetting would abandon a move another lane correctly started.
- `SEAT_RESULT_THE_PUBLISH_REFUSAL_WAS_LIVE_NOT_SPENT…` has **no** twin anywhere. Its staged
  deletion would delete the document outright. Reset is the only correct door.

Two paths, identical in `git status`, opposite remedies — distinguished only by whether a twin
exists. The refusal text now says so rather than printing one door for both.

That first pair is also why `background/finding_classes --check` was **FAIL (1 failures)** on the
shared tree — `TWO ROOMS … present in records AND root` — which blocks every lane's commit, not
just this one.

## What this does not catch

A lane that has **already pulled** the landing and then rewrites over it is invisible here: its disk
copy differs from HEAD, so the path is out of scope by construction. That is rules 1 and 2's blind
spot and it stays theirs. And the verdict is a **photograph**, not a standing fact — a path leaves
the set the moment a lane starts genuinely editing it. Measured twice four minutes apart while
another lane's commit held the index lock, two paths moved in and out exactly this way. A stale
answer must never be re-read as a current one.

## What is next

- The rule is a **census with a CLI**, not yet a door: nothing calls it before a commit. Wiring it
  into the pre-commit chain is the obvious next step and is deliberately not taken here — a control
  that refuses honest work is worse than one that reports, and it should be watched reporting for a
  stretch first. The population it fires on is a failed cycle's leftovers, so the honest expectation
  is that it reads zero on a clean tree and non-zero only after a refusal.
- `surgical_land` could refresh the index entries for the paths it lands, which would close the
  source rather than detect it. That is the structural fix and it is a bigger change than this one.
