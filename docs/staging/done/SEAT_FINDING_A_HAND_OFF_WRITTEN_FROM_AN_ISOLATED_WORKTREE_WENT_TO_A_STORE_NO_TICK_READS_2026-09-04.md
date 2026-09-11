**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# A hand-off written from an isolated worktree went to a store no tick reads

Filed 2026-09-04 by the delivery seat. **Fixed and landed in the same commit as this finding.**

## The defect

`background/seat_continuation.STORE` was built from `PROJECT_DIR`, which is derived from the
module file's own location. Run from a linked worktree — **which is how every headless executor
turn runs** — it resolved to the worktree's own copy. The store is untracked, so no commit carries
it either. `--hand-off` reported success, wrote valid JSON, and the file died with the worktree,
while `delivery_lane.next_item` went on reading the shared tree's store.

Measured, not inferred:

| tree | `docs/observability/.seat_continuation.json` |
|---|---|
| `/home/rich/synthetic-enterprise` (shared) | 14,383 bytes, written the same day |
| the executor worktree | **no such file** |

## Why it is worse than an ordinary bug

This module exists to stop the seat's judgement dying at the turn boundary. Its own docstring quotes
the director: the contradiction *"resolves onto me pressing enter — the biggest single drag on this
project for a fortnight."* **The turns that most need continuity are the isolated ones, and they
were the only ones structurally unable to get it.** No error, valid output, and the next piece of
work simply never arrives.

**This entry exists only because somebody checked.** Nothing in the mechanism could report it: the
writer succeeded, and the reader has no way to know a hand-off was written somewhere else.

## The fix, and the option not taken

`seat_continuation.shared_tree_dir()` reads the `.git` **file** a linked worktree carries
(`gitdir: <main>/.git/worktrees/<name>`) and resolves the main tree from it, in pure Python, with
no subprocess. Every uncertainty — a normal checkout, an unreadable `.git`, a pointer that names no
`.git` directory, a resolved tree that does not look like this project — returns the current
behaviour unchanged, so the worst case is today's, never a hand-off written somewhere new.

**Tracking the store was the other option and it is worse.** It would make every hand-off a
committed file three lanes merge, and it would still not work: a worktree's commit is invisible to
a tick until it lands *and* the shared tree fast-forwards, which nothing does automatically. The
store is runtime state and belongs where its reader looks.

`tests/background/test_a_hand_off_from_a_worktree_reaches_the_shared_store.py` — eight legs, a
reachability null control (a normal checkout still resolves to itself), four fail-closed legs, and
one that fires only when the suite runs from a worktree and states its premise rather than passing
vacuously. Two mutations proved: `STORE = PROJECT_DIR / ...` and a no-op resolver each fail two legs.

They are a new module because every test in `test_seat_continuation.py` does
`monkeypatch.setattr(seat_continuation, "STORE", ...)`, so by construction not one of them can
observe where `STORE` points — which is the entire subject.

## Adjacent, noticed and not touched

`seat_continuation`'s docstring still states as fact that *"`surgical_land` cannot land from a
`git worktree` at all"*, citing a 2026-08-31 refusal. That is no longer true — the executor lane's
sanctioned door is `tools/surgical_land` **from** a worktree, and this commit landed through it.
The docstring builds its whole "why not a self-advancing seat" argument on that claim, so correcting
it is a real revision of the module's reasoning rather than a typo, and it is not being smuggled
into a commit about the store path. Next piece.
