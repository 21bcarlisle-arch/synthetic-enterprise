**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: ten of ten survive every caller suite, and not one of them can see the subject

**Measured 2026-09-06, delivery seat, isolated worktree at `7c74f28c2`, claim id
`converged-battery-next-subject`. Subject: `tools/generate_company_data.py`, the **fifth** subject
of the convergence-evidence sweep. Pre-registration:
`docs/staging/records/SEAT_PREREG_THE_SECOND_FLOOR_SEPARATES_A_CALLER_THAT_CATCHES_FROM_A_SUITE_THAT_IS_BLIND_2026-09-06.md`,
landed at `e1143b8ea` before the battery ran. Instrument:
`python3 -m tools.company_data_contract_battery`. Results file:
`/var/tmp/company_data_battery_57034257af20.json`.**

---

## Read this before the table: the reducer was wrong and the cells were not

This subject was scored twice. The first run (fingerprint `ad4a2adfcc3d`) printed
`SURVIVED ALL 4 CALLER SUITES: [M1..M7]`. The subject has **three** callers; the fourth suite in
that population was the subject's own dedicated tests, and it is what struck M8–M10 off the list.
Cause and repair:
`SEAT_FINDING_THE_BATTERYS_OWN_SPEC_ENTERED_THE_SUBJECTS_TESTS_INTO_THE_CALLER_VERDICT_2026-09-06.md`.

Everything below is the **re-run under the corrected spec** (`57034257af20`), from scratch — the
engine refused to resume the old file, which is the fingerprint guard working on its first live
application to a spec change. The reducer was **not** recomputed by hand over the kept rows:
recomputing a verdict by hand over rows a different spec recorded is the same act as resuming them,
and this instrument has already published one verdict no run produced.

Both runs agree cell for cell — forty per-suite outcomes, every floor, identical. **What changed is
what the machine says those cells mean, and that is the whole of the difference between eight
unproved contracts and ten.**

## The floors, which ran first and are what make the table mean anything

| round | result |
|---|---|
| BASELINE | all four green at HEAD — 61 / 18 / 95 / 16 passed, 0 reds to deselect |
| POISON (`Exception` at import) | the repair suite **RED**. **All three caller suites GREEN.** Both controls (`test_delivery_lane`, `test_atom_notes_store`) **GREEN** |
| HARD POISON (`BaseException`) | all three caller suites **still GREEN** — genuinely blind, none swallows |
| NULL (behaviour-preserving edit) | all four **behaviour only** — no suite grades this module's text |

## The ten contracts

| id | contract | 3 callers | repair suite | predicted? |
|---|---|---|---|---|
| M1 | an EMPTY mix is unavailable, never a zero mix that reads as a DOMESTIC book | all survived | survived | yes |
| M2 | a mix with no positive revenue is unavailable | all survived | survived | yes |
| M3 | unclassified revenue stays in the denominator | all survived | survived | yes |
| M4 | the DOMINANCE threshold is what makes a book non-domestic | all survived | survived | yes |
| M5 | a genuinely MIXED book says mixed | all survived | survived | yes |
| M6 | a segment divides by ITS OWN n, never the whole-book denominator | all survived | survived | yes |
| M7 | account counts come from the `segment` field, not an id substring | all survived | survived | yes |
| M8 | the cost-to-serve distribution fails closed on an empty sample | all survived | **DIED** | yes |
| M9 | the arrears distribution fails closed | all survived | **DIED** | yes |
| M10 | gross arrears exposure is a FLOOR, not a net | all survived | **DIED** | yes |

**Forty mutation cells: forty as predicted.** The three kills are the three the pre-registration
named, by the three test functions it implied — `test_fail_closed_on_empty_sample_r15`,
`test_arrears_fail_closed_on_empty_ledger_r15`,
`test_arrears_gross_exposure_is_positive_only_floor`.

## The one prediction that was refuted, and it is the floor

The pre-registration named S4 — `tests/background/test_process_run_complete.py`, 95 tests, 65s,
driving `prc._process()` eleven times — as **the uncertain cell and the reason the second floor
exists**:

> S4 is the uncertain cell … green under the first floor whatever happens (its call site catches
> it), and I predict **RED under the second** — reaches and swallows.

**Wrong.** S4 is green under both floors. It is blind, not swallowing, and so are the other two.
**Zero of three callers swallow. The shape the second floor was built to catch does not occur on
this subject.**

The mechanism is not a mystery and it is not anybody's carelessness.
`tests/background/test_process_run_complete.py` monkeypatches the caller's own wrapper out of
existence in three fixtures — `:374`, `:439`, `:523`:

```python
monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
```

so the function body holding `from tools.generate_company_data import …` never runs at all. The
comment beside it gives the reason and the reason is correct:

> `generate_dashboard_json` writes to the REAL `site/data/dashboard.json` (hardcoded path inside
> `generate_dashboard_data.py`) — mock it to avoid corrupting the live dashboard

The pre-registration fixed what this would mean before it was known, and it stands:
**`generate_dashboard_json`'s company leg is covered by nothing in `tests/background/`.**

**The round that refuted its own reason is still the round that made the answer readable.** The
first floor left three greens the call sites could have produced two entirely different ways —
never reached, or reached and swallowed — and on the four previous subjects the engine would have
stamped all three `NEVER REACHES` and moved on. Here that stamp is *earned* rather than assumed,
because a floor those `except Exception` handlers demonstrably cannot catch produced the same
green. **A control that comes back with the answer you did not predict, on a question you could not
otherwise have settled, is the control working.**

## What this subject establishes that the four before it did not

`ops_repo` was the sweep's first REACHABLE-and-unproved column: three callers, all reaching, zero
kills. This is its opposite and the pair is the point.

The subject's premise expired nine days ago. It was ranked for having **zero test importers**;
`cbd5f6298` gave it `tests/tools/test_generate_company_data.py`, 16 tests, dedicated. That
reclassification is true, and **it moved the evidence on the converged surface by exactly nothing.**

M1–M7 are `segment_revenue_mix` and `_book_mix` — the converged surface, the one thing two separate
callers import. All 16 tests in the dedicated suite are about `_cost_to_serve_distribution` and
`_arrears_distribution`; not one names the mix. So the suite proves precisely the three contracts
**no caller shares**, and none of the seven the convergence is made of.

**A dedicated suite is not evidence about a converged surface. It is evidence about whatever it was
written for** — and `converged_contract_screen` counts importers, not what they import. Its
"1 direct importer / DEDICATED" row for this subject is accurate and points at a body of coverage
disjoint from the surface the screen exists to rank. That is a screen finding, and it is the second
one this sweep has produced about the instrument that selects its own subjects.

Five subjects in, the load is carried by the floor every time. Not once has a survivor column been
the interesting number.

## What this does not establish

* **Three callers is the whole first-party caller population**, so there is no sampling bound to
  declare. But the screen is a proxy, blind to callers reached by subprocess or dynamic dispatch.
* **Ten contracts is what I chose to write down, not the module.** Ten green rows are ten
  contracts.
* **The two `except Exception` call sites are not proved correct.** The second floor showed that no
  suite runs them; that is the opposite of showing they swallow properly. `process_run_complete`'s
  and `generate_world_data`'s guards are untested, which is not a claim that they are wrong.
* **`tests/tools/test_website_integrity_fix.py:379` actually calls
  `prc.generate_dashboard_json(tmp_path / "run.json")`** — the one suite in the tree that drives
  this call site for real. It is outside the graded population, and the pre-registration named it
  **in advance** as the next place to look if the caller columns came back empty. They did. Whether
  it carries any evidence about this subject is **not answered here** and is the next measurement,
  with its prediction to be written before it runs.

## Next

`tools/run_phase3b_recalibration.py` is the last ranked subject. Ahead of it:
`segment_vocabulary` and `grid_intensity_feed` carry the same mixed `survived_all` population this
subject's spec had, and `fuel_mix`'s result is already published — the caller-population answer
there is ten of ten, not eight of ten. Auditing those two beats adding a sixth subject.
