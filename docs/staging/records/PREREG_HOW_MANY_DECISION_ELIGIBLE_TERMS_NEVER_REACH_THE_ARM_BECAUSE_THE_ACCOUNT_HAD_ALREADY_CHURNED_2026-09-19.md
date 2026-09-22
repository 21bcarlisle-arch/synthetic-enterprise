**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `churn-truncation-destroys-the-decision-surface-before-the-arm-is-asked`

# Pre-registration: how many decision-eligible terms never reach the arm because the account had already churned

**Written 2026-09-19 at 18:5xZ, BEFORE the run was launched and with no artefact on disk.** The
instrument and these predictions land in the same commit; the artefact does not exist yet. Anything
in this file that the run refutes stays here beside the result, per CLAUDE.md — a prediction filed
after the answer is not a prediction.

---

## 1. The question, and why it needs a run

`docs/staging/SEAT_RESULT_THE_PRODUCT_GATE_REFUSES_CAP_SEGMENTS_NOT_DECISIONS_AND_EVERY_DECISION_THAT_EXISTED_WAS_DECIDED_2026-09-19.md`
§6.2 established a BOUND and said so: the schedules carry **294** decision-eligible terms across
226 legs, the funnel saw **107**, so *at least* **187** decision-eligible terms never reached the
value arm. It is a bound and not a count because the two figures came from two censuses over two
populations, run minutes apart — the reading this project keeps having to withdraw.

**What is being run:** one value-arm pass over one seed and one roster, and then
`tools/svt_refusal_census.census()` over the same bound world in the **same interpreter**, via
`tools/churn_truncation_census.py`. The withheld terms are counted **directly** off
`simulation/run_phase2b.py`'s new `terms_never_offered_log` — one row per `continue` above the
rate-chain call, carrying the rule that withheld it. The subtraction becomes a **control on** the
direct count rather than the source of it.

## 2. What I predict, in the artefact's own keys

| key | prediction | why |
|---|---|---|
| `reconciliation.terms_lost_to_prior_churn` | **150–200**, and the single largest term | the successor rule cannot contribute (row 3), so churn has to carry essentially all of the 187 |
| `reconciliation.residual` | **0 to +20** | the census builds the same schedules the run walks, with a nominal EAC that moves rates and no dates; I expect a small positive from run-side paths the schedule census has no analogue for, not a large one |
| `terms_never_offered.per_rule.successor_term_not_activated.decision_eligible_terms_on_the_census_population` | **0** | `svt_refusal_census` builds schedules for `live_population()`; successor legs come from `successor_supply_points()` and are a disjoint roster, so their terms were never inside the 294 |
| `terms_never_offered.per_rule.account_already_churned.by_tariff_type` | **majority `'svt'`** | ~90% of this book's terms are on the default tariff, so most withheld TERMS are cap segments — which is exactly why the eligible count, not the raw count, is the number that may be subtracted |
| `terms_never_offered.terms_never_offered_total` | **well above 187** — I expect 1,000+ | same reason: the raw withheld count is dominated by SVT segments on departed accounts |

**And the class verdict I expect to have to defend:** the 187 are **class 1 — decisions genuinely
extinguished because the customer left**, not an assembly rule that could admit them. If that
holds, the decision surface really is 107, more rosters is the only route, and I press
`EP17_varied_population_draw`.

## 3. What would refute me, stated before the numbers exist

- **`residual` above +20 or below 0.** Either says the two populations are not the ones I named:
  positive means decision-eligible terms leave the schedule surface by a path neither census
  models; negative means I counted a withheld term the schedules never built. In that case the
  headline count is not yet established and the honest output is the residual, not the share.
- **A material `successor_term_not_activated` contribution.** That is the assembly-rule class, and
  a material part there dissolves the `EP17_varied_population_draw` ask rather than pressing it —
  the roster we already hold would carry more decisions than the arm has been asked about.
- **`terms_lost_to_prior_churn` materially below 150.** Then the 187 is not mostly churn, and the
  rest of the bound belongs to something nobody has named yet — which would be a bigger finding
  than the one this run was launched for.
- **An empty or absent `terms_never_offered_log`.** The instrument did not fire; the run is VOID,
  not a result of zero. `classify` refuses rather than reporting zero for exactly this reason.

## 4. What this run may NOT be used for, decided now

**No exclusion gets relaxed on the strength of it.** That is the symmetric error the gate finding
declined to commit, and relaxing a gate before the count behind it is published is the same
mistake in the other direction. R12: every count in the artefact is a diagnostic; the churn loss
falling is not an improvement.

**No money figure comes out of this.** A decision count is a count of opportunities to be graded
and is not evidence about the selection leg's sign or size.

## 5. Provenance

- Instrument: `simulation/run_phase2b.py` (`TERM_NEVER_OFFERED_RULES`,
  `terms_never_offered_log`), `tools/churn_truncation_census.py`,
  `tests/tools/test_churn_truncation_census.py` (12 controls, five mutations checked to fire
  before the run was launched).
- Artefact: `docs/observability/churn_truncation_census_2026-09-19.json`.
- One seed, one roster, value arm only, `report_end` at the world's own default.
