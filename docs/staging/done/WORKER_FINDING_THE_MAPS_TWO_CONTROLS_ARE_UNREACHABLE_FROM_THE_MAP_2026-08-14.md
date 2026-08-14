# [WORKER-FINDING] The map's two controls cannot be selected by editing the map, and both are red at HEAD right now (2026-08-14)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** measured, not repaired — filed per
`SELF_INTERRUPT_DISCIPLINE` (queue, do not fix on sight; this tick's draw was PB2 FRAME).

Found while landing `7a5221b0b` (PB2 FRAME), which had to write `docs/design/maturity_map.yaml`.

## The measurement, `observed-with-evidence`

Two controls in `tests/design/test_simplifications_store.py` take
`docs/design/maturity_map.yaml` as their subject:

- `test_map_within_size_ratchet_when_store_populated` — the 409,600 B spine ratchet
- `test_counts_match_file_contents` — every atom's declared `simplifications_count` against its
  store file's real count

`tools/pre_commit_test_gate.py::select_targets` was called directly this tick:

| edited path | selects `test_simplifications_store.py`? |
|---|---|
| `docs/design/maturity_map.yaml` | **no** (7 targets, none of them this file) |
| `docs/design/simplifications/<atom>.yaml` | **no** (2 targets) |
| `tools/simplifications_store.py` | yes |
| `tests/design/test_simplifications_store.py` | yes |

So both controls are reachable only from the *implementation* and from *themselves* — never from
either of the two data files they exist to gate. Every edit that can actually break them is the
edit that cannot select them.

**Both are red at HEAD as of this finding**, and neither red was introduced by this tick:

- `git show HEAD:docs/design/maturity_map.yaml | wc -c` = **410,095 B**, i.e. **495 B over** the
  409,600 ratchet. It was already 410,095 at `175392b92`, the parent of this tick's commit.
- `test_counts_match_file_contents` reports two violations, both from the two commits before this
  tick: `D30_the_belief_band_is_this_books_length` (map declares no count at all; store file has 1)
  and `SITE2_two_sided_wall_exhibit` (map declares 4; store file has 5).

**And a commit went through the full gate anyway.** `7a5221b0b` edited `maturity_map.yaml` and
landed via `python3 -m tools.surgical_land`, which runs the repo's own `pre-commit` hook against a
clean extract of the resulting tree — receipt `gate-rc 0`, verified with `--verify`. That commit is
byte-neutral on the map (two `simplifications_count` digits and a date), so it did not *worsen*
anything; the point is that the gate returned green while the map sat 495 B over its own ratchet
with two count mismatches under it.

## Why this is a separate finding from the spine-ratchet one already filed

`WORKER_FINDING_THE_SPINE_RATCHET_HAS_EIGHT_BYTES_LEFT_AND_ITS_REFILL_IS_A_DOORBELL_NOTICE_2026-08-14.md`
measured the same ratchet and states its enforcement mechanism as:

> "because the pre-commit gate selects tests by path stem, it reds *at the commit*, not while the
> change is being written."

**That sentence is false**, and this finding is the refutation. It does not red at the commit
either. The earlier finding's headroom table is not disputed — its arithmetic is intact and its
"eight bytes left" reading was correct for the tree it measured. What it got wrong is the belief
that something would stop the ninth byte. Nothing did: the map is now 495 B past the line and three
commits have landed on top of it.

This is R15's FAIL-SILENT shape at the selection layer rather than inside the assertion — the
control's body is fine and would fire correctly if it ever ran. `inferred`: the same question should
be asked of every other control whose subject is a *data* file rather than a module, because the
selection map is keyed on code paths and a data file has no implementation stem to match. That
generalisation is not measured here.

## What repair looks like — recommendation, not a request

Add `docs/design/maturity_map.yaml` and `docs/design/simplifications/**` to whatever entry in
`select_targets` already maps a path to `tests/design/test_simplifications_store.py`, so the two
controls become reachable from their own subject. `pre_commit_test_gate.py:115-125` already carries
a comment describing this exact class being fixed once before for the map-hygiene tests, so the
precedent and the place are both established.

Two things this repair must not do, both R15:

1. **It must be mutation-proven from the data side.** Editing the map to add one byte over the
   ratchet must RED at the commit. Adding the selection entry without that proof reproduces the
   defect one layer up — a selection rule nothing checks is the same fail-silent.
2. **It will immediately red HEAD**, because HEAD is 495 B over and has two count mismatches. That
   is the control working, not a reason to raise the ceiling. The ratchet moves only by the
   director's word (`CLAUDE.md`: never to make a red test green). The map must be *drained* into
   the store — which is what the earlier finding's rehome recommendation already says — and the two
   counts corrected. **Sequencing matters: drain first, then wire the selection**, or every lane
   wedges on a red it cannot land a fix through.

The two count mismatches are cheap (one added field, one corrected digit) but were deliberately
**not** fixed in this tick: `D30` needs a `simplifications_count` line added, which grows a map
already over its ratchet, and choosing to grow it is the drain decision above, not a bookkeeping
one.

## Evidence

- `tools/pre_commit_test_gate.py::select_targets` (called directly; table above)
- `tests/design/test_simplifications_store.py:68` (`MAP_SIZE_CEILING = 400 * 1024`), `:227`, `:297`
- `git show HEAD:docs/design/maturity_map.yaml | wc -c` → 410,095
- `python3 -m tools.surgical_land --verify 7a5221b0b` → `receipt consistent … gate-rc 0`
- `docs/staging/WORKER_FINDING_THE_SPINE_RATCHET_HAS_EIGHT_BYTES_LEFT_AND_ITS_REFILL_IS_A_DOORBELL_NOTICE_2026-08-14.md`
  (the prior finding whose stated mechanism this refutes)
