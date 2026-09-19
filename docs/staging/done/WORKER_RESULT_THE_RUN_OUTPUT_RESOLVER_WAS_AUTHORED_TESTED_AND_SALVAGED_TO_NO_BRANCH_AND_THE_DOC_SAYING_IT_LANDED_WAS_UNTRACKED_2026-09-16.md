**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the-arms-producer-picks-its-run-output-from-an-untracked-glob"

# The run-output resolver was authored, tested and salvaged to no branch, and the document saying it landed was untracked

Worker seat, scheduled tick, 2026-09-16, against `770497ddd`. Lands the Lane 0 item
"the-arms-producer-picks-its-run-output-from-an-untracked-glob" for real.

---

## Premise check, and it was spent in a way the draw could not see

The draw reported both cited commits — `79f7484f3`, `2bc442bab` — already ancestors of
`origin/main`, and asked whether the work had landed by another route. The honest answer turned
out to be **neither yes nor no**.

`resolve_run_output` — the exact repair this item asks for — had already been written, tested and
measured by the previous scheduled tick. It was in no branch. The route it took:

| where the work was | what a reader of the tree saw |
|---|---|
| `tools/couple_value_based_pricing.py` at `5af1e3e86` | nothing: `5af1e3e86` is an auto-salvage on **no branch**, ancestor of no ref |
| the result document asserting **"## What landed"** | nothing: **untracked** in `docs/staging/` |
| `origin/main`, `HEAD`, every local branch | `latest_run_output()` — the untracked lexical-max glob, unchanged |

`background/fork_salvage.py` runs from `worker-tick.service`'s `ExecStopPost`, i.e. *after* the
bounded invocation is killed at `TimeoutStartSec`. It did its job: the bytes survived. But its own
commit message says it lands "on the fork's OWN branch only -- NOT merged to main", and the merge
decision it defers had no owner. So the state left behind was a completed repair that **read from
the queue exactly like an abandoned one**, and a result document making a landing claim that
nothing could grade — the document cites no sha in its header block, so
`landed_manifest_check` has no claim surface to refuse.

**This is the class, and it is not about this file.** A bounded tick that finishes its work and is
killed on the way out leaves (a) an untracked "it landed" document and (b) bytes on an unreferenced
commit. Both halves are invisible to the queue, and the pair is indistinguishable from a tick that
achieved nothing — except that re-doing the work throws away a tested repair. The draw's premise
check asks *"are the cited commits ancestors?"*; the question that would have caught this is
**"does the named mechanism exist at HEAD?"** — here `git log --all -S resolve_run_output`, which
answers in one second and names the salvage.

## What I verified before trusting a word of it

The prior document's evidence is a claim about a tree, so it was re-measured, not read.

**The base is not a revert.** `ad3a9acb9` (the salvage's parent) holds copies of both files that
are **byte-identical** to `origin/main`'s. Landing the salvage bytes therefore reverts nothing on
main — it is a pure forward move. The five new tests are **purely additive**: the fifty-two
existing test names are unchanged and none is removed.

**The mechanism works in a real second checkout.** A clean `git archive` extract of `origin/main`
with the salvage bytes overlaid:

```
resolved: run_output_latest.json | resolved_by=tracked_run_output
                                   reproducible_across_checkouts=True
untracked dated candidates in this checkout: 4
```

Four untracked candidates — the same shape of checkout whose lexical max is the June run holding
14 accounts. The default now reaches the tracked file instead, and
`docs/reports/run_output_latest.json` is present in the extract because git put it there, which is
the whole property the glob could not be given.

**57 tests green** in that extract.

## Evidence the new controls can fail — re-run here, not quoted

Four mutations of the resolver, each applied to the extract and the suite re-run:

| mutation | result |
|---|---|
| default tier globs instead of taking the tracked run | **5 failed**, incl. `…the_DEFAULT_run_output_is_the_TRACKED_one_and_the_GLOB_is_OPT_IN` |
| a missing tracked run falls back to the glob instead of refusing | **1 failed**: `…a_checkout_WITHOUT_the_tracked_run_REFUSES_rather_than_picking_one_of_the_glob` |
| a caller-named path that does not exist falls through to the tracked run | **1 failed**: `…a_run_output_NAMED_by_the_caller_wins_and_a_MISSING_one_never_falls_back` |
| `reproducible_across_checkouts` hardcoded `True` | **3 failed**, incl. `…the_artefact_says_whether_a_SECOND_CHECKOUT_would_read_the_SAME_file` |

The prior document claimed each mutation fired "exactly the intended test and nothing else". The
first fires five. That is an overclaim about blast radius, not about the property — every mutation
is caught, which is what a control owes. Corrected in that document beside its own table.

## What landed

`tools/couple_value_based_pricing.py` and `tests/tools/test_couple_value_based_pricing.py`, the
salvage bytes, landed by `tools.surgical_land --content` onto a tree merged up to `origin/main`
first. `--content` is the route because the working-tree copies of both files are the stale
week-old copies recorded in the prior document, and one of them holds a *different* lane's
unlanded `bill_scale_for` repair — a pathspec commit would have carried that in and reverted
`79f7484f3`'s stamping at the same time.

The prior tick's result document is landed **with a correction block at its head** rather than
deleted or silently rewritten. Its measurements were right; only its tense was wrong.

## What is owed next, and is NOT fixed here

1. **The stale working copies are still on disk**, and still tangled — unchanged from the prior
   document's item 1. `tools/couple_value_based_pricing.py` (mtime 2026-09-09) holds the authored
   `bill_scale_for` / `annual_bill_gbp` repair, absent from main, tangled with a revert of
   `79f7484f3`'s stamping. `tools/isolate_hunks.py` is the route and it is a separate item.
2. **`docs/reports/run_output_latest.json` carries no `_cache_meta.git_commit`**, so in a fresh
   checkout `producing_commit` on the run side reads `None`. The reproducible tier is currently
   *less* self-describing than the glob tier it replaces. The fix belongs in whatever reduces a run
   into that file.
3. **Nothing asks whether a salvage commit holds work main lacks.** The salvage tool defers a merge
   decision to an owner that does not exist. A one-leg check — *are there auto-salvage commits
   reachable from no branch whose tracked-file bytes differ from main?* — would have surfaced this
   repair the moment it was orphaned, and would have saved this invocation. That is the smallest
   mechanism that can fail here, and it is handed on rather than built inside this item's scope.
4. The site feed still does not surface this provenance to a reader of the page; the artefact
   carries it and `generate_value_arms_data` passes through unchanged.
