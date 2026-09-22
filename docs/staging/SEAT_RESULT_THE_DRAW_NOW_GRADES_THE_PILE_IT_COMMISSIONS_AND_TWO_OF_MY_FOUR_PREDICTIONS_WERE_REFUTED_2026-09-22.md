**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

**Filed:** 2026-09-22 · **Claim id:** `the-lane-0-draw-never-asks-the-landing-door-to-classify-the-pile-it-commissions`
**Lands:** `background/delivery_lane.py` (`path_note`, `_path_verdict`, `_NAMED_PATH`, wired into
`doorbell`), `tests/background/test_the_draw_classifies_the_paths_it_names.py`
**Pre-registration:** `docs/staging/records/SEAT_PREREG_WHAT_THE_DRAWS_OWN_PATH_CLASSIFIER_WILL_SAY_ABOUT_THE_FOUR_LIVE_FOCUS_ITEMS_2026-09-22.md`,
written before the instrument existed.

# The draw now grades the pile it commissions, and two of my four predictions were refuted

## 1. Dispositions first

**The premise check was right and the work was still owed.** `028ab23d9` is an ancestor of
`origin/main` — that is the point of the item, not a refutation of it: the classifier landing is
what makes "the draw never asks it" a defect rather than a wish.

**Both duplicate-work rivals resolved to "carry on", and one was my own draw.**
`the-lane-0-draw-never-asks-...` is held in `.delivery_lane_claims.json` with `paths: []` at
`claimed_at` 1790058936 — the most recent row, i.e. this turn's own claim.
`restore-the-six-live-reverts-before-anything-regenerates-from-them` is genuinely different work on
the same subject: it *restores* reverts, this *makes the draw see them*. It held
`tools/stale_copy_refusal.py` dirty, so **nothing here edits that file** — the new code lives
entirely in `background/delivery_lane.py` and only calls the door's classifier, which is what the
item asked for anyway.

## 2. What was built

A fourth sibling to `premise_note` / `rival_note` / `successor_note`. Those three ask git, the
claims file and the continuation store whether the work is already spent. None can answer the
question the pile items get wrong, because it is not about commits or claims — it is about **bytes
on disk**, and the only thing here with an opinion about those is the landing door.

`path_note` extracts every path-shaped token from an item's `what`/`why`, resolves it, and runs
`stale_copy_refusal.judge` (readable suffixes) or `clock_judge` (everything else) over it — the
same pair `census` runs, on one path instead of the whole tree. Seven tags, and the fourth is the
one the commissioning item did not ask for:

| tag | means | the door it licenses |
|---|---|---|
| `already landed` | identical to HEAD | none — the item's ask for it is **spent** |
| `predates landing` | copy is older than the last commit to its own path | `refresh_to_head` |
| `holder work` | supplies names HEAD lacks **and** reverts something | `isolate_hunks --survey` + `--content` |
| `dirty` | differs from HEAD, reverts nothing | ordinary; **whose work it is, this cannot say** |
| `untracked` / `deleted` / `directory` | not contested | none |
| `ungraded` | the check could not run | **not a clean verdict** |

`dirty` is deliberately **not** folded into `holder work`. A file that differs from HEAD and
reverts nothing is ordinary uncommitted work, and whose it is, git cannot answer from a path alone.
Calling it holder work would be this project's commonest publishing error — a category nobody
defined, differenced, then treated as a driver. It says `dirty` and says what it does not know.

The note **annotates and never refuses**, for `premise_note`'s reason: an item naming a file that
predates a landing is often still the right work — restoring that very revert is focus item 1 on
this record — so a filter would suppress the item written to fix the thing it detected.

## 3. A defect the first live run found, in the loudest category the note has

`blob_at` is `git show HEAD:path`, which **succeeds on a tree** and hands back its listing, so
`is not None` vouches for every directory — and `Path.is_file()` is False for one. The first live
run graded `docs/staging`, `docs/staging/done` and `site/data` as *"tracked at HEAD and NOT on disk
— a deletion, not a pile"*. **Three false deletion alarms on three separate live focus items**, on
the first run of an instrument built to stop false claims about piles. `git cat-file -t` is what
separates them; nothing cheaper does. Fixed, and `test_a_directory_is_not_reported_as_a_deletion`
names it.

## 4. Reachability, measured on the live tree rather than asserted

A note whose interesting branches are unreachable passes every per-tag test leg by leg. Run over
all **459** dirty paths on the shared tree:

| tag | count |
|---|---|
| `dirty` | 323 |
| `deleted` | 115 |
| `holder work` | 9 |
| `predates landing` | 8 |
| `already landed` | 4 |

Every substantive branch fires on real bytes. The 8 `predates landing` rows are the live reverts —
`docs/institutional/knowledge_map.md`, `docs/design/simplifications/A49_...yaml`,
`docs/data-sources/weather.md` among them, all outside the `READABLE` suffixes and therefore reached
only by the clock rule.

Six mutations were run against the control and all six were **killed**: directory fix removed,
every path graded `dirty`, `path_note` unwired from `doorbell`, the cap silenced, `ungraded`
collapsed into `dirty`, the unresolved count suppressed. Source restored byte-identical afterwards
and verified.

## 5. The predictions, and where I was wrong

| # | prediction | outcome |
|---|---|---|
| 1 | `restore-the-six-live-reverts` returns ≥2 `predates landing`, incl. `net_new_acquisition.py` and `generate_value_arms_data.py` | **REFUTED** |
| 2 | `tools/stale_copy_refusal.py` grades as holder work | **REFUTED** |
| 3 | 30–70% of resolvable named paths are `already landed` | **REFUTED — too low** |
| 4 | ≥1 named path resolves to nothing | **CONFIRMED** (1, in the arms item) |

**1 and 2 were refuted by the world moving under the measurement, not by the instrument.** Both
named reverts and `stale_copy_refusal.py` itself were ` M` on the shared tree when I read it at the
start of this turn and **clean by the time the instrument existed** — the sibling lane landed its
restore mid-turn (`cc5cc0032` for the door). This is the third time in two days the shared tree has
moved inside a single turn's measurement, and it is worth naming as a class: *a working-tree
observation taken at draw time has a shelf life of minutes, and any prediction keyed to one is a
prediction about a tree that no longer exists.* The verdicts are right; my predictions were stale
before they were tested. Kept here beside the claim rather than revised.

**3 was refuted in the direction that matters.** Across the four live focus items, **7 of 7 file
paths — 100%, not 30–70% — grade `already landed`** (10 resolvable paths, the other 3 directories).
Every file the current focus list names has nothing to land. My range was a guess anchored on the
HDD item's 5-of-10 and it was too conservative.

**This partly triggers the prereg's own refutation clause.** I registered that if no named path
graded a revert or holder work, the classifier adds nothing a `git status` would not, and the
honest outcome is to record that its value is the `already landed` column alone. On today's focus
items that is exactly what happened. Two things stop it being the whole story: the column is not
what `git status` gives you — `already landed` is *identical to HEAD*, which fired on 4 paths git
reported as **changed** — and the 8 `predates landing` / 9 `holder work` rows live in the same tree,
one item away from being named by the next pile. The value is real and it is currently
**concentrated in one column**, which is more than I can say from one day and less than the item
claimed.

## 5a. Postscript: the first promotion was refused and the re-measure moved again

`promote_worktree_landing` refused — origin had moved three commits (`cc5cc0032`, `34b2f16df`,
`5c330ac62`), one of which changes `tools/stale_copy_refusal.py`, the classifier this note calls.
Re-gated on the new base, never rebased. All ten controls stay green against the changed classifier.

**The live reading changed inside the same turn, again.** On the new base the four focus items grade
`3 already landed, 1 directory, 1 dirty` / `1 already landed, 1 dirty` / `1 already landed, 2
directory` — two paths that were `already landed` forty minutes earlier are `dirty` now. The §5
figure of 7-of-7 stands as what was true when it was measured and is **already false**, which is the
strongest available evidence for the class §5 names: a working-tree observation has a shelf life of
minutes. It is left uncorrected above, with this beside it, because a prediction and a measurement
quietly revised to match today's tree are worth nothing.

**This sharpens what the note is for.** A per-path verdict is not a fact to cache; it is a reading
taken *at draw time* and printed *into the item that is about to be acted on*, which is the only
moment it is both cheap and current. Any future move to precompute these verdicts into the record
would reintroduce exactly the staleness this closes.

## 6. Known gap, stated rather than hidden

`_NAMED_PATH` requires at least one `/`, which is the one property separating a repository path
from a dotted module name — every item on this lane carries `python3 -m tools.surgical_land`, and a
reader that graded that would report unresolved rows on every item and train the reader to skip the
note. **The cost is that a top-level file named in prose — `CLAUDE.md`, `DIRECTION.yaml` — is never
graded.** That is the chosen side, not an oversight: pile items name directory-qualified paths, and
widening the pattern buys those two names at the price of every version number and abbreviation in
the prose. If a top-level file ever needs grading, the fix is an explicit allowlist of root
filenames, not a looser pattern.
