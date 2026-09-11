**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: a converged module's BEHAVIOUR is proved everywhere and its REFUSALS only where it is named — and two of the four caller kills prove nothing at all

**Result document. The pre-registration is
`docs/staging/records/SEAT_PREREG_WHICH_SUITE_PROVES_THE_SEGMENT_VOCABULARY_CONTRACTS_2026-09-05.md`,
written before the run and kept unrevised beside this — a staging daemon moved it from the root into
`records/` mid-turn, which is that room's ordinary behaviour and not a loss. It scored 3 of 7 on the room sets, its
loudest standing prediction was REFUTED, and the refutation is worth more than the prediction was.
Claim id `register-low-water-evidence-convergence-sweep`. Battery run in a `git archive HEAD`
extract at `1cfc48c01`; the subject and all nine suites are byte-identical to `origin/main`, so the
result holds either side of the merge landed this turn.**

---

## The battery

`simulation/segment_vocabulary.py`. Seven mutations, each applied **alone**, target asserted present
**exactly once** before patching, `__pycache__` cleared between every run, all nine suites run
**separately**. Baseline: **312 passed**, nine of nine green — which is what makes the extract a
valid instrument rather than an assumption.

| # | contract attacked | direct suites | caller suites |
|---|---|---|---|
| | | norm · w2_15 · served | arrears · livepop · pay_src · popdraw · debt_obl · sme_dist |
| M1 | a `CompanyBookLabel` (V2) always raises | · **DIED** · | — none — |
| M2 | `default=None` makes absence an error | **DIED** · · | — none — |
| M3 | a non-string raises | · · · | — none — |
| M4 | a present-but-unknown segment raises | **DIED** · **DIED** · **DIED** | — none — |
| M5 | lookup is case-insensitive | **DIED** · **DIED** · **DIED** | **DIED** · **DIED** · **DIED** · · · **DIED** |
| M6 | `"ic"` is an I&C alias | **DIED** · **DIED** · **DIED** | — none — |
| M7 | `BUSINESS_SEGMENTS` holds I&C | **DIED** · **DIED** · | · · · · · **DIED** |

## The standing prediction was refuted, and then the refutation half-collapsed on inspection

I predicted **every one of the six caller suites kills nothing**. Four of them killed something. On
the face of it the sweep's running hypothesis — proof concentrates in the room that names the module
— is simply wrong at this subject.

**It is not, and the reason is the finding.** Reading *which test* did the killing splits the four
callers in two:

* **arrears** and **livepop** killed M5 with genuine segment assertions —
  `test_payment_method_ic_chaps_threshold`, `test_payment_outcome_bacs_ic_can_dispute`,
  `test_a_suspended_segment_never_reaches_the_book`. Those are real caller-side proof of the
  vocabulary's behaviour, and they are the honest refutation of my prediction.
* **pay_src** and **sme_dist** killed M5 and M7 with nothing but **golden-output and determinism
  tripwires**: `test_advancing_pbs_leaves_sme_distress_byte_identical`,
  `test_advancing_distress_leaves_population_draw_byte_identical`,
  `test_advancing_distress_does_not_perturb_global_random`,
  `test_deterministic_replay_survives_intervening_global_rng_use`. Every one of those fires on **any**
  perturbation of the world's output. None of them mentions a segment.

**A mutation killed by a byte-identity test is DETECTED, not PROVED.** That kind of test cannot tell
a defect from an intended improvement — it goes red for both, and the correct response to it is
often to re-bless the golden file. Counting it as evidence that a caller proves the contract is the
`reaching`-column error moved one level down: last time the miscount was suites that never name the
module, this time it is *kills* that never name the contract. So the corrected score is **two**
caller suites hold real proof, not four — and the six-caller prediction was wrong for two of them
and right, in substance, for the other four.

## The shape this subject actually has, and it is a new one for the sweep

Sort the seven contracts by whether breaking them changes what the world DOES:

* **Behavioural** — M5 (the case rule), M6 (the alias), M7 (the business tuple). Break one and bills
  route differently, so they are caught in three to seven rooms, callers included. **M5 died in
  seven of nine.** These are over-proved, not under-proved.
* **Refusals** — M1 (the V2 seal), M2 (`default=None`), M3 (non-string), M4 (unknown-string). These
  are the contracts the module *exists* to hold. Every one of them died **only in rooms that import
  the module by name**, and **zero** caller suites caught any of the four.

That is the general statement, and it is sharper than the one the sweep started with:

> **A refusal has no output signature, so no golden, determinism or end-to-end test can ever catch
> its removal. Convergence concentrates refusals into one module; the proof of a refusal can
> therefore only ever live in a suite that names that module — and the count everybody reads
> (321 reaching suites here) is guaranteed to be blind to exactly the contracts that matter most.**

The previous subjects showed proof concentrating by accident of which caller happened to have
strong tests. This one shows it concentrating **by construction**, for a whole category of contract,
and no amount of caller-side testing will ever move it.

## M3 was proved by nothing, and is now proved

`if not isinstance(segment, str): raise UnknownSegmentError(...)` → `return default` **survived all
nine suites**. A tree-wide search finds `None` as the only non-string ever passed to
`normalise_segment`, and `None` is caught by the *absence* branch one line earlier — so the guard
was driven by nothing anywhere, not merely by nothing in the nine rooms.

**Said precisely.** The shipped code is CORRECT and nothing is mis-reporting today, which is why
this is LATENT. What the battery establishes is that the contract was held in place by nothing: any
edit trading that guard for `return default` would have been caught by no test in any of the nine
suites. The branch is reachable — every call site reads `bill.get("segment", "resi")`, a bill is
built from JSON, and a malformed feed hands this a number or a list — and the failure it would open
is the original C5/C6 mis-route: every non-string silently becoming a household.

**Repair:** two legs in the module's own suite,
`tests/simulation/test_segment_case_normalisation.py` — seven parametrised non-string cases and one
asserting the refusal survives a default in hand, because absent and wrong are different and only
the first has a defensible default. Confirmed by re-running the battery: M3 now **DIES** there with
8 failures, and the unmutated suite is green at 49 passed (was 41). No new file: the dedicated suite
is where the contract lives, and a second file would be a control guarding a control. The suite
already asserts at length that real strings normalise, so it cannot pass vacuously.

## A control that cannot fail, found by the battery and NOT repaired here

`tests/sim/test_w2_15_segment_vocabularies.py::test_the_vocabulary_is_sourced_not_re_declared`
asserts `tuple(sme_distress.BUSINESS_SEGMENTS) == tuple(vocab.BUSINESS_SEGMENTS)`. But
`sme_distress.py:122` reads `BUSINESS_SEGMENTS = tuple(_vocab.BUSINESS_SEGMENTS)` — the left side is
*derived from* the right, so both move together and the equality cannot fail.

**Proved, not argued:** M7 empties I&C out of `vocab.BUSINESS_SEGMENTS`, and under M7 that suite
reported exactly **one** failure — `test_the_lowercase_spelling_no_longer_raises`, which asserts
against a literal. The sourcing test passed through a mutation that gutted the very tuple it claims
to check. That is the pre-registration's M7 sub-prediction, **CONFIRMED**.

It is filed rather than fixed because the contract itself is not at risk (M7 dies in two rooms
anyway) and the honest repair is a real design question, not a one-liner: equality can never
distinguish "copied from the canon at import" from "coincidentally equal literals", so the property
wants a source-level check — and `tools/segment_case_guard.py` already AST-scans `simulation/` for
exactly that class. **The next hand should ask whether that test is redundant with the guard rather
than write a third mechanism.**

## Scoring the pre-registration: 3 of 7, and the misses run the opposite way to last time

- **M1 dies in w2_15 only — RIGHT**, and via the two tests named.
- **M2 dies in norm only — RIGHT.**
- **M3 survives all nine — RIGHT.** The nomination held, and it was the one that mattered.
- **M4 — WRONG.** Predicted norm + w2_15; `served` killed it too, via
  `test_a_curriculum_typo_serves_everyone_rather_than_no_one`.
- **M5 — WRONG, and badly.** Predicted two rooms, possibly three. It died in **seven**.
- **M6 — WRONG.** Predicted two; `served` made three.
- **M7 — WRONG on the room set** (sme_dist killed it), **RIGHT on the sub-prediction** that w2_15's
  sourcing test would not be the killer.

Last turn's three misses all came from *under*-reading suites — grading them by their test names.
These four are the mirror: I under-estimated how far a behavioural change propagates, because I was
reasoning about which suites *discuss* segments and not about which suites would notice the world
moving. **Both errors are the same error** — grading a suite from its subject matter instead of from
what its assertions actually touch — and it is now the second thing this sweep has caught itself
doing twice.

## Two things confirmed about the instrument, by hand, at two subjects

The screen's `direct` column was re-derived by hand and the grep over-counts at **both** subjects,
exactly as its own finding predicts:

* `segment_vocabulary` — grep says 4 test files, screen says 3. The extra,
  `tests/tools/test_segment_case_guard.py`, mentions the name only in prose, in a string assertion,
  and in a *synthetic* module its fixture writes into a temp tree. **Excluded from the battery**, so
  it could not be scored as a suite that cannot fail for this subject.
* `tools/generate_grid_intensity_feed` — grep says 5 test files, screen says 2. Three of the five
  contain no import of it at all.

## What this run does not establish

Whether a suite outside the nine kills a survivor. With 321 reaching suites, "nothing else covers
M3" is not claimed from the battery — it is claimed from the tree-wide search for a non-string
caller, which is a different and weaker instrument (a dynamic or `**kwargs` call site would be
invisible to it). The repair stands either way: a contract proved incidentally somewhere else is the
same fragility one file further away.

The six caller-primary suites are **one suite per caller, a sample and not a census** — the callers
are named by 79 suites in total. A "no caller killed this" row means the suite carrying that
caller's name did not kill it.

## Housekeeping this turn, recorded because two of them are small findings

1. **The merge landed and the five-path conflict is spent.** `c69089f22`, by
   `surgical_land --merge origin/main` from the shared tree. The BLOCKING finding of 2026-09-05
   (*"a five-path conflict nothing unattended will resolve"*) described a state at 5-ahead/32-behind
   that no longer exists: `git merge-tree` now writes a tree with **no conflicts**, and the merge
   re-derived `CLASS_NO_CALLER_AND_NEVER_RUNS` on the way through. **That finding can be archived.**
2. **`origin_reconcile.advance_shared_tree` reports success for the opposite direction.** Called on a
   tree that is 0 behind and **5 ahead**, it returns
   `{"advanced": True, "reason": "fast-forwarded onto origin/main with nothing in the way"}` and
   pushes nothing. The wording reads as "this tree reached origin" to anyone who has not read the
   body; it means only that the *pull* leg had nothing to do. This is the
   `surgical_land`-never-pushes shape at a second site, and the habitual `HEAD..origin/main` check
   is empty either way. LATENT; the fix is one sentence of reason text, not a behaviour change.
3. **The claim was not held.** `delivery_lane --landed register-low-water-evidence-convergence-sweep`
   answered *"bound NOTHING … it is NOT CLAIMED"*. The store holds one unrelated id. This is the
   already-filed "drawn from `focus:` with no claim at all" state — the bind is inert and the work
   is unbound however much lands, so the paths in this turn's commit are recorded here instead.

## Where the sweep goes next

`tools/generate_grid_intensity_feed` (8 callers, 2 direct) was drawn with this subject and **was not
run** — one battery per subject is the honest unit and this one produced a class statement worth
writing down properly. Its `direct` count is confirmed above, so the next hand starts at the
mutation list rather than the population.

**And it should attack refusals first.** That is the transferable result: at a converged module, the
behavioural contracts look after themselves and the refusals are where a battery earns its cost.
