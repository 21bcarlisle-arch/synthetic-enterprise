**Severity:** LATENT · **Lane:** D_billing_metering

# The inertness flag is blind to the population its own function names as the edge-setter

**Found:** 2026-08-18, D30 DISCOVER/FRAME pass 6 (worker tick, LANE 3 idle draw). Measured in a
detached worktree at HEAD `310cac5ce` (`git worktree add --detach`), shipped `build_scenario` /
`measure_scenario_constant_census` / `score_triad`, n=300, seeds 7 and 23, the company's memory
perturbed ONLY through the declared `organ_failure_window_drift_days` — never a monkeypatch.
Every claim below is `observed-with-evidence` unless labelled otherwise (R9).

**Class:** controls that cannot fail — the field is blind to its named subject, and the control
over it derives its expectation from the same blind read.

---

## Observed, with evidence

`tools/couple_w2_11_d5.py::measure_scenario_constant_census` now measures TWO populations off the
same book. Its own comment, at lines 6774–6785, states which one owns the belief edges:

> The line above ages EVERY record; the belief edges are read off OBSERVED FAILURES only
> (`measure_belief_window_resolution`), and those are two different books. … Measuring only the
> dense one made `describes_this_book` answer True, with zero violations, on books where the
> failure-side edge was twenty days off the register's declaration: R15's FAIL-OPEN pattern, in
> the control that exists to stop an edge rotting unnoticed.

It publishes `"edge_setting_population": "observed failures"` as a field, and adds a second
verdict `describes_this_books_failure_span` beside `describes_this_book` so the invoice-side
verdict cannot green the edge question.

**Fifty-three lines below that comment, the three `scored_company_*` fields still read the
invoice population:**

```python
oldest = ages[-1] if ages else None                      # EVERY record
f_oldest = failure_ages[-1] if failure_ages else None    # the edge-setting population
...
"scored_company_headroom_days": None if oldest is None else window - oldest,
"scored_company_is_inert":      None if oldest is None else window >= oldest,
```

These two fields are attached to the BELIEF dimensions (`score_triad`, lines 11068–11073) and
their prose reaches the published ledger. They are the only quantities in the function that are
about whether the belief figures can MOVE — that is, the only ones whose subject is exactly the
population the comment above says they must not be read from.

`git blame` says why nobody joined them: `scored_company_headroom_days` is from `156004d135`
(2026-08-11) and the failure-span half is from `febf7e51f4` (2026-08-18). The 2026-08-18 pass
repaired the verdict half of this function and left the inertness half on the dense population,
seven days after the inertness half was written.

## The falsification, with its null control

Seeds 7 and 23, n=300, drift −309 and −308 (company window 91d then 92d) — the only step at
which the invoice top (92) and the failure top can disagree on this book:

| seed | W | f_oldest | inv_oldest | published `is_inert` | `belief` | `belief_population_mix` |
|---|---|---|---|---|---|---|
| 7 | 91 | **91** | 92 | **False** | 0.1518987341772152 | 0.07999999999999997 |
| 7 | 92 | **91** | 92 | True | 0.1518987341772152 | 0.07999999999999997 |
| 23 | 91 | 92 | 92 | False | 0.1411764705882353 | 0.07666666666666666 |
| 23 | 92 | 92 | 92 | True | 0.13529411764705881 | 0.07666666666666666 |

**Seed 7 is the defect.** At W=91 the company already remembers every one of the 102 observed
failures (oldest 91d), so the parameter is inert — and the two belief figures are BIT-IDENTICAL
across the step, which is what inert means. The published field says `is_inert=False`, and the
caveat that rides on it renders the "SITS INSIDE IT … the belief figures MOVE with that
parameter" sentence. They do not move. Told wrongly, in prose, on the dimension it is about.

**Seed 23 is the null control.** Same book size, same two windows, same flip of the field — but
here the failure population reaches the invoice top (both 92), so the field is CORRECT at both
values, and the belief figure genuinely moves (0.1412 → 0.1353). The error appears exactly on the
seed where the two populations disagree and vanishes on the seed where they agree, so this is a
wrong-population read and not a generally broken boolean.

On the offline scenario the two tops differ by ONE day, which is why six Hours walked past it. On
the live book they differ by 91.

## It is live on the published artefact, twice, with two different numbers

`docs/observability/coupled_gap_ledger.json`, entry `W2_11_payment_behaviour_source`,
`measured_at` 2026-08-18T17:59:31Z, `run_git_commit` `145a1490f`. Both belief caveats now reach
`components.dimension_caveats` (the 2026-08-18 leg-2 repair works — verified here at the written
artefact, not at the result dict). Inside that one blob, on the same dimension, for the same
6000d company:

* `belief_resolution_caveat` — "31 observed failure events, oldest 3378d before `as_of`, against
  a company window of 6000d — SATURATED, with **2622d** of headroom"
* `scenario_constant_census_caveat` — "THE BELIEF DIMENSIONS' OWN BAND IS SMALLER, **and is the
  one that sets their edges**: they read OBSERVED FAILURES only, which here span 30d to 3378d" …
  and then, two sentences later: "it holds 6000d of memory, **2531d** past the top of the band"

6000 − 3378 = 2622. 6000 − 3469 = 2531. The second sentence computes the scored company's
headroom against the INVOICE top immediately after telling the reader that the invoice band is
not the one that sets these edges. Two headroom numbers for one company in one entry, 91 days
apart, both published, neither labelled as measuring a different population.

The live verdict itself is not wrong (6000 clears both tops), so this is LATENT and not BLOCKING:
what is published wrongly today is the headroom figure, by 91 days.

## And the control over it pins the defect

`tests/tools/test_couple_w2_11_d5.py:8566`, inside the test written to prove these fields read
the scored company:

```python
assert measured["scored_company_headroom_days"] == (
    measured["scored_company_window_days"]
    - measured["measured_oldest_age_days"]), drift
```

The expectation is derived from `measured_oldest_age_days` — the same invoice field the defect
reads. R15's TAUTOLOGY pattern one level down: on the population question this control cannot
fail, because a correct implementation reading `measured_failure_oldest_age_days` would make it
RED. It does not merely miss the defect; it pins it.

Its sibling `test_the_inert_verdict_is_falsifiable_in_both_directions` (line 8579) exercises the
switch at drifts −320 (W=80) and +200 (W=600) — 320 and 508 days clear of the 91/92 step, the
only band on this book where the two populations disagree. Both directions, never at the edge.

## What a repair must show

1. `scored_company_headroom_days` and `scored_company_is_inert` read
   `measured_failure_oldest_age_days`, with `measured_oldest_age_days` kept and published as the
   invoice-side figure it correctly is (the constants half of this function is about invoices and
   must not be made red by a question it was never asked).
2. The seed-7 W=91 case above as the falsifier, with the seed-23 W=91 case beside it as the null
   control — the same flip, one book where the field must read True and one where it must read
   False.
3. The control at 8566 re-derived from the edge-setting field, and mutation-proven: an
   implementation that reverts to the invoice population must turn it RED.
4. Both spans named in the caveat prose wherever a headroom is quoted, so the two numbers in one
   ledger entry can never again be read as one quantity.
5. A guard that the two `scored_company_*` fields and `edge_setting_population` are derived from
   the same list, so the next population split cannot separate them again.

## Disposition

QUEUED, not fixed on sight (SELF-INTERRUPT DISCIPLINE). The repair is BUILD on
`tools/couple_w2_11_d5.py` and `tests/tools/test_couple_w2_11_d5.py` — both in atom
`D30_the_belief_band_is_this_books_length`'s `file_scope`, which is `loop_stage: idle`, and this
tick's draw is DISCOVER/FRAME only. Recorded as note 6 of that atom's register in the same
commit as this document.

R12: no published number was tuned. Every figure above was measured in a throwaway worktree to
find out whether a field this atom publishes about the company it grades reads the population it
is about. It does not.
