**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The strand half now asks the tree's clock as well as the item's prose, and the drawn item's own window literals were wrong by two hours

Claim: `the-strand-check-asks-the-prose-for-its-paths-and-the-work-landed-somewhere-else`.

## The premise, re-measured before starting

The doorbell's premise check said commit `118374229` is already an ancestor of `origin/main`. **It is,
and the item says so itself** — `tree_verdict`, `_stranded_paths` and `STRANDED` landed there on
2026-09-17 and the item builds ON that landing rather than asking for it again. The premise is not
spent. Nothing to release.

## What was wrong

`_claim_paths` returns `named_paths` — the paths a draw stamps from the ITEM'S PROSE, before any work
is done. The strand half asked git about those and only those. When the prose predicted the wrong
place, git was asked the wrong question and answered it correctly.

**Measured on this lane's own ledger, not inherited from the item:**

| | |
|---|---|
| row | `the-svt-household-has-no-route-back-to-a-fixed-term` |
| drawn | 2026-09-18 **19:04:59** |
| window closed | 2026-09-18 **20:44:59** |
| `named_paths` | three DOCUMENTS (a market-research note and two staging docs) |
| the turn's work | `simulation/renewals.py`, mtime **19:30:21** — 25.4 min into the window |
| in the named set? | **no**, nor were the other three code paths |

`_stranded_paths` asked about three documents, they were clean, and the lane published `not_done`.
Four paths out of four invisible. "It is built and it is sitting there" was structurally unsayable.

### Correction to the drawn item, recorded beside it

The item states the window as *"drawn 21:00 BST, closed 22:40, `simulation/renewals.py` at 19:30"*.
**The ledger says 19:04:59 → 20:44:59.** The item is wrong by about two hours. What it was right
about is the RELATION it rests on — the mtime falling strictly inside the window and outside every
named path — and that is what held and what the repair keys on. A claim's factual assertion about
the tree is an un-re-asked prediction; this one was half right, and the half that was wrong was the
half that reads like evidence.

## What landed

A second question, asked **only when the named set comes back clean**, of the whole tree, keyed on
the clock: *which paths hold uncommitted bytes whose mtime falls between the draw and the close?*

- `_dirty_with_mtimes` — one scan, so the two questions cannot disagree about what a dirty path is.
  `_stranded_paths` is refactored onto it; its `mtime <= window_closed` discriminator and its
  fail-open direction are untouched, as the item required.
- `_window_attributable_paths` — the new question. `drawn <= mtime <= min(close, now)`.
- `STRAND_CANDIDATE` — a fourth verdict, kept distinct from `STRANDED` because it is a WEAKER claim
  and the reader's action differs: **land those, only LOOK at these**. Its own alarm key.
- `_attributed_by_time` — one writer for the published sentence, because the caveat is the
  load-bearing half.
- `_nothing_answered`'s last branch — **the property the control is keyed to.** "This is a genuine
  miss and the work may still be undone" is what the orientation brief prints and what sends a
  reader off to redo work. Every clause it rested on was about commits on the PREDICTED paths. It
  now cannot be reached while the window holds attributable bytes.

### The lower bound is the whole design, and here is why, at real inputs

Dropping the pathspec buys reach at the cost of every other lane's ordinary work, so the time band
has to do all the discriminating the names were doing. Over the SVT window above, on the live tree:

| question | paths returned |
|---|---|
| 537 dirty entries in the tree | — |
| `mtime <= window_closed` (the strand discriminator, asked tree-wide) | **347** |
| `drawn <= mtime <= window_closed` | **4** |

347 is a wall of noise that would be ignored inside a week. A control nobody reads is not a control.

### And the count is the strength of the attribution, so the sentence says so

Two just-closed windows on the same tree yield **28** and **57** candidates, because three lanes
were writing through them. Four is a list to open; fifty-seven says the window was too busy for a
clock to single anything out. There is no threshold here and no published source for one — the
reader gets the number, what it means, and an explicit `oldest 5 of 57` so the truncation is not
silent.

## What was refuted in passing

Two errors of my own, corrected before landing rather than after:

1. **The broken-scan branch minted a THIRD residual voice.** Accurate sentence, invisible to every
   consumer: `tests/background/residual_voices.py` keys `could_not_ask` on the `CANNOT ANSWER`
   marker and `looked_and_found_nothing` on *"asked git … none."*. A reading that is neither is the
   exact conflation `_nothing_answered` exists to end, arriving one question later wearing correct
   words. It now speaks `could_not_ask`.
2. **My working copy of `test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` was
   BEHIND HEAD** — the exact blob of ancestor commit `1cbf684ed`, superseded by `38a8241f3`. It
   still asserted the pre-2026-09-18 claim that a failed git and an empty git are indistinguishable
   at the wrapper, which HEAD had already refuted. Diff direction: 52 lines only in HEAD, 15 only in
   the working copy, all of them the superseded text. HEAD's bytes were written over it; no holder
   hunks existed. Had I hand-edited the stale copy to make my change pass, I would have landed a
   rival's reverted text.

Two sibling `_git` fakes took `*args` only and so raised `TypeError` on the seam's own `cwd` kwarg —
a stand-in drifted from its subject. Widened to `(*args, cwd=None)`, named rather than `**k`, so any
OTHER kwarg still fails loudly, which is the strictness those fakes are for.

## Controls

One control over the whole partition, extended from three values to four rather than a second file:
`test_ALL_FOUR_VERDICTS_ARE_REACHABLE_FROM_ONE_FIXTURE`. `silent-id` had to be re-cut — it used to
be silent because nothing matched its NAMES, and the whole-tree question would now answer it from
another row's bytes; it is silent here because its WINDOW is elsewhere in time, which is the only
honest way left to be silent and is the property the new reading rests on.

**Twelve mutations, each fired by the leg written for it**, run in a `git archive` extract so no
mutation ever touched the shared tree:

| mutation | leg that fired |
|---|---|
| `tree_verdict` stops asking the second question | partition, SVT geometry, caveat, truncation, alarm |
| whole-tree question reuses `mtime <= close` (drop the lower bound) | partition, before-the-draw |
| `_nothing_answered` stops asking (`tree_verdict` untouched) | **genuine-miss property**, broken scan |
| `_attributed_by_time` drops its caveat clause | by-time prose |
| the truncation is printed silently | `oldest N of M` |
| the whole-tree question is asked FIRST | partition, two strand legs, order |
| a broken scan falls through to genuine-miss | broken scan |
| the broken scan mints its own voice | broken scan |
| candidate routed through the STRANDED alarm | LOOK-vs-LAND |
| `_nothing_answered` ALWAYS takes the candidate branch | the mirror |
| `_window_attributable_paths` returns the whole dirty tree | partition, fresh-bytes, before-the-draw |
| candidate verdict drops `named_paths` | SVT geometry |

The property leg is keyed to the property and not to today's phrasing: it asserts only that the
flattering verdict cannot be reached while the window has attributable bytes, never which words
replace it. Its mirror asserts a clean window still earns the sentence — without it the property leg
is satisfied by a reading that never concludes anything, which is the same defect fail-silent.

## Live reading the hour this landed

Two of the fourteen most recent rows now carry the candidate sentence where they carried an
unqualified `not_done`. One of them is this claim's own window: the mechanism found its own
uncommitted bytes.

## Not mine, found while gating

- `tests/architecture/test_static_quality_ratchet.py` reds on I001 `1308 → 1307`. Per-file census:
  the single dropped violation is in `tests/tools/test_generate_maturity_map_data.py`, another
  lane's uncommitted edit. Lowering the baseline would bind their in-flight work, so it is left.
- `tests/background/test_a_recorded_red_says_which_branch_its_tree_was.py` is UNTRACKED and red —
  another lane's new file, in no commit.
