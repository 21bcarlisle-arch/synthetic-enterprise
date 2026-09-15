# PREREG — does requiring a control noun beside `blind` move only domain vocabulary?

**Filed:** 2026-09-15, before any classification was run and before `finding_classes.py` was edited.
**Lane:** Lane 0 delivery, claim `the-blind-pattern-must-co-occur-with-a-control-noun`.
**Severity:** RECORDED · **Lane:** H_harness
**Subject:** `background/finding_classes.py:225`, the `controls_that_cannot_fail` pattern
`\bblind(ed|s|ness)?\b`.

---

## The defect, as the record already states it

`SEAT_FINDING_THE_ENVELOPE_AND_THE_FORK_MERGE_ARE_ENTANGLED_ON_ONE_FILE_…_2026-09-15.md` (landed
`35aa7e8b1`) records that its own first draft title — *"The **blind** envelope is built, gated and
verified…"* — scored into `controls_that_cannot_fail`, a class about a control blind to its own
subject. It fired on *blind envelope* / *blind book* / *fabric-blind*, this project's domain
vocabulary for a book that cannot see a home. The author's response was to **re-title the document
to avoid the trigger word**, and to record that workaround as the recommended move. That is what
this claim exists to remove.

## What is already established, and is therefore NOT a prediction

Stated so nothing below reads as a prediction that was really a lookup:

- The pattern at `:225` is verbatim `\bblind(ed|s|ness)?\b`, compiled `re.I`, still live at
  `79f1bd9bc`. `35aa7e8b1` is an ancestor of `origin/main` and did not change it.
- `classify_subject` matches against `subject_of()` = the filename with underscores replaced by
  spaces, a newline, then the document's first `# ` heading. So a pattern that wants to see two
  tokens must cross a `\n` — `.` alone will not.
- `classifiable_documents()` globs the staging **root only**. The two PREREGs this cluster produced
  live in `records/` and are therefore out of the operational population; they are still classified
  here as SUBJECTS, because the pattern is what is on trial, not the room.

## The predictions

Written before any of the four measurements below was run.

**P1 — the cluster's own natural title misfiles today.** The withdrawn first-draft title *"The blind
envelope is built, gated and verified against the real feed"* classifies `controls_that_cannot_fail`
before the change, and **UNCLASSED** after it.

**P2 — both PREREG subjects misfile today.** `PREREG_DOES_THE_BLIND_ENVELOPE_DELTA_APPLY_AND_RENDER_
AT_ORIGIN_MAIN_2026-09-15` and `PREREG_DOES_THE_BLIND_ENVELOPE_RE_MERGE_ONTO_THE_POST_FORK_
PRODUCER_2026-09-15` both classify `controls_that_cannot_fail` before, and **UNCLASSED** after.

**P3 — the narrowing moves between 3 and 15 documents across all four rooms**, and **every** document
whose class it changes carries a domain `blind` (blind envelope, blind book, fabric-blind, blind
seed), not a control blind to its subject.

**P4 — P3 will have at least one exception, and it will be a control-blindness title carrying no
noun from the named set** (control, test, gate, guard, check, assertion, gauge). The candidate I
expect is `SEAT_PREREG_THE_SECOND_FLOOR_SEPARATES_A_CALLER_THAT_CATCHES_FROM_A_SUITE_THAT_IS_BLIND_
2026-09-06` — *suite* is the control noun there and it is not on the list.

P3 and P4 are deliberately in tension. If P4 holds, P3's "every" is refuted by the document P4
names, and the honest fix is to widen the noun set rather than to record the loss as acceptable —
**a narrowing is asymmetric, and only the false positive gets a comment unless the false negative is
measured too.** If P4 fails, the named set is sufficient as given and I will say so.

**P5 — `--check` is green before and after.** The change moves no document that is a live member of
a consolidated class, so the consolidation's own invariants do not move. If this is refuted, the
narrowing has removed a real member and the class document must be re-rendered in the same commit.

## What done means for this claim

1. `:225` only matches when a control noun co-occurs in the subject.
2. A control that FAILS if the narrowing is reverted, and fails for the right reason — one that
   asserts both directions: the domain phrase does NOT classify, and a genuine control-blindness
   phrase DOES. A one-sided control here would pass against a pattern that matches nothing.
3. The entanglement finding's own "still open" paragraph is corrected in place, beside the claim.
4. Landed and promoted.

## Results — measured 2026-09-15, corpus of 31 staged documents carrying a blind-token

Hand-labelled from the match context before any candidate rule was scored, so the ground truth does
not reference any design: **21 true positives** (a mechanism blind to its own subject), **10 false
positives** (6 × `BOARD_SPEC_*` "blind practitioner spec", 2 × blind-envelope PREREG, 1 ×
"fabric-blind arms", 1 × "blind spread / blind arm").

*(The first scoring pass defined the false-positive label with the candidate rule inside it, which
made "design B keeps 0 false positives" tautological. It was relabelled by hand and re-run; the
numbers below are from the non-circular pass.)*

**P1 — HELD.** The withdrawn first-draft title classifies `controls_that_cannot_fail` before and
**UNCLASSED** after.

**P2 — HELD.** Both blind-envelope PREREG subjects classified `controls_that_cannot_fail` before
and are UNCLASSED after.

**P3 — REFUTED on the count, HELD on the direction.** The rule I shipped changes 10 documents, in
range; but the rule P3 was *about* — the control-noun requirement — changes **26**, outside the
stated 3–15. Every document either rule *removes* does carry a domain or method `blind`, so the
"every" clause holds for the shipped rule. It does not hold for the directed one, which removes 16
documents that are nothing of the kind.

**P4 — HELD, and badly understated.** I predicted "at least one exception" and named
`SEAT_PREREG_…_A_SUITE_THAT_IS_BLIND` as the candidate. That document is indeed one of them. **There
are sixteen.** The named noun set (control, test, gate, guard, check, assertion, gauge) misses the
way this project actually names controls — census, oracle, flag, gap, repair, rule, band, digest,
route, clause, field — and one of the sixteen is the only live root member of the class.

**P4 also has a consequence the prereg did not anticipate.** It said the honest fix would be to
*widen the noun set*. That is wrong too: widening it re-admits the cluster, because a finding about
the blind envelope names the envelope's door **TEST** or its eight skipped **CONTROLS** by
construction. The co-occurrence rule is not merely under-tuned; it is the wrong discriminator.

**P5 — HELD, AND THE GREEN MEANS NOTHING. This is the most important line in the document.**

What I wrote first: *"`--check` is PASS before and after… The only root member keeps its class. The
directed rule would have dropped it, and `--check` would have gone red."* Kept here rather than
revised, because **the second and third sentences are false and I landed them in `7646e25f0`
before checking either.**

Measured afterwards:

| | live root members | archived | refused out-of-lane | `check()` |
|---|---|---|---|---|
| shipped (predicative) | 0 | 35 | 1 | PASS |
| refuted (control-noun) | 0 | 35 | 0 | PASS |

`controls_that_cannot_fail` has **no live root members at all**. The document I called "the only
root member" is lane `A_strategy_governance`, so the lane guard refuses it consolidation — under the
directed rule it would simply have stopped being visible as contested (`refused_out_of_lane` 1 → 0),
with nothing reporting it.

And `--check` is **PASS under both**. The 16 documents the directed rule would have damaged are all
in `done/`, and `archived_instances()` reads the class document's own instance list and checks only
that the file still exists — it never re-classifies. So the directed rule would have stranded
**seven** archived instances under a class they no longer belong to, and every gate in this
repository would have stayed green.

**P5 was therefore satisfied by a control that cannot see the thing P5 was asking about.** The
prediction was badly designed, not merely wrongly reasoned: I chose as my safety check the one
control structurally incapable of failing on this change. Filed with its remedy as
`SEAT_FINDING_THE_CLASS_REGISTER_IS_BLIND_TO_A_PATTERN_CHANGE_OVER_ITS_ALREADY_ARCHIVED_INSTANCES_2026-09-15.md`.

## What the measurement chose instead

`blind` must be used **predicatively about a mechanism**: blind *to*, blind *in*/*about*/*toward*,
blind*ness*, *blinds*, blind *spot*, or *is/was/goes/became* blind. Scored against the same corpus:
**20 of 21 true positives kept, 0 of 10 false positives kept.** The single true positive it drops is
this PREREG, which names `blind` as a token rather than using it — out of the root population in any
case.

Grammar, not vocabulary, is what separates the two populations, and no amount of reasoning about the
finding's text would have reached that. It came from printing the corpus.

A **blacklist of the domain compounds** (`blind envelope|book|arm|spread|practitioner`) scores
identically today and was rejected: it needs a new entry every time the domain coins a noun, and it
fails OPEN — the day someone writes *blind tariff* the misfiling is back and nothing says so.

## Done, against the four criteria above

1. ✅ `background/finding_classes.py` — three predicative patterns replace the bare one.
2. ✅ `tests/background/test_finding_classes.py` — 13 legs in three groups (domain vocabulary is
   NOT classed; a genuine control-blindness title IS; a domain blind beside a control noun is NOT),
   plus two mutation proofs that load a real mutated module: reverting to the bare pattern refiles
   all five domain subjects, and substituting the co-occurrence rule drops the true positives and
   re-admits the cluster.
3. ✅ The entanglement finding's "still open" paragraph is corrected in place and its recommended
   workaround withdrawn.
4. Landed and promoted — see the commit this document lands in.
