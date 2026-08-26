# PB3 — three of four exit criteria are already at HEAD; what remains is (d), and (d) has a known contaminant whose repair has silently landed

**Atom:** `PB3_book_growth_as_earned_outcome` · **Lane:** W2_customer_generator · **Stage:** DISCOVER (doc-only)
**Written:** 2026-08-25, worker tick. **Nothing was committed by this tick and nothing tracked was edited — deliberately; see §5.**

All claims `observed-with-evidence` unless labelled `inferred` (R9).

---

## 1. The drawn atom is largely already built

The tick drew PB3 as a BUILD atom at `level_current: 0`, `loop_stage: build`, `block_reason: null`.
It is not level 0 in substance. Measured against the atom's own amended exit criteria:

| criterion | state at HEAD (`5eff5ab32`) | evidence |
|---|---|---|
| (a) mechanisms named and wired — churn, acquisition cost, competitor field | **PARTIAL** — churn and cost wired; competitor field is *not* a rival supplier | §2 |
| (b1) arrival stream FIXED, our own market position alone moves the book BOTH ways | **BUILT AND PROVEN** | §3 |
| (b2) arrival stream EMPTIED, the book still grows | **BUILT AND PROVEN** | §3 |
| (c) no step change that is not a modelled acquisition or loss event | **LANDED** `9d21b2a1c` | §3 |
| (d) company belief vs world truth, gap measured and reported | **ABSENT** | §4 |

So the remaining BUILD work in this atom is **(d), and the residue of (a)** — not a from-scratch build.
This is the [[a build atom's deliverable may already be built and dark]] shape: the drawn level is
stale rather than the code being missing, and building it again would be waste.

## 2. (a) — what is wired, and the one part that is not

Wired, `observed-with-evidence`:

- **Churn and the win side read the SAME elasticity.** `simulation/market_switching_propensity.py`'s
  DESNZ-calibrated `_savings_to_rate` is resolved by *both* legs; `simulation/acquisition_funnel.py:146`
  carries the (b1) note and `_quote_to_application_rate(segment, price_differential_pct)` is the win-side
  entry. `test_b1_the_win_side_reads_the_SAME_elasticity_the_loss_side_does` asserts the shared object
  rather than a private copy — which is what makes R12 goal-seeking on book size structurally
  unavailable, not merely forbidden (the atom's own registered simplification says so).
- **Acquisition cost is booked.** `9d21b2a1c` ("the campaign's 1,295 quotes were paid for in a JSON file
  and never in the accounts") closed exit (c)'s "costs a penny" clause;
  `simulation/run_phase2b.py:820` and `simulation/live_population.py:729` carry it.

Not wired, and honestly declared in the code rather than hidden — `simulation/net_new_acquisition.py:66`:

> "It also does not model a competitor's counter-offer: `B4_competitor_field` is PB3's named couple and
> is a separate atom. Today the loss side is the funnel's own leakage, which is real but is not yet a
> rival supplier taking the customer."

Map state of the three named organs, `observed-with-evidence`:

    B4_competitor_field            lane B_commercial          L1  harden
    W2_3_competitor_field          lane W2_customer_generator  L1  harden
    B10_competitor_switching_response  lane W2_customer_generator  L0  idle
        file_scope: ['sim/competitor_field.py', 'tests/sim/test_competitor_switching.py']
        -> `sim/competitor_field.py` is ABSENT from the tree.

`inferred`: PB3 cannot honestly claim "won and lost **against the market**" at its full strength while the
loss side is funnel leakage and no rival supplier exists — that is B10's deliverable, and B10 is unbuilt.
This is the coupled-triad rule biting correctly: *no company capability is complete until it has faced a
world that can defeat it.* **Recommendation:** PB3's level should stop at **L2**, not the drawn L3, and
name B10 as the couple that carries it to L3. L3 on a book whose only rival is its own funnel's leakage
would be a level claimed on a world with no opponent in it.

## 3. (b1)/(b2)/(c) — run, not assumed

Both the code and its tests are committed at HEAD; the only uncommitted PB3 path is its simplifications
register, which is inside the in-flight EP1 landing's pathspec (§5).

    git show HEAD:tests/simulation/test_net_new_acquisition.py | grep -c 'def test_b1\|def test_b2\|def test_c_'   -> 12
    python3 -m pytest tests/simulation/test_net_new_acquisition.py -q   -> 42 passed in 11.20s
    ... -k "b1 or b2"                                                   -> 10 passed in 0.79s

The suite carries its own mutation controls, which is what makes this evidence rather than decoration
(R15): `test_MUTATION_b1_a_price_blind_funnel_makes_both_directions_vanish`,
`test_MUTATION_b1_the_market_crisis_floor_on_the_dearer_side_flattens_it`,
`test_MUTATION_b2_a_campaign_gated_behind_the_ARRIVAL_flag_goes_flat`,
`test_MUTATION_c_the_PRE_BUILD_run_books_none_of_it`. The (b1) null control that the 2026-08-18
re-amendment demanded is present and separate from the claim it guards
(`test_b1_the_prospect_STREAM_is_identical_across_the_three_price_positions` asserts the quoted
prospect ids byte-identical at all three price positions, so the win difference is attributable to the
offer and not to a reshuffled draw).

## 4. (d) — absent, and its contaminant

**Absent, `observed-with-evidence`:** `docs/observability/coupled_gap_ledger.json` carries 15 atom keys
and **no PB3 key**. No `tools/couple_pb3*.py` exists. Every other coupled pair reports through a
`tools/couple_*.py` writer emitting `{gap, g0, raw_gap, metric, baseline, components, note,
twin_atom_id, run_git_commit, measured_at}` (shape read from the `W2_2_population_draw` entry).

**The belief/truth pair PB3 needs already exists on the seam.** `company/interfaces/growth_desk.py`'s
`GrowthCampaignPlan` carries `believed_win_rate`, `realised_win_rate` and `planning_on`, sourced from
`saas/growth_mandate.py:342-344`. The company sizes each year's quote budget from
`expected_quotes_per_win`, which inverts its *belief*; the world then decides the *outcome* through the
funnel. That is a genuine belief-vs-truth pair on the one number that drives the campaign, and it is
already recorded per year.

**The contaminant, and why it is not a blocker.** The open LATENT finding
`WORKER_FINDING_THE_COMPANY_NOW_LEARNS_A_WIN_RATE_FROM_YEARS_AN_ENGINEERING_CAP_DECIDED_2026-08-24.md`
measured the realised win rate decaying 0.169 → 0.051 across years whose outcome
`SETTLEMENT_CUSTOMER_YEAR_BUDGET` — a *machine* limit — decided, and correctly refused to fix it
company-side, because a company that could see which of its own losses were artefacts would be reading
the simulation.

That refusal binds the COMPANY. **It does not bind the HARNESS**, and (d) is harness-side: the gap
measurer is permitted to see both sides, which is the whole point of the coupled triad. So the legal
shape of (d) is a gap **partitioned by binding reason** — `by_year[*]["binding"]` is already emitted by
`plan_growth_campaign` (`simulation/net_new_acquisition.py:634`, values include `settlement_engine`) —
reporting the belief-vs-truth gap over market-decided years as the score, and the machine-decided years
separately as a declared exclusion with its own count. Nothing crosses to the company; the company's
belief is measured exactly as it formed it. A single unpartitioned gap number would be the R15
FAIL-OPEN here: it would read as the company's error and would partly be the box's.

**And the contaminant may already be smaller than the finding says.** `observed-with-evidence`: the
finding's own recommended repair — its option (1), "raise or remove the settlement customer-year budget
so wins are decided by funnel and market rather than by machine capacity", which it called *"the only
repair that removes the distortion rather than relocating it"* — **landed the same day and the finding
was never updated**:

    6474e3cc1  2026-08-24  sim: raise settlement customer-year budget 600 -> 1200 so the funnel,
                           not the engine, decides the book
    git show HEAD:simulation/net_new_acquisition.py | grep 'SETTLEMENT_CUSTOMER_YEAR_BUDGET = '
      -> 429:SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200.0

The finding's table of settlement-bound years was measured at 600.0 and **no re-measurement at 1200.0
exists**. Whether any year of the shipped run is still `settlement_engine`-bound is therefore an open
question with a cheap answer, and it is the first step of the (d) build, not a separate investigation.

**Why this tick did not run that measurement.** It requires `live_population()` at the shipped
configuration. That is the same call the 2026-08-24 OOM finding attributes twelve sim-runner kills to on
this box, and a 25-minute pre-commit gate was in flight (§5). Spending the memory to satisfy a
measurement that is not urgent, at the risk of the OOM killer reaping the gate that is unblocking every
lane in the repository, is a bad trade. It is named here as step 1 rather than guessed at.

## 5. Why nothing was committed, and nothing tracked was edited

`observed-with-evidence`: the EP1 store-roll landing, attempt 4, was live throughout this tick —
PID 1160950, own session leader, no wrapper, started 11:00:24, 25 minutes elapsed at last check, its
gate `pytest` (PID 1161466) running the selected targets, HEAD unchanged at `5eff5ab32`.

Both live BLOCKING findings in `W4_the_wall` state the constraint and it is arithmetic, not deference:
`surgical_land` re-gates **from zero** on a lost HEAD race, so any commit by any lane restarts a
~45-minute gate that is the tree-wide unblock for every level move in the repository. PB3's own
simplifications register is inside that landing's pathspec, so PB3 cannot record a level move until it
resolves either way.

Nothing tracked was edited either, which is the stricter half and the one that was learned expensively
today: **a worker holding work out of a commit must hold it out of the TREE, not out of the pathspec.**
The producer and `sim_runner` read the shared working tree, and the level gate reads the tree rather
than the pathspec — a staged map edit held back from its commit refused every publish cycle from 09:25
to 11:20 UTC while the publish-gate state file read `total_red: 0`. This document is untracked, sits
under `docs/design/` (not `docs/staging/`, so the OPS12 severity scanner does not see it), and is
deliberately named `_DISCOVER.md` rather than `_FRAME.md` so it cannot register as FRAME saturation for
this atom (`background/supervisor.py::_atom_has_frame_doc` excludes DISCOVER-stage filenames — and reads
only paths listed in the atom's `evidence`, which this tick did not touch).

## 6. What the next tick does, in order

1. **Wait for PID 1160950.** If it landed, the simplifications count red is clear and PB3's map is
   movable. If it failed, that is the fourth failure and `tools/surgical_land.py`'s full re-gate on a
   lost HEAD race is the thing to fix (a targeted re-gate of the intersection of this commit's selection
   with the paths the base move touched is available and is a two-minute retry, per the timing-spread
   finding's note).
2. **Re-measure the settlement-bound years at 1200.0** and update the LATENT win-rate finding with the
   result — its own recommended repair has landed and its published table is stale.
3. **Build (d)** as `tools/couple_pb3_book_growth.py`: believed vs realised win rate per year,
   partitioned by `by_year[*]["binding"]`, market-decided years as the score and machine-decided years
   as a declared exclusion with its count. Mutation control: a writer that pools the two partitions must
   fail the control, because that is exactly the number that reads as company error and is not.
4. **Self-certify PB3 to L2, not L3** (§2), recording B10_competitor_switching_response as the couple
   that carries it to L3.
