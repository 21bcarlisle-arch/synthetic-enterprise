# WORKER FINDING — the 252-cycle wedge was FIVE instances of one class, and `pytest -x` served them one per tick

**Severity:** BLOCKING · **Lane:** H_harness
**class:** uncommitted-and-orphaned-work
**found:** 2026-08-14, unwedging the publish gate (252 consecutive failures, ~7,163 min)
**status:** INSTANCES LANDED (see the commit list below — each verified in a tree, not in a status
line). **CONTROL 2 BUILT 2026-08-14, and LANDED 2026-08-14 in `f5d855558`** (tree `cdf6c7f70`,
receipt gate-rc 0) — the recommendation of this document, mechanised: the gate now runs a
report-only census behind its own fail-fast verdict, and the doorbell states the DEPTH.
Controls 1 and 3 stay owed and are located below, so the discharge releases what was built and
nothing else.

**CORRECTION 2026-08-14, recorded rather than smoothed over: "BUILT" was true and "in a tree" was
not.** For most of a day this document carried the Discharged field below while
`background/process_run_complete.py`, `background/supervisor.py` and the whole 286-line test file
sat STAGED IN THE INDEX and on no ref — `git ls-tree HEAD` was empty for the test and
`run_red_census` was absent from the gate at HEAD. The discharge nevertheless parsed
`released=True`, because `finding_severity.parse_discharge` validates cited artefacts against the
DESK, so a re-render would have read this class down to LATENT on a control no second reader could
run. That is this document's own subject — a record outrunning the code — appearing in this
document's own release field, and it is the fifth instance of the mechanism in three days. The work
was ADOPTED and landed unchanged (it was read and is correct), not rebuilt. **R2: committed is not
running** — the census is live for the next gate invocation, not for the process that was mid-run
when it landed.
**Discharged:** `tests/background/test_publish_gate_red_census.py::test_the_census_names_both_reds_behind_one_fail_fast_verdict`, `tests/background/test_publish_gate_red_census.py::test_mutation_the_fail_fast_only_payload_fails_the_names_both_assertion`, `background/process_run_complete.py`, `background/supervisor.py` — control 2 is live and mutation-proven both ways; the residue is named in "What is still owed" below.

## What was observed (observed-with-evidence)

The publish gate had been RED at every HEAD since `19d8f94da`. It was not one defect with a long
tail. It was **five separate instances of the same mechanism**, stacked behind `pytest -x`:

| # | red the gate printed | what was actually missing | where it was |
|---|---|---|---|
| 1 | `AttributeError: module 'tools.simplifications_store' has no attribute 'atom_name'` | `atom_name` + the 297 store docs | INDEX, never in any tree |
| 2 | `PB3_book_growth_as_earned_outcome: map notes_rehomed=['name'] != store fields ['discover_note','name']` | one line of `maturity_map.yaml` | working tree, unstaged |
| 3 | `growth_desk.py — gbp × 13 (register allows 0)` | its `PORTABILITY_DEBT.md` row | INDEX, never committed |
| 4 | `E402: baseline 193, now 195` / `F811: baseline 95, now 96` | both repairs, comments and all | INDEX, never committed |
| 5 | (would have been next) | `policy_cost_coverage` supplier + its test | unstaged / **untracked** |

Instances 1, 3 and 4 were each **already written and sitting in the index**. Nobody had to diagnose
them. They had to be *committed*.

## The two mechanisms, stated separately because they need different controls

**(a) A pathspec commit names the paths the author EDITED, not the paths their change OBLIGES.**
Already filed twice. Instance 3 widens it past "supplier symbol": what `growth_desk.py` owed was not
code at all, it was a row in the register its own control reads. The obligation can be a *data* file.

**(b) `pytest -x` turns a stack of N independent reds into N sequential ticks.** This is the part
nothing has filed. The gate stops at the first failure, so each tick sees exactly one cause, fixes
it, and hands the next one to the tick after. Five causes therefore cost five diagnose-fix-verify
cycles *at minimum*, and in practice far more, because between them the false-FIXED records
(`WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED...`) sent ticks looking elsewhere. The
wedge's duration was set by the SERIALISATION, not by the difficulty of any one red.

`-x` is right for the *blocking* decision — one red is enough to refuse a publish. It is wrong for
the *diagnostic* the wedge draw reads. Those are two different questions being answered by one run.

## The repairs, in the order they landed

* `c78b7a118` — `atom_name` + 297 store docs + the PB3 map line + the orphan-baseline freeze
* `0e5e5e5ba` — the `growth_desk.py` portability-debt row
* (third landing, this tick) — the E402/F811 repairs and the `policy_cost_coverage` unit

## The controls this actually asks for (R15 — each must be able to fail)

1. **A manifest claiming a path LANDED must be checkable against a tree.** Already proposed by
   `WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED...`; still the right build. Must read
   `git ls-tree`/`git cat-file`, never `git status` alone (TAUTOLOGY), and must RED on an
   unreadable ref rather than pass (FAIL-SILENT).
2. **The wedge draw should see the WHOLE red set, not the first one.** When the publish gate reds,
   re-run once with `-x` dropped (`--maxfail` high) purely to *report*, and put the full list in the
   doorbell. The blocking verdict stays `-x`. Mutation test: inject two independent reds and assert
   the doorbell names both — a version that names one fails.
3. **A dirty-index census on the wedge path.** When the gate is red, the draw should state how many
   paths sit in the index uncommitted. In this episode that number was 311, and it was the answer
   every time. Fails correctly by construction: with a clean index it reports zero and adds nothing.

Control 2 is the cheap one and would have collapsed five ticks into one. It is the recommendation.

## Method note worth keeping

The ruff ratchet's own finding called locating its violations "a bisect over the commits since
2026-08-06". It is not. Extract the freeze commit and HEAD, run the census's own ruff invocation in
each, and diff the violation **location sets grouped BY FILE**: line-number churn cancels inside a
file, and the true delta falls out in a single pass. Two files, +1 each, in about a minute. Recorded
because the bisect framing is what deferred the repair in the first place.

---

## What was BUILT for control 2 (2026-08-14, worker tick, RUNG 1c draw)

`background/process_run_complete.py::run_red_census` — on a red gate ONLY, the gate's own argv is
re-run once with fail-fast dropped and `--maxfail=50`, purely to REPORT. The whole red set reaches
`.last_gate_blocking_tests.json`, the NTFY the director reads, and `.publish_gate_state.json` —
which is the file the supervisor's RUNG-1 unwedge draw reads, so the doorbell now names every red
instead of the first. `background/supervisor.py::_wedge_depth_clause` turns that into the sentence
a drawn worker acts on: *"N tests are red at this HEAD … fix them TOGETHER in this tick."*

Four properties, each one a test rather than a sentence — the three the document asked for, plus
one it did not (the last), which the build itself surfaced:

1. **The blocking verdict is untouched.** The census runs after the verdict is decided and its
   return code is never read. `-x` STAYS on the gate, deliberately and against the tempting
   simplification of just dropping it: a red suite run to completion near
   `GATE_SUITE_TIMEOUT_SECONDS` becomes a TIMEOUT, and a timeout carries *no* node ids at all.
   Trading one reliable node id for a possible five is the wrong direction, and the census is
   exactly how the trade is avoided.
2. **It can never outlive the publish path's own bound.** `red_census_budget_seconds` DERIVES the
   budget from what is left of `PUBLISH_PATH_TIMEOUT_SECONDS`, capped at 20 min. Not a second
   hand-typed number: a wrapper bound that drifted from the work it wrapped is the multi-day
   wedge already recorded at `PUBLISH_PATH_ALLOWANCE_SECONDS` (its own duration is stated there,
   deliberately NOT repeated here — see the note at the end of this section). Too little left ⇒ the census is SKIPPED
   and says so, never run unbounded.
3. **"One red" and "we only looked at one" are distinguishable.** Every record carries a census
   STATUS (`complete` / `partial` / `fail_fast_only`) and every payload states it. Without that
   field a complete census finding one red is byte-identical to no census at all — which is this
   finding's own subject one level up, and would have made the control unfalsifiable. Anything
   but the three declared words reads as `fail_fast_only`; a record written before the field
   existed reads as `fail_fast_only`, because that is precisely what it was.
4. **The union is keyed on the NODE ID, not the printed line.** Found by the test, not by
   reading: the two runs are independent, so one test can arrive as `FAILED x` from the gate and
   `ERROR x` from the census. Deduping on the decorated line reported it twice and inflated the
   depth. An inflated depth is the same class of lie as a truncated one, so the merge strips
   pytest's outcome word before comparing.

**A duration written in prose is billed as this document's own cost.** The first draft of the
paragraph above cited another episode's length while explaining the budget derivation, and the
class render immediately attributed those hours to THIS finding — its recorded cost went 0 → that
number and the class total moved with it, though this document has never measured its own damage
in hours. The citation is reworded above rather than left to stand; the harvester's inability to
tell a document's own episode from one it merely mentions is filed separately as
`WORKER_FINDING_A_CITED_DURATION_IS_BILLED_AS_THE_DOCUMENTS_OWN_COST_2026-08-14.md`.

`GATE_MAX_CITED_BLOCKING_TESTS` 5 → 12, and `_blocking_clause` now says how many it withheld.
Under `-x` that cap could never bind — there was only ever one id to cite. The census is the first
thing that gives it a set to truncate, and a cap that can look like the answer is the shape this
whole document is about.

**Evidence:** `python3 -m pytest tests/background/test_publish_gate_red_census.py` — 20 passed,
including the mutation the document itself specified: the pre-repair payload (fail-fast id alone)
is re-created and asserted to FAIL the names-both assertion, so the fires-test cannot be a
tautology.

## What is still owed (recorded and accepted, not silently dropped)

* **Control 1 — a manifest claiming a path LANDED must be checkable against a tree.** NOT built
  here and NOT lost: it is owed by the sibling finding this document names,
  `WORKER_FINDING_A_FINDING_RECORDED_ITS_OWN_INSTANCE_AS_FIXED_AND_THE_FIX_HAD_NEVER_BEEN_COMMITTED_2026-08-14.md`,
  which stays BLOCKING in `H_harness` and carries the requirement (`git ls-tree`/`git cat-file`,
  never `git status`; RED on an unreadable ref rather than pass).
* **Control 3 — a dirty-index census on the wedge path.** Not built. Its remedy already exists and
  is UNWIRED: `background/tree_divergence.py::measure` already runs on the publish path
  (`_publish_tree_divergence`, immediately before the gate) and writes its artefact. The whole of
  control 3 is carrying that number into the wedge draw beside the depth clause. Recorded here so
  the next tick builds it rather than re-deriving that it exists.

Neither residue is discharged by the field above, which names only control 2's falsifiers.
