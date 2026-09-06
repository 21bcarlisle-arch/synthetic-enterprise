**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the battery's own spec entered the subject's tests into the caller verdict, and the engine had a field to stop it

**Found 2026-09-06, delivery seat, isolated worktree, claim id `converged-battery-next-subject`.
Subject: `tools/company_data_contract_battery.py`, the sweep's fifth spec. Repaired in the same
commit as this finding.**

---

## What it printed, and what was true

The fifth subject's battery finished ten mutations across four suites and printed:

```
SURVIVED ALL 4 CALLER SUITES: ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7']
```

The subject has **three** callers. The fourth suite in that population is
`tests/tools/test_generate_company_data.py` — the subject's own dedicated tests. It is the only
thing that killed anything, and it killed exactly M8, M9 and M10.

So the correct caller-population answer is **all ten contracts survived every caller suite**, and
the line above struck three of them off that list on the strength of a suite no caller reaches
through. `killed_by` for M8–M10 read
`['tests/tools/test_generate_company_data.py']` — a field whose whole meaning is *which caller
proved this*, answered by a non-caller.

**The error is in the flattering direction.** It under-reports the survivor count, which is the
number that measures the evidence gap. Seven unproved contracts is a smaller finding than ten.

## The engine already had the field, and its docstring says why

`tools/contract_battery.py` has carried this since the fourth subject:

```python
#: A suite written AS THE REPAIR, scored as its own column and never folded into
#: `survived_all` -- otherwise the pre-registered question becomes unanswerable the
#: moment the repair lands.
repair_suite: str | None = None
```

`survived_all`'s population is `spec.suites`; the repair column is scored, reported beside it as
`caught_by_own_suite`, and excluded from the verdict. `ops_repo` used it correctly. The fifth spec
declared the same suite under a constant it invented — `DIRECT_SUITES` — and concatenated it:

```python
SUITES = DIRECT_SUITES + CALLER_SUITES        # <- the defect, one operator wide
```

## Why this is worth writing down rather than just fixing

**The pre-registration argued this exact hazard, correctly, and then the spec let it in through a
different door.** `SEAT_PREREG_THE_SECOND_FLOOR_SEPARATES_A_CALLER_THAT_CATCHES_FROM_A_SUITE_THAT_IS_BLIND_2026-09-06.md`
spends a whole section excluding `tools/test_generate_company_data.py` — a **byte-identical copy**
of the same file, resurrected in another lane's dirty index — and gives the reason in the right
words:

> `survived_all`'s population is the CALLER suites; entering the subject's own dedicated tests into
> that column as well as the direct one would have the subject grading itself, and the number would
> still read as a caller result.

Every clause of that is true of the copy it *kept*. The prose reasoned about the population; the
spec expressed the population; and nothing checked that the two agreed. This is the shape where a
mechanism built to replace an exhortation contains one: the argument was in the docstring, not in
the code, and the code is what ran.

The near-miss is what makes it instructive. Excluding the twin felt like the hard call and was made
carefully. It was the *easy* half — the twin was uncommitted, so a reader would have caught it. The
tracked original walked in beside it wearing a different constant name.

## The repair, and its cost

`tools/company_data_contract_battery.py` now sets `repair_suite=REPAIR_SUITE` and
`SUITES = CALLER_SUITES`.

The spec fingerprint moves `ad4a2adfcc3d` → `57034257af20`, so the engine **refuses** the old
results file rather than resuming it — which is the 2026-09-06 adoption repair
(`SEAT_FINDING_THE_BATTERY_ADOPTED_ANOTHER_LANES_RESULTS_AND_PUBLISHED_EIGHT_SURVIVALS_IT_NEVER_APPLIED_2026-09-06.md`)
working exactly as built, on its first live application to a spec change rather than a collision.
The forty cells were re-run from scratch under the corrected spec. **The reducer was not corrected
by hand over cells recorded under the old one** — recomputing a verdict by hand over kept rows is
the same act as resuming them, and this instrument has already published one verdict no run
produced.

## It is not one spec. It is three of five, and one of them is already published

The obvious next question is whether the other specs do the same thing, and it costs one grep:

| spec | population | `repair_suite` |
|---|---|---|
| `direction` | `SUITES = (...)` | **set** |
| `ops_repo` | `SUITES = (...)` | **set** |
| `segment_vocabulary` | `SUITES = DIRECT_SUITES + CALLER_SUITES` | absent |
| `grid_intensity_feed` | `SUITES = DIRECT_SUITES + CALLER_SUITES` | absent |
| `company_data` | `SUITES = DIRECT_SUITES + CALLER_SUITES` | absent → **repaired here** |

**`grid_intensity_feed`'s result is already published, and its two kills came from a direct suite.**
`SEAT_RESULT_ONE_SUITE_PROVES_TWO_OF_FUEL_MIXS_TEN_CONTRACTS_AND_NOTHING_PROVES_THE_OTHER_EIGHT_2026-09-06.md`
records M1 and M2 as `KILLED by explore_carbon only` —
`tests/tools/test_grid_intensity_feed_and_explore_carbon.py`, which is in that spec's
`DIRECT_SUITES`, not its eight `CALLER_SUITES`. So the machine's `survived_all` there excluded M1
and M2 from the survivor list on a non-caller's kill, and **the caller-population answer for
`fuel_mix` is ten of ten, not eight of ten.**

Two things keep this from being a false-publication incident, and both matter:

* that result's **prose is honest and specific** — it says "one *suite*", never "one caller", and
  its own paragraph at the bottom names `test_elexon_fuel_outturn.py` and
  `test_grid_intensity_feed_and_explore_carbon.py` as the direct pair. A reader who read the whole
  page was not misled;
* the discrepancy is between the **machine field and the pre-registered question**, not between the
  page and reality.

But "the prose happened to be careful" is not a control, and the machine field is what the next
subject's comparison will read. **`survived_all` does not mean the same thing in three of the five
specs, and nothing anywhere says so.** Cross-subject statements of the form "four subjects in, the
load is carried by the floor every time" are computed over that field.

## What this does not establish

`segment_vocabulary` and `grid_intensity_feed` are **not repaired here** — each needs a re-run
under a corrected fingerprint, and `fuel_mix`'s is ten suites by ten mutations. Whether either
published *headline* changes is not settled by this finding: for `fuel_mix` the prose already
carries the right distinction, and for `segment_vocabulary` I have not read the result. That audit
is the follow-on, and it is named rather than assumed harmless.

There is also no control that would have caught this. The engine cannot know that a suite named in
`suites` is the subject's own — but it can be told to ask, and a spec-level check that no entry in
`suites` is the subject's dedicated test file is the smallest mechanism that would fail here. That
is not built, and is named as the follow-on rather than done quietly.
