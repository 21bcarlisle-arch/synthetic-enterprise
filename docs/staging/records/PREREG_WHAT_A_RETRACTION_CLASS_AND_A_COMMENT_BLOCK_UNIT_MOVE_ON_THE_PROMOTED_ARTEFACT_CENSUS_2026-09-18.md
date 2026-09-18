**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** promoted-artefact-claim-census

# PRE-REGISTRATION — what a RETRACTION class and a comment-BLOCK claim unit move on the promoted-artefact census

**Filed:** 2026-09-18, before editing `tools/promoted_artefact_claim_census.py` and before running
the changed census even once.
**Claim id:** `repair-the-census-that-reads-a-retraction-as-a-live-claim`

---

## The duplicate-work check, answered

The draw named one rival live claim — `republish-the-arms-decomposition-over-one-priced-book` — on
the ground that it "already holds `tools/generate_value_arms_data.py`, which this item names".

**The premise is a draw-time prediction and it is false.** Read out of
`docs/observability/.delivery_lane_claims.json` on the shared tree at 2026-09-18, that claim's bound
paths are:

```
docs/observability/value_cycle_ab_s1_three_arm.json
docs/staging/PREREG_WHAT_REPAIRING_THE_STRATIFIED_FIXTURE_MOVES_ON_THE_TWO_REDS_2026-09-18.md
docs/staging/SEAT_FINDING_THE_STRATIFIED_FIXTURE_CONSTRUCTS_...md
docs/staging/SEAT_RESULT_BOTH_STRATIFIED_REDS_WERE_THE_SAME_CLASS_...md
docs/staging/done/SEAT_FINDING_THE_STRATIFIED_FIXTURE_CONSTRUCTS_...md
site/data/value_arms.json
site/test_the_baseline_comparison_reaches_the_reader.py
site/test_the_stratified_concordance_reaches_the_reader.py
```

`tools/generate_value_arms_data.py` is not among them. **It is genuinely different work**, and the
draw itself directs this one away from that file: *"Fix the class at the census, NOT the instance at
the contested producer."* This turn touches `tools/promoted_artefact_claim_census.py` and
`tests/tools/test_promoted_artefact_claim_census.py` only — **zero path overlap with the rival**,
which is a stronger separation than the note asked for. Disposition: **carry on**, neither
`--landed-under` nor `--release`.

---

## The defect, stated as a class

The census's STALE leg asks: *if the bytes at this promoted path were replaced by a newer run, would
this sentence become false?* It answers that by looking for a run-identity literal that matches
neither the artefact now at the path nor any dated sibling the module pins.

**A past-tense account of a WITHDRAWN claim cannot become false under a promotion.** Its truth
conditions are historical — it says what the text used to say, over a closed interval that has
already ended. Nothing copied onto the canonical path today can touch it. The census cannot see
that distinction and grades the retraction exactly as it grades a live claim.

The single instance refusing `--check` today is
`tools/generate_value_arms_data.py:9883`, token `2026-08-31`, whose text is:

```
# the 2026-08-31 run" until 2026-09-09, which was true for as long as `THREE_ARM_PATH`
```

…the tail of a comment block whose head (9882) reads *"This sentence read \"published beside"*. The
live expression beside it is a `{when}` placeholder resolved from the other panel's payload. **The
code is correct and the census is wrong.**

**Why the class matters more than the instance.** CLAUDE.md requires *"Correct yourself plainly, in
the record, beside the claim"* — a wrong prediction kept next to the result is the only evidence the
experiment predated its answer. This control refuses the whole tree for exactly that habit, and the
cheapest way to clear the red is to **delete the account of the defect**, which destroys the
attribution and turns the census green. The control is paying for the destruction of its own
evidence.

---

## What I am building, and why each half is not a narrowing

Two changes. The draw forbids narrowing the predicate to silence one comment, and the standing rule
is that *a narrowing added to fix a false positive is asymmetric and only the false positive gets a
comment*. Both halves below are designed to be **symmetric** — each can raise rows as well as clear
them, and each is graded rather than asserted.

### (A) The claim unit for comments becomes the contiguous BLOCK, not the physical line

`_module_strings` currently emits one row per `#` line, because that is what `tokenize` hands back.
A wrapped comment is ONE piece of prose; splitting it at the 100-column ruler is an artefact of the
formatter, not of the writing. `_sentences` already exists to cut a 200-line docstring into claim
units — the correct order is **join the block, then split into sentences**.

This is a WIDENING. A sentence whose target reference sits on one line and whose run-identity token
sits on the next is invisible to the census today and becomes visible after it.

### (B) A RETRACTION is classified, graded, and reported — never silently dropped

A row is a **retraction** when its sentence carries BOTH:

1. a past-tense **saying-verb** about what the text itself said — `read`, `said`, `stated`,
   `called`, `claimed`, `previously`, `used to`, `withdrawn`, `no longer`; AND
2. a **closure** — the claim is said to have ENDED, and when: `until <run-identity token>`,
   `no longer`, `became false`, `was repaired`, `has since`, `stopped being`.

Both halves, in one sentence. "Previously" alone does not buy silence: a writer must state *when*
the claim stopped standing, which is precisely the attribution the project wants kept.

**And it is GRADED, which is what stops it being an escape hatch.** A retraction asserts *this
stopped being true*. The census already knows whether it is still true. So:

- retraction, token does NOT match the current run → **the retraction is accurate**. Reported in its
  own surface section with its line and text, counted, and excluded from STALE.
- retraction, token DOES still match the current run → **FALSE RETRACTION**, a new refusing class.
  You say this ended; the artefact at the path says it did not.

Both outcomes are reachable, so the leg can fail. The limit I am NOT pretending past: this census
cannot detect prose that lies. A writer who fabricates "read X until D" about a claim that is still
live is caught (that is the false-retraction leg); a writer who fabricates one about a claim that is
genuinely dead is not, and no regex over English could be. That limit goes on the surface, not in a
footnote.

---

## PREDICTIONS, before running anything

**P1 — (A) alone does NOT clear the 9883 red.** Joining the block and re-splitting produces the
sentence *"This sentence read \"published beside the 2026-08-31 run\" until 2026-09-09, which was
true for as long as `THREE_ARM_PATH` resolved to that run and became false the moment the 21:01Z
re-take was promoted onto the canonical name"*, which still carries token `2026-08-31` against
`THREE_ARM_PATH` and is still ungraded-as-retraction. STALE stays at 1. **If (A) alone clears it,
(A) is a silencer and I have mis-designed it.**

**P2 — (A) alone raises the total row count.** I predict at least one NEW row appears that the
line-at-a-time unit could not see. I do not know how many, and I do not know whether any is STALE.
**If (A) raises ZERO new rows, its claim to be a widening is unevidenced** and I must say so rather
than keep the flattering reading.

**P3 — (A)+(B) takes STALE to 0 and `--check` to exit 0**, with 9883 reported under RETRACTIONS
rather than deleted or excused.

**P4 — the three pre-repair instances out of `77d92e0d1^` still replay.**
`test_the_narrowing_catches_only_one_of_the_three_named_instances` and
`test_the_census_catches_a_docstring_naming_a_promoted_path_as_a_guards_sole_witness` stay green
unchanged. This is the control that the repair did not buy its quiet with the defect the census
exists for; **if either goes red, the retraction predicate is eating live claims** and the design is
wrong, not the test.

**P5 — no OTHER currently-reported row is reclassified as a retraction.** The 8 ORDERING rows and
the 2 UNCHECKABLE rows are live claims. If (B) swallows any of them, the saying-verb+closure pair is
too loose.

Results, including any of these that are refuted, go in the SEAT_RESULT beside this file.
