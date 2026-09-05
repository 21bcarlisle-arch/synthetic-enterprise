**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: which suite is each `segment_vocabulary` contract standing on?

**Written 2026-09-05 by the delivery seat BEFORE the battery ran, in the shared tree at
`1cfc48c01`. Claim id `register-low-water-evidence-convergence-sweep`. The predictions below are
kept unrevised beside the result whatever they score — a prediction filed after the answer is not a
prediction.**

---

## Why this subject, and what makes it different from the two before it

The sweep has three subjects behind it and each showed a different shape:

* `background/register_low_water.py` — four caller suites, one contract proved by **nobody**, two
  proved by **one**.
* `background/ops_repo.py` — three callers and **no test importer at all**; every caller's suite
  patched the shared function by name in the caller's own namespace.
* `simulation/run_phase3b_recalibration.py` — six callers, zero direct importers.

Those are all *thinly named* modules. `simulation/segment_vocabulary.py` is the opposite case and
that is the reason to run it next: **8 callers, 3 direct importers, 321 reaching suites**, and the
three direct suites are visibly thorough — `test_segment_case_normalisation.py` alone has explicit
legs for the unknown-string refusal, the cohort refusal, the absent-default, `default=None`, and
`is_business` case-insensitivity.

So the question here is NOT "is this covered". It is the sweep's actual question, which is
different: **where does the proof physically live, and does any of the 8 callers' own suites hold
any of it?** A module can be well proved and still have all of its proof in one room.

## The screen's `direct` column is confirmed by hand, and the grep is wrong the way it predicts

`grep -rln segment_vocabulary tests/` returns **4** files. The screen says **3**. The extra file is
`tests/tools/test_segment_case_guard.py`, and it is not an importer: every occurrence is either
prose, a string assertion (`assert "segment_vocabulary" in messages[0]`), or a *synthetic* module
the fixture writes into a temp tree (`_write(canon, "segment_vocabulary.py", source)`). It cannot
execute a line of the real module.

That is the upper-bound failure the screen's own finding names, live and independently reproduced.
**It is excluded from the battery**, because including it would score a suite that cannot fail for
this subject — the mistake the previous turn caught only after running it.

## The nine suites, and how they were chosen

**Direct (3)** — they import the real module:

| suite | |
|---|---|
| `tests/simulation/test_segment_case_normalisation.py` | the dedicated suite |
| `tests/sim/test_w2_15_segment_vocabularies.py` | the three-vocabularies seal |
| `tests/simulation/test_served_segments_curriculum.py` | imports `CANONICAL_SEGMENTS` only |

**Caller-primary (6)** — one suite per calling module, the suite named for it. This mirrors the
`register_low_water` battery, where each caller contributed one suite:

| caller | suite |
|---|---|
| `simulation/arrears_engine.py` | `tests/simulation/test_arrears_engine.py` |
| `simulation/live_population.py` | `tests/simulation/test_live_population_seam.py` |
| `simulation/payment_behaviour_source.py` | `tests/sim/test_w2_11_payment_behaviour_source.py` |
| `simulation/population_draw.py` | `tests/simulation/test_population_draw.py` |
| `simulation/segment_debt_obligation.py` | `tests/sim/test_segment_debt_obligation.py` |
| `simulation/sme_distress.py` | `tests/sim/test_w2_6_sme_distress.py` |

**A stated bound, not a silent one.** The callers are named by far more suites than these — 16 for
`arrears_engine`, 27 for `population_draw`, 79 mentions in total. One suite per caller is a
**sample, not a census**, and a survivor below therefore means "not killed by the suite that carries
this caller's name", never "not killed by anything in the tree". The seventh caller,
`simulation/sme_payment_behaviour.py`, has exactly one suite and it is
`test_segment_case_normalisation.py` — already in the direct set, so its row would be a duplicate
and it is not run twice. The eighth caller, `tools/segment_case_guard.py`, is the AST guard whose
suite is the non-importer excluded above.

## The seven mutations

Each applied **alone**, target string asserted present **exactly once** before patching,
`__pycache__` cleared between runs, every suite run **separately**. A survivor is otherwise
indistinguishable from a patch that never applied, which has happened here before.

| # | Contract attacked | the mutation |
|---|---|---|
| M1 | a `CompanyBookLabel` (V2) always raises | drop the `isinstance` refusal |
| M2 | `default=None` makes absence an error | return `RESIDENTIAL` instead of raising |
| M3 | a non-string raises | return `default` instead of raising |
| M4 | a PRESENT-but-unknown segment raises, never falls back | return `default` on `KeyError` |
| M5 | lookup is case-insensitive | drop `.casefold()` from the key |
| M6 | `"ic"` is an I&C alias | remap `"ic"` onto `RESIDENTIAL` |
| M7 | `BUSINESS_SEGMENTS` is SME **and** I&C | drop I&C from the tuple |

M4 and M5 are the two that matter: **M5 is the original C5/C6 defect restored** (an `"SME"` bill
matching no lower-case literal) and **M4 is the silent-fallback-to-`resi`** the module's
`UnknownSegmentError` docstring says it exists to remove. M6 is the same mis-route reached through
the alias table instead of the case rule.

## Predictions, per mutation

Graded from reading the three direct suites' bodies and the caller suites' names only. The previous
turn scored 3/7 and every miss came from grading a suite by what its tests were *called* — recorded
here so the same error is visible if it repeats.

| # | prediction |
|---|---|
| M1 | dies in **w2_15 only** (`test_the_seal_holds_for_every_label`, `test_the_refusal_survives_a_default`) |
| M2 | dies in **normalisation only** (`test_absence_can_be_made_an_error`) |
| M3 | **survives all nine** — no leg anywhere passes a non-string |
| M4 | dies in **normalisation + w2_15** |
| M5 | dies in **normalisation + w2_15**, possibly `served` (`test_a_served_segment_survives_in_any_spelling`) |
| M6 | dies in **normalisation + w2_15** |
| M7 | dies in **normalisation + w2_15** — but NOT via w2_15's `test_the_vocabulary_is_sourced_not_re_declared`, which compares `sme_distress.BUSINESS_SEGMENTS` to `vocab.BUSINESS_SEGMENTS` and moves with the mutation on both sides |

### Two standing predictions

1. **Every one of the six caller-primary suites kills nothing, for all seven mutations.** If it
   holds, this module is the `generate_company_data` shape at a *well-proved* subject: 321 suites
   reach it, 3 name it, and 100% of the proof is in the room those 3 occupy. A caller could be
   re-pointed at a different normaliser and its own suite would not notice.
2. **At least one contract survives all nine suites** — M3 is the nomination, and the `register_low_water`
   precedent (M1 there, proved by nothing) says the survivor is usually the type/error branch nobody
   drives.

### The M7 sub-prediction is the interesting one and is called out separately

`test_the_vocabulary_is_sourced_not_re_declared` asserts
`tuple(sme_distress.BUSINESS_SEGMENTS) == tuple(vocab.BUSINESS_SEGMENTS)`. If `sme_distress` really
does source the tuple from `vocab`, **both sides of that assertion move together under M7 and the
test cannot fail** — a convergence tautology, and the R15 catalogue's "same number by opposite
routes" shape reached from a third direction. The prediction is that M7 dies in w2_15 anyway, via
`test_the_lowercase_spelling_no_longer_raises`, which asserts `is_business_segment("i&c") is True`
against a literal. **Whether the sourcing test can fail at all is a separate question from whether
M7 is caught**, and the battery answers both because it reports the killing test by name.

## What this run will not establish

Whether some suite outside the nine kills a survivor. With 321 reaching suites the honest position
is that a survivor here is a statement about the named rooms, not about the tree — and a contract
proved incidentally by a suite that never names the module is the same fragility one file further
away, so the repair would stand either way.
