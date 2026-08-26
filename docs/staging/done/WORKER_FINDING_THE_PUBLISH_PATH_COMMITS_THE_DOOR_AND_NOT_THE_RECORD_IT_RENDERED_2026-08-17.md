# FINDING — the publish path commits the door and not the record it rendered, so the public figure has never existed in the repo

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `D35_the_render_site_sweep_stops_at_this_processs_edge` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-17)
**Class:** an R10 class-closure was applied to the derived side of a seam and re-opens one hop
upstream, because the generator reads the WORKING TREE and the commit pathspec lists only what
the generator wrote

Full derivation and every number: `docs/design/simplifications/D35_the_render_site_sweep_stops_at_this_processs_edge.yaml`
(2026-08-17 entry, Findings 2 and 3).

## The observation

At `HEAD` and at `origin/main`, the Proof door and the ledger of record disagree about this
project's own payment-triad headline, and the door's number has never been committed:

    docs/observability/coupled_gap_ledger.json  W2_11  gap   0.0859375
                                                      measured_at 2026-08-12T06:10:09+00:00
    site/data/proof.json  /coupled_gaps/pairs[5]       value 0.0833907649896623
                                                      measured_at 2026-08-17T15:11:25+00:00

    $ git log -S'0.0833907649896623' -- docs/observability/coupled_gap_ledger.json
    (no output)

The door is five days AHEAD of the record, not behind it. The working tree holds a third value
again (`0.0311284046692607`, measured_at 15:38 today, uncommitted) — three live values for one
figure on one machine. Commit-granularity lower bound on the current run: **93.4h and still
open**, `observed-with-evidence`, 2026-08-17.

## The mechanism (read off HEAD, not inferred)

`tools/generate_proof_data._coupled_gaps` renders `entry.get("gap")` from
`background.coupled_triad.load_gap_ledger()`, and `GAP_LEDGER_PATH` is the **working-tree**
file. `background/process_run_complete.py` then commits the result under a pathspec that closed
the orphaned-at-commit gap for the whole derived surface — its own comment says so:

> "the durable fix is to commit the WHOLE generated data surface, not to add another explicit
> path line each time a door is built. Any future `site/data/*.json` is now tracked automatically."

`docs/observability/coupled_gap_ledger.json` is not in that pathspec. So the publish commit
carries the rendering and not the source it was rendered from, and the door legitimately
publishes a measurement the repo cannot reproduce. This is the CLAUDE.md IaC test —
reconstruct-from-repo-alone — failing on a published figure.

## Why it is that module's subject and not this atom's

The repair is in `background/process_run_complete.py`'s pathspec and/or the generator's source
selection, neither of which is in D35's `file_scope`
(`tools/couple_w2_11_d5.py`, `tests/tools/test_couple_w2_11_d5.py`). QUEUED under
SELF-INTERRUPT DISCIPLINE.

## What the repair is not

Adding the ledger to the publish pathspec is the cheapest fix (it would have removed 36 of the
43 diverging pair-commits measured over the last 78 commits) but it is **not** a fix on sight:
the ledger is a file other lanes also write, so listing it re-enters the known
"a pathspec commit still carries another lane's staged hunks" class. It needs the same
deliberate design a shared-file pathspec always needs here.
