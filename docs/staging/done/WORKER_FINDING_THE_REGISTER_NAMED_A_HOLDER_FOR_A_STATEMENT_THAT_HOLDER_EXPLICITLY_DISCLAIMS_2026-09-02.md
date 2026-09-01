**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `the-only-control-holding-the-level-anchor-is-red-and-reports-a-constant-pass`

# The register named a holder for a statement that holder's own docstring disclaims — and it acquired that claim inside the commit correcting it for exactly that shape

**Found:** 2026-09-02 at clean HEAD `e70ab4749` (== `origin/main`, 0 ahead / 0 behind), working the
Lane 0 delivery direction. Verified by `git archive HEAD` into a clean stem outside this tree.

---

## 1. The drawn premise is refuted: those two legs are not red

The direction stated, and asked not to be taken on trust:

```
expect: 2 failed, 24 passed, 1 xfailed
        AssertionError: only 7 years had their margins checked
```

Measured at clean HEAD, in a stem:

```
tests/architecture/test_switching_rate_commons.py .....x..x........................
31 passed, 2 xfailed in 4.57s
```

The work moved between the doorbell being written and this tick. `f97c34eb0` ("the year the level
anchor is wrong about is the year its only control cannot see") and `4871e53ee` ("a register
claiming indirect cover cannot see its own holder being xfailed") landed it. Against the direction's
own **done means** list, at HEAD:

| Clause | State at `e70ab4749` |
|---|---|
| Cause of the emptying named in writing | **Done.** 2022 stopped being **PRODUCED**: it is 100% crisis-forced-passive, C1b routes every passive roll to the SVT segment table, so the renewal capture carries zero 2022 decisions. Datable to `b46318106`. |
| Leg keyed to the property, not a count | **Done.** `assert len(world) >= 8` is gone; `test_every_comparison_year_is_either_read_or_refused_with_a_corroborated_cause` replaces it, and corroborates each refusal through a second reader of the capture. |
| Refusal names the missing year and its reason on the surface | **Done.** Both in the return value and in the instrument's printed table (`NO READING`, no `nan` anywhere). |
| One mutation-proven leg | **Done**, several. |
| `_HELD_INDIRECTLY` re-justified or corrected | **Done** — and the direction's suspicion was right: the register's indirection claim *was* the thing that was wrong, and it was corrected in the register rather than patched in the assertion. |
| Both legs green | **Not, and correctly not.** The band leg is `xfail(strict)`: the world is genuinely out of band in 7 of 7 readable years, −1.10pp to −15.90pp. Discharge is a re-fit against the committed capture, which is a different item and a different pathspec. Held open loudly rather than left quietly failing. |

So the drawn repair was already landed. What follows is what was found while verifying it.

## 2. The finding: the correction introduced the defect it was correcting

`4871e53ee` exists because `_HELD_INDIRECTLY` claimed the anchor was *"held through its EFFECT — the
world's realised departure rate … band-checked every run"* while that holder had been marked
`xfail(strict)`. A register claiming cover its holder was not providing. The commit added
`test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding`, which is a good
leg: symmetric, property-keyed, mutation-proven.

In the same edit the entry acquired two numbered statements about why the indirection is holding
nothing, and this sentence:

> **"Both statements are held by `test_a_register_entry_naming_a_holder_discloses_whether_that_holder_is_holding`, so this text cannot go stale in the flattering direction when the re-fit lands."**

Ninety lines below, that leg's own docstring says:

> **"WHAT THIS LEG DOES NOT CLAIM. It cannot tell whether the holder is a GOOD holder — that the stored-capture read path makes it a per-re-capture drift detector rather than a live assertion is recorded in the entry's prose and in the holder's own docstring, not asserted here."**

Statement (i) — THE HOLDER IS XFAIL — was held. Statement (ii) — the anchor module is not in the
holder's read path — was held by **nothing**, while the register said it was held. The register being
corrected for claiming unprovided cover acquired, inside the correction, a second claim of unprovided
cover, and the two sentences sat in one file with nothing able to compare them.

**Statement (ii) is true.** Verified three ways at clean HEAD:

- `tools/measure_departure_level.py` never imports `simulation.departure_level_anchor`. Its only two
  mentions of the anchor are in prose (lines 110, 399).
- Its reading is `json.loads(DEFAULT_TABLE.read_text())` over
  `docs/reports/c2_departure_factors.json` — a stored capture carrying the `sim_level_anchor` of the
  run that produced it.
- Multiplying every `YEAR_LEVEL_ANCHOR` entry by seven leaves `world_realised_rate_pct()`
  bit-identical.

## 3. Why (ii) is the statement that costs

(i) is visible: the marker is on the leg, and anyone reading the band control sees it. (ii) is a claim
about a path nobody reads. A reader who trusts the indirection believes an anchor edit is band-checked
every run. It is band-checked **once per re-capture**. That gap is how a 1.98x fallback on 2022
survived a capture, a fit and two preregistrations.

## 4. The repair

`tests/architecture/test_switching_rate_commons.py`, one file, this commit:

1. **New leg** `test_the_disclosed_read_path_is_checked_against_the_read_path_the_holder_actually_has`.
   It measures the read path rather than asserting today's answer: perturb `YEAR_LEVEL_ANCHOR` ×7,
   re-read the holder's reading, and require the entry's disclosure to **agree** with whether it
   moved. Leave the instrument on the stored capture and the entry must keep saying so; re-wire it to
   read the live table and the entry claiming *"not in its read path at all"* must be corrected. It
   does **not** assert the anchor is unreachable — that would pin the control to today's wiring and go
   red on the improvement.
   - The table is mutated **in place**, not rebound. Rebinding the module attribute is invisible to a
     `from … import YEAR_LEVEL_ANCHOR` captured at import time, so that re-wire would read as "does
     not reach" and the disclosure would stay green while going false — the flattering direction.
   - ×7 and not the ×2 the register cites, so the probe cannot confuse "unreachable" with "reachable
     but insensitive at the cited size".
   - The probe asserts its own perturbation is visible through `year_level_anchor` before concluding
     anything, so a no-op mutation cannot report "does not reach" for every possible read path.
   - Restoration verified: the table is byte-identical after the leg runs.
2. **Register corrected** to name two holders, one per statement, with the reason they are separate:
   the two disclosures go stale independently.
3. **Disclosure leg's docstring corrected** so its DOES-NOT-CLAIM paragraph is not read as a live gap
   after the gap is filled.
4. **Splice artefact repaired**: the sentence *"It holds an entry only where the world runs"* appeared
   twice, once truncated mid-clause, from the `4871e53ee` insertion.

**Mutation-proven, both directions, `python3 -B` in a clean stem:**

| Mutation | Result |
|---|---|
| Delete the read-path disclosure from the entries | **FIRES**, naming the entry and the stored capture it actually reads |
| Wire `world_realised_rate_pct` to multiply by `year_level_anchor(y)`, entries untouched | **FIRES** the other way: "the instrument now sees the live table — the indirection is stronger than the entry admits" |

`32 passed, 2 xfailed` at the repaired file.

## 5. The generalisable shape

**A control that holds a register's disclosures is itself a claim needing a holder, and the natural
place to write the claim is the register it is holding — where nothing checks it.** `4871e53ee`
mechanised one disclosure and asserted the other in prose, one line apart, in the artefact whose
whole defect is prose asserting cover. The catalogue entry is *a register claiming indirect cover
cannot see its own holder*; this is that at the next level up, and the give-away is a sentence
containing the word **"Both"** where only one thing was built.

Cheap check that would have caught it: when a docstring says *"this leg does not claim X"*, grep the
file for something claiming X **is** held.

## 6. Owed next

- The band leg's `xfail(strict)` stands. Discharge is the re-fit of `YEAR_LEVEL_ANCHOR` against the
  committed 148-row capture, 2022 excluded as unidentified. Different pathspec, not this item.
- `YEAR_LEVEL_ANCHOR[2022]` is still held by nothing. Named honestly in the register and in the
  refusal; naming is not holding. See
  `SEAT_FINDING_THE_DEPARTURE_LEVEL_UNIONED_ONTO_ACCOUNT_YEARS_AND_2022_HAS_NO_LEVER_2026-08-31.md`.
- **Ops, separate and unblocked in passing:** `/tmp` (12G tmpfs) was at 98% and refusing writes —
  `git archive` extracts abandoned by earlier turns, eight of them at 256M each, plus pytest scratch.
  It wedged this turn's test output before it wedged anything else. Reaped the non-worktree stems
  older than 60 minutes and all but the newest three pytest dirs; 3.3G free. The two `/tmp` paths that
  are registered git worktrees were left alone. This will recur: nothing reaps `git archive` stems,
  and every lane is told to make one.
