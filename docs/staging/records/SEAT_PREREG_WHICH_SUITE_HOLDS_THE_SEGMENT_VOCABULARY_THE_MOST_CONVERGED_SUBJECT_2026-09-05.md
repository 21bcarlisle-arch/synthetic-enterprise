**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: which suite holds the segment vocabulary, the most converged subject on the screen

**Written 2026-09-05, delivery seat, from an isolated worktree at `1cfc48c01`, BEFORE any mutation
is applied. Claim id `register-low-water-evidence-convergence-sweep`.**

The drawn direction is to ask the low-water question of every *other* converged mechanism: which
single caller suite is each shared contract standing on? Three subjects have been answered so far —
`background/register_low_water.py` (one contract proved by no suite, two by one),
`background/ops_repo.py` (nothing in `tests/` imported it at all), and
`simulation/run_phase3b_recalibration.py` (four shared contracts on one suite, and the caller that
documents the reuse proves none of it). Three is not a class. This is the fourth.

## The subject, and why it is next

`simulation/segment_vocabulary.py` — **8 first-party callers, 3 test files importing it, ~321
reaching it transitively.** It is the highest-caller row the screen ranks, and unlike the three
already answered it *does* have dedicated suites. That is the point: the screen ranks and does not
grade, and a subject with three dedicated suites is exactly where "has a suite" is most likely to
be mistaken for "each contract is proved".

It is also the subject with the most to lose. This module exists because two sim-side modules
compared segments case-sensitively and every real `SME` bill was billed as a household — C5 and C6,
silently, for the whole history. The repair was to make one normaliser the only sanctioned route.
**A repair that becomes the only route concentrates the risk: if a contract here is unproved, every
caller inherits the hole at once.**

## The callers, and the contract each one takes

| contract | callers that use it |
|---|---|
| `normalise_segment` | 4 direct — `arrears_engine`, `live_population`, `population_draw`, `sme_payment_behaviour` |
| `is_business` | 2 — `payment_behaviour_source`, `sme_distress` |
| `CANONICAL_SEGMENTS` | 2 — `live_population`, `tools/segment_case_guard` |
| `UnknownSegmentError` | 2 — `live_population` (catches it), `sme_distress` (catches it) |
| `_ALIASES` | 1 — `tools/segment_case_guard` (the guard IS the alias table) |
| `CompanyBookLabel` | 1 — `segment_debt_obligation` mints it; `normalise_segment` refuses it |
| `BUSINESS_SEGMENTS` | 1 — `sme_distress` re-exports it |
| the canonical spellings `SME` / `I&C` | 3 — `arrears_engine`, `population_draw`, `sme_payment_behaviour` |

## The battery

Nine mutations, each applied **alone**, with its target asserted present **exactly once** in the
source before the patch is applied — a surviving mutation that was never actually applied is the
failure mode this project has already filed. After each, all ten suites below are run
**separately**, and a mutation "kills" a suite only if that suite's own pass count changes.

    M1  normalise_segment: an unknown alias returns `default` instead of raising
    M2  normalise_segment: the CompanyBookLabel (V2) refusal is deleted
    M3  normalise_segment: `.casefold()` dropped from the lookup key (the original defect)
    M4  _ALIASES: the "ic" entry removed (the spelling saas/smart_meter_rollout declares)
    M5  _ALIASES: "iandc" ADDED (the entry W2_15 says is deliberately absent)
    M6  BUSINESS_SEGMENTS: I&C dropped, leaving (SME,)
    M7  is_business: compares the RAW segment, without normalising
    M8  SME: the canonical spelling changed to "sme"
    M9  CANONICAL_SEGMENTS: I&C dropped from the tuple

The ten suites, with their baseline measured before this document was written — **10 suites, 295
tests, all green, 51s**:

    tests/sim/test_w2_15_segment_vocabularies.py            13
    tests/simulation/test_segment_case_normalisation.py     41
    tests/simulation/test_served_segments_curriculum.py     32
    tests/tools/test_segment_case_guard.py                  20
    tests/sim/test_w2_11_payment_behaviour_source.py        44
    tests/simulation/test_population_draw.py                45
    tests/sim/test_segment_debt_obligation.py               14
    tests/sim/test_w2_6_sme_distress.py                     29
    tests/simulation/test_dd_collection_book.py             20
    tests/simulation/test_live_population_seam.py           37

The first four are the module's own; the other six are one suite per remaining caller.

## Predictions

Filed before the answer is known, and they will be kept beside the result whichever way it goes.

* **P1 — I predict the two dedicated vocabulary suites between them kill all nine**, and that at
  least six of the nine are killed by `test_segment_case_normalisation.py` alone. If that holds,
  the subject has the *opposite* shape to the three already measured: not an unproved contract, but
  a well-proved one whose proof is concentrated in one file.
* **P2 — I predict M4 (`"ic"` removed) is killed by NOTHING.** It is the only alias sourced from
  the *other side of the wall* — `saas/smart_meter_rollout.Segment` spells the corporate segment
  `IC` — and no sim-side test population contains that spelling. If it survives, the alias table
  has an entry that exists for a caller no test ever exercises.
* **P3 — I predict M6 (BUSINESS_SEGMENTS loses I&C) is killed by `test_w2_6_sme_distress.py`**
  (it re-exports the tuple as its own module constant) **and NOT by
  `test_w2_11_payment_behaviour_source.py`**, whose subject reaches the tuple only through
  `is_business`.
* **P4 — I predict M8 (`SME` respelled) kills the widest set — five or more suites** — because
  "SME" is the spelling every population carries. This is the one contract I expect to be
  over-covered rather than under-covered.
* **P5 — I predict `test_dd_collection_book.py` and `test_live_population_seam.py` kill nothing**,
  despite `arrears_engine` and `live_population` being two of the four `normalise_segment` callers.
  Both suites drive book-level arithmetic on populations that are entirely residential, so the
  segment branch they depend on is never taken with a non-resi value.

**If P5 holds it is the finding**, and it is the low-water shape again in a subject that looks
well covered: two callers converge on the normaliser, and their own suites cannot tell whether it
works.

## What this cannot establish

A mutation that survives every suite is either a missing test or an equivalence, and this document
does not get to assume the flattering one — each survivor is classified individually in the result,
with the reason named. And the ten suites are a *sample* of the ~321 that reach this module: a
mutation killed by none of these ten may still be killed by the eleventh. The claim is therefore
about which suites *hold* each contract, never that no test anywhere covers it.
