# A rev-per-customer threshold test reds the moment the grown book is committed

**Severity:** LATENT
**Lane:** H_harness
**Rank:** after the director's named set (memory work → monthly aggregation → Knowledge pages);
above the rest of the backlog, because it becomes a BLOCKING landing gate for every lane the
instant `docs/reports/run_output_latest.json` is committed.
**Status:** QUEUED, not fixed on sight (SELF_INTERRUPT_DISCIPLINE — this is my own finding, and
the supply of these is infinite).
**Class:** a test that pins an ABSOLUTE figure which is really a function of population size

## What is on disk, measured not inherited

`tests/saas/reporting/test_phase_cn_unit_economics.py::test_revenue_increases_by_2022` asserts

```python
assert m and int(m[0].replace(",", "")) > 200_000, "2022 rev/cust should exceed £200k in crisis year"
```

against `_section_unit_economics(json.load(open("docs/reports/run_output_latest.json")))`.

`docs/reports/run_output_latest.json` is **modified in the working tree** — the producer
regenerated it with the six-fold-larger book (2fd9a390f). I rendered the SAME function over both
copies of the artefact, changing nothing else:

| artefact | 2022 rev/cust | this test |
|---|---|---|
| `HEAD:docs/reports/run_output_latest.json` | £248,047 | passes |
| working-tree copy | £51,652 | **fails** |

`observed-with-evidence` (R9). The ratio is ~4.80, which is the book growing, not the economics
changing: revenue per customer is a QUOTIENT, and only its denominator moved.

## Why this is not a code defect

`_section_unit_economics` is untouched by any uncommitted diff in the tree, and by this tick's
landing in particular. The function is right; the assertion froze the population that existed
when it was written. The sibling assertions in the same file (`test_all_years_present`,
`test_best_year_identified`) are population-independent and stay green — which is the tell.

## Why it is LATENT rather than nothing

Nothing published is wrong today, and the red does not block a pathspec landing, because
`tools.surgical_land` gates `HEAD` + the named paths and therefore materialises the OLD artefact.
It becomes BLOCKING the moment the regenerated artefact is committed — most likely by the
publisher's own auto-process cycle, which commits `docs/reports/**` without any lane choosing to.
At that point the pre-commit gate reds for every lane that touches a `saas/reporting/**` stem,
and the failure will look like it belongs to whoever landed next rather than to the book growing.

## What the repair is, and what it must NOT be

Not a raised threshold — that re-freezes the same premise at a new number and buys one book-growth
event. The assertion's real intent is *revenue per customer RISES INTO the 2022 crisis*, which is a
statement about the SHAPE of the series and is invariant to book size. Derive it: compare the 2022
row against the 2019–2021 rows from the same table, and assert the ordering. Then the test measures
the crisis, which is what it is named for.

**R15 note for whoever builds it:** the null control is a run output with the crisis flattened —
the rewritten test must go RED on that, or it has only learned to read a table. Pinning the
threshold higher would pass that control trivially, which is the second reason not to.

## Related, same class, different subject

`WORKER_FINDING_THE_POLICY_COST_CLAMP_TESTS_ENCODE_A_PREMISE_THREE_TABLES_HAVE_SINCE_OUTGROWN_2026-08-24.md`
— a test pinning a finding's COUNT rather than deriving it. Same shape (an authored-time constant
standing in for a derivation), different table. If a third instance arrives, this stops being two
findings and becomes an invariant the whole class fails against (R10).
