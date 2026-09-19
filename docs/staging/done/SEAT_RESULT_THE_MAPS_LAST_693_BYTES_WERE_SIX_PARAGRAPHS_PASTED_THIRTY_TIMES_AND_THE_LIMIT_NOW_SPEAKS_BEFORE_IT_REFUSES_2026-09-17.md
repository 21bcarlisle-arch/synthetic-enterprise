**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# RESULT: the map's last 693 bytes were six paragraphs pasted thirty times, and the limit now speaks while the write still succeeds

Delivery seat (lane 0), 2026-09-17. Claim
`drain-the-maturity-map-so-a-level-move-stops-wedging-every-lane`. Discharges
`SEAT_FINDING_THE_MAP_IS_185_BYTES_FROM_ITS_RATCHET_CEILING_SO_THE_NEXT_LEVEL_MOVE_WEDGES_EVERY_COMMIT_2026-09-17.md`
(all three of its remedies).

## What the headroom actually was, measured

| | bytes |
|---|---|
| headroom when the finding was filed | 185 |
| headroom at the start of this turn | 693 |
| **headroom now** | **9,900** |
| ratchet (`MAP_SIZE_CEILING`, unraised for the fourth time) | 409,600 |

**693 bytes was below the median.** Over the 200 most recent commits touching either half, 127 grew
the map, and the growth distribution is median **+695**, p75 +2,008, p90 +4,451, p95 +6,404, max
+19,406. So the next ordinary map commit was about an even-money bet to wedge `tests/design/` for
every lane, and the finding's "under two lines of comment" was if anything generous.

That distribution is also where `MAP_SIZE_WARN_HEADROOM = 8 * 1024` comes from — derived, not
picked: it is above p95, so a lane that sees the warning has roughly 19-in-20 odds that its own next
map commit still lands. A warning has to arrive with room left to act in, which is the one property
the refusal it backs up cannot have.

## What the bytes were

**9,207 bytes of byte-identical text, six paragraphs across thirty rows.** Not accreted prose and
not a growing field — the two shapes the previous drains (H32, H41) were built for. Each paragraph's
subject is a *family* of rows (the R1–R5 re-ranking, the EP adapter block lift, the three-stage
supersession, the phase-1 dial inheritance, two "minted ahead of its predecessor" mints) and it had
been pasted onto every member.

**One copy had drifted into being false where it sat.** The "Derived, not picked: 45 gives the eleven
R1–R5 atoms 75% of a dial-weighted draw" paragraph is pasted onto rows carrying `dial_inherited: 50`
and `60` — with the paragraph directly above it saying the derivation "was for 45 and is NOT redone
here". A reader of that row is told a number that is not the row's. That is what recitation costs
beyond bytes, and it is the argument for one home rather than thirty.

All six now live in `docs/design/MATURITY_MAP.md` §8a, once, each naming the rows it covers, with
the director's wording kept. The rows keep the one-line pointer to the ruling they already carried.

## What now warns, and where

1. **`tools/maturity_map_store.size_warning()`** — the limit read the other way round. It states the
   headroom, says *this commit fits*, and names the remedy downward only (drain, rehome), never
   raising the ceiling. Over the line it changes register: it says the map is OVER, and that
   `tests/design/` is now red for **every lane**, not just this commit.
2. **`tools/level_promotion_gate.py` prints it on every commit that stages the map.** That gate
   already holds the staged bytes of both halves and already fires on exactly the commits that move
   a row. It **never changes the exit code** — a warning that can refuse is a second ratchet under a
   softer name, and the level move this gate exists to record must not be blocked by the map's size.
   `test_a_map_OVER_the_ceiling_is_still_ALLOWED_by_THIS_gate` pins that boundary.
3. **`python3 -m tools.maturity_map_store`** prints bytes/ceiling/headroom, for the moment before
   the write — the only moment the number can change a decision rather than explain a refusal.
   Named in `CLAUDE.md` beside the cheap-gate list.

**`MAP_SIZE_CEILING` moved to `tools/maturity_map_store.py`** so the refusal and the warning read one
number. Two copies of one limit is the VAT shape this project has already paid for — one rule, five
implementations, fixed in one of them in July and still live in another in August. The one-byte
mutation proof in `tests/tools/test_pre_commit_gate_store_surface.py` now sizes itself from the new
home, still by reading the source text rather than importing it (importing would make the proof
agree with whatever the control agrees with).

## The drain's own control, and the refusal it actually issued

`tools/drain_map_duplicated_provenance.py` re-loads both halves after rewriting and compares the
atom records for **deep equality** — a comment drain may not move a single parsed value. It also
asserts the copy count of every block before touching anything.

**That second control fired on the first run and it was right to.** It found 11 copies of a
paragraph where the census counted 9, because the three-stage supersession block *ends* with its own
copy of the 45-derivation. Deleting the containing block first leaves exactly the 9 free-standing
copies. A drain that had silently deleted 11 would have removed two paragraphs nobody had reviewed.

`--check` is the falsifier and is idempotent: exit 0 means no duplicated block is left in the map.

## Two reds in the working tree were other lanes', and only one was repairable

Running the cheap gates found `tests/design/` and the ruff ratchet red, neither of them mine:

- **`test_ungradable_build_rows_allowlist_has_no_FIXED_entries`** — a working copy of
  `tests/design/test_maturity_map_contract.py` ten days older than the commits that fixed it had
  re-added `A49` and `H47` to `LEGACY_UNGRADABLE_BUILD_ROWS`, undoing two landed delistings. Pure
  stale copy, no holder work; refreshed with `tools/refresh_to_head.py --write` (preserved at
  `refs/preserved/refresh-to-head/map-allowlist-reversion-2026-09-17`). `tests/design/` is 143 green
  after it. **This was wedging every commit in the tree, not just mine.**
- **`I001: 1307` against a frozen baseline of 1308** — attributed to one file, by diffing the
  per-file violation set between the working tree and a clean HEAD extract:
  `tests/tools/test_generate_maturity_map_data.py` carries another lane's uncommitted work which
  sorts its imports and adds a test. Live work, not stale; left alone. Landed via
  `tools.surgical_land`, which gates the tree the commit *would* create, so the census in the gated
  tree is HEAD's 1308.

## The falsifiers

    python3 -c "from tools import maturity_map_store as m; print(m.size_headroom(), m.size_warning())"
    python3 -m tools.drain_map_duplicated_provenance --check   # 0 duplicated blocks left
    python3 -m pytest tests/tools/test_maturity_map_store.py tests/tools/test_level_promotion_gate.py \
                      tests/tools/test_pre_commit_gate_store_surface.py tests/design/ -q

If the first prints a headroom under 8,192 with `None` beside it, the warning has been narrowed and
the next lane is blind again. If it prints a negative number, the gate is wedged for every lane.

## What I did NOT do

**The rest of the map's comments are not drained, and most of them should not be.** 79.5 KB of
comment survives across both halves and the bulk of it is the provenance the map is *for*: why a row
is short of its target, what a park waits on, which director decision bounds an exit. The reviewed
remainder splits into two kinds I deliberately left:

- **Build narrative on rows whose evidence doc is named beside it** (W2_30 is the clearest, ~3.6 KB).
  Its home is the store's note tenant, the route H32 used — but that is a field migration with a
  hash proof, and comments have no key and no tenant. It is real work with a real design in it, not
  something to do in passing.
- **Director canon quoted at length** (~15.7 KB over seven blocks). The sources are tracked, in
  `docs/staging/done/DIRECTOR_CANON_*_2026-09-07.md`, so these *look* like recitation. They are not
  safe to cut on that basis: each states the deliverable for a row at `level_target` it has not
  reached, and the canon doc states it for the ruling as a whole. Cutting them would move the
  definition of done one hop away from the row that owes it. If the next drain wants these bytes, the
  question to settle first is whether the row's exit criteria can be stated in two lines with the
  canon § as the pointer — which is a judgement about each row, not a sweep.

With 9,900 bytes of headroom and a surface that speaks at 8,192, that judgement is no longer on
anybody's critical path, which was the point.
