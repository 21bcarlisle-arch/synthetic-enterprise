**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The 22:24Z origin_reconcile.py draft is superseded on origin; dropping it exposed a refresh_to_head probe defect (2026-11-13)

## Premise, re-measured

On the shared tree, `background/origin_reconcile.py` (mtime 2026-11-12 22:24Z) differs from its HEAD
(40a48b5d84, 69 behind origin) in three hunks. All three are already on origin/main (138b0e46f8):
- `_origin_has_entry` helper, and `_absent_here_and_on_origin` calling it: identical on origin, l.622/642.
- `identical_tracked_twins` treating a lane's edit to a path origin deletes as answered: identical, l.608.
- `reconcile()` detail putting the advance's reason ahead of the blocking clause: on origin in other
  words (l.3017), with a fuller comment (76 held of 1,478). The draft's 4 comment lines quote the
  older snapshot (1,393 / 1,315) and add nothing the origin comment lacks.

So there is nothing to land. Disposition: **dropped** on the shared tree 2026-11-13, via
`tools.refresh_to_head --base origin/main --discard-prose`. The draft's bytes are at
`refs/preserved/refresh-to-head/origin-reconcile-2224-draft-bytes` (e0a5bede25). Recover with
`git show e0a5bede25:background/origin_reconcile.py`.

Correction: a redundant second `--write` under the same slug re-preserved HEAD's bytes and moved
`.../origin-reconcile-2224-draft` to 9779884d4, a commit that holds no draft. Nothing was lost. The
draft commit was re-pinned under `-bytes` before any gc could run. The tool overwrites a preserved ref
whose slug is reused; a refusal there is the obvious next guard and is not built here.

## Defect found on the way

The refresh refused with PRESERVATION FAILED although the preservation was sound. `_probe` picked the
longest added line, and that was the `ls-tree` call the draft *moved* into the helper. Its occurrence
count is 1 on both sides of the edge, so `git log -S` cannot report the commit. Fix: a probe must
change the count (`tools/refresh_to_head.py::_probe`). Test:
`test_a_moved_line_is_not_a_probe_because_its_count_does_not_change`, which fails against the old `_probe`.

## Duplicate-claim check

`the-final-bill-issue-day-has-one-home-beside-bill-due-date` holds this path for billing work. That is
not this item; this is a drop, not a build.
