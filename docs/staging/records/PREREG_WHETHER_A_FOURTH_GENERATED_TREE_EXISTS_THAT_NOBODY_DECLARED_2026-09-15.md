# PREREG — does a FOURTH generated tree exist that nobody declared?

**Written 2026-09-15 by the delivery seat, BEFORE any directory was counted.** Lane 0, claim
`does-a-fourth-generated-tree-exist-that-nobody-declared`.

The five preceding frames all widened **how a path is spelled** (helper +8, signature default +9,
instance attribute +1, named segment +4, whole string +10). This asks the other half: not how a
path is spelled but **which trees are declared at all**. `GENERATED_TREES` has held three
`(parent, child)` pairs since it was written and nothing has ever asked whether three is the right
number.

---

## 1. Why this one is NOT the harmless shape the last one was

The whole-string frame provably could not move the commit gate: `offends()` decides a `file_scope`
entry by tree PREFIX, and every member `generated_artefacts()` can return already sits under one of
those prefixes, so `s in generated` is **subsumed**.

An addition to `GENERATED_TREES` is the opposite. It moves `_tree_prefixes()`, which is the
*subsuming* predicate — so **every `file_scope` entry under the new prefix starts offending at
once**, and `gate_violations()` refuses the commit for each one not in `FROZEN`. `FROZEN` was
measured on 2026-08-19 against exactly three prefixes. Widening the prefix set without
re-measuring the freeze makes the freeze read STALE and blocks **every lane's** commit, not just
this one's.

So the order is forced, and it is the reason this was carved out of the previous turn rather than
folded into it: census → candidate → re-measure `FROZEN` against the wider set → land both
together or land neither.

## 2. The instrument, and why it is not the obvious one

`generated_artefacts()` **cannot** answer this. It is keyed to `GENERATED_TREES` and returns only
paths under the three declared prefixes, so asking it where the undeclared generated trees are is
asking a question of the thing whose blindness is the subject. Using it would be a control that is
evidence about itself.

The tree-agnostic instrument is `_write_reached_paths()` — the raw write-site scan, which resolves
a destination from a write SITE (`.write_text`, `.write_bytes`, `open(..., "w")`, the destination
of an `os.replace`-shaped move) with no knowledge of which trees are declared. That is the set this
census is computed over.

## 3. What I am measuring

For every directory `D` in the repo, at every depth (so `docs`, `docs/observability`,
`docs/observability/scale_probe_10k` are three separate rows), over all files at any depth below:

- `tracked(D)` — files under `D` that git tracks.
- `reached(D)` — paths under `D` in `_write_reached_paths()`.
- `density(D) = |tracked(D) ∩ reached| / |tracked(D)|`.

And separately `|reached(D) - tracked(D)|` — write-reached paths git does **not** track. A
directory whose generated output is gitignored is still a generated tree, and a census keyed only
to tracked files would score it 0 and call it authored. That is a distinct failure mode from low
density and is counted separately rather than blended into one fraction.

**A constraint worth stating before it bites:** `GENERATED_TREES` members are exactly two segments.
A generated tree that is one segment deep, or three, cannot be expressed in that structure at all.
If the census's best candidate is not two segments, the finding says so rather than rounding it to
the nearest expressible thing.

## 4. The predictions

Each marked HELD or FALSIFIED in the finding, beside the result, whichever way it falls.

| # | Prediction |
|---|---|
| Q1 | The three declared trees all score `density ≥ 0.5`. **This is the calibration and it is the one I most expect to be wrong**: if a declared tree scores low, density is not what the declaration is tracking and the rest of this census is measuring the wrong quantity. |
| Q2 | Two-segment directories with `tracked ≥ 3` and `density ≥ 0.5` that are NOT under a declared prefix: **1**, accepting 0–5. |
| Q3 | At least one near-neighbour of a declared tree — a sibling sharing its first segment (`docs/*`, `site/*`) — appears in Q2's list. I name `docs/status` as the single most likely, because `LATEST.md` is described as live state and live state is written. |
| Q4 | For the strongest candidate, the number of NEW `gate_violations()` entries its declaration creates (live violations not in `FROZEN`) is **≤ 4**, accepting 0–15. If it is 0, the addition is free and lands on the strength of the census alone. |
| Q5 | **0** currently-`FROZEN` entries go stale. A widening of the prefix set can only ADD violations, never remove one, so every frozen pair stays live. If this is falsified my model of `offends()` is wrong and nothing else here should be trusted. |
| Q6 | At least one directory has `|reached - tracked| ≥ 5` — i.e. a materially gitignored generated tree — and it is NOT under a declared prefix. |
| Q7 | The highest-density undeclared directory in the whole census is **not** two segments. (Stated so the §3 constraint is a prediction rather than a caveat.) |

## 5. What I do with each answer

- **Q1 FALSIFIED** — stop. Density is the wrong instrument; the finding records the calibration
  failure and the census is not used to justify any addition.
- **Q2 = 0** — there is no fourth tree, three was right, and that is the deliverable. The census
  lands as the evidence, `GENERATED_TREES` is untouched, and the next reader has a number instead
  of an open question.
- **Q2 ≥ 1 and Q4 = 0** — the addition lands with the census, no freeze change needed.
- **Q2 ≥ 1 and Q4 > 0** — `FROZEN` is re-measured against the wider prefix set and the new live
  pairs are added to it **in the same commit**, each with the date and the reason, or the tree is
  not added at all. A green gate on a stale freeze is not an option here: a half-landed widening
  blocks every lane.
- **Q6 HELD** — recorded, not acted on. A gitignored generated tree cannot starve an atom the way
  a tracked one does, because the unmerged-work guard reads git; it is evidence about the census's
  own coverage, not a second candidate list.
