**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A concept link would have surfaced none of the three repeat-defect families (2026-11-14)

*Answers `DIRECTOR_STEER_WOULD_LINKING_FINDINGS_TO_CONCEPTS_HAVE_CAUGHT_OUR_REPEAT_DEFECTS_MEASURE_IT_2026-11-14`.
The prediction was filed first:
`SEAT_PREREGISTRATION_WOULD_A_CONCEPT_LINK_HAVE_SURFACED_THE_EARLIER_FINDING_2026-11-14.md` (same folder).*

## Answer

**0 of 3 families caught, in every reading. By the steer's rule, drop it.** No concept-link field, no
orientation line, no store and no gate.

| Family (members) | Strict, A | Strict, B | Hindsight, A | Hindsight, B |
|---|---|---|---|---|
| VAT (16) | 0/14 | 0/14 | 0/14 | 1/14 |
| Half-month DD / stub period (4) | 0/3 | 0/3 | 0/3 | 0/3 |
| Bill shock (9) | 0/8 | 0/8 | 0/8 | 1/8 |

**What the readings mean.**
- *Strict* uses the register as of each later finding's date, from git. *Hindsight* uses today's
  register.
- *A* tags on the filename and H1 title. *B* adds the first 1,500 characters of the body.
- A later finding counts as *caught* when an earlier member, filed on a strictly earlier date, shares a
  concept tag with it. The tagger is `tools/the_map._terms` and `_term_pattern`, the module search's
  own matcher.

**What the two hindsight-B catches go through.** Both are noise.
- One VAT finding is caught through `build.mutation`, which lists 230 items by its date.
- One bill-shock finding is caught through `collect.payment_method`, which lists 19.

Neither concept is the family's subject.

## Why

The strict reading is 0 by construction: the register was created on 24 Oct (ebc3c34e2e), and every
member of all three families predates it. The hindsight reading is the real test, and it fails
anyway. **Today's register has no concept for VAT, for bill shock, or for the first direct debit's
period.** A repeat defect repeats because its subject was never named as one thing, and a link to a
concept cannot surface a subject the register does not hold.

Each family's own word, searched as plain text, finds every member: `VAT` in a filename returns all 16.
So the memory these cases lacked was not a link. It was a single concept with its homes declared. The
register already has the mechanism for that: one home per layer, with the second-home check. The
lever is minting concepts for subjects that have already repeated. That needs no new field and no new
store.

## Prediction against result

| Family | Predicted (hindsight A / B) | Result (A / B) |
|---|---|---|
| VAT | not / not | not / not |
| Half-month DD | not / **caught** | not / **not** |
| Bill shock | not / not | not / not |

**The half-month text-B prediction was wrong.** None of the four members uses the register's
direct-debit labels ("dd amount", "direct debit review", "setting the direct debit amount") in its
opening 1,500 characters. The overall call (0 of 3, drop) held.

## Coverage and precision (today's register)

- **Coverage.** 3,735 dated staging items under `docs/staging/**`. Text A tags **297 (8.0%)** and text
  B tags **1,012 (27.1%)**.
- **Precision.** A hand-checked sample of 30 (item, concept) pairs from text A, seed 20261114:
  **25 of 30 correct (83%)**.
  - Three of the five misses are rung names (R1, R3, R4) matching `settle.reconciliation_run`.
  - One is a machine LAUNCH-UNLANDED record tagged `tariff.default_tariff`.
  - One is a worktree report tagged `build.dead_code`.

## Corrections to the steer's facts

- **71 concepts, not 76.** Read today from `docs/design/the_map/concepts.yaml`.
- **The ~4% count holds.** 200 of 4,730 files in `docs/staging/*.md` plus `done/*.md` carry a leading
  `**Knowledge:**` line, which is 4.2%. The steer said 199 of 4,720.

## Netflix original

`netflixtechblog.com/ontology-driven-observability-building-an-end-to-end-knowledge-graph-at-netflix-scale-421392cf5adf`
returned **403**, so the original is unread. The vendor post reports **no** before/after figure: no
accuracy, no change in time-to-root-cause and no incident count. Its one number is a "four hours"
example investigation, which is a baseline. The vendor presents "the ontology gradually stops being a
schema and starts being a memory" as an elided Netflix quote. That could not be checked against the
original.

## Limits

- The family selection uses the family's own word in a filename. That favours finding members. It
  does not favour the tagger, which never sees the selection term unless a concept carries it.
- The precision sample is text A only.
- The probe script ran from `/tmp` and was not kept. Its whole method is stated above, and it reuses
  `tools/the_map` unchanged.
