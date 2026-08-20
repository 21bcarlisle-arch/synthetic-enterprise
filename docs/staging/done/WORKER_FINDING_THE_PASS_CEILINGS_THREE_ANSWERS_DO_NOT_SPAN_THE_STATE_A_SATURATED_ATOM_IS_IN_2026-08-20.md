**Severity:** LATENT · **Lane:** H_harness

# FINDING — the pass ceiling offers three answers, and a saturated atom can be in a fourth state none of them describes

**Found by:** the `EP6_wall_protocol_typing` BUILD self-refill draw, 2026-08-20 (pass 37). The
ceiling refused the draw, correctly. Establishing which of its three answers was true is what
surfaced a fourth.

## Observed, with evidence

Every claim is `observed-with-evidence` (R9), read off the live tree at HEAD `5f1553fea`.

`tools/discovery_pass_ceiling.py::STAGE_DECISIONS` gives a saturated `build`-stage atom exactly
three answers:

> land the level move, or record `infeasible_here` if the move needs an instrument this seat
> cannot obtain, or close it — another build pass at the same level is no longer an available
> answer

For `EP6_wall_protocol_typing` (35 passes, 28 since its level last moved, second worst in the
project) **none of the three is true**, and this was established from the atom's own blind-review
battery rather than from judgement:

| answer | why it is not true |
|---|---|
| land the level move | 9 of the battery's 12 DISQUALIFYING questions are outstanding; `tests/tools/test_cold_eyes_battery.py` refuses the move |
| record `infeasible_here` | 7 of those 9 (Q2, Q3, Q5, Q6, Q10, Q13, Q14) are **ordinary build work this seat can do** |
| close it | nine atoms (`EP7`–`EP15`) declare `depends_on: [EP6_wall_protocol_typing]` |

The fourth state, stated once: **the level TARGET is unreachable in this epoch, and build work
remains.** Q9 and Q15 require contract tests against real counterparty test environments (DCC
SIT/UIT/UEPT, CSS test, DIP). `tools/company_network_isolation.py` makes reaching them a WALL,
and doing so means contacting real organisations and spending real money — reserved classes 1
and 2. So `level_target: 3` on this atom cannot be met in epoch 3 by any amount of building,
while seven real build items sit in front of it.

## Why the notation cannot express it

`infeasible_here` is the closest fit and it is the wrong one, because the ceiling renders it as:

> BLOCKED ON AN INSTRUMENT, not on work … Neither promotable nor closable — the passes cannot
> move the level until the instrument lands, so **do not record another pass as if they could**.

Recording EP6 that way would retire seven items of live build work behind a sentence about an
instrument. That is the mirror-image abuse of the same notation: the notation exists to stop a
lane taking unbounded passes on an unmovable atom, and used here it would let a lane shed work
it simply had not done. Both misuses are silent.

## The class

Not FAIL-OPEN. This is `WORKER_FINDING_DECISION_WITHOUT_A_DO_NOTHING_OPTION` seen from the other
end — a decision surface whose option set does not span the state space, so the honest answer has
to be smuggled in as whichever wrong option is least damaging. The ceiling's own docstring already
records this class happening once: its single shipped verdict, *"promote to build, or close it"*,
told a `build`-stage atom to promote to the stage it was already in. That was repaired by making
the verdict stage-aware. This is the same defect one level out — the verdict is now right about
the STAGE and still silent about the EPOCH.

## Recommendation, not an ask (NEVER_ASK_WITHOUT_RECOMMENDING)

**A fourth answer: `target_unreachable_this_epoch`**, carrying the epoch that would lift it and a
live predicate, exactly as `infeasible_here` carries `blocks`/`predicate`/`needs`. It differs from
`infeasible_here` in the one way that matters: it does **not** suppress the draw. The atom keeps
being drawn for its remaining build work; what it stops doing is counting passes toward a level
that this epoch forbids. `tools.cold_eyes_battery.unpayable_here` is a working predicate of the
required shape and returns `('Q9','Q15')` today.

**Deliberately not taken in this tick.** Changing the ceiling in the same tick where it refuses my
own draw is precisely the shape `DIRECTOR_INSTRUCTION_PASS_CEILING_AND_EP1_EP6_PROMOTION_2026-08-19.md`
warns about — *"a file that grants a release, authored by the agent the release unblocks, is
exactly the shape that should be distrusted."* Queued per SELF_INTERRUPT_DISCIPLINE.

**The curriculum half is the director's and is flagged, not decided.** If `level_target: 3` is
unreachable for `EP6` in epoch 3, the target is either wrong or the atom is an epoch-4 item.
Targets are explicitly reserved to him under R13, so this is named here and nowhere else.

## A note on this document's own filename

It was first filed as `..._HAS_NO_ANSWER_FOR_A_TARGET_UNREACHABLE_THIS_EPOCH_...`, and the
commit gate refused it: `background/finding_classes.py:229` matches the bare pattern
`unreachable` and consolidated it into `no_caller_and_never_runs` — a class about **code
nothing reaches**, where this is about a **level target** no amount of building can reach in
this epoch. Same word, unrelated senses, and the classifier reads only the filename stem plus
the H1 heading (`finding_classes.py:321-327`), so no amount of body text could correct it.

Renamed, because consolidating a non-member would corrupt the class it joined — the fix is not
to make the matcher's verdict true by filing it under a heading I do not mean. Recorded here
rather than fixed silently: this is a second live instance of membership turning on a single
word in a title, after `WORKER_FINDING_ONE_OLD_LEVEL_MOVE_BOUGHT_AN_ATOM_FORTY_THREE_UNBOUNDED_
PASSES_2026-08-19.md`, which hit the same mechanism from the other side (it belonged to a class
and matched nothing, and was left visibly `unclassed` for the same reason). One word, two
opposite failures, one mechanism — worth a pattern with a word boundary and a code-shaped
qualifier rather than a bare substring.

## Related

- `tools/cold_eyes_battery.py` — the L3 criterion for EP6 as a closed set, shipped this pass.
- `WORKER_FINDING_ONE_OLD_LEVEL_MOVE_BOUGHT_AN_ATOM_FORTY_THREE_UNBOUNDED_PASSES_2026-08-19.md`
  — the same module, the previous defect, and its still-unbuilt half (the ceiling reaches only
  the idle discovery draw; `build` and `harden` rungs still do not consult it, which is why this
  draw reached me at all).

---

## DISPOSITION — BUILT AND LANDED, 2026-08-20, commit `a02ad8a2c` (EP6 pass 38)

`tools/discovery_pass_ceiling.py::exit_criterion()` + the fourth branch in `decisions()`.
Live on the tree, quoted from the CLI unedited:

> `EP6_wall_protocol_typing` [build] -- THE TARGET IS UNREACHABLE HERE **AND** BUILD WORK
> REMAINS -- both are true at once, and none of the three answers above says so. 2 of this
> atom's own recorded exit criteria need an act in a RESERVED class (Q9, Q15) ... 7 are
> ordinary build work (Q2, Q3, Q5, Q6, Q10, Q13, Q14) and must keep being drawn. Do NOT
> record `infeasible_here`: its verdict retires the payable half.

**Built differently from the recommendation above, and the difference is the point.** This
document proposed a new map field, `target_unreachable_this_epoch`, carrying its own
`blocks`/`predicate`/`needs` triple. What shipped has NO new field: the state is DERIVED from
records that already exist, because `unpayable_here` is already a strict subset of
`battery_outstanding`. Both halves non-empty is the fourth answer; unpayable with nothing
payable IS `infeasible_here` and the verdict now says so in those words; payable-only leaves
the ordinary build decision byte-identical. A field nobody remembers to set is a fifth way for
this to go quiet — the shape `WORKER_FINDING_A_MINT_DECLARES_STORE_FIELDS_IT_NEVER_WRITES`
names — and the derived reading cannot be forgotten because it is computed on every call.

**The self-grant objection this document raised is answered rather than waived.** It declined
to take the item because changing the ceiling in the tick the ceiling refuses is the shape the
director's own instruction file warns about. Pass 38 was not refused by the ceiling: it was
refused by the ORPHAN RATCHET, on pass 37's `tools/cold_eyes_battery.py` having no caller that
runs. Wiring the battery into the ceiling is what the ratchet demanded and what this finding
demanded — one edit, arrived at from two directions, neither of them a lane releasing itself.
And it grants nothing: the atom's level is still HELD at 2 and its nine outstanding criteria
still refuse an L3 record (`test_EP6_MAY_NOT_BE_RECORDED_AT_L3_WHILE_ITS_OWN_BATTERY_IS_OUTSTANDING`).

**R15:** 8 tests. The discriminator mutation was RUN, not asserted — replacing
`if crit["payable"]:` with `if True:` reds
`test_MUTATION_nothing_payable_left_is_the_THIRD_answer_and_must_not_be_masked`, which is the
dangerous direction (telling a genuinely instrument-blocked atom to keep drawing work that does
not exist). Both battery sources RAISE `CeilingUnavailable` when unreadable. Null controls:
an all-payable criterion keeps `STAGE_DECISIONS["build"]` verbatim; an atom with no recorded
battery returns `None` and is untouched.

**STILL OPEN, and it is not this document's:** whether `level_target: 3` is right for
`EP6_wall_protocol_typing` in epoch 3. Q9 and Q15 need reserved-class acts, so the target
cannot be met here by any amount of building. Sent to the director by NTFY with a
recommendation (retarget to 2 for this epoch; move Q9/Q15 to `EP19_counterparty_qualification_paths`).
Targets are his under R13. The seven payable items keep being drawn either way.
