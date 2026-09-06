**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The leg contamination never touched the published ceiling — it was the full-coverage rung

**Found:** 2026-09-06, delivery seat, claim
`the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Pre-registration:
`records/SEAT_PREREGISTRATION_WHAT_THE_HEAD_INSTRUMENT_SAYS_ABOUT_THE_FIGURE_THE_PAGE_IS_PUBLISHING_2026-09-06.md`
(written before the run; **one of its four predictions is refuted**, and the refutation is the
useful part).

No instrument was changed here. This is a measurement with the instrument **as it stands at HEAD**,
run against the current book, and a correction to the causal story two earlier findings published.

---

## Why the run was made

The selection correction landed at `06fc90189` and the household re-keying at `3851553ec`. But
`docs/observability/r1_inference_ceiling.json` was last **committed** at `613f9bd17` — before the
re-keying. So at HEAD the site publishes `+0.6127`, `p=0.0249`, `clears` as R1's ceiling, and those
figures were produced by the pre-keying instrument on a book the instrument's own docstring now
describes as 213 supply points where there were 149 households, with a large share of the target
column drawn by hashing gas-leg ids that belong to no household.

Nobody had run the **committed** instrument against the current book. That is what this is.

```
python3 -m tools.r1_inference_ceiling --run docs/reports/run_output_3851553ec_20260906T175920Z.json
```

## The result

| | published at HEAD | HEAD instrument, current book |
|---|---|---|
| households graded | 213 | **164** (census: 264 supply points → 177 households, 87 legs folded) |
| pair-rung n | 69 | **69** |
| ceiling (best of 45) | +0.6127 | **+0.6308** |
| corrected bound p95 | +0.5529 | **+0.5776** |
| p | 0.0249 | **0.0299** |
| verdict | clears | **clears**, margin +0.0532 |
| full-coverage rung | cannot tell, p=0.8507 | **cannot tell, p=0.4328** |
| `every_graded_row_is_a_household` | (absent) | **true** |

**The two corrections compose at HEAD.** The leg guard in `true_traits` does not fire, because
`observable_rows` now keys through `household_of` before it is reached — which is the arrangement
the guard was written to require, confirmed rather than assumed.

**And the committed instrument reproduces the in-flight lane's headline exactly** — `+0.6308`,
`p=0.0299`, `bound 0.5776`, `households 164`. Their working copy is +451/−278 lines against the
committed file, and none of it moves the headline; it adds a point estimate on top. That is worth
recording because it was the thing I was least sure of: there is **no disagreement between the two
instruments to resolve**.

## What refutes the published causal story

The pre-registration's P2 said the ceiling would move by more than 0.02 once 38% of the target
column changed from noise to truth. **It moved by 0.0181.** Refuted, and the reason is visible in
the per-field table:

| field | scope | old n → new n | old held-out → new | |
|---|---|---|---|---|
| `perceived_bill_saving_gbp` | decision_only | 69 → 69 | +0.4799 → +0.4799 | **identical** |
| `company_churn_estimate` | decision_only | 69 → 69 | +0.2362 → +0.2362 | **identical** |
| `expected_term_margin_gbp` | decision_only | 56 → 56 | −0.0061 → −0.0061 | **identical** |
| `resentment_score` | decision_only | 69 → 69 | refused → refused | **identical** |
| `mean_recent_margin_rate` | account_state | 213 → 149 | −0.0422 → +0.0537 | moved |
| `portfolio_premium_pct` | account_state | 213 → 149 | −0.0509 → −0.0401 | moved |
| `svt_rate_gbp_per_mwh` | account_state | 69 → 146 | −0.1263 → −0.1286 | moved |
| `rate_vs_svt_pct` | account_state | 69 → 146 | −0.3530 → +0.0898 | moved |
| `unit_rate_gbp_per_mwh` | account_state | 100 → 164 | refused → −0.1192 | moved |
| `company_eac_kwh` | account_state | 69 → 164 | −0.0645 → −0.0880 | moved |

Every field that exists only where a decision was reached is **byte-identical** across the
re-keying. Every field the company holds continuously moved. That is not a coincidence and it has a
mechanism: a gas leg is registered at a renewal on the electricity point, so the decision-time
fields were **already effectively household-keyed** and the legs never carried them. The pair rung
is built from the intersection of those fields — which is why its n is 69 before and after, and why
the winner barely moved.

**So the contamination was never in the published figure.** It was in the full-coverage rung, which
took every id it could find, including the 87 legs. Two findings on this claim published the
opposite implication — that the 213-household figure and the ceiling drawn from it were both
compromised. The ceiling was not. The rung that was compromised is the one that has read
`cannot tell` all along, and its p has moved from **0.8507 to 0.4328** now the fabricated share of
its target column is gone.

`SEAT_FINDING_R1S_CEILING_WAS_A_SELECTED_MAXIMUM...`'s refutation section is right that
*"the full-coverage rung's cannot tell at p=0.85 was never a coverage result"*. It is confirmed
here. What is **not** established, and what that section implies, is that the pair rung shared the
defect.

## What I cannot attribute, and will not

The published book (`23cbe058b`) and the book measured here (`3851553ec`) are **different books**,
and the instrument changed between them. Two things moved, so no single number here can be credited
to re-keying alone. Specifically:

- the reductions (213 → 149, 213 → 164) can only be leg folding, which cannot raise a count;
- the **increases** (69 → 146, 100 → 164, 69 → 164) cannot be leg folding alone. They are either
  the later book's account-state logging, or folding giving a household a field only its gas leg
  carried — and **this run cannot separate those two**. It is not claimed either way.

The one-variable version is cheap and is the hand-off: re-run the committed instrument against
`run_output_23cbe058b_20260906T141424Z.json`, the *published* book. Same book, new instrument,
one variable. That isolates re-keying exactly, and it is what would let the increases be attributed.

## Grading the pre-registration, beside the result

| | prediction | outcome |
|---|---|---|
| P1 | households fall to 149–177, nothing refuses | **confirmed** — 164, `every_graded_row_is_a_household: true` |
| P2 | the ceiling moves by more than 0.02 | **REFUTED** — +0.0181, and the refutation is this finding |
| P3 | still clears, margin under +0.10 | **confirmed** — clears by +0.0532 |
| P4 | the full-coverage rung stops reading p≈0.85 | **confirmed in direction** — 0.8507 → 0.4328, still `cannot tell` |

P1 and P3 were declared in the pre-registration as **informed, not blind**: I had read the other
lane's uncommitted artefact before writing them and claimed no credit for them then. P2 and P4 were
the two that could embarrass the record and one of them did.

## What was deliberately NOT done

**No regenerated `site/data/delivery.json` or `docs/observability/*.json` is landed here.** Another
lane holds that whole chain dirty in the shared tree with `delivery.json` already staged at the
corrected figures, and their instrument is further along than HEAD's. Landing a third variant of
the same number is the documented failure this project calls two lanes fixing one defect
concurrently, and the numbers agree anyway, so racing them buys nothing and risks wedging the
fast-forward. The artefact regenerated by this run stayed in this worktree, uncommitted.

**The page is still wrong until they land.** That is the live exposure and it is theirs to close,
not a second writer's.

## What is still open

Unchanged by this: the published `+0.6308` is a **selected maximum**, so its magnitude remains an
upward-biased estimate of the ceiling. The in-flight lane is building the honest point estimate
(a three-way partition that re-runs the selection and scores the winner on a third of the book
neither step saw). Until that lands, **A49 must not be read as holding a bound** — which A49's own
gate language now says.
