**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — census-the-promote-by-copy-class) · **Class:** controls_that_cannot_fail

# RESULT — the promote-by-copy class is five targets, and the census is blind to the half that reaches the reader

Scores `docs/staging/records/SEAT_PREREGISTRATION_WHICH_PUBLISHED_SENTENCES_A_PROMOTE_BY_COPY_WOULD_FALSIFY_2026-09-09.md`,
written before the census tool was run once. **Two of its six predictions are refuted, and one of
the refutations is the finding.**

---

## 0. The drawn premise was NOT spent

The item cites `77d92e0d1`, already an ancestor of `origin/main` — which is expected, because the
item asks for a **census of the class that commit found**, not a re-land of it. No census of this
class existed anywhere in `docs/staging/`. The work was real and is done.

## 1. The scope is five targets, and it is discovered rather than listed

A path is a promote-by-copy target **iff a dated sibling of the same stem sits beside it**. That is
the mechanical signature of the convention, and `tools/promoted_artefact_claim_census.py` derives
it from the tree rather than naming filenames, so a sixth target is picked up for free.

| target | dated siblings |
|---|---|
| `docs/observability/value_cycle_ab_s1_three_arm.json` | 7 |
| `docs/observability/value_cycle_ab_s1_noise_floor.json` | 6 |
| `docs/reports/run_output_latest.json` | 4 |
| `site/data/snapshots/LATEST.json` | 8 |
| `site/state/live_decisions_latest.json` | 40 |

Nine dated stems have no canonical twin and are correctly outside the class.

## 2. A LIVE INSTANCE, found by the census, in the file `77d92e0d1` had just repaired

`generate_value_arms_data.py` said, in the present tense:

> `THREE_ARM_PATH` now carries the 21:01:30Z run in world `39a192ce04c1eda8`

**It does not.** The 09-09 pair was promoted onto the canonical path later the same day —
`three_arm.json` is byte-identical to `..._20260909.json` (`md5 2d3819c2…`) and carries
`generated_at 2026-09-09T01:24:34Z`. The sentence went false **with an empty source diff**, which
is the whole class. Repaired at `tools/generate_value_arms_data.py:176` by naming the dated sibling
(`..._20260908b.json`) instead of asserting a stamp in the present tense.

The published page was NOT affected: `site/data/value_arms.json` carries
`run_generated_at 2026-09-09T01:24:34Z`, so `77d92e0d1`'s repair — deriving the claim from the
payload — held under exactly the event it was built for. **The residue was prose-side, as P4
predicted.**

## 3. THE FINDING: the census catches one of the three instances it was built from, and the two it misses are the two that reached the reader

**P2 is refuted, and this refutation is worth more than the census.** Replaying the pre-repair
producer out of `77d92e0d1^` through the finished census:

| instance | shape | caught? |
|---|---|---|
| `_current_world_bound` docstring naming the promotion target as a guard's **sole witness** | prose naming the file | **yes** |
| `how_to_read_this`: "published beside the **2026-08-31** run" | published feed string | **no** |
| headline: "a **LARGER** advantage than the GBP 17,453 below" | published feed string | **no** |

The reason is structural, not tuning. Run unnarrowed the census reported **406** stale claims
across 27 modules — every `# measured 2026-08-19` in any file that also reads a run output. That is
the aimed-left failure: matching the concept (a date) rather than the mechanism (a claim about
which run sits at a promoted path). Requiring one **sentence** to carry both a reference to the
target and a run-identity claim takes 406 → 1 and makes the tool usable.

**And that same narrowing is what makes it blind to the published half.** A reader-facing sentence
never names a file path — that is what makes it reader-facing. It says *the panel below*, *the
run*. No widening or narrowing over module text can pair those with a target, because **the pairing
is not in the text.** Pinned as an explicit assertion in
`test_the_narrowing_catches_only_one_of_the_three_named_instances`, so the blindness cannot be
forgotten and cannot be quietly tuned away.

So the class splits in two, and only one half is censusable:

- **prose half** — a comment or docstring naming the target. Caught. One live instance, fixed.
- **published half** — a composed sentence in a feed. **Structurally invisible to text matching.**
  The only thing that works here is what `77d92e0d1` already did: derive the claim from the
  artefact's payload so there is no literal to go stale. There is no census shortcut.

## 4. Two ways the tool was fail-open, both found by running it rather than reading it

**The whole-payload grade was vacuous.** Graded against its raw text, `run_output_latest.json`
yields **28,676** distinct run-identity tokens — every customer's `acquisition_date`. Against a set
that size *every* date claim is "supported", so the leg returned quiet for every reader of the
most-read promote target in the tree. **A control that is useless without ever visibly failing
open.** Repaired structurally rather than by a threshold: run identity lives in shallow metadata,
dates that are data live inside collections. 28,676 → 17.

**A bare clock or date could never match a payload.** Prose cites "the 21:01:30Z run"; the artefact
writes `2026-09-08T21:01:30Z`. The `\b` before the clock alternative cannot fire inside the full
stamp — the preceding `T` is a word character — so the citation and the payload could not meet, and
every bare-stamp claim was stale by construction. Found by a **false STALE on a claim that was
true**; the same bug pointed the other way would have been silent. Both sub-tokens are now emitted.

## 5. What did NOT ship, and why that is the honest answer

**P6 is refuted: no gate ships, and the census must not become one.** The remaining STALE row is

> `# the 2026-08-31 run" until 2026-09-09, which was true for as long as THREE_ARM_PATH`

— a **dated historical record**, a wrong claim kept beside the result, which this project *requires*
rather than tolerates. A record of what was true on a date is *supposed* not to track the artefact;
a claim about which run is on the page is supposed to track it exactly. **The two are the same
shape in text**, and tense does not separate them either (`dd_opening_arms`'s "was produced on
2026-09-01" is past-tense and is a claim about current state). Separating them by field or file
name would be an allowlist excusing the very mechanism the control points at.

So `--check` refuses on the source leg only and is **not wired into the pre-commit gate**. A gate
that reds on correct prose trains its readers to bypass it. `feed_claims` reports and never
refuses, and says on its own surface that it fails open — it raises 70 rows on `value_arms.json`
of which every inspected one is a legitimate `withdrawn_on` / `history[].on` record or a simulation
probe date.

**P1 (5–15 hits) is refuted in the raw direction and held after narrowing** — 406 unnarrowed, 14
graded claims after. **P3 held**: the `run_output_latest.json` readers produced hits and nearly all
were false. **P5 held**: `site/data/value_arms.json` is untouched by this turn; the census opens
nothing under `site/data/` for writing and imports no generator.

## 6. A second finding, filed not fixed

**`docs/reports/run_output_latest.json` publishes no run identity at all** — no `generated_at`, no
producing commit, nothing a reader's claim about which run it is could be checked against. Eighteen
modules bind that path. Its truth is currently establishable only from `git log` (last written
`0247f3061`, 2026-09-01, which is what makes `dd_opening_arms`'s docstring true). The census now
reports this class as **"we cannot tell"** — its own category, kept out of both the defects and the
passes, with the branch asserted reachable by test because nothing in the tree currently fires it.

## What is next

1. Give `run_output_latest.json` a `generated_at` and a producing commit. It is the most-read
   promote target in the tree and the only one whose identity is unpublished.
2. The published half needs feed fields to declare whether they are a **record** or a **claim about
   the current run**. That declaration is the only thing that would make `feed_claims` able to
   refuse, and it is a real repair rather than a regex.
