**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: closing the collection gap the forty-two tests fell through

**Written 2026-09-05, delivery seat, isolated worktree at `f4df63cd9`, BEFORE the move is made or
any suite is run from its new home. Claim id `register-low-water-evidence-convergence-sweep`.**

The predecessor commit `f4df63cd9` filed
`SEAT_FINDING_FORTY_TWO_TESTS_LIVE_WHERE_NO_RUNNER_LOOKS...` at severity **BLOCKING** and
deliberately did not repair it, naming three routes for the drifted feed and one uncontested
instruction: *"The collection gap should be closed regardless of which is chosen."* This turn
closes it. The predictions below are recorded before the answers are known.

## What is being done

1. `git mv` the four real suites `tools/test_generate_{company,regulatory,decisions,market}_data.py`
   → `tests/tools/`, correcting `PROJECT = parent.parent` → `parent.parent.parent` in the three
   that are location-dependent.
2. Wire `tools/generate_regulatory_data.py` into `background/process_run_complete.py`'s regen
   cycle beside its already-wired siblings, and its artefact into the publish commit list — the
   finding's route 2, chosen for the reason stated below.
3. Regenerate `site/data/regulatory.json`.
4. Add a control that makes this species unable to recur silently.

## Why route 2, and not the other two

The finding called route 2 "the real repair for a dead feed, and a larger change than this
finding's subject". Opening the call site says otherwise: `process_run_complete` already wires
`generate_proof_data`, `generate_company_data`, `generate_activity_cost_data`,
`generate_book_growth_data` and `generate_value_arms_data` in one contiguous block, each with the
same stated reason — **R11 no-orphan-transition: "a generated surface must ride the regen cycle or
it silently freezes against its live sources."** `generate_regulatory_data` is the one sibling
that was never added. The change is four lines in an established local pattern whose reason is
already written down five times in the same function.

Route 1 (regenerate only) is explicitly the one that "buys a green test rather than a working
mechanism" — it would re-stale the day a regulatory module lands. Route 3 (delete) belongs to
whoever owns Door 3, as the finding says, and is not this sweep's to take.

## Predictions, recorded before measuring

* **P1** — the four suites collect and pass from `tests/tools/` after the `parent.parent`
  correction alone. Expected **41 pass, 1 fail**, the failure being
  `test_live_cache_matches_regeneration` and nothing else. *If any OTHER test reds on the move,
  the move surfaced a second location dependency the finding did not name, and that is the
  result, not a nuisance.*
* **P2** — regenerating `site/data/regulatory.json` clears that one failure and nothing else
  changes. The drift is `module_count: cache=63 fresh=67`; I predict the regenerated file differs
  in `module_count`, in whatever RAG/obligation figures it reads from `company.json`, and in its
  freshness stamp — and that **no per-scheme badge flips**, because no scheme calc module moved in
  or out of the report layer in seven weeks.
* **P3** — the new architecture control, run against the tree as it stands BEFORE the move, is
  **red** and names exactly the four suites. `tools/test_execution_metric.py` is NOT named: it
  matches pytest's filename pattern but defines no test function, and the control is keyed to
  "defines a test" rather than "is named like one". The three `company/risk/*_test.py` production
  modules are likewise not named.
* **P4** — no other `site/data/*.json` feed is disturbed. The only generator being newly called is
  the regulatory one.

**The prediction I am least sure of is P2.** `regulatory.json` reads `obligation_count`,
`overall_rag` and `status_counts` out of `site/data/company.json`, which is itself a generated
artefact that has moved in seven weeks. If those blocks have changed shape rather than value, the
regeneration could fail or emit a differently-keyed payload, and the moved test would red for a
reason that has nothing to do with `module_count`. That would make this a chain, not a pair, in
exactly the sense `tests/tools/test_a_published_surface_is_reproducible_from_its_committed_input.py`
already flags as "wants its own thinking" — and I would file it rather than force it green.

## What this will NOT establish

Moving a suite into a collected directory proves a runner now looks at it. It proves **nothing
about whether those 42 tests are good controls** — none has been mutation-tested, and 41 of them
have a pass record exactly one run long. Whether any of them can fail is a separate question and
is not answered here.

Nor does closing the collection gap answer the drawn sweep question. `generate_company_data`'s
contracts (`segment_revenue_mix`, reached from two generators; `generate`, from the publisher)
still stand on whatever those 16 tests happen to cover, and that has not been examined.
