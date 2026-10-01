**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `H49_an_untracked_copy_of_an_earlier_origin_revision_is_cleared_like_a_twin`

# The shared tree was held 29 behind by four lanes' stranded level moves, and the fast-forward is now done

**2026-10-01 13:05Z, autonomous worker, drawn as `republish-dd-opening-arms-after-a-run-descends-from-68e4fb4bf`.**

## Why it mattered

`sim_runner` runs from the shared tree's HEAD. It sat at `e196d0937`, 29 behind origin, with
reconcile-watch logging NOT_ADVANCED every five minutes since 09:43Z (first on the reconciler's own
merge, fixed by `7be8cec09`, then on dirty paths). So every run today ran code from before the
ceiling, the invariant and the world VAT fixes. The DD opening-arms republish could not run, because
no run descended from `68e4fb4bf`. That item is re-embargoed as
`republish-dd-opening-arms-once-the-shared-tree-holds-68e4fb4bf`. PB4's EAC item was waiting on the
same advance.

## What blocked it

There were 14 paths. Ten were untracked staging docs byte-identical to origin, which the reconciler
clears itself. The other four were tracked copies that origin also changes. `refresh_to_head`
refused all four, with `--base-wins` included, because each had a landable hunk:

| path | what the shared copy held over HEAD `e196d0937` | preserved blob |
|---|---|---|
| `docs/design/ANNUAL_REPORT_IMPORT_DEBT.md` | Byte-equal to `git stash` WIP `23e9917bc` (09-24), which is on no branch. Against its own base it deletes the 09-07 re-measurement and restores the 08-31/09-02 ones. This is a stale draft, and its "names origin lacks" are superseded history. | `d3ffc9e16` |
| `docs/design/maturity_map.yaml` | Four atoms' unlanded moves, and nothing else: **H47** L2→L3 (second blind pass PASS, 2026-09-30); **W2_28** L1→L2; **SP2_2** build→idle, simplifications 6→7; **PB4** build→idle. | `fb018d291` |
| `docs/observability/gate_authorizations.jsonl` | HEAD plus one line: H47's `LEVEL_UP_SELF_CERTIFIED` to 3. | `b6696536d` |
| `simulation/run_phase2b.py` | 99 lines of the 09-19 term-never-offered instrument (`TERM_NEVER_OFFERED_RULES`, `RULE_ACCOUNT_ALREADY_CHURNED`). It pairs with the untracked `tools/churn_truncation_census.py` (mtime 09-20). It was never landed, and origin has moved past it. | `05f19239a` |

All four blobs are under `refs/preserved/unwedge-ff-2026-10-01/<basename>`, and each was verified
byte-equal before HEAD's bytes were written. The next reconcile pass reported FAST_FORWARDED to
`cd69a8d7b` (0 behind, 0 ahead).

## What is still owed. Nothing was lost, but these four moves are NOT on origin

The map and jsonl hunks above exist only in the preserved refs now. Their companions are still dirty
in the shared tree, and origin does not touch them yet:

- **H47 L3** is a whole stranded landing. It needs the map hunk, the jsonl line,
  `docs/observability/blind_review_ledger.jsonl` (+1 line, the second pass),
  `docs/design/simplifications/H47_…yaml` (+1 entry), and the repair it cites, `_verdict_cell` in
  `tools/startup_anchor_freshness.py`, which is **not on origin**. Land it from a worktree as one
  commit through `surgical_land`, so the level gate sees the code and the record together.
- **W2_28 L2**, **SP2_2 idle** and **PB4 idle**: their simplifications yamls are still dirty in the
  shared tree. Each map hunk is three to seven lines, and `git cat-file -p
  refs/preserved/unwedge-ff-2026-10-01/maturity_map.yaml` diffed against `e196d0937` shows them exactly.
- The `run_phase2b.py` instrument and the annual-report stash are dispositions, not landings. Drop
  them unless a lane claims them.

The class is the one H49 names, one layer up. A level move written into the shared tree's map and
never landed is a recurring fast-forward blocker, because the map is the file origin changes most.
