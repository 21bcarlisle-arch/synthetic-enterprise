**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: one suite proves two of `fuel_mix`'s ten contracts, and nothing proves the other eight

> **CORRECTION, 2026-09-06.** The title's *"one suite"* is exact and stays. What needs saying is
> **which** suite: `test_grid_intensity_feed_and_explore_carbon.py` is a DIRECT importer of the
> subject, not a caller — and this spec wrote `SUITES = DIRECT_SUITES + CALLER_SUITES`, so it sat
> inside the verdict meant to answer *"did any CALLER prove this"*. **On the callers alone the
> answer is ten of ten surviving, not eight**, and no row carries a machine verdict at all because
> `test_ep13_embedded_generation_bound.py` — a member of `CALLER_SUITES` — was never graded. The
> ten rows below are unchanged and correct. The prose already drew the distinction (it says "one
> *suite*", never "one caller", and names the direct pair at the bottom); the machine field did
> not.
>
> **The sweep table at the foot of this page has one wrong row.** `segment_vocabulary | 8 suites |
> refutes it — no unproved contract` is true of that subject's ten-suite population and false of
> its callers, where three of eight are unproved. Both subjects moved the same way — less caller
> evidence than published, never more — and this page's closing conclusion survives it.
> Re-reduced from the same cells, no test re-run:
> `SEAT_RESULT_THREE_OF_SEGMENT_VOCABULARYS_CONTRACTS_ARE_PROVED_ONLY_BY_ITS_OWN_SUITE_AND_SO_WERE_BOTH_OF_FUEL_MIXS_2026-09-06.md`.

**Measured 2026-09-06 01:35–02:05 BST, delivery seat, worktree `/var/tmp/se-gif-battery` at
`6c92cc0c7` with `sim/cache` linked from the shared tree. Claim id
`convergence-sweep-subject-4-grid-intensity-feed`. Results:
`/var/tmp/gif_fuel_mix_battery_CACHED.json`. Spec:
`tools/grid_intensity_feed_contract_battery.py`. Engine: `tools/contract_battery.py`.**

**Subject: `tools/generate_grid_intensity_feed.fuel_mix` — the sweep's fourth, and the only name
of its five-name converged surface this module defines. The other four are re-exports; the
pre-registration at `da7336230` establishes that and it is why they are not graded here.**

---

## The answer

| | |
|---|---|
| contracts mutated | **10** |
| caller suites graded | **9** of 10 |
| contracts killed by any suite | **2** (M1, M2) |
| suites that ever killed anything | **1** — `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` |
| suites that never reach the subject | **6** of 8 `ep13_*` callers |
| suites that reach it and prove nothing | **2** |
| suites grading TEXT rather than behaviour | **0** |

```
M1  an unusable BIOMASS cache RAISES                        KILLED  by explore_carbon only
M2  an unusable FUEL OUTTURN cache RAISES                    KILLED  by explore_carbon only
M3  the outturn is normalised to SETTLEMENT PERIODS          nothing
M4  the returned tuple's ORDER is the contract               nothing
M5  the THERMAL FLOOR reaches the published feed             nothing
M6  the ZERO-CARBON MUST-RUN block reaches the feed          nothing
M7  must-run coverage is its OWN measurement                 nothing
M8  the BIOMASS ENVELOPE is returned                         nothing
M9  the floor comes from the THERMAL cache                   nothing
M10 biomass rows are period-ised before the yearly envelope  nothing
```

## The two pre-registered predictions, and one of them is wrong

**Prediction 1 — CONFIRMED, and understated.** *"`fuel_mix` is proved by
`test_grid_intensity_feed_and_explore_carbon.py` and by nothing else in the ten-suite
population."* It is the only killer. But it proves **two of ten** contracts, not `fuel_mix`: the
two written as `with pytest.raises(FuelOutturnUnavailable)`, which are the two the suite's own
docstrings name as `MUTATION (must fire)`. Every contract nobody wrote a test *for* is unproved,
which is the ordinary reading — the finding is that **eight of them are contracts the module's
docstring argues for at length and no suite in the tree can distinguish.**

**Prediction 2 — REFUTED.** *"At least one `ep13_*` suite reddens under the NULL round — i.e. at
least one of the six textual readers is grading bytes and has been counted as evidence."* All
nine graded suites came back **behaviour only**, under a null marker built to be maximally
provoking for exactly this hazard: a no-op module-level assignment *and* a comment naming
`ep13_input_ceiling` and `ep13_biomass_oracle_bound`.

The prediction was reasonable and the reason it failed is worth keeping. Those six callers
`read_text()` the subject and walk it as an AST, and their docstrings say the walk is deliberate —
*"a substring search would be satisfied by this module's name in a comment and defeated by an
import written any way but the one it looked for."* **The null round put exactly that comment in
front of them and they were indifferent to it. The claim in those docstrings is now measured
rather than asserted.**

That the hazard did not fire does not make the round waste: without it, the two kills above are
"a suite went red", and with it they are "a suite executed the mutated line". The engine's null
round exists because of this subject and this subject is the one that clears it.

## The six that never reach it, and the two that reach it and prove nothing

The import-time floor split the eight `ep13_*`-family callers cleanly:

* **Never reach the subject (6):** `biomass_oracle_bound`, `ccgt_level_ceiling`,
  `ccgt_swap_ceiling`, `input_ceiling`, `peer_bound`, `per_fuel_oracle_bound`. Every one imports
  `fuel_mix` inside a function body their suite never calls. Their sixty green cells above were
  never at risk. This is the pre-registration's hazard 3 confirmed and larger than predicted: the
  lazy import makes the floor grade *"does this suite execute the calling path"*, and for
  three-quarters of the ep13 family the answer is no.
* **Reach it and prove nothing (2):** `tests/background/test_process_run_complete.py` and
  `tests/sim/test_elexon_fuel_outturn.py`. Both redden under the poison, both killed zero of ten.
  `test_elexon_fuel_outturn.py` is one of the **two suites the drawn direction named as the direct
  importers** — the prime candidates for holding this contract. It imports the feed at line 343
  for one unrelated test and proves nothing about `fuel_mix` at all.

Both control suites stayed green under the poison, so the floor discriminated and the
reachability column is sound.

## What is NOT graded, said plainly

`tests/tools/test_ep13_embedded_generation_bound.py` — the tenth suite — **was excluded and has no
cell in any row above.** It costs **655.1 seconds** per run against a whole-population total of
~90s for the other nine. At eleven rounds that is one suite for two hours, and it is the measured
reason both of this claim's first two battery attempts died after their baseline without scoring
a single mutation. Excluding it is a stated bound on the answer, not a silent cap: **a contract
killed by none of the nine is unproved by the suites a reader would look in, which is not the
same claim as unproved anywhere in the tree.** That suite is the one place the remaining doubt
lives and grading it is a separate, budgeted run.

## Where this leaves the sweep

Five subjects now have rows, and the shape the sweep was drawn to test is holding with one
refutation:

| subject | killers | shape |
|---|---|---|
| `register_low_water` | 1 suite | proved by one caller |
| `run_phase3b_recalibration` | 1 suite | proved by one caller |
| `ops_repo` | 0 | reaches, patches by name, proves nothing |
| `segment_vocabulary` | 8 suites | **refutes it** — no unproved contract |
| **`fuel_mix`** | **1 suite, 2 of 10 contracts** | **proved by one caller, and mostly not at all** |

The one that refutes it is the one whose module exists to be a vocabulary — a module whose whole
surface is what every caller asserts about. `fuel_mix` is the opposite: a composition whose
contract is an *order* and a *set of loaders*, and nothing in the tree asserts either. **A
converged module's evidence tracks what its callers have reason to say about it, not how many
callers it has** — and caller count, which is what the screen ranks on, is uncorrelated with it
across all five.

## What would close the eight

Not eight tests. One control over the whole return, keyed to the property rather than today's
values: `fuel_mix()` returns seven members in a fixed order, each from its own named loader, and
each non-empty when the caches are present. That is one test that M3–M10 all fire against, and it
is the shape CLAUDE.md's own rule about rare branches asks for — one control over the partition,
not a leg per branch. It is not written here: the sweep grades, and a repair scored inside the
run it repairs is the thing `repair_suite` exists to keep out of `survived_all`.
