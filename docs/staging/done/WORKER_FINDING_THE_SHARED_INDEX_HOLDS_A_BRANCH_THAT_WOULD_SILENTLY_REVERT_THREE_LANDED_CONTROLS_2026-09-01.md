**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `the-only-control-holding-the-level-anchor-is-red-and-reports-a-constant-pass`

# The shared index holds a branch that would silently revert three landed controls — including the only one that can see 2022

**Found:** 2026-09-01 at HEAD `77e1d68e6` (== `origin/main`), while preparing an ordinary pathspec
commit for `tests/architecture/test_switching_rate_commons.py`. Found by checking the file's state
before editing it, not by a control. **Nothing in the tree would have refused this commit.**

---

## 1. The state

```
$ git status --porcelain tests/architecture/test_switching_rate_commons.py
MM tests/architecture/test_switching_rate_commons.py

worktree blob  ba01b3277   index blob  915fa848a   HEAD blob  f187c0fc8
$ git diff --cached --stat   ->  172 insertions(+), 193 deletions(-)
```

`MM` — the index differs from HEAD *and* the worktree differs from the index. The staged change is
a net **deletion**, and what it deletes is landed work.

**The index blob matches no ancestor version of this file** (checked against all 25 commits that
touched it). So this is not a stale checkout replaying an old commit — it is a live branch that was
taken from before `58c496f64` and never rebased onto it.

## 2. What it would remove

`58c496f64` is HEAD's most recent commit to this file. Its message: ***"the band control was green
on a population the published band is not about."*** The staged index reverts it:

| at HEAD (`58c496f64`) | in the index |
|---|---|
| `_PRINCIPAL_SUBJECT` — the long form, route-qualified, with the reason the name must carry the route | collapsed back to `"the world's own realised departure rate (tools.measure_departure_level)"` |
| `_SUBJECT_ROUTE_QUALIFIERS` | deleted |
| `test_the_register_names_the_route_its_principal_subject_can_see` | deleted |
| `test_the_whole_book_departure_level_is_inside_the_published_band` | deleted |
| `test_the_whole_book_reading_refuses_with_a_named_cause_and_never_the_renewal_one` | deleted |

```
$ grep -c "def test_the_whole_book_departure_level_is_inside_the_published_band" <worktree>
0
```

**The middle one is the only control in the tree that can see 2022.** The renewal-route reading is
structurally blind to 2022 (zero renewal decisions in the capture); the whole-book reading is not,
and it reports 2022 at 12.83% against a 2.9–4.3% band. Deleting it removes the one route by which
the year the level anchor is 1.98x wrong about could ever be caught. See the finding filed
alongside this one.

The deleted `_PRINCIPAL_SUBJECT` text states, in its own words, why it was written:

> *It read "the world's own realised departure rate" — a WHOLE-BOOK name on a reading that is a mean
> over renewal DECISIONS. C1b gave the world a second way to leave and the register kept the old
> name, so every green in this file read as a statement about the book when it was a statement about
> the households that reach a renewal roll.*

That is the exact defect the revert would reinstate.

## 3. Why this is BLOCKING rather than RECORDED

**A pathspec commit is enough to fire it.** `git commit <path>` commits the worktree content of that
path, which carries the staged hunks. Any lane that edits this file for any reason — and it is the
switching-level register, so several will — lands the revert as a side effect of its own change,
under its own commit message. There is no `--no-verify`, no bypass, no carelessness required. The
ordinary, legal, documented route does it.

**And it would read as the opposite of what it was.** This turn's Lane 0 direction was to repair the
two red legs *in this file*. Had that been done by the ordinary route, the commit message would have
said the accountability route was restored while the diff removed three controls. The finding that
caught it would have been unavailable, because the evidence would have been in the commit that
destroyed it.

**Neither red is visible from the side that matters.** At clean HEAD the three tests exist and pass.
In the worktree they do not exist — and a test that has been deleted does not fail; it is simply not
collected. The count moves and nothing names it. This is the same shape as the finding filed beside
it, one level up: *absence and exclusion are indistinguishable to anything that counts.*

## 4. What was done about it this turn

**The file was not touched.** The repair it was drawn for was landed in
`tests/architecture/test_a_departure_reading_declares_its_population.py` instead — an uncontended
file already scoped to exactly this subject — and the two legs in this file remain red at HEAD.
That is a worse outcome for the drawn item and the right one for the tree: landing a revert of three
controls to turn two legs green is a trade nobody would accept if it were stated, and the whole
point of this finding is that it would not have been stated.

## 5. Owed, by the lane that holds the branch

1. **Rebase the branch onto `58c496f64`** rather than merging over it. The two lines of work are not
   in conflict: the index adds `_UNIT_DERIVED_READINGS` and widens `_SCOPE` to `tools/`, which is
   real work and should land. It simply must not land *instead of* the route qualification.
2. The worktree also has one unaccounted census candidate,
   `tools.fit_year_level_anchor:_MARKET_PARAMETER_NAMES`, which is red in the tree and green at
   HEAD — that lane's own work is mid-flight and currently red.
3. **Then** re-key the two legs onto `realised_rate_coverage()` and correct `_HELD_INDIRECTLY`, per
   §6 of the finding filed beside this one.

## 6. The shape, for the catalogue

**A `MM` path whose staged diff only REMOVES landed content is an armed revert, and the trigger is
the ordinary pathspec commit.** The tree's own hygiene rules — commit by pathspec, never `-A` — are
what make it fire, because a pathspec is chosen to protect *other* files and says nothing about the
staged state of the one you meant to edit. **Check `git status --porcelain <path>` and the direction
of `git diff --cached` before editing a shared file, not before committing it** — by then the edit
is already fused to the revert.
