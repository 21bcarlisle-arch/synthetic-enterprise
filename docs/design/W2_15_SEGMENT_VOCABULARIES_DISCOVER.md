# W2_15 — one vocabulary, or three? (DISCOVER)

**Atom:** `W2_15_segment_case_sensitivity_siblings` · lane `W2_customer_generator` · epoch 2 · L0→L2
**Queued from:** the `W2_sme_segment_case_normalisation` build (2026-08-08), under SELF-INTERRUPT
DISCIPLINE — found, not fixed on sight, because it was outside that atom's `file_scope`.
**Status:** DISCOVER answered; the answerable half is mechanised. See "What is NOT closed".

---

## The question

`W2_sme_segment_case_normalisation` closed a class: a market-segment string compared in the wrong
CASE silently mis-routed a customer (C5/C6, two real microbusinesses, were billed as households for
the entire history). It shipped `simulation/segment_vocabulary.py` as the canon and
`tools/segment_case_guard.py` as the R10 class closure.

That build then found three things it could not touch, and the DISCOVER question was whether they
are **one vocabulary that drifted** — in which case the work is a merge — or **several vocabularies
that were never the same thing** — in which case the work is a named seam, and merging them would
destroy a measurement.

**The answer is: one drift and two genuine seams.** Both halves matter. A reader who concludes
"three rival spellings, tidy them into one" deletes the belief-vs-truth gap C11 is scored on; a
reader who concludes "they're all separate, leave them" leaves a latent crash in the SME twin.

---

## The three vocabularies

| | V1 — world-true market segment | V2 — company-observed book label | V3 — population cohort id |
|---|---|---|---|
| Owner | `simulation/segment_vocabulary.py` | `simulation/segment_debt_obligation.py` | `simulation/segments.py` |
| Spellings | `resi` / `SME` / `I&C` | `resi` / `sme` / `iandc` | `resi_standard`, `sme_smart`, `gas_resi`, … |
| Means | what the customer **is** | what the company **recorded** | which tariff/meter/fuel **cohort** they were drawn into |
| May be wrong? | no — it is the answer key | **yes, deliberately** | n/a — different axis |
| Case-safe? | via `normalise_segment()` | by construction (`_norm` lower-cases first) | n/a |

V1 and V2 look like the same three concepts spelled differently. They are not. **V2 is allowed to
disagree with V1 about a specific customer** — `observed_segment()` mis-records a share of accounts
at onboarding, and the whole W2_9/C11 coupled triad exists to measure the resulting fraction of
accounts on the wrong debt T&C. Coercing V2 onto V1 would make the company's belief equal to the
truth by construction: a tautology in exactly the R15 sense, and it would silently zero the gap
rather than turn anything red.

V3 was already sealed by the previous build (`normalise_segment` rejects a cohort id rather than
guessing that `sme_standard` means `SME`); this atom only added a test that the rejection is not an
accident of spelling.

---

## Finding 1 — `sme_distress` was drift. Merged.

`simulation/sme_distress.py:112` declared `BUSINESS_SEGMENTS: Tuple[str, ...] = ("SME", "I&C")` —
the same two strings as the canon, spelled the same way, but a **second declaration of a vocabulary
that already had an owner**. `is_business_segment` tested membership with a bare `in`, which is
case-SENSITIVE, and `generate_business_distress` **raises** on a non-match:

```
>>> sme_distress.is_business_segment("sme")     # before
False
>>> sme_distress.generate_business_distress(customer_id="C1", segment="sme", ...)
ValueError: segment 'sme' is not a business segment ('SME', 'I&C')
```

This was LATENT, not live: every caller today spells it canonically, so nothing is mis-billed. It is
also a *different* failure mode from the original defect — a **crash**, not a silent mis-route.
Louder, but not better: it would have taken down the twin for a real microbusiness the first time an
upstream feed spelled the segment its own way, which is precisely what `saas/smart_meter_rollout`
already does elsewhere (`IC`, no ampersand).

**Fixed** by sourcing `BUSINESS_SEGMENTS` from the canon and routing the predicate through
`normalise_segment()`. An unrecognised segment stays `False` rather than raising, so the caller's own
error message — which names the residential life-event stream as the right home — survives.

## Finding 2 — `segment_debt_obligation`'s label sets are a seam. Sealed, not merged.

Its `_DOMESTIC_LABELS` / `_SME_LABELS` / `_IANDC_LABELS` are correct by construction (`_norm`
lower-cases before matching, so no spelling can take the wrong branch) and were therefore already
exempt from the segment-case class. The finding is not about its inputs but its **outputs**: it emits
`resi`/`sme`/`iandc` as V2, and nothing marked them as V2.

## Finding 3 — the trap, and why it is worse than "iandc raises"

`iandc` is not in `_ALIASES`, so `normalise_segment("iandc")` raises. The atom recorded this as "a
silent trap the moment anyone pipes one into the other". Measured, it is worse than that: the block
was only **partial**.

```
bare 'resi'  -> normalise -> 'resi'   SILENT COERCION
bare 'sme'   -> normalise -> 'SME'    SILENT COERCION
bare 'iandc' -> REFUSED (loud)
```

Two of the three V2 labels are also valid V1 aliases. A pipe from the company's book into the canon
would have run **green through any resi/SME population** and blown up the first time an I&C customer
appeared — a bug that hides behind test-population composition, which is the same shape as
`docs/staging/WORKER_FINDING_MUTATION_VALID_ON_ONE_SUBPOPULATION_ONLY_2026-08-09.md` and the
hardest kind to find later.

**Closed at the type, not the string.** `observed_segment()` now returns `CompanyBookLabel`, a `str`
subclass that carries the label's provenance out of the module that minted it; `normalise_segment()`
refuses the type as a class. It compares equal to the bare string, keys a dict, and serialises to
JSON unchanged, so C11 and the W2_9/C11 coupling are untouched — asserted against the real consumer
(`company.compliance.segment_debt_policy.select_debt_terms`), not a stand-in.

A string-based block could not have done this: `resi` and `sme` are legitimate V1 aliases arriving
from other sources, so there is no string to reject. Only the provenance distinguishes them.

---

## Finding 4 (new) — the guard was fail-open on a type annotation

Not in the atom's notes; found while testing whether the guard could see Finding 1.

The guard's constant-collection channel — the one its own docstring calls the back door, the one that
catches `_IC_SEGMENTS = ("ic", "I&C")` coming back — visited `ast.Assign` only. An **annotated**
assignment is `ast.AnnAssign`, a different node. So:

```python
_IC_SEGMENTS: Tuple[str, ...] = ("ic", "I&C")    # guard: clean, rc=0
_IC_SEGMENTS = ("ic", "I&C")                     # guard: 1 violation, rc=1
```

**Adding a type hint switched the control off.** This was not academic: the one real segment
vocabulary in `simulation/` was annotated, which is why the guard had never once looked at the
constant this atom is about. It reported `clean (83 files scanned)` the whole time.

R15 names three killer patterns; this is a fourth shape of FAIL-OPEN worth writing down — **a
control keyed to one syntactic form of a construct that has two**. The guard was not wrong about
what to look for, only about where that thing is allowed to live in the tree. Closed by
`visit_AnnAssign`, with the annotated/bare pair asserted to agree for every shape the guard claims.

---

## What the guard can and cannot see (stated, not left to be inferred)

The atom's own note was right that an AST scan cannot catch Finding 1's defect: the defect is in the
COMPARISON, and seeing that a name compared with `in` was built from literals 240 lines earlier needs
dataflow the scan does not do. Saying so is required — otherwise the guard's green reads as coverage
it does not have.

But the scan is not helpless here. What it CAN see is the **private copy that makes the unsafe
comparison possible**. Remove the copy and the comparison has nothing case-sensitive left to compare
against; keep it and the class regenerates. So the guard now flags a collection of ≥2 canonical
segment literals declared outside the canon module, and the honest framing is that this is a
*proxy* for the comparison defect, chosen because it is the reachable half.

**STILL NOT COVERED — do not read a green guard as covering this:**

- a case-sensitive comparison against a vocabulary **imported by name** from another module;
- a vocabulary built at runtime (`tuple(x.upper() for x in ...)`);
- anything outside `simulation/` — the guard's root. `saas/` and `company/` are not scanned, and
  `tools/couple_w2_9_c11.py` compares `true_seg in ("sme", "iandc")` today. That is correct (it is
  V2, lower-case by construction) but it is correct **unguarded**.

The residual mitigation is the same one the canon module has always asked for: route segment tests
through `normalise_segment()`.

---

## Evidence

- `simulation/segment_vocabulary.py` — three-vocabulary docstring, `CompanyBookLabel`, the V2 refusal
  in `normalise_segment()`, and the comment pinning why `iandc` is deliberately absent from `_ALIASES`.
- `simulation/segment_debt_obligation.py` — `observed_segment()` returns `CompanyBookLabel`.
- `simulation/sme_distress.py` — `BUSINESS_SEGMENTS` sourced from the canon; case-insensitive predicate.
- `tools/segment_case_guard.py` — `visit_AnnAssign`; duplicated-vocabulary violation; limits documented.
- `tests/sim/test_w2_15_segment_vocabularies.py` (13 new) + `tests/tools/test_segment_case_guard.py`
  (13 -> 20). All 33 green.

**R15 mutation proof — four mutations run, all fire:**

| Mutation | Control that must fire | Result |
|---|---|---|
| `observed_segment` returns a bare `str` | the V2 seal | 2 failed (`provenance`, `seal_holds_for_every_label`) |
| delete `visit_AnnAssign` | the annotated-constant channel | 2 failed (`TestAnnotatedAssignment`) |
| delete the duplicated-vocabulary check | the copy proxy | 3 failed (`TestDuplicatedCanonicalVocabulary`) |
| restore `BUSINESS_SEGMENTS = ("SME","I&C")` + bare `in` | the merge | 2 failed, **and** the guard reports the violation on the restored file |

Guard on the real tree: `SEGMENT CASE GUARD: clean (84 files scanned)`, rc=0 — and it is now actually
looking at the constant it previously walked past.

## What is NOT closed (why L2, not L3)

- **COUPLED TRIAD.** The company has not been tested against a world that spells a segment
  adversarially. Until the belief-vs-truth gap is measured for a mis-spelled feed, no L3.
- **No HARDEN / Expert Hour** pass on this atom.
- The `saas/` and `company/` trees are unscanned, per the limits above.
