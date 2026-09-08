**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# Seventeen merges are credited with deletions another lane chose, and one of them is the receipt

Answers the **second** *What is next* item in
`SEAT_FINDING_THE_STALE_COPY_GUARD_RE_ASKS_ON_A_MERGE_AND_MAKES_ONE_LANE_DECLARE_ANOTHERS_DELETION_2026-09-08.md`
— *"Census `--drops` declarations against the commit that actually chose each deletion."* The first
item (threading the merge ref) landed at `6ed73f07e` and was re-measured at HEAD before this turn
started, not taken from its own result doc.

## The question had to be re-stated before it could be measured, and the restatement is the finding

**`--drops` leaves no machine-readable mark on the commit.** It is an argument to a landing; the
guard prints the declared paths and the commit carries nothing. So the census as literally
specified — *find the `--drops` declarations* — **cannot be run against the record at all**. That is
not a limitation of the tool; it is a property of the record, and it is why the misattribution was
invisible rather than merely unnoticed.

The answerable question, and the one the finding actually cares about, is the population `--drops`
was the only route through: **a name lost from a file that survives a merge, where this side never
touched that path since the merge-base.** Every such path is one the guard refuses today only for
want of the merge ref, so every one is a path some lane had to declare as its own.

**"Deletion" has two populations here and they are disjoint, not nested.**

| | what it is | in scope? |
|---|---|---|
| A | a **name** lost from a file the merge keeps | **yes — the whole subject** |
| B | a whole **file** the merge removes | no |

`stale_copy_refusal.judge` returns `None` when either blob is absent — *"a deletion is explicit — so
neither is this control's business"* — so the guard never fires on B, `--drops` can never declare
one, and no lane is ever credited by a declaration for one. B was measured anyway so the reader who
asks finds it answered: **48 merge-adopted file deletions across 22 merges.** Real, ordinary, and
not this finding's. The counts do not add and are not added.

## What the census found

`tools/merge_attribution_census.py`, over all 446 merges reachable from HEAD:

* **45 paths across 17 merges** are credited with a name loss they **adopted**.
* **173 name-level items**, of which **133 trace to 17 distinct choosing commits**.
* **40 could not be traced and are printed as such**, per name, never folded into the total.

The heaviest single misattribution is `1719f0122`, carrying **71 names** whose deletion `102c29790`
chose. `3881f47da` accounts for 16 across `company/crm/vulnerability_index.py` and its test.

**`22df46614` is in the output with `_staged` charged to `d3e0e408b`** — the receipt the finding was
written from, recovered by the instrument rather than asserted from the prose. That is the census's
poison round and it is a test (`test_the_census_finds_the_receipt_it_was_built_from`), keyed to two
immutable ancestors of main so it cannot rot.

**So: yes, it had happened before, seventeen times, and nothing would have said so.**

## Two things I got wrong, kept beside the result

**The first draft was blind to 94% of its own rows.** `strict_symbol_subset` details are symbol
names; `predates_landing` details are distinctive **lines**. Reading both as symbol names never
matches a line, so every `predates_landing` row reported *"chooser not established"* — **113 of
120** — in a voice indistinguishable from history genuinely not holding the answer. Not fail-open,
fail-**silent**, which is worse here because the number looked like a finding about git. Fixed by
`_carries(..., rule)`; the untraced remainder fell to 40.

**The walk ran the wrong way and the tests could not tell.** It took the *earliest* deletion on the
ref side. A mutation reversing the walk **survived**, and establishing which — equivalence or
missing test — showed it was neither: the rule itself was wrong. A name can be deleted, re-added and
deleted again, and after the re-add the name is *present*, so the earliest deletion is not what the
merge adopts — it was undone. Now newest-first, driven by
`test_a_name_deleted_re_added_and_deleted_again_is_charged_to_the_LAST_deletion`, and re-adding
`--reverse` turns it red.

A third mutation also survived: an `UNPARSEABLE` early return. That one **was** an equivalence — the
symbol path already returns `""` for an error-message token — so it was **deleted** rather than kept
with a comment claiming a role it never had. Its test asserted the property over a rev range that
did not exist, so the walk was empty; it now carries a poison round proving the same walk can return
a sha.

Final battery: 5 mutations, **5 killed, 0 survived**. 6 tests in
`tests/tools/test_merge_attribution_census.py`; 118 across it and the two guard suites it stands on.

## What is next

* **The 40 untraced names are not yet characterised.** Sampling says they are mostly prose lines
  from paths *added* on the ref side within the range, where there is no parent blob to compare —
  so the absence has no single choosing commit. That is a plausible reading, **not a measured one**,
  and it is stated as unmeasured rather than banked.
* The census has **no caller** — it is on `docs/design/orphan_baseline.json` as one hand row, like
  its sibling censuses. Whether attribution should be checked continuously or asked when a
  who-deleted-what question arises is a real choice and I have not made it. Nothing here is a
  control until that is decided.
