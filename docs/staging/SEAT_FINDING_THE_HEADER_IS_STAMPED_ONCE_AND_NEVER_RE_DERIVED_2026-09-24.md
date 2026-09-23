**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the frozen `repeats=1` was the worst case of a defect the whole alarm population had, and the header is now derived

Drawn as
`escalate-derives-its-repetition-count-from-the-document-rather-than-trusting-a-callers-literal-1`.
Answers the pre-registration in
`docs/staging/records/SEAT_PREREG_WHETHER_THE_FROZEN_HEADER_IS_THREE_FAMILIES_OR_THE_WHOLE_POPULATION_2026-09-24.md`,
which was **partly refuted** — see below, beside the prediction rather than instead of it.

## The premise, re-measured at draw

Not spent. `612bd9ffe` is an ancestor of `origin/main`, but it is the **finding** landing, not the
fix: `escalate()` at HEAD still took `repeats: int` as a required argument and wrote it into the
body unchanged. The duplicate-work check named this claim's own id, held in
`.seat_work_in_hand.json` by this draw — my own claim, not a rival's.

## Settling what the field MEANS, which the finding said to do first

Three quantities, all of which sound like "how many times", and the whole defect is one being
written where another was meant. They are now named separately in `alarm_repetition.py` and are
never summed or differenced:

| name | what it counts | who can know it |
|---|---|---|
| `repeats` | consecutive firings without a state change | **only `notify()`** — it holds the transition store that decides when the streak breaks |
| `days` | distinct dates the condition was observed to hold | the **document**, from its own machine-written lines |
| `members` | distinct members of the family that have fired | the **document**, from its instance list |

**`repeats` is now optional and defaults to absent.** A caller that does not measure a streak
passes nothing, and the document states the absence with its reason rather than a `1`. This is the
R10 class fix the finding asked for: it covers the four existing direct call sites and every future
one, and no caller has to invent a number to satisfy a signature.

**Why not rename `repeats` for everyone** (the finding's other sound option): the quantity
`notify()` measures is real and useful — `DEADMAN_WORKTREE_UNDECLARED` genuinely went 3 → 298 — and
renaming it would have left the document with no derived count at all. The two derived counts are
additions, not a replacement, and the caller's streak is reported beside them under its own name.

## The wider defect, which the pre-registration was written to test

While reading `escalate()` I noticed the header paragraph was written into the body **once, at
birth**, and never rewritten. `_note_still_live` appends; nothing touches the header.

**Registered prediction: all live documents carrying a still-live line would show a header count
lower than the maximum count in their own lines.**

**Result: 4 of 7. Refuted on "all", confirmed on the direction.**

| document | header | max still-live | days | members |
|---|---|---|---|---|
| `STRETCH_LOG` | 3 | **2132** | 6 | 1 |
| `DEADMAN_WORKTREE_UNDECLARED` | 5 | **298** | 8 | 10 |
| `DEADMAN_LAUNCH_ARTEFACT_UNLANDED` | 3 | **230** | 5 | 2 |
| `TREE_DIVERGENCE` | 12 | 16 | 8 | 4 |
| `RUN_MARKER_SWEEP` | 3 | 3 | 2 | 1 |
| `SEAT_CONTINUITY` | 1 | 1 | 8 | **23** |
| `DELIVERY_LANE_STRANDED` | 1 | 1 | 5 | **18** |

**Why it was refuted, and this is the useful part:** `repeats` is a streak counter that **RESETS**
(`DEADMAN_WORKTREE_UNDECLARED` runs 3, 22, 51, 70, 106, 298, 3), so "max of the lines" is not a
monotone total and the header is not obliged to be below it. My prediction assumed a quantity that
only grows. It does not — which is itself the argument for not letting `days` and `repeats` share
a sentence, and it is why the remedy counts dates and members instead of trusting either.

**The direction held, and `STRETCH_LOG` is worse than anything the original finding named**: a
header reading 3 above a line reading 2132, in a family that comes through `notify()` with an
honestly measured count. So the literal `1` was the worst case of a defect the whole population
had, and fixing only the three direct callers would have left eight documents frozen.

## What was built

`escalate()` now derives the two counts it can establish from the document itself, on **every**
firing, and writes them into a delimited self-updating block:

- `document_counts()` / `_observation_dates()` — shared with the re-ask's `last_observed()`, so
  one reader serves both. Two readers of one record would drift, and a re-ask archiving on a
  different set of dates from the one the header reports would be unarguable with.
- `_refresh_counts()` — the single derivation point, called last on both branches so it reads a
  document that already carries today's lines.
- `_threshold_line()` — names `ESCALATE_AFTER_REPEATS` as **not applied** for a direct caller,
  instead of printing a number below the bar next to the bar as though the bar had been cleared.
- `_note_still_live()` — leads with what the call observed; carries the caller's streak only when
  there is one.

**No migration to run.** `_refresh_counts` places the block three ways, and the second is "over the
legacy fixed paragraph" — so each of the ten live documents repairs itself the next time its
condition is observed. Verified against real copies of `SEAT_CONTINUITY` and `STRETCH_LOG`:
*"fired **1 times without its state changing**, over **95.9h**"* became *"observed to hold on **8
separate day(s)**, between 2026-09-15 and 2026-09-22, and **23 member(s)** of the family
`seat-continuity` have fired"*. The third placement is the BIRTH path, so the insert branch is
exercised by every new document rather than being dead code the day a migration finished.

**The live documents are deliberately NOT repaired in this commit.** They are written by running
daemons; staging ten of them would carry whatever another lane appended mid-turn inside my commit.
They repair themselves, which is the design.

## The controls, and the one that went green

Seven new controls, four mutations run against them:

| mutation | verdict |
|---|---|
| `_refresh_counts` becomes a no-op (header stamped at birth again) | **RED**, 3 tests |
| a direct call site passes `repeats=1` again | **RED**, the call-site census |
| the counts block writes an observation-shaped line | **RED**, 2 tests |
| `repeats` defaults to the literal `1` | **GREEN — the control did not reach it** |

**The green one is the finding inside the finding.** Every test named `repeats=` explicitly, so
nothing exercised the DEFAULT — which is the entire mechanism by which the four call sites now
avoid inventing a number. The helper was changed to OMIT the argument rather than pass `None`
(different calls; only one is what production makes) and the mutation then bit. Recorded in the
helper's own docstring, beside the code, rather than here only.

The call-site census carries **both legs** (`calls >= 4` as well as `not offenders`), because an
offender census with an empty result is green whether the pattern is right or the population is
empty.

## What this does NOT claim

- Not that the three direct callers should go through `notify()`. The defect was the hardcoded
  `1`, not the door, and that is unchanged.
- Not that `days` is a better measure of severity than `repeats`. It is a different one, available
  to every family; `repeats` is sharper where it exists and is still reported.
- Not that the ORDER 60 ranking will now move. The finding's claim that understatement is what
  kept these documents unranked is **still a plausible partial answer and still unchecked** —
  checkable against the draw log now that the counts are honest, which is a later measurement.
