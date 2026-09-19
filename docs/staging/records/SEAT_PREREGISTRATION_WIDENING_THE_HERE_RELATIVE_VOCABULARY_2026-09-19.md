# PRE-REGISTRATION — widening the here-relative vocabulary past its noun list

**Severity:** RECORDED
**Lane:** `H_harness`

RECORDED, not BLOCKING: this document is the method — the predictions filed before the measurement
and the results appended beside them. The defect it went looking for is carried, with its severity,
by `SEAT_FINDING_THE_HERE_RELATIVE_VOCABULARY_IS_AN_UNBOUNDED_ALLOW_LIST_2026-09-19.md`, and
putting a second blocker on the same subject would double-count one finding.

*Filed 2026-09-19, BEFORE the measurement, by the delivery seat. Claim
`the-here-relative-detectors-noun-list-has-no-run-so-a-live-pointer-is-invisible-to-every-sweep`.*

---

## The premise, re-measured at draw time

`dc92d2d65` is an ancestor of `origin/main`; the work it cites has not landed by another route.
The premise is LIVE:

* `site/test_a_here_relative_pointer_has_one_home.py::_HERE_RELATIVE` admits a bare noun before
  `above|below` from a closed list — `table|panel|chart|figure|row|block|section|list|column|note|box|card|band`.
* `site/data/value_arms.json` publishes, in `_population_repair_bias`'s `clause`:
  *"it was measured on `18327d977` against `a178b56d6`, **20 paths of pricing code away from the
  run above**"*. `run` is not in that list, so `_here_relative_phrase` returns `None` for it.

**And the sharper fact, which is why this is worth a turn.** The comment at
`tools/generate_value_arms_data.py:10510` records that this very string was repaired on
2026-09-19 — *"NAMES THE CHOOSING FIGURE rather than pointing up at it, and the same repair is made
to the two sentences `_population_repair_bias` composes around this one"*. The repair named the
**figure** and left **the run** pointing. The lane that made it was reading a census the detector
had built, and the detector could not see the second pointer in the string it was repairing. A
control certified a repair to a defect class while blind to a live instance of that class **inside
the same sentence**.

## The duplicate-work check, resolved

The draw named two rival claims. Both are dispositioned, neither takes this work:

* `the-here-relative-detectors-noun-list-has-no-run-...` is reported as "already held by another
  writer". It is held by **this draw** — `claimed_at` 1789848603 against a draw-time `now` of
  1789848645, forty-two seconds. Self-reference, not a rival.
* `churn-truncation-destroys-the-decision-surface-before-the-arm-is-asked` holds
  `tests/tools/test_the_value_arms_pages_undriven_pointers.py`, which this item also names. It has
  bound **zero** paths and its subject is churn truncation, not pointer vocabulary. Genuinely
  different work on a shared file. Carrying on, and keeping my edits off that file where I can.

## The prediction, filed before the measurement

The item says "add `run` and audit the rest of the noun list". I predict the noun list is **the
wrong axis**, and that the audit will show enumerating it cannot be finished:

1. **P1 — the noun list is unbounded against live prose.** A census of deictic `the <noun>
   above|below` across `site/data/*.json` will return **more than 50 distinct nouns**, of which
   fewer than 8 are in the current list. If it returns under 20, P1 is refuted and simple
   enumeration is the right fix after all.
2. **P2 — the obvious inversion (match any noun, deny-list the comparators) is refused by a
   measured counter-example that is already on the record.**
   `tests/tools/test_the_proof_pages_undriven_pointers.py:43` records that admitting `range|interval`
   picks up `generate_value_arms_data.py:1693`, *"whether a larger settled book moves the interval
   above"*, where `above` is the direction a **number** moves. I predict a bare-noun inversion
   re-admits that string and others like it, so the discriminator is **grammatical, not lexical**:
   the deictic reading needs the noun phrase to be a definite one whose head is post-modified by
   `above|below` and followed by a finite verb or a clause boundary.
3. **P3 — widening to see `"the run above"` puts it into the `tied` census of
   `tests/tools/test_the_value_arms_pages_undriven_pointers.py`, and that census REFUSES it as
   unjudgeable** rather than passing it, because `_REFERENTS` has no registered referent for a
   `run`. The red I get first will name the vocabulary, not the page.
4. **P4 — the repair is to NAME the run, not to re-point it.** The run the clause points at renders
   in more than one region (`#arms-legs-first` and `#arms-redraw` both carry this run's figures),
   so — exactly like the four of six that `dc92d2d65` repaired — **there is no here-relative word
   that is true from both**. If it turns out to render in exactly one region, P4 is refuted and
   the cheaper repair (keep the pointer, register the referent) is correct.

## What "done" means for this turn

This is DIRECTION, not an atom, so the seat sets the bar. Done is:

* the vocabulary sees `"the run above"`, and the widening is **argued from a measurement** rather
  than from a longer guess at the noun list;
* the four consumers — `site/test_a_here_relative_pointer_has_one_home.py`,
  `site/test_a_producers_here_relative_pointer_has_one_home.py`,
  `tests/tools/test_the_value_arms_pages_undriven_pointers.py`,
  `tests/tools/test_the_proof_pages_undriven_pointers.py` — are green against the widened
  vocabulary, with every newly-caught pointer **repaired in its producer**, not exempted;
* `site/data/value_arms.json` is rebuilt from the repaired producer, so the page a reader fetches
  carries the repair and not just the code;
* whatever the widening catches that this turn cannot finish is filed as a finding with its
  instances named, rather than left for the next census to re-derive.

**What would refute the whole item:** if the widened vocabulary catches nothing beyond `"the run
above"`, then the blind spot was one word wide and the structural story in P1/P2 is wrong. I would
say so here and add the noun.

---

# RESULTS, appended after the measurement

**P1 — HELD.** The deictic census over `site/data/*.json` returned **70+ distinct head nouns**
against 8 registered. Enumeration cannot finish. Not refuted: the count is far above the 20 that
would have made simple enumeration right.

**P2 — HELD, and in a stronger form than predicted.** I predicted the bare-noun inversion would be
refused by the recorded counter-example and that a *grammatical* discriminator would separate the
two senses. **The second half of that was wrong.** I built the grammatical version — definite noun
phrase, head post-modified by `above|below`, followed by a finite verb or clause boundary — and it
catches `generate_value_arms_data.py:5371` *anyway*, because that string's `above` is followed by
"is NOT ESTABLISHED". The clause `"whether a larger settled book moves the interval above"` is
itself the subject of a finite verb, which is the very pattern I wrote the lookahead to trust.
Measured: 92 producer literals matched by the grammatical rule against 34 by the current one, with
the known false positive among them. **So the discriminator is neither lexical nor grammatical**,
and the remedy in the finding is a partition rather than a better regex. Recording this because a
prediction filed after the answer is not a prediction: my proposed fix was refuted by my own
measurement, and the finding says so rather than quietly shipping the version that failed.

**P3 — HELD exactly.** The first red named the vocabulary, not the page: 8 pointers refused as
*"not a pointer this rung knows what to check"* by
`test_every_tied_here_relative_pointer_is_true_from_the_region_it_lands_in`. Fail-closed worked —
the rung refused to judge rather than passing them on silence.

**P4 — HELD, and it found more than predicted.** The run pointers' subjects do render on both sides,
so naming the subject was the correct repair for all of them. **The unpredicted result is the one
that matters**: `_staleness_caveat`'s *"the run published above"* is not merely unjudged, it is a
**live two-home pointer** — `/capabilities/#arms-errorbar` and `/capabilities/#arms-headline` — i.e.
a live instance of the parent defect that four purpose-built controls were passing. I predicted the
widening would expose *unjudged* pointers; it exposed an *actual defect on the deployed page*.

**The item was not refuted.** The refuting condition I filed was "the widened vocabulary catches
nothing beyond `the run above`". It caught **ten** pointers across **eight** symbols, on two
separate axes, one of them a live two-home defect.

## Against "done" as I defined it

* Vocabulary sees `"the run above"` — **yes**, and the widening is argued from the census and the
  refuted-inversion measurement, not from a longer guess.
* Four consumers green — **yes, 30 passed**, from a 30-passed baseline, with every newly-caught
  pointer **repaired in the producer**; nothing was exempted and no `_REFERENTS` row was added to
  make a red go away.
* Feed rebuilt — **yes**. The only numbers that moved are provenance stamps moving *forward*
  (`publishing_tree_commit` 960e723ab → dc92d2d65, catching up to HEAD; run artefact 16:45 → 19:00).
  Every figure — £4,579, 98.5%, 104 of 2,824, 2.5 SEs, bar 2.11 — is byte-identical. Checked, not
  assumed.
* What could not be finished is filed with its instances named — **yes**,
  `SEAT_FINDING_THE_HERE_RELATIVE_VOCABULARY_IS_AN_UNBOUNDED_ALLOW_LIST_2026-09-19.md`.

## AND A RIVAL LANE LANDED THE SAME ITEM WHILE THIS WAS GATING — appended after promotion refused

`2957c2cc9` landed the same drawn item independently, between this turn's `surgical_land` and its
`promote_worktree_landing`. **This does not retract the results above** — every one was measured
before the collision was known — but two of them must be read differently now:

* **P1 stands as measured and is no longer the useful framing.** The other lane censused 16,083
  strings and produced a *curation rule* — a noun earns its place by having no comparison sense in
  the live corpus — plus three refused candidates with counter-examples. That is a better answer
  to "the list cannot be closed" than my partition proposal, which is withdrawn in the finding.
* **P2's refutation of my grammatical fix stands and is now doubly evidenced.** Their independent
  measurement refused `reading` and `line` for exactly the comparison-sense reason my grammatical
  lookahead failed to capture.

**What the collision does NOT touch is the participle axis.** Their census was `<noun>
above|below`; no run of it could return a participle. All eight `published above|below` pointers
were still live on `origin/main` after their landing — verified by grep against their landed file,
not assumed — including `_staleness_caveat`'s live TWO-HOME pointer. The merge keeps their nouns
whole and adds the participle branch, the eight repairs and the mutation leg.

**The seat's judgement on the duplicate-work check.** The draw warned of two rival claims and I
cleared both — correctly on the evidence available, since the rival was a *worker* lane whose claim
was not in `.delivery_lane_claims.json` at draw time. The check reads the claim store; a
concurrent lane not holding a claim there is invisible to it. Filed as a note on the mechanism, not
as a defect in this turn: the honest cost was one duplicated noun-audit, and the merge recovered
the non-duplicated half rather than discarding either side.

## One thing I had to add that the item did not ask for

Widening the vocabulary and then repairing every instance of it leaves the two new entries matching
**nothing** — delete `run` from the regex and no other leg in the file notices. That is this
project's recurring shape, so
`test_MUTATION_the_2026_09_19_widening_can_still_FIRE_on_the_wordings_it_was_added_for` holds the
branch open, keyed to the vocabulary rather than to today's page. Mutation-proven three ways, each
run against the real tree and reverted: drop `run` → reds; drop `published` → reds; widen
`_LANDMARK` to exempt everything → reds; restored → green.
