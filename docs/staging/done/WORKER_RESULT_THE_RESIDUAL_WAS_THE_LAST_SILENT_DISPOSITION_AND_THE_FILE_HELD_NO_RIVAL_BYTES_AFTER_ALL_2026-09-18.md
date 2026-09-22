**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-disposition

# The residual was the last silent disposition, and the file held no rival bytes after all

**Filed:** 2026-09-18 · **Claim id:**
`the-ordinary-not-done-sweep-still-returns-an-empty-reason`
**Landed:** `2984864c7` — an ancestor of `origin/main` as of 14:12 UTC, carried there by the
reconciliation lane's `2373224d2`.

---

## State in one line

The repair a prior invocation built and never landed is now in a commit, on origin, with a
whole-partition control beside it; `disposition_of` no longer has a return site that answers with
an empty string.

## What the item asked, and what was actually there

The doorbell was right about the important thing and wrong about one detail, and the detail is
worth recording because it would have cost a turn to get wrong in the other direction.

**Right:** PID 2436269 was dead (its 5,400s turn expired ~11:47 UTC; I read the tree at 14:01),
the bytes were on disk, and HEAD carried none of them. `git show HEAD:background/delivery_lane.py
| grep -c _nothing_answered` was `0` against a working copy of `3`. The work was complete and in
the worst state work can be in.

**Wrong:** the item predicted rival bytes in `background/delivery_lane.py` — "the shared tree has
485 modified paths and other lanes' work in that file's neighbours" — and told me to build
HEAD-plus-my-hunks with `isolate_hunks`. I ran it and it reported **5 of 5 hunks mine**, and the
isolated bytes came back byte-identical to the working copy. The neighbours were contested; the
file was not. I landed through `--content` anyway, because the isolated bytes cost nothing once
built and they close the window in which another lane edits the file in place between the survey
and the commit — but the premise that made the instruction load-bearing was not true.

## What landed

`_nothing_answered` splits the residual into four branches, ordered least to most trustworthy: a
join **raised** (loudest — a truer disposition may have been lost); **no paths**, so the commit
query could not be built and git was never asked; **paths and hits**, all already bound; and
**paths and no hits**, the only branch that has earned "we looked and found nothing". The three
`except` clauses in `_disposition` now thread an `unanswered` list instead of swallowing the
reason — a declared `None` and a silent `None` had been collapsing into the flattering branch.

Two non-window returns carried the same silence and went with it: `NOT_DRAWN` could not
distinguish "never handed out" from "the store did not open", and `DELIVERED` with no bound paths
published the identical empty string as `NOT_DONE`.

## The control can fail — proven in an extract, not the shared tree

`tests/background/test_every_disposition_names_what_was_checked.py`, 4 tests, keyed over the
**whole partition** rather than one leg per branch, on synthetic ids rather than the live ledger.

| mutation | result |
|---|---|
| residual restored to `{"disposition": NOT_DONE, "evidence": ""}` | **4 of 4 red** |
| the unbound-commit join's `unanswered.append` replaced with `pass` | **1 red** — and the failure message shows a crashed join reading byte-identical to a clean miss, which is the defect itself |

The second is the one that matters: it proves the `unanswered` thread is load-bearing and not
decorative. Both were applied in a `~/.cache` extract with its own `git init`; a mutation in the
shared tree reddens whatever another lane has in flight.

## Live reading after the repair

All four rows the lane holds today read `delivered`, so the residual is not exercised on the
current ledger — which is exactly why the control is keyed to the partition synthetically. The
one branch I could exercise live is the new one:

```
a-name-no-ledger-has-ever-held
  not_drawn | no row under this id in the draw ledger (.delivery_lane_claims.draws.json)
            -- it was never handed out, or the store did not open
```

That return site published `""` before this commit.

## Noticed, NOT established — for whoever picks it up

`tests/architecture/test_static_quality_ratchet.py` is red on the shared working tree: I001 at
**1307** against a frozen **1308**, i.e. the tree is one *better* than the floor and the baseline
is stale. Two facts and no conclusion:

* It is **not mine.** Both files I landed are I001-clean (`ruff check --select I001` passes on
  each), and a clean file cannot *lower* the count.
* It did **not** block me — `surgical_land` gated and landed, because the pre-commit selection is
  by subject module stem and that ratchet was not in my subject's selection.

A `git commit` from the heartbeat lane (PID 3197047) was refused at 14:04 with HEAD unmoved, and
I do **not** know that this ratchet is why — I did not measure it and am not going to assert it.
The honest bound is narrower still: that ratchet censuses the **working tree**, which carries 485
modified paths from several lanes, and its own module comments say at length that a dirty-tree
reading is not a HEAD reading and that a baseline re-frozen from a dirty tree reds every other
lane. So "1307 vs 1308" is a statement about the shared tree this afternoon and about nothing
else. **Do not re-freeze the baseline from it.** Establishing whether clean HEAD is red needs an
extract with a real `.git`, which is a different item than this one.
