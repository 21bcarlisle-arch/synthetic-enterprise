**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The hook chain is timed step by step for the first time, and forty seconds of it went to segmenting every assignment in the tree

**Filed** 2026-09-17 · worker · lane 0 delivery
**Item** `the-commit-hook-chain-has-grown-five-fold-and-that-is-what-the-publisher-keeps-losing-to`

> **The chain now has per-step attribution instead of one number, and the first cut is landed:
> `discover_maintained_surfaces` went 42.2s → 2.0s with byte-identical output, proven against the
> unfiltered walk over the real tree.** The two larger contributors are measured, named and NOT
> cut this turn, and they are written down here rather than left to be re-derived.

**LANDED** `54e5a5c87`, merged at `0d9ff275d`, pushed to origin/main. Re-measured at HEAD after the
push: **1.25s, 8 surfaces** — the cut is live, not merely committed.

---

## The item's own premise was partly spent, and one clause of it was wrong

Two claims in the drawn item did not survive re-measurement, and both were already repaired by the
sibling claim `decouple-the-early-exit-floor-from-the-regime-constant...`:

- **`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04 = 134` does not exist.** The constant at HEAD is
  `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17 = 333`. The item named a constant nine characters
  and thirteen days out of date.
- **The fail-open it asked me to fix is already closed.** `_recent_hook_chain_seconds` no longer
  "drops any row whose duration exceeds its ceiling". It drops a row only when
  `duration > ceiling AND outcome != "timeout"` — a row that proves *from its own fields* that it
  was not bounded by this deadline — and keeps it as a `None` hole so the skip can count it. The
  1381s row is excluded because it held **two chains**, which the publisher's own log states. That
  is the conservative direction, not a fail-open.

I carried on rather than releasing: the sibling repaired the **control**, and this item is about
making the **chain** cheaper. Genuinely different work on the same subject.

## What nothing had ever measured

`commit_hook_duration.jsonl` records ONE number per commit. So a chain that grew five-fold could be
watched growing and could not be attributed, and every argument about which step was expensive was
an argument about which step *looked* expensive. `tools/time_the_commit_hook_chain.py` is the
instrument the direction asked for. Measured 2026-09-17 on a quiet box, 16 cores:

| step | seconds | fires on |
|---|---|---|
| **site_lane_gate** (`pytest site/`) | **142.9** | any `site/**`, `site/data/**` or `generate_*_data.py` |
| **test gate's always-run control set** | **185.4** | any commit staging a code file |
| **startup_anchor_freshness** | **33.6** | any commit staging a startup anchor |
| orphan_ratchet | 21.6 | every commit |
| company_network_isolation | 4.7 | every commit |
| annual_report_import_ratchet | 4.4 | every commit |
| file_scope_generated_paths | 3.8 | every commit |
| running_total_order | 2.8 | every commit |
| the remaining eleven steps | < 1 each | — |

The observed 333s and 667s rows are these numbers, not a mystery: a publisher commit stages
`site/data/*` and pays the site suite; a code commit pays the control set; a commit doing both pays
both.

## The cut that landed

`startup_anchor_freshness.discover_maintained_surfaces()` called `ast.get_source_segment()` once per
`Assign` node across `tools/` + `background/`. That function **re-splits the entire file into lines
on every call**, so the scan was O(assignments × file size): **42.2 seconds to return eight
surfaces**, paid by every commit that stages an anchor.

The repair is a prefilter that is *exact, not approximate*: skip a file with no literal `"docs"` in
it, and segment only nodes whose line span includes a line that has one. A node's source segment
lies wholly within `lineno..end_lineno`, so a node spanning no such line cannot match the regex —
and the line set is a **superset** of the matching nodes, so nothing the unfiltered walk found is
lost.

- **18,947 `get_source_segment` calls → 450.** 218 of 445 modules are never segmented at all.
- **42.19s → 2.01s, `IDENTICAL: True`** against the unfiltered walk over the real tree.

## The control, and the mutation that proves it fires

`test_the_prefilter_finds_exactly_what_the_unfiltered_walk_finds` grades the two implementations
*against each other*, not against a list of today's surfaces — so it stays true when a new surface is
declared and reds the moment the prefilter narrows.

The mutation it is written for is the tempting wrong version: prefilter on `node.lineno` alone
instead of the node's whole span. Applied in a clean extract, it reds with the multi-line
declaration named:

```
prefiltered: {'docs/status/PLAIN.md': ...}
unfiltered:  {'docs/status/PLAIN.md': ..., 'docs/status/SPREAD.md': ...}
```

**The real-tree leg PASSED under that mutation** — today's tree happens to contain no multi-line
`"docs"` declaration. That is precisely why the synthetic leg exists, and it is worth saying plainly:
a real-tree-only control here would have been green on a defect.

## What I did NOT cut, with its measurement

A sixth sharper cause with no repair is a failure, so these are stated as owed work, not as
observations:

1. **The site lane gate, 142.9s.** Its own docstring justifies running the WHOLE suite on any
   `site/data/**` change with *"`pytest site/` is fast (~6s, ~164 tests): no cost reason"*. Measured
   today: **854 tests, 171s** — the count is 5x stale and the time 28x. The claim that licensed the
   broad trigger is no longer true, and the publisher stages `site/data/*` every single cycle, so
   the publisher pays this every cycle. Inside it, two module-scoped fixtures cost 51s of the 171s.
   **Narrowing the trigger is the wrong first move** — it would hide the class the broad trigger
   exists for. Making the suite cheaper is the right one.
2. **The always-run control set, 185.4s across 38 files.** It was ~12 entries and is now 38; the
   09-10 commits that grew it are `bea5c02f2`, `fcbf92b9b`, `a613d5dce`. Two files are 46% of it:
   `test_a_control_reads_python_as_code.py` (45.6s) and `test_publish_scope.py` (39.4s). Both are
   whole-tree AST censuses, and there are several more in the list — each re-parsing the same tree
   from scratch. A shared parse is the structural repair and it is bigger than one turn.
3. **`pytest-xdist` is not installed on this box.** 16 cores sit idle through a 185s serial run.
   Installing it is a real-world action and I did not take it; it is the single largest available
   lever and it belongs to the director, not to me.

## Incidental, found while measuring — not this item's subject

Run standalone against the shared tree, three of the always-run 38 returned rc1:
`test_a_control_reads_python_as_code.py`, `test_static_quality_ratchet.py`,
`test_the_one_launcher_is_the_only_launcher.py`. A red in the shared worktree measures several
lanes at once, so this is a pointer to check, not a finding.

## The claim was swept WHILE I WAS LANDING IT, and the item's own subject is why

`--landed` refused with *"it is NOT CLAIMED"*, twice, after a successful land and after the push.
This is a live instance of
`SEAT_FINDING_THE_CLAIM_WINDOW_IS_SPENT_BY_THE_LAND_PROMOTE_RACE_SO_A_TURN_THAT_LANDS_CORRECTLY_READS_AS_UNCLAIMED_2026-09-15.md`,
and the cause is the thing this item exists to fix:

- Five gate cycles were spent reaching a green tree (census row, orphan ratchet, then the
  orphan ratchet again because it cannot see an untracked file). At ~4 minutes a gated cycle,
  that alone is ~20 minutes.
- Attempt 5 **lost the race to the publisher mid-gate** and re-gated on a new base — the exact
  failure the item describes: *"a landing that takes eleven minutes to gate cannot win a race
  against lanes that land more often than that."*
- Then `origin/main` had moved 12 commits, needing a gated `--merge` and a push.

The 100-minute window expired inside that sequence. **A turn that lands correctly, merges correctly
and pushes correctly still reads as `LANDED NOTHING`.** The sweep is not wrong about the clock; the
clock is being spent by the chain. That is a second, independent argument for cutting the chain,
and it is the one that costs whole invocations rather than seconds.

## Two gate frictions worth recording, both hit on the way

1. **The orphan ratchet cannot see an untracked file, so `--freeze` is a no-op before `git add`.**
   Running `orphan_ratchet.py` and `--freeze` on a working tree holding a new module reports the
   tree CLEAN and freezes nothing, while the commit gate — whose subject is the tree the commit
   would create — refuses it. The freeze only records the decision after the file is staged. That
   cost one full gate cycle, and the refusal message's instruction ("add it with `--freeze` in the
   SAME commit") is true but omits the staging step it depends on.
2. **`surgical_land -m` with backticks is shell-expanded and dies silently**, producing a zero-byte
   log and no process. Passing argv from Python instead of a shell is the reliable form.

## Done-condition

The item's DONE is "a worst recent chain that has come DOWN, evidenced by new rows in the same
series". This commit's own chain is the first such row. **One cut of ~40s does not by itself return
a 667s chain to the 134s regime**, and claiming otherwise would be the sixth sharp cause. What has
changed that could not change before: the chain is now attributable, so the next turn starts from a
table instead of from a guess.

The item's second done-condition — *"one non-null `last_clean_publish` the gate stamped on its own
grading"* — is **NOT met and I am not claiming it**. It depends on a clean publish cycle, and the
publisher raced me twice during this turn.

**THIS DOCUMENT IS NOT YET COMMITTED.** `background.finding_classes --check` fails on two TWO ROOMS
documents belonging to another lane —
`PREREG_THE_PUBLISH_WEDGE_IS_ONE_FILE_2026-09-17.md` and
`SEAT_PREREG_DOES_THE_FAMILYS_DISCRIMINATION_READING_REACH_THE_PAGE_BESIDE_THE_ADVANTAGE_2026-09-17.md`
— each present in both `docs/staging/` and `docs/staging/records/`. The root copies were written
ten minutes before I looked, so that is a live repair in flight and not mine to resolve; the test
gate's staging branch refuses any commit staging a `docs/staging/` path while it holds. The code
landed without this document because the code commit stages no staging path. Whoever picks this up:
the refusal is deterministic, so re-check that gate before spending a cycle on it.
