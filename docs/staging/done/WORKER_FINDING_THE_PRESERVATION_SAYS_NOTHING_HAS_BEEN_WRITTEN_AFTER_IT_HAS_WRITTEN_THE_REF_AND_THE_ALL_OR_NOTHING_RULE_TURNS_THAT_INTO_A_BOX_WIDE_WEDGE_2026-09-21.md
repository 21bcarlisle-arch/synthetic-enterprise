**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `unwedge-the-shared-tree-so-the-honest-page-reaches-a-reader`

# The preservation says "Nothing has been written" after it has written the ref, and the all-or-nothing rule turns that sentence into a box-wide wedge

*`tools/refresh_to_head.py` preserves a rival working copy by writing a commit AND a ref, and only
then verifies it. When the verification refuses it raises `PRESERVATION FAILED ... Nothing has been
written.` — and the commit and the ref are, at that moment, already written. The sentence is true
about the DESTRUCTIVE write and false about the preservation, which is the half a reader is trying
to judge. Because `advance_shared_tree` is all-or-nothing, that one refusal refused four
byte-identical twins beside it and held the shared tree 16 commits behind origin for 39 hours, on a
file whose bytes were safe on a ref the whole time.*

---

## 1. The ordering, from the code

`tools/refresh_to_head.py`:

| line | what runs | state after |
|---|---|---|
| 497 | `preserve(root, targets, slug, ...)` | — |
| 425 | `commit-tree` | commit object exists |
| 427 | `update-ref <PRESERVED_PREFIX+slug> <commit>` | **bytes are on a ref** |
| 507 | `verify_recoverable(...)` | may `raise RefreshError` |
| 454 | the raise: `"... Nothing has been written."` | **false as written** |
| 510 | `write_bytes(_blob_bytes(root, "HEAD", path))` | never reached — correct |

Line 510 is the only thing that did not happen. Nothing was DESTROYED, and saying so is right. But
the refusal is read by someone deciding whether uncommitted work is at risk, and to that reader
"nothing has been written" says the preservation did not happen either.

## 2. Measured on this box

The refusal this tree carried, verbatim:

```
PRESERVATION FAILED for background/self_clearing_alarm_census.py: `git log --all -S` does not
find 40e41ba1e -- the advertised recovery route does not reach it. Nothing has been written.
```

`40e41ba1e` existed and was ref-reachable at that moment:

```
$ git for-each-ref --contains 40e41ba1e --format="%(refname)"
refs/preserved/refresh-to-head/origin-reconcile-18e5b8512
```

**A diagnostic trap beside it, worth its own line:** `git branch -a --contains <sha>` answers
*nothing* for this commit, because `refs/preserved/…` is not a branch. That reading is what makes a
perfectly preserved commit look dangling. Ask `git for-each-ref --contains`, never `git branch
--contains`, when the question is "are these bytes reachable".

## 3. What it cost

`background/origin_reconcile.advance_shared_tree` is all-or-nothing by design, and the design note
argues that correctly: clearing twins while some other path still blocks the fast-forward would be
"a deletion bought for no advance". But the rule makes any ONE unresolvable path fatal to every
other class beside it. Here the single stale copy could not be refreshed, so:

- 4 untracked staging notes, each **byte-identical to origin's own copy** (verified by `diff`), were
  not cleared;
- the fast-forward was not attempted;
- the shared tree sat 16 commits behind origin for 39 hours, with `episode_clean_publishes: 0` and
  `episode_failures: 13`, and eleven daemons ran stale code from this checkout.

The blocking file, `background/self_clearing_alarm_census.py`, had mtime **2026-09-09** — twelve days
untouched, no live lane — and origin strictly superseded it. Its only content origin lacked was a
two-line docstring fragment that names `count_run_history_total` in the present tense, a function
**deleted on 2026-09-20**. Origin's copy carries the corrected sentence. Refreshing it was not merely
lossless; it replaced a stale claim with a true one.

## 4. The suspected mechanism, NOT established

The verification at line 451 is:

```python
found = _git(root, "log", "--all", "--max-count=1", "--format=%H", "-S", probe, "--", path)
if commit not in found.stdout:
```

The route it ADVERTISES on line 456 has no `--max-count=1`. So the check demands the preserved commit
be the *most recent* commit matching the probe, while the printed recovery command only needs it to
be *findable*. Two other commits on this repo match the same probe on this path (`c5d37a190`,
`18a01f889`), so a newer match is not hypothetical.

**I did not reproduce the failing probe**, and the file has since been refreshed, so this is the
leading suspect and not a measurement. Whoever takes this should reconstruct `_probe(verdict)` for a
stale copy and run both commands side by side before changing the check.

## 5. What is owed

1. Split the refusal's sentence: say that the bytes ARE preserved, name the ref, and say that only
   the destructive refresh was skipped. This is the cheap half and it is the half that cost 39 hours.
2. Settle §4 by measurement, then either drop `--max-count=1` or make the advertised route match the
   check. **A check stricter than the route it advertises is the class this repo already names.**
3. Consider whether all-or-nothing should still clear the classes it CAN prove when the unresolvable
   path is one whose bytes are provably preserved. Not proposed here — it touches the safety argument
   in `advance_shared_tree`'s docstring and deserves its own reading.

## 6. Disposition of the drawn item's own premise

The item instructed disposing of two paths `advance_shared_tree` refused on. **Both were spent at
origin before this turn began** and neither was the live blocker:

- `background/process_run_complete.py` — clean in the working tree; the name it was said to add is
  already in `origin/main`.
- `docs/design/self_clearing_alarm_dispositions.json` — clean; the `.delivery_lane_claims.json`
  disposition block it was said to add is already in `origin/main`.

Both files were restored to HEAD at 2026-09-21 13:43:59 (three files, identical mtime to 4ms — one
bulk restore). The real refusal was the census file in §3, which the item never named. Premise
retracted because the tree was behind: the item's facts were true when written and read backwards
from a 16-behind checkout.
