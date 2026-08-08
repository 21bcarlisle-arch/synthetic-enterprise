# The join test tier — tests that watch the seams

**Atom:** `AO3_join_test_tier` (lane `H_harness`, L0→L2, `depends_on: AO1_capability_index`)
**Sources:** `docs/staging/ADVISOR_FINDINGS_MISSING_TEST_TIER_2026-08-04.md`,
`docs/staging/DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md`
**Built:** 2026-08-08

---

## 0. Purpose, guarantee, why — before any mechanism

**Purpose.** Catch the *parts-pass-system-fails* defect: the failure mode behind every
serious break this project has had.

**Guarantee.** For each of five named chains, a change injected at one end is asserted to
arrive **at the other end, at the right magnitude**, through the **real production
functions** in between. Not that each stage runs. Not that each stage is individually
correct. That the *propagation itself* exists.

**Why this tier and not more unit tests.** The measured distribution is 1,109 unit files,
10 end-to-end, 1 integration. That is not a shortage of tests; it is the wrong *shape* of
test for this project's actual failure history:

| Break | Every part behaved as specified |
|---|---|
| Worktree reaper + branch deletion | …and together they deadlocked |
| Work scanner + `blocked_on` | …and together they hid 31 atoms |
| Each daemon | …and two of each were running |
| Publish gate + site rebuild | …and together they wedged on Method reachability |
| Fork execution + kill path | …and together they turned finished work back into queued work |

A unit test cannot see any of these, because no unit is misbehaving. **The defect lives in
the join.** Five tests — one per loop — is the whole tier. It is deliberately small: this
is not a coverage programme, it is a set of five tripwires across the seams that have
actually broken.

**The safety condition on structural refactoring.** The director's ruling is that this is
not a parallel nicety: **no structural refactor lands before the joins it crosses are
watched.** Refactors are exactly the change class that severs a join while leaving every
part green.

---

## 1. The five joins

Each test feeds real input at one end, asserts the outcome at the other, and asserts
nothing crossed the epistemic wall on the way.

| # | Chain | Links watched | Arrival assertion |
|---|---|---|---|
| 1 | **Work loop** | run completes → publish state → next draw | the next draw returns *real work*, and no state exists where unfinished work is present but nothing is drawable |
| 2 | **Physical** | weather → premise demand → settlement → book | a colder national temperature raises premise demand, settled volume, and wholesale cost — the last to within the volume×price identity |
| 3 | **Money** | meter read → bill → payment → arrear → recovery/write-off | an under-reading estimate shrinks the bill; a failed payment opens an arrears case for the bill's own amount; write-off and recovery reconcile against it |
| 4 | **Market** | price → hedge → settlement → P&L | a price move alone changes the hedge decision, and the hedged book is strictly less exposed to the spike than the unhedged one |
| 5 | **Customer lifecycle** | join → bill → serve → leave | acquisition and departure dates bound settlement exactly; debt at departure is carried out of the relationship, not deleted with it |

Chain 1 is the one the advisor singled out: *"this one alone would have caught most of the
last fortnight."*

---

## 2. The wall makes these stronger, not harder

The epistemic wall constrains **the company at runtime**. It does not constrain a **test**.
A test sits outside the system by design — it must see the simulation's truth *and* the
company's belief, or it could never verify the wall holds at all. The existing verifier
(`tools/epistemic_verifier.py`) already works this way.

The upgrade available here is that the current check is **static** — it scans for forbidden
imports and leaked symbols. A join test can make the **dynamic** claim: run the whole
chain, then assert that no item of ground truth influenced a decision the company took.
That is the stronger property, and the one that catches a leak arriving by a route nobody
thought to scan for.

**The one real rule.** Test helpers that reach across the wall must live where production
code cannot import them, and *that must itself be enforced* — otherwise the test scaffolding
becomes the back door. Enforced here by
`tests/system/test_report_only_landing.py::test_no_production_module_imports_the_test_tree`,
mutation-proven.

---

## 3. Report-only first landing — and what promotes it

**The director pre-ruled the mitigation, and it is not a judgement call:** join tests may be
brittle at first, and a red join test would otherwise block publish. So the **first landing
is report-only** — *land it report-only even if it looks green on day one.*

Mechanised, not promised. The `join_report_only` marker is registered in
`tests/conftest.py`, and `background/process_run_complete.py::PUBLISH_GATE_MARKER_EXPR` is
`"not operational and not join_report_only"`, so the publish gate **deselects** the tier.
A red join test can alarm; it cannot wedge the live-site publish.

This opens a second fail-open channel by construction — any content test could be silenced
by taking the marker. It is closed by **containment**: no module outside `tests/system/`
may carry `join_report_only`
(`test_join_report_only_marker_is_confined_to_the_system_tier`), mutation-proven in both
directions.

**Promotion condition (a stable week).** Remove `join_report_only` from
`PUBLISH_GATE_MARKER_EXPR` once the tier has run a full week without a false red. The
delay is the director's; do not shorten it because day one is green.

---

## 4. R15 — the fail-open shape to hunt here

> *A join test that passes when the chain it spans is disconnected.*

That is the shape, and it is the whole risk of this tier: a test that asserts "the chain ran
and produced a number" passes just as happily when the middle link has been cut and the
number is coming from somewhere else. **Each of the five therefore carries a proof that it
fires when its own join is cut.**

The proof is in `tests/system/test_join_cut_mutation.py`. Its discipline:

- The **chain driver and its arrival assertion live in `tests/system/chains.py`** and are
  imported *verbatim* by both the join test and the mutation test. The mutation does not
  get its own copy of the assertion — a mutation test that re-implements the assertion
  proves nothing about the assertion that actually ships.
- **The cut is applied to the production module, not to the test.** Each mutation
  monkeypatches a real function in `simulation/`, `company/`, `saas/` or `background/` so
  the link genuinely stops conducting, then runs the *same* driver and asserts the *same*
  assertion raises. This is the lesson from
  `feedback_tautology_reappears_inside_r15_tests`: only mutating the source finds it.
- **Both directions.** Every cut is paired with an uncut control asserting the same driver
  and assertion pass — so a mutation proof cannot succeed merely because the assertion is
  broken.
- **Each driver asserts its own premise.** A driver whose two scenarios do not actually
  differ at the input raises before it can produce a vacuously-passing comparison
  (`feedback_mutation_must_dominate_the_natural_spread`,
  `feedback_population_control_needs_a_vacuity_guard`).

Cuts currently proven, one or more per chain:

| Chain | Cut applied to the production source |
|---|---|
| Work loop | `supervisor._maturity_map_draw_concurrent` returns `[]` while unfinished work is present |
| Physical | `demand_model.heating_degree_days` → constant 0.0 (weather stops reaching demand); `run_settlement` price lookup starved (demand stops reaching the book) |
| Money | `simulate_read` always returns an actual read (the estimate stops reaching the bill); `payment_outcome` always succeeds (failure stops reaching arrears) |
| Market | `hedge_decision.estimate_price_volatility` → constant (price stops reaching the hedge decision); `hedge_fraction` forced to 0 (hedge stops reaching P&L) |
| Lifecycle | contract-window bound removed (join/leave dates stop reaching settlement) |

---

## 5. What this tier is not

- **Not a coverage target.** Five tests. Adding a sixth needs a named join and a named
  failure it would have caught. Test-count increases are not a value answer (R12, and
  CLAUDE.md's NEXT_PHASE rule).
- **Not a replacement for the unit tier.** The 1,109 unit files are not the problem; the
  advisor measured the ratio at 0.95 and called it normal.
- **Not a gate.** Report-only until promoted (§3).

## 6. Smaller gaps noted by the advisor, not built here

Registered, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — queue by default):

- **No type checker.** A `ruff.toml` and `mypy.ini` exist; no type checking runs in any gate.
- **The gate runs locally only.** The test gate is a local pre-commit hook; a gate that
  runs on one machine is bypassed by that machine being unavailable — which has happened.
- **No staging environment.** Everything is production, which is why a bad commit wedges
  the live site rather than a copy of it.
- **Unit-tier quality is unmeasured.** The tier imbalance is measured; whether the 1,109
  unit files are individually good is not — a sample read well, the rest were not read.
