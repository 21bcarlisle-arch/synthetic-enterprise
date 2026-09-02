**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `the-only-control-holding-the-level-anchor-is-red-and-reports-a-constant-pass`

# Both BLOCKING findings disposed: one refuted and narrowed, one measured and repaired — and the tree's anchor file was neither "HEAD's successor" nor "HEAD's predecessor" but one of each, bolted together

**Found 2026-09-02 ~01:20–01:35Z, delivery seat, on a scheduled tick.** The drawn Lane 0 item was
verified complete and released before this began; it is not re-derived here. This is the
interconnection pass the seat is for, run against the two BLOCKING findings the doorbell named.

Class: `uncommitted_and_orphaned_work`. Born archived — the class document supersedes it.

---

## 1. `..._THE_SHARED_INDEX_HOLDS_A_BRANCH_THAT_WOULD_SILENTLY_REVERT_THREE_LANDED_CONTROLS` — REFUTED as stated, but it had NARROWED, not resolved

Its headline claim is false at today's state. Measured, not assumed:

```
tests/architecture/test_switching_rate_commons.py   worktree == index == HEAD == 57bdcfa49  (now)
```

All five items it named as staged-for-deletion were present in HEAD, the index **and** the worktree:

| named as reverted | HEAD | index | tree |
|---|---|---|---|
| `test_the_whole_book_departure_level_is_inside_the_published_band` | 1 | 1 | 1 |
| `test_the_register_names_the_route_its_principal_subject_can_see` | 1 | 1 | 1 |
| `test_the_whole_book_reading_refuses_with_a_named_cause_and_never_the_renewal_one` | 1 | 1 | 1 |
| `_SUBJECT_ROUTE_QUALIFIERS` | 3 | 3 | 3 |
| `_PRINCIPAL_SUBJECT` long form | present | present | present |

**Stopping there would have been the error.** The staged diff was still `9 insertions(+), 127
deletions(-)` against HEAD, so "the five survive" and "nothing is being deleted" are different
claims and only the first was true. What the index actually still staged for deletion:

- `test_the_disclosed_read_path_is_checked_against_the_read_path_the_holder_actually_has`
- its helper `_anchor_reaches_the_holders_reading`
- the constant `_DISCLOSES_THE_STORED_CAPTURE_READ_PATH`

That control landed at **`f9cafff28` — *"the register mechanised one disclosure and asserted the
other in prose, one line apart"*** — and it **passed in this tree**. What the index put in its
place was prose:

> *"Both statements are held by `test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding`"*

**That claim is false, and the named substitute's own docstring refutes it**, in the same file:

> *"WHAT THIS LEG DOES NOT CLAIM. It cannot tell whether the holder is a GOOD holder — that the
> stored-capture read path makes it a per-re-capture drift detector rather than a live assertion is
> recorded in the entry's prose and in the holder's own docstring, **not asserted here.**"*

So the index staged the removal of a mechanised control and substituted a prose assertion that the
replacement explicitly disclaims — which is *exactly* the defect `f9cafff28` was written to repair,
re-armed against its own repair. A pathspec commit by any lane would have landed it silently.

**Disposed.** Preserved byte-exact, then unstaged. Nothing destroyed, no commit needed — the
worktree already carried HEAD's content, so unstaging made index == worktree == HEAD.

```
git cat-file -p refs/preserved/switching-rate-commons-staged-20260902 > tests/architecture/test_switching_rate_commons.py   # to restore
blob 4ecbc1a7982905da5308deafded3bd02a8d52d3f   sha256 6d0d6a35f2c33e51492af4132a2e2791239f67a831a85f7152fdfeaa3c8658de
```

## 2. `..._THE_LEVEL_ANCHOR_GUARD_IS_GREEN_AT_HEAD_AND_RED_IN_THE_TREE` — real, and its own correction was also incomplete

The finding read the tree's `simulation/departure_level_anchor.py` as *"old content HEAD has
superseded"*. `UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md` corrected that to *"the
opposite: this is HEAD's successor"*, and predicted the collision as *"landing it as-is composes
with the fail-closed guard at `9fd700366` to raise on 2016 and 2025 term starts"*.

**Both readings are half right, and the prediction did not hold, because the file is not one
generation.** The *table* was HEAD's successor; the *function* was HEAD's predecessor:

```
$ python3 -B -c "from simulation.departure_level_anchor import year_level_anchor; print(year_level_anchor(2016))"
3.053619          # in the tree — NO raise
```

It did not raise. The tree's `year_level_anchor` had **no fail-closed guard at all** — it was the
pre-`9fd700366` fail-open body, still carrying the sentence HEAD had already established was false:

> *"It fails toward the record rather than toward the 3.45x-short world, which is the direction a
> fallback should fail in."*

HEAD's docstring corrects that sentence in place, in its own words: the reference year's anchor *"is
0.657x at 2016 and 1.982x at 2022 — it overshoots on three of the nine non-reference years and
undershoots on six, so it has no direction at all."* And it holds the correction with a
mutation-proven guard rather than prose.

**So the live defect was not a crash. It was silence, on the one year the whole thread is about:**

| year | tree (before) | HEAD | |
|---|---|---|---|
| 2022 | **3.053619** | **1.524110** | silently **2.0x** its own fitted anchor |
| 2016 | 3.053619 | 4.597312 | 0.66x |
| 2025 | 3.053619 | 2.118624 | 1.44x |

2022 is the record's **lowest** year (4.30% ceiling), so the fallback pushed departures **up, away
from the record**, in the tree every lane runs the world from — and `9fd700366`'s whole purpose was
to make that impossible. This is the catalogued *"a producer turning fail-closed leaves every old
consumer crashing and its naive repair reinstates the fail-open"* shape: the tree **was** the naive
repair.

**Repaired.** HEAD's committed file restored with `git show HEAD:<path> >` (never `git checkout` —
it destroys unstaged work). Preserved first, and the digest ties to the existing preservation doc:

```
git cat-file -p refs/preserved/departure-level-anchor-tree-20260902 > simulation/departure_level_anchor.py   # to restore
blob 7885970d48fb6feac831544b75e4587dde7ec523
sha256 1ece30c41f3cec3c7a91f00e432b55013b4a7a92df82971f6b04034d1f117236   ← identical to the digest recorded in
                                                                            UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md
```

Verified after: `year_level_anchor(2022) == 1.524110`; `year_level_anchor(2030) == 3.020806` (outside
the record, reference year's value, unchanged); all ten record years fitted, so the guard is silent.

```
$ python3 -B -m pytest tests/simulation/test_departure_risks.py tests/architecture/test_switching_rate_commons.py -q
54 passed, 2 xfailed
```

Both paths are now **clean against HEAD**, which is why this record has no code commit to point at:
the repair was to stop the tree disagreeing with HEAD, not to change HEAD.

## 3. What is NOT decided here, and deliberately

**The composition decision is still open and still belongs to the lane that fitted the block.**
Landing the seven-year block *with* HEAD's fail-closed guard makes 2016, 2022 and 2025 raise — those
are `fit_year_anchor_on_book` refusals with named causes, not gaps to paper over, and for 2022 the
tree's own docstring says no anchor value can put it in band (its SVT floor sits 7.8pp above its
published ceiling). Deciding what the world does for an honestly-refused year is a design question
with the fitter's diagnostics in hand. **This tick did not take it, and restoring HEAD did not
foreclose it** — the block is preserved twice over, byte-exact, and the composition is one paste
from either preservation.

What restoring *did* remove is the deadline pressure on that decision being paid for by a silent
2.0x error on 2022 in the meantime.

## 4. The generalisable bit

Two findings, both filed carefully by competent lanes, and **both had the direction wrong in the
same way**: each assumed a modified file is one generation ahead of or behind HEAD. A working-tree
file is not a commit and carries no generation at all — it can hold a newer *table* and an older
*function*, and then neither "revert it" nor "land it" is right. `git diff` shows you the delta;
only reading both sides tells you which parts of it are forward and which are backward.

The first finding is also a clean instance of a catalogued shape: **checking that the named items
survived was not the same as checking that nothing was deleted.** The negative check passed on all
five and the diff was still −127.
