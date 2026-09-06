**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

# Two controls demand opposite shapes for `blocked_on`, so the field is unusable by the first atom that uses it

**Found:** 2026-09-06, delivery seat, registering six decided-not-authorised phase rows from the
weather, housing and people rulings. Each names its predecessor as its blocker. Both controls fired,
and they cannot both be satisfied.

---

## The two controls

`tests/design/test_maturity_map_contract.py::check_edges` — **`blocked_on` must be a LIST of atom
ids.** A bare string is explicitly classed as prose and rejected:

```
    depends_on/blocked_on, when given, must be a LIST of existing ids.
    ... Any other shape (a bare string, i.e. prose) ... is a violation.
```

`tests/design/test_maturity_map_facets.py::check_block_hygiene` — **`blocked_on` must be a SCALAR.**
It does `s = str(blocked_on).strip()` and requires `s` to be a known releaser token or an existing
atom id. Handed the list the first control demands, it stringifies to `"['W1_14_weather_cells…']"`
and reports:

```
  blocked_on="['W1_14_weather_cells_for_household_heat_load']" resolves to no known releaser
  (...) and no existing atom id -- an unresolvable release condition cannot be unblocked or judged
```

A list fails hygiene. A scalar fails edges. **`null` is the only value that satisfies both**, and
`null` means "not blocked".

## Why nobody has hit it

Measured across the live map: of 103 atoms before this turn, **not one had a non-null `blocked_on`**.
Every blocked atom in the repo — `EP16_anchored_generators`, `EP17_varied_population_draw`,
`C31_time_is_the_currency_that_does_not_exist` — carries `blocked_on: null` and states its condition
in prose in `block_reason`.

So both controls have been vacuously green for their whole lives. The contradiction is reachable only
by the first atom that actually populates the field, and this turn was it. Six rows, six refusals, on
the first use of a field the schema has always offered.

**This is the R15 shape twice over.** Each control passes its own mutation test, because each mutates
against `null` and neither has ever seen the other's required shape. Two controls over one property
where the first answers, and the second is unreachable — except here they answer *differently*, so
the second is not merely unreachable, it is contradictory.

## What I did, and why it is not the fix

The six rows ship with `blocked_on: null`, the release condition stated in `block_reason` (director
verbatim, including the disjunctive two-limb condition on the weather phase 3), and the actual edge
carried in `depends_on`, which is list-typed and satisfies both controls. **Nothing is lost** — that
is the pattern every other blocked atom already uses, and it is why the defect stayed invisible.

But it means the harness now has a schema field that **no atom may ever populate**, and the next seat
to try will pay the same two cycles I did — one refusal per control, in series, because the gates fire
serially and each costs a full run.

## What would close it

Pick one shape and make the other control agree, with the choice recorded:

- **`depends_on` is already the list-typed edge**, so `blocked_on` carrying a *second* list of atom
  ids is redundant by construction. The cheaper resolution is to let `blocked_on` be a scalar releaser
  token or single atom id — its documented purpose — and **remove it from `EDGE_FIELDS`** in the
  contract test, leaving `depends_on` as the only list edge.
- Either way the fix needs an R15 mutation on the surviving control that fires on a **populated**
  `blocked_on`, not on `null`. A mutation graded against `null` is what let both of these ship.

The falsifier is direct: populate `blocked_on` on one atom with each shape and run both suites. Today
that yields a refusal whichever shape you choose, and that is the whole finding.
