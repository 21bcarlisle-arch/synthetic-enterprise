# [SEAT FINDING] The maturity map's atom set had already fallen 22 atoms in 3 commits, and two of them are explained nowhere

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `census-register-low-water-third-question`
**Filed** 2026-09-05. Pre-registration, written before any measurement below:
`docs/staging/records/SEAT_PREREGISTRATION_HAS_THE_MATURITY_MAPS_ATOM_SET_ALREADY_FALLEN_2026-09-05.md`.
Predecessors, all landed today: `dc5fcbbc8` (`removed_dispositions()`, the alarm census),
`605ec3995` (`removed_claims()`, the canon register), `6f4e6b1f4`
(`background/register_low_water.py`, the shared mechanism, wired at `finding_classes`).

---

## The premise, re-measured at draw time

The drawn item cited `dc5fcbbc8` as already an ancestor of `origin/main`, and it is. The premise is
NOT spent: that commit is the *predecessor*, not the work. The work — asking the third question of
the sibling registers — was carried by `6f4e6b1f4` for three of the four and explicitly left one
piece open, naming it in its own commit message: **`maturity_map.yaml` measured, holed, and NOT
wired**, because "the map is a bare list with nowhere to hang a retirement reason, and choosing
that home is the work." That is what this turn did.

## A false claim in the record, found before starting

`background/register_low_water.py`'s docstring table said of the map: **"Wired here."** Nothing
wired it. `grep -rn register_low_water` returned `finding_classes.py` and one test file, and the
same commit's own message said, correctly, "measured and written up, NOT wired". A module making a
checkable claim about itself that nothing checks — one line below a table whose canon row was
*also* stale (another lane wired `removed_claims()` in `605ec3995` while the measurement was in
flight; `c8e77bacc` corrected the finding document but not the module). Both rows are now corrected
beside the original text, and the map row is true by the work rather than by the sentence.

## What was measured

Every one of the **1,023 committed revisions** of the map's two halves, walked, extracting the
union of atom ids at each.

| | |
|---|---|
| Commits touching a map part | 1,023 |
| Commits where the UNION of both halves SHRANK | **3** |
| Atoms lost across those three commits | **22** |
| Atoms at HEAD | 314 |
| Of those 22, argued in the commit that removed them | 20 |
| **Of those 22, mentioned nowhere at all** | **2** |

The three commits: `7d01fffba` (2026-08-08, −2), `82007ad44` (2026-08-10, −1), `7403b89c1`
(2026-08-24, −19).

**The two that nobody explained.** `D6a_ageing_gap_metric_reshape` and
`D6b_ambiguous_remittance_misdating` left in `7d01fffba`, a commit titled *"C15: floor
derive_supply_start at the account's own first observable"* whose message does not mention either
atom anywhere. Two work items vanished as an unremarked side-effect of a commit about something
else. The other twenty are the opposite: `7403b89c1` argues its nineteen at length (H_harness held
135 of 316 atoms; 62 were `provenance: proposal`; 23 sat below target; their dependency edges were
*checked*, not assumed), and `82007ad44` names its one as a duplicate id wedging publish.

**From the map alone, those two cases are indistinguishable**, and that is the whole argument for
refusing a removal rather than reporting it.

## Against the pre-registration

**P1 (3–15 commits show a union shrink) — CONFIRMED, at the bottom of the band: 3.** This is the
number that decided the mechanism. §4 of the pre-registration recorded a stopping condition: if
removals were routine, a refusing gate would be the wrong shape and a report the right one. Three
in 1,023 is 0.3%, so a refusal costs almost nothing and the gate is the right mechanism. That
condition was written down before the number was known.

**P2 (the split reads as >200 deletions over the live half, zero over the union) — CONFIRMED:**
`7f11d9c7d` (2026-08-26) shows −224 over the live half and −0 over the union. `_whole_map` is
load-bearing, not decorative.

**P3 (`refile()` preserves the union key set) — CONFIRMED by running it**, not by reading: on a
copy of the live map it moved 1 atom to the closed half, union 314 → 314.

**P4 (>0 atoms lost, order tens) — CONFIRMED: 22**, and the three shrink commits account for
exactly 22, so nothing was lost and restored.

**P5 (the reason's home is a THIRD sibling file) — CONFIRMED.** Both halves are top-level YAML
*lists*, concatenated by `map_text()` and line-scanned for `- id:` by `moap_coherence` and
`merge_atom_status`; a `_retired` mapping inside either one breaks that contract. The register is
`docs/design/maturity_map_retired.yaml`, deliberately a mapping so no reader can mistake it for a
third half of the map.

**P6 ("wiring it costs no new git reads") — REFUTED, and the refutation is the better design.**
`_whole_map` was indeed already computed at both revisions, but `git show` returns the same `None`
for "the path is not at that revision" and "git could not answer" — opposite claims. An established
absence is an empty baseline (a genuinely new map can't have lost anything); a failed probe is *no*
baseline and must refuse. Separating them needs a `git ls-tree` probe the gate did not have. The
prediction was wrong because "it's free" was a claim about the happy path only.

## What was built

`tools/level_promotion_gate.low_water_failures()` — two rungs, run FIRST in `main()` because it is
the only control there whose subject is the register rather than a row of it. Every other rule in
that file iterates atoms, so an atom deleted by the commit is the subject of none of them.

* **Rung 1** — an atom in HEAD's map and not in the staged one is refused unless
  `maturity_map_retired.yaml` names why. Baseline is the UNION of both halves, so `refile()` is not
  a removal. **No subject-gone exception**, deliberately: an atom genuinely abolished and a map
  quietly losing a row are the same observation from the map alone.
* **Rung 2** — the retirement register is **append-only**, with exactly one way out: the atom came
  *back*. Without it the reason can be erased one commit after it cleared rung 1, by which time the
  atom is gone from HEAD's map and rung 1 has no subject. The un-retirement exception is what stops
  the regress (a retirement reason for retiring a retirement reason) without granting a free pass.

Rung 1 calls `register_low_water.removed_rows` rather than copying it. There were already three
hand-rolled implementations of this control (census, canon, generic), each carrying its own copy of
the `or ""` null treatment and the None-never-empty refusal; a fourth would regress every repair
the generic holds the moment one of them is fixed and this one is not.

The trigger set is widened to include the retirement register. Keyed to the map's halves alone,
rung 2 would be **unreachable by construction** — a commit deleting a retirement row and nothing
else stages neither half.

**Twelve mutations, all killed** (`M1` rung returns nothing; `M2` unestablished baseline reads as
empty; `M3` probe failure reads as present; `M4` rung 2 never refuses; `M5` rung 2 drops the
un-retirement exception; `M6` unreadable retirement register reads as empty; `M7` `retired_reasons`
swallows a non-mapping; `M8` the trigger drops the register; `M9` `main()` never calls the rung;
`M10` `main()` calls it and drops the result; `M11` `atom_ids` finds nothing; `M12` the seeded
register loses its unexplained rows). The wiring is proved separately from the rungs, end-to-end
through `main()` against a real git index, because a control that calls the shared helper survives
mutation of the caller.

**M3 and M6 survived the first pass**, and both named a real hole rather than an equivalence: no
leg drove `_tree_tracks` itself (every leg passed the flag in directly), and no leg drove the
tracked-but-unreadable branch of the retirement register — the branch where reading `{}` instead of
a refusal would empty rung 2's entire subject set. Three legs added; both then killed.

## What is NOT done

**The 22 recovered rows are inert to the gate**, and honestly so: the gate's baseline is HEAD, and
none of those atoms is in HEAD's map. They are in the register because the record of why they went
lived only in a commit message, which no reader of the map consults. Nothing re-derives them.

**Three implementations of one mechanism remain** — `removed_dispositions` (census),
`removed_claims` (canon), `removed_rows` (generic, now with two callers). `c8e77bacc` already filed
this as the largest thing outstanding here. Re-pointing the two specialisations at the generic is a
separate change with its own proof burden and is not attempted in the same turn that adds a caller.

**Nobody asked the third question of the register that answers the third question.** The retirement
register is append-only and its own low-water mark is guarded by rung 2, which terminates the
regress — but rung 2 lives in the same file as rung 1, so a commit that deletes
`level_promotion_gate.py` outright takes both. That is true of every gate in the pre-commit chain
and is the pre-commit hook's problem, not this control's; recorded so the next reader does not have
to rediscover where the line was drawn.
