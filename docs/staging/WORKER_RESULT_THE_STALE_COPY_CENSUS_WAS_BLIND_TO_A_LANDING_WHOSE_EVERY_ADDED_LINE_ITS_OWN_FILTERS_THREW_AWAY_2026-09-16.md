**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — drain the stale copies the census says would revert a landing)

# The census was blind to the one stale copy that reddened the suite, because every line its landing added was thrown away by one filter or the other

**2026-09-16, scheduled tick, worker seat.** The drawn item asked for a drain of 13 paths and got
one. The drain is done — 12 down to 5 — but the part worth keeping is that the census could not see
a ninth path, and the ninth was the only one breaking anything.

## The premise, re-measured — and it was wrong in its stated form

The item said eight of the thirteen were *"residue from `dcb8c6d10`'s own landing 30 minutes before
the census ran"* and asked me to **confirm that by mtime against the commit time and clear them**.

Measured. `dcb8c6d10` landed at **2026-09-16 08:52:21**. Every one of the twelve had an mtime
*predating* its own landing commit — the `simulation/svt_*.py` family by eight days
(`2026-09-08 08:42`), `tests/simulation/test_run_phase2b.py` by sixteen (`2026-08-31 17:13`). Not one
postdated it.

So the mtime evidence **confirmed the census verdicts rather than clearing them**. The prediction
was that mtime would exonerate the eight; it convicted them. The cause is that `dcb8c6d10` was
landed through `surgical_land --content`, which never touches the working tree — so a correct
landing leaves the pre-landing bytes on disk by design, and "residue from its own landing" is
exactly backwards. The eight were real.

Recorded here beside the claim rather than quietly revised, because the item's done-condition was
written on that prediction: *"finished when the list contains only paths whose mtime postdates their
own landing commit."* Under the true reading no path can ever satisfy that, and the honest
done-condition is the one I worked to — **every remaining entry is holder work with a named door**.

## What was actually done

| class | paths | route | commit? |
|---|---|---|---|
| refreshable — HEAD strictly supersedes | 8 | `refresh_to_head --write --slug` | **none, and that is correct** |
| the ninth, invisible | 1 (`simulation/renewals.py`) | needed the control repaired first | `d0f398b98` |
| holder work — supplies names HEAD lacks | 5 | `isolate_hunks` → `surgical_land --content` | not yet |

The eight refreshable paths needed **no commit at all**: the repair is the disk write, because the
defect was working-tree bytes that HEAD already superseded. Preserved at
`refs/preserved/refresh-to-head/drain-stale-gate-finding-classes` and
`.../drain-stale-svt-gasroll-family` before being overwritten.

## The finding: an empty evidence set read as "no complaint"

`judge` guards rule 1 with `if distinctive:`. That makes **every filter in `distinctive_lines` a
silent fail-open** — filter the set to nothing and the staleness question is not weakened, it is
*deleted*, and the copy falls through to the symbol-subset leg alone.

`dcb8c6d10` added exactly five lines to `simulation/renewals.py`: three comments, and
`fuel="electricity",` twice. The comment filter took the three. The uniqueness filter took the other
two — correctly, since a line added twice cannot discriminate. **Zero survivors.**

The working copy of `renewals.py` was dated **2026-09-04**, twelve days older than its own last
landing, and dropped the argument that same commit had just made required. The census graded it
**clean**. Meanwhile:

    TypeError: build_svt_schedule() missing 1 required keyword-only argument: 'fuel'

Eight siblings from that one landing were caught and named with remedies. The ninth — the only one
that reddened anything — was the one the filters emptied. Rule 2 could not see it either: the copy
changes an **argument at a call site**, so every module-level name survives.

This file already knew the shape for the *other* filter.
`test_a_repeated_line_is_not_evidence_of_freshness` says in terms that *"the filter must not empty
the evidence set — an empty set makes rule 1 unreachable."* It was asserted of uniqueness and never
of comments.

## The repair — a fallback, not a widening

Comments are weak evidence, not no evidence. A licence header says nothing about provenance, which
is a reason to **prefer** code, not a reason to discard evidence when there is no code to prefer. So
the comment exclusion now applies only while it leaves something behind: `_trivial` keeps its length
and bracket-noise floors unconditionally and takes `comments_are_evidence`; `distinctive_lines`
returns the strong set whenever non-empty and only then falls back.

**Narrow by construction** — reachable only where the strong set is already empty, so it cannot move
a verdict that has evidence. Measured over the 47 modified readable files on the tree: it moves
**two**, and both genuinely predate their own landing by mtime (`2026-09-04` < `2026-09-16`, and
`2026-09-06 17:14` < `2026-09-07 05:44`). The second, `tests/design/test_maturity_map_contract.py`,
is holder work and routes to `isolate_hunks`, not to a destructive refresh.

**Mutation-proven:** restore the pre-fix `_trivial` and, on a fixture reduced to `dcb8c6d10`'s exact
shape, `distinctive_lines` returns 0 lines and `judge` returns `None` on a copy that reverts a
landing. With the fallback: 3 lines and `predates_landing`. Three controls landed, with both sides
of the partition constructed — the fallback fires where needed, and does **not** fire while code
evidence survives, because a fallback that had quietly become unconditional would pass the first
test and nothing else would notice.

## What is left, and why none of it is a refresh

Five paths remain, all holder work:

- `background/supervisor.py` — supplies `PUBLISH_GATE_WINDOW_SECONDS`
- `tests/background/test_finding_classes.py` — supplies 6 names
- `tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py` — supplies 6 names
- `tests/design/test_maturity_map_contract.py` — supplies 6 names (**newly visible**; this is the
  repair above earning its keep)
- `tests/simulation/test_the_tariff_type_read_has_one_home.py` — **an instance of the live BLOCKING
  finding**, not a landing to make. Its one "name HEAD lacks" is
  `test_the_two_commodities_are_read_differently_and_that_is_the_finding`, a control HEAD
  *deliberately deleted* when it went red exactly as its own docstring contracted. Counting names
  reads a deleted control as work to land, which is
  `SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND_2026-09-08.md`
  verbatim. Landing it would re-introduce a control the trunk killed on purpose.

## Two tree repairs made in passing, neither needing a commit

- **TWO ROOMS**, blocking `finding_classes --check` (rc=1) and therefore every lane's commit.
  `SEAT_RESULT_THE_LAST_158_REFUSED_RENEWALS_...md` sat in both `docs/staging/` and
  `docs/staging/done/`. `staging_two_rooms_repair --repair` left it as a hand-resolve. HEAD holds
  **only** the `done/` copy; the root copy was an uncommitted re-add (04:43) older than the
  archival (07:14), and the discharge is corroborated on disk — the control it contracted to delete
  is gone, its named successor exists. Removed; its blob was already an object in the repo, so the
  removal is losslessly reversible. Gate now PASS.
- **The static quality ratchet** is red in the shared tree (`I001` census 1307 vs baseline 1308) and
  **green in a clean HEAD extract**. The single file responsible is
  `tests/tools/test_generate_maturity_map_data.py`, which another lane is holding with an
  uncommitted import-order fix. Not mine, and not a blocker to a `surgical_land` landing, which
  gates the tree the commit would create rather than the shared working tree.

## Predictions filed, for the next session to refute

1. The four genuine holder-work paths will each land cleanly through
   `isolate_hunks --keep` → `surgical_land --content`, because each supplies names that are
   additions rather than resurrections.
2. `tests/simulation/test_the_tariff_type_read_has_one_home.py` will **not**, and cannot, until the
   holder-work rule stops counting names — it will keep re-appearing in every census as holder work
   for a control that no longer exists.
