# WORKER FINDING — the published saturation edge is a property of how many customers were drawn, and it is false on the book `measure()` scores

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Raised:** 2026-08-18, worker tick, D28 DISCOVER pass 5 (LANE 3 idle draw). Derivation and
full evidence: `docs/design/D28_DETECTION_EXIT_THRESHOLD_PREDICTOR.md` §3–§4.
**Owner:** `tools/couple_w2_11_d5.py` — the `file_scope` of `H27_payment_belief_gap`
(`loop_stage: harden`) as well as of D28/D31, so this is drawable now (note 4's correction:
a `file_scope` shared by thirty atoms is idle only if EVERY owner is).
**Intended rank (P-1):** top of `D_billing_metering` — it is a false statement in a component
of a published ledger entry.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE).

## What was observed

`score_triad` stamps, onto every detection result:

```python
det.components["recon_saturation_band_days"] = (
    ORGAN_QUERY_GRID["flagged_via_reconciliation"]["saturates_below"],
    ORGAN_QUERY_GRID["flagged_via_reconciliation"]["saturates_above"],
)   # tools/couple_w2_11_d5.py:9685
```

Two literals. The same pair therefore rides every book the scorer is ever run over — the
offline `measure()`, the live triad, and `docs/observability/coupled_gap_ledger.json`, where
`W2_11_payment_behaviour_source / components / recon_saturation_band_days` reads `[-6, 82]`
today. The prose sibling (`recon_saturation_caveat`) does name its scope — "n=300,
seeds [7, 11, 23]" — but the machine-readable tuple carries none, and this module's own
comment three lines above says why that matters: *"the ledger writer, the live wiring and the
dashboard read `components` and never the prose (D22)."*

**The upper number is not a property of the book. It is a property of the draw size.**
Measured predictor-side over 25 books (n ∈ {150, 300, 600, 1200, 2400} × seeds
{7, 11, 23, 3, 41}), same book shape throughout — one-cycle spread, one `as_of`, same grace
line, same terms:

| upper edge | seed 7 | seed 11 | seed 23 | seed 3 | seed 41 |
|---|---|---|---|---|---|
| n=150 | 70 | 80 | 75 | 77 | 87 |
| n=300 | 80 | **82** | 75 | 77 | 87 |
| n=600 | 85 | 84 | 75 | 84 | 87 |
| n=1200 | 87 | 87 | 85 | 84 | 87 |
| n=2400 | *none* | 87 | 87 | *none* | *none* |

*none* = the reading is still moving at the grid's last point, so there is no upper saturation
inside the grid at all. `saturates_below = −6` is **invariant on all 25** — the two edges are
different kinds of object and only one of them is a bound.

**And it is false on the book `measure()` itself defaults to.** `measure(n_customers=4000)`,
via the SHIPPED scorer (not the predictor), publishes **seven distinct figures** across the
region the component calls one:

| k | +82 | +83 | +84 | +85 | +86 | +87 | +88 |
|---|---|---|---|---|---|---|---|
| `gap` | 0.136214 | 0.136626 | 0.137037 | 0.137449 | 0.138272 | 0.138683 | 0.139095 |
| `flagged_size` | 885 | 883 | 882 | 881 | 879 | 878 | 877 |

## Why the control did not catch it (R15)

`measure_organ_query_grid_saturation` defaults to `n_customers = 300` — the draw size the
declaration was authored at. The register is re-derived, honestly and every run, **exactly
where it had already answered**. That is atom D28's own founding sentence, recurring on the
**population-size axis** rather than the grid axis, on the register D28 itself re-derived to
close the grid-axis version. Neither the D31 grid-extent repair nor the D28 density repair
touched this axis, because both moved the *grid* and neither moved the *book*.

Not a tautology and not fail-open: the control genuinely measures and would fire if the
declaration were wrong **at n=300**. It is the third R15 pattern's neighbour — a control whose
SUBJECT was chosen by a harness convenience (`n_customers=300`, a default), so the population
it can fail on is the one that produced the declaration.

## Options, and the recommendation

1. **Scope the published tuple to what it was measured on** — emit
   `recon_saturation_band_days` as `{"below": −6, "above": 82, "measured_on": {"n": 300,
   "seeds": [7, 11, 23]}}`, so a consumer holding a reading over a different book can see
   that the band is not that book's. Cheapest, and it makes the machine-readable half say
   what the prose half already says.
2. **Derive the band per run from the book actually scored.** The predictor in
   `docs/design/D28_DETECTION_EXIT_THRESHOLD_PREDICTOR.md` §1 returns both edges from the
   ledger and the truth records at 0.2 s on a 600-account book — ~250× cheaper than the sweep
   and cheap enough to run inside `score_triad`. This is the D19/D20/D22/D23/D25 rule
   (a published sentence moves when its subject moves) applied to the one field on this
   result that is still a literal.
3. **Sweep the control across the population axis** — `measure_organ_query_grid_saturation`
   over more than one `n`, and declare the upper edge as a band or as absent, the way
   `undefined_drifts` already handles a reading that stops existing.

**Recommendation: 2, then 3, and 1 only if 2 is deferred.** 1 alone leaves a number that is
wrong for every consumer who was not going to check its scope anyway; 2 removes the class
(no literal left to decay) and pays for itself the first time the live book's edge differs
from the offline one; 3 is what stops it re-decaying and is worth little without 2.

Whichever is taken, the **lower** edge should be re-declared as the closed form
`−(DEFAULT_RECONCILIATION_GRACE_DAYS + 1)` with the on-time-payment precondition stated, not
left as the literal `−6`: it is the half that genuinely is a bound, and today the two halves
are indistinguishable in the register.

## Falsifiers this finding owes its builder

Run before recommending, not after (both already run, results above):

* **Positive** — the declared `saturates_above` must reproduce on a book the declaration was
  not authored on. RED today: 82 against 84/87 at n=600/1200 and against *no edge* at n=2400.
* **Null control** — the same test on `saturates_below`, which must stay GREEN across the same
  25 books, or the test is measuring draw noise rather than a scope error. GREEN today
  (−6, 25/25).
* **Mutation** — pin the control's `n_customers` and the positive falsifier must go GREEN
  while the defect is untouched. That is the shape of the control as shipped, which is why
  this is filed as a control finding and not only a number finding.
