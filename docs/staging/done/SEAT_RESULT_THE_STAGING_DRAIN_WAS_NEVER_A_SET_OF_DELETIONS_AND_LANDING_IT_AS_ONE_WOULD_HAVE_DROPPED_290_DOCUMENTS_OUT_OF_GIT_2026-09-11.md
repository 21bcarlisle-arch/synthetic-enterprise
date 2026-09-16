**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Knowledge:** none — this is tree/archive state, not domain understanding.

# The staging drain was never a set of deletions, and landing it as one would have dropped 290 documents out of git

Closes the Lane 0 item *"the staging drain is on disk and in no commit"*
(claim `the-staging-drain-is-on-disk-and-in-no-commit`).

Landed: `fffa6c579` (40 moves), `a1db11325` (249 moves + 1 commons repair).

---

## The drawn premise was true and its conclusion was not

The item said: land the 293 uncommitted `docs/staging/*.md` deletions, having verified each
has a surviving copy at depth two or more under `docs/staging/`. Both halves of that check
out on disk. The instruction that follows from them does not, because of the word the check
never asked:

    git ls-files docs/staging/ | grep <basename>    -> only the ROOT path
    find docs/staging -mindepth 2 -name <basename>  -> docs/staging/done/<basename>, and `??`

**The surviving copy was untracked.** `docs/staging/done/` is a normally tracked directory —
2,728 tracked paths at the time — so nothing about it looked unusual; these 290 were simply
additions to it that nobody had ever staged. The working tree did not hold 290 deletions.
It held 290 half-finished MOVES, and "land the deletions" is the destructive half of an
archive.

Counted properly: 290 unstaged root deletions, each pairing with exactly one deeper copy,
289 of them in `done/` and one (`DIRECTOR_CONSOLE_2026-08-30.md`) in both `done/` and
`console/`. The other 3 of the item's 293 were already staged `D` in the shared index by an
earlier lane, with the files back on disk untracked — not mine to commit, and the reason my
first count came to 290 and not 293.

276 of the 290 archived copies are byte-identical to HEAD. The other 13 are strictly
richer: the archive copy carries an appended `## DISPOSITION` section the root copy never
had. So the move loses nothing in either direction, and `git show --numstat` records 287 of
the 289 as pure renames.

## Landing the archive is what made four dead pointers visible, and one was outside staging

Nothing had ever read these documents' claims, because they had never been in git. Tracking
them put them in front of the gates for the first time:

| what refused | the pointer | why it was dead |
|---|---|---|
| `landed_manifest_check` | `PREREG_WHAT_THE_ELECTRICITY_SVT_LEG_...` | filed into `records/` by `71d3cfa16` on 09-08 |
| `landed_manifest_check` | `SEAT_RESULT_THE_ELECTRICITY_SVT_TABLE_...` | **this commit's own move** |
| `landed_manifest_check` | `SEAT_RESULT_BOTH_SVT_LEGS_...` | **this commit's own move** |
| `commons_source_supersession` | `gb_domestic_switching_rate.json`'s `open_finding` | **this commit's own move** |

Three of the four were made stale by the drain itself. Every one is true in substance and
dead as a pointer, so each was repaired by naming where the document actually is rather
than by dropping the claim — the gate offers "land the path or drop the claim" and the
honest third option was neither.

The fourth is the one worth keeping. A **regulatory commons artefact** recorded as
`[ACTIONED] superseded` carried `"open_finding": <a root staging path>`, and the
supersession gate RESOLVES that pointer. A staging-root tidy reached into
`docs/domain_artefact_library/` and would have left a published regulatory artefact citing
nothing. It is the only `open_finding` in the whole library aimed at a moved path — asked,
not assumed.

### The distinction that stopped this being done with sed

186 references to these 249 paths exist in 44 files. Only 4 were repaired. The rest are
prose citations in comments, research notes and — 139 of them — observability LOGS. A log
records what was true when it was written; rewriting one to keep a path resolvable is
falsifying the record to please a grep. The rule applied was: repair a pointer something
**resolves**, never a path something **mentions**.

## What I did not do, and why each is deliberate

* **`docs/staging/done/SEAT_FINDING_THE_SITE_WEDGE_IS_CLEARED_..._2026-09-08.md`** — deferred,
  the single remaining half-finished move. It claims `site/data/delivery.json` landed. That
  path is in the tree, but the SHARED INDEX holds a different version (`5fae4804c` vs the
  tree's `61143a2ff`): another lane's generated feed, mid-landing. The claim is not wrong,
  it is unreadable while two versions are in play, and the file is not this lane's to commit
  or to clear. It stays one path instead of 250.
* **`docs/staging/reference/HEAD_RED_REGISTER.md`** — `e4aa02359` untracked it on purpose.
  Untouched, and the drain never went near it.
* **The two live unarchived registers in the root**, the 3 index-staged root deletions and
  the 2 `docs/staging/records/` deletions — five index entries belonging to other lanes.
* **39 untracked new root items.** The root is `disk=151, HEAD=112`. The difference is live
  queue arrivals from other lanes during the turn. Landing another lane's unfiled draft is
  the holder-work hazard, not the drain.

## The index residue was the hazard the item named, arriving through my own repair

Immediately after `a1db11325` the shared index read **`AD` on all 290 root paths** — staged
as present, absent from the worktree. That is precisely the resurrection the item warned
about ("any lane that runs a producer or takes a careless pathspec resurrects them"), and
the landing that fixed the problem is what re-created it. Cleared with
`tools.stale_copy_refusal --index-residue`, path-limited to the 290 I could prove were mine
(absent from disk AND absent from HEAD) — the tool's own printed repair also named
`simulation/household.py` and seven other paths belonging to other lanes, and running it
verbatim would have unstaged their work.

Root paths tracked at HEAD but absent from disk: **290 → 1**, and the 1 is the deferral above.

## What is next

**343 archived documents in `docs/staging/done/` are still untracked.** The drain fixed the
290 whose root half was deleted; these have no root half left to point at them, so no
deletion advertises them and nothing refuses on their behalf. They are the same class — the
archive existing only in this one tree — minus the symptom that made this one drawable. If
`done/` were ever rebuilt from a fresh checkout, they go.

Second: the four dead pointers were found because tracking a document is what first makes
its claims checkable. 343 untracked documents are 343 sets of unchecked claims, and the
four-in-290 rate here says roughly a handful more are waiting.
