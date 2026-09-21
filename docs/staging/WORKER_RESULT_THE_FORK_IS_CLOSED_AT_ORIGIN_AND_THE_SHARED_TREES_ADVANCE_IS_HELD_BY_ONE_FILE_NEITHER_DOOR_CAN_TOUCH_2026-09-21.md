**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `close-the-fork-that-has-refused-eleven-publishes`

# The fork is closed at origin and the shared tree's advance is held by one file neither door can touch

*Eleven consecutive `commit_did_not_land` refusals with cause `behind_origin`, 36.4 hours with
nothing published, and both doors refusing the fork. The cause is found, fixed and landed
(`995fd0d85`), and the merge that had refused for a day and a half gated clean and pushed on the
first attempt after it (`6a9f49cf9`). Origin now carries this machine's work and `origin/main...HEAD`
reads **8 behind / 0 ahead** — the fork at origin is closed. The SHARED TREE has not advanced, and
that is a different refusal with a different owner: two uncommitted paths that `advance_shared_tree`
cannot prove lossless, one of them 1h45m old when this was written.*

---

## 1. The cause, measured rather than argued

`WORKER_FINDING_THE_STALE_COPY_GUARD_REFUSES_A_MERGE_..._2026-09-20.md` §4 left open *which check
returned rc=1*, because `origin_reconcile._classify_merge_failure` keeps 400 characters after
`GATE RED` and those 400 characters were a different gate's verdict. Re-run with both streams kept:

1. `_land_once` judges the merged tree **with** the merge ref and PASSES it — its own stdout reads
   `[stale-copy] 46 path(s) adopted from origin/main (0bdee00b7)`. It pins the already-gated token
   to `91a49e0e3`.
2. The **first block of `tools/git-hooks/pre-commit`** re-stamps `docs/status/LATEST.md` and
   `git add`s it. That path is one of the 47 this merge carries, so the index the hook writes out is
   `eb8cb2718` — not the tree the token names.
3. The sha comparison in `stale_copy_refusal.staged()` therefore fails and the **whole tree** is
   re-asked, with no merge ref and no `--drops`, reading origin's own landed deletions
   (`count_run_history_total`, `DOCS_SHADOW`, `SITE_SHADOW`) as this lane reverting them. That is
   why the refusal's wording was `COMMIT REFUSED` and not `MERGE REFUSED`.
4. Its printed remedy is `refresh_to_head`, which refreshes to the HEAD that is itself behind.

Attributed on ONE tree state, both directions run: on the same extract the whole-tree re-ask returns
those two paths and the delta re-ask returns none.

**Repair:** re-ask the DELTA — the paths that differ between the tree the token names and the tree
the index now writes out — not the whole tree. `995fd0d85`, with a control that runs both legs of
the partition on one tree state so a guard that refused everything or passed everything fails one.

**The prior finding's diagnosis is refuted and corrected in place** (§6 there): `strict_symbol_subset`
and `adopted_from_merge` are both correct, and `violations(merge_ref=origin/main)` returns an empty
list on the live fork.

## 2. What is now true, re-read after the fact rather than inferred from the steps

| | before | after |
|---|---|---|
| `surgical_land --merge origin/main` | `GATE RED rc=1`, 2 false stale-copy losses | `landed MERGE 6a9f49cf9`, rc=0 |
| `origin_reconcile` | `REFUSED_GATE` | merge gated clean **and pushed** |
| `origin/main...HEAD` | 7 behind / 9 ahead | **8 behind / 0 ahead** |
| shared tree advanced | no | **no — see §3** |
| `episode_clean_publishes` | 0 | **still 0 — see §3** |

## 3. WHAT IS NOT DONE, and why it is not this claim's to force

`advance_shared_tree` refuses the fast-forward on 9 paths. Seven it can prove lossless. Two it
cannot, and they are the whole blocker:

* `background/process_run_complete.py` — *"this copy supplies 1 name(s) origin/main lacks, and EVERY
  hunk carrying one also deletes a name origin/main has"*. So `isolate_hunks --keep` has no selection
  that takes the work without the revert, `--content` would land the revert, and `surgical_land`
  would rightly refuse it. Its mtime was **07:52 today**, 1h45m before this was written — old enough
  to be stranded, recent enough that it may be a live lane's mid-repair, and nothing here can tell
  which. `refresh_to_head --write --slug` would clear it recoverably; **that is a judgement for the
  lane holding it, not for a reconciliation, and it is deliberately left undone.**
* `docs/design/self_clearing_alarm_dispositions.json` — *"this control has no reader for .json files,
  so it CANNOT establish that the copy has nothing to lose. An unavailable check is a failed check."*
  A 9-line diff, 5 days old.

The publish gate reads the SHARED tree, so `episode_clean_publishes` cannot leave zero until those
two clear. **The claim's stated `done` is therefore partly unmet and is recorded as unmet.** What
changed is that the reason is no longer a control refusing on a false reading of its own: it is two
named files with a named owner, and the loop that manufactured its own `behind_origin` is broken.

## 4. A SECOND, SEPARATE WEDGE found on the way, and cleared

`docs/observability/.publish_gate_state.json` also recorded the liveness heartbeat refused by the
SITE LANE — `3 failed, 875 passed` — which refuses **any** shared-tree commit touching `site/**`,
`site/data/**` or a `generate_*_data` producer, and the publisher's commit is exactly that.

All three reds had one cause, and it was not in the site code: seat-authored prose in the direction
record reaching a payload field the harness door renders in **two** regions
(`/harness/#delivery-decided` and `/harness/#delivery-next`). Three here-relative phrases —
`item below` in `DIRECTION.yaml`'s focus `why`, and `THE ROW ABOVE` / `at the top of the list`
across 14 occurrences in `decisions.jsonl` — each claiming a direction from wherever they render.
Repaired by naming the landmark; the three tests are green.

**Both source files are another writer's uncommitted work, so the repair is a WORKING-COPY repair
and is deliberately not committed here.** It unwedges the site lane for the next lane to commit; it
does not survive a regeneration from unrepaired sources.

**This will recur.** `what_it_decided.focus[].why` and `what_next().focus[].why` are the same rows,
so every focus `why` the seat writes has two homes by construction, and a seat writing "the item
below" wedges the site lane for every lane in the tree. The control is doing its job and catching it
at the door; the durable fix is one home for that field, and it is not filed as done here.

## 5. What this cost

Two gate cycles: one shared-tree pathspec commit refused by seven reds no part of the diff could
reach (other lanes' dirt — `pytest-of-rich` fingerprints in three live ledgers, a stale ruff
baseline), then the same change landed through `surgical_land`, which gates HEAD-plus-the-paths and
is the right door on a tree three lanes hold work in.
