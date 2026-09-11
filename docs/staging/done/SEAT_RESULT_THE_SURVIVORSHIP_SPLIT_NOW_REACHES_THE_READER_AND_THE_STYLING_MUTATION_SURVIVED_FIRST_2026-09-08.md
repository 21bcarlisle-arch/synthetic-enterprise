**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — no attainable book can read the effect the skill instrument measured) · **Class:** no_caller_and_never_runs

# RESULT — the survivorship split now reaches the reader, and the mutation that mattered survived first

`SEAT_RESULT_THE_UNSCORED_DECISIONS_ARE_EXACTLY_THE_DEPARTURES...` (2026-09-08) landed the
measurement and said plainly what it had NOT done:

> *"The rendered surface. The data layer refuses honestly; no page element reads
> `method_skill.survivorship` yet, so by this project's own rule ("done means the rendered value
> changed") the reader-facing half is NOT done and is not claimed to be."*

That half is now done. The drawn Lane 0 premise itself is spent — its question was answered at
HEAD in `2cfc4ec5f`, and re-measuring it would have re-run a landed claim.

## What landed

**`survivorshipBlock(sv)` in `site/capabilities/index.html`**, rendered immediately after
`skillFunnel(msk.drop_out)` — the same population re-described, and the funnel's own consequence
(*"only a larger settled book moves it"*) is exactly what it qualifies.

- **Available branch:** the four counts as a table — dropped for want of a settled row, of those
  the world recorded as departures, of those not attributable to one, and **SCORED decisions the
  world recorded as a departure** — followed by the run's own verdict. The refuting count is
  printed as plainly as the others: a page that hid it while printing the verdict could not tell
  a reader the two had come apart.
- **Withheld branch:** the absence, on the surface. Every run on disk predates the split, so this
  is the branch the live page is in today.
- **No sentence is authored in the door.** `run_value_cycle_ab._survivorship_reading` composes the
  verdict from the counts and the page renders it. A door that typed the survivor-conditioned
  paragraph would go on asserting it after the run that refutes it.

## The battery — 6 mutations, 6 killed, and the sixth only after a fix

| # | mutation | outcome |
|---|---|---|
| 1 | drop `survivorshipBlock` from the render | killed (3 controls) |
| 2 | hard-code the conditioned paragraph in place of `sv.reading` | killed |
| 3 | render the refusal unconditionally (`if (true)`) | killed |
| 4 | read `msk.drop_out` instead of `msk.survivorship` | killed |
| 5 | style the verdict amber on every input | **SURVIVED** → fixed → killed |
| 6 | re-borrow the reserved phrase in the refusal | killed |
| 7 | render one sentence for both absences (feed-predates and run-predates) | killed |

**Reachability was proved before anything asserted what the block says.** The live feed is in the
withheld branch, so every control here would have passed against a door with no available branch
at all. `test_the_survivorship_split_CAN_reach_the_reader_at_all` drives the branch that will
exist the day a run carries the measurement.

**M5 was a missing test, not an equivalence, and it is the one worth recording.** Every control in
this door reads `_text()` — tags stripped — so a mutation touching only MARKUP survives all of
them. On this page markup carries meaning: amber qualifies the headline figure, muted footnotes
it, and a block styled amber on every input tells the reader every run is survivor-conditioned.
`_render(raw=True)` was added for that one claim, and the docstring says to use it only for a
claim about styling — a figure asserted against raw HTML reds on a correct page, which is what
`_text` exists to prevent.

## THE THIRD STATE, which only the commit gate could have found

The block shipped with two branches — the run measured the split, or the run predates it — and
that was wrong. **The FEED can predate the producer.** `_skill_survivorship` writes a withheld
branch carrying its own named reason, but a `value_arms.json` generated before that function
existed carries no `survivorship` key at all, so `sv` is `undefined` in the door. The published
feed at HEAD is exactly that.

The consequence was a refusal that did not name its reason — `prose(sv ? sv.reason : "")` rendered
**"Not measured by this run."** with nothing after it — which is the one thing a refusal on this
page may not be.

**No local run could have caught it, and that is the durable half.** Every run in this working
tree read a REGENERATED `value_arms.json` carrying the key, so the withheld branch was reached and
the no-key branch was unreachable. The commit gate builds the tree the commit *would* create, read
HEAD's feed, and raised `KeyError: 'survivorship'` on my own control. This is the sign-flip shape:
uncommitted state in the shared tree hid a defect that is present in every clean extract.

Two things changed:

1. **The door tells the two absences apart.** A run predating the split is not ours to fix; a feed
   predating the producer is, and the page now says so — *"That one is OURS: regenerating the feed
   from a run that measured the split is all it needs."*
2. **Both absences are DRIVEN in the control, not observed.** Whichever state the published feed
   is in, the other is locally unreachable, so the partition control now renders both from driven
   feeds and asserts they differ. A page that rendered one sentence for both could not tell a
   reader which absence anyone can act on.

Verified in a clean `git archive HEAD` extract with only these three files copied in — 90 passed,
1 skipped — because a green in this working tree is not evidence about the tree being committed.

## What the first draft got wrong, kept beside the fix

The refusal originally read **"We cannot tell from this run"** and turned
`test_a_reading_that_CLEARS_its_null_does_not_say_it` red. The existing control was right. That
phrase is the director's, reserved on this page for one verdict — the concordance sitting inside
its null — and two different unknowns wearing one form of words is the recurring shape this
project pays for. A reading that cannot be told from chance and a split a run never took are
different states. The wording is now **"Not measured by this run"**.

A page-wide assertion that the phrase is absent was then added and was itself wrong: the live page
says exactly that about the concordance, correctly. It is removed, and the reason is a comment
beside where it was — the reservation is enforced by the control that already caught the
collision, demonstrably, and a control that only guards my own control is not worth having.

## THE RECEIPT, ADDED 2026-09-08 BY THE LANE THAT LANDED IT — `549026bd0`

When this document was written the work it describes was **in the working tree and on no branch**.
`SEAT_FINDING_THE_WHOLE_VALUE_ARMS_CLUSTER_IS_TWO_LANES_IN_FIVE_FILES_AND_A_PATHSPEC_LAND_DELETES_EITHER_HALF_2026-09-08.md`
found it there and asked for exactly this line: *"a result doc is not a receipt."* It is one now.

`549026bd0` lands the survivorship half **from HEAD**, not from the worktree copy — the bytes are
HEAD plus the survivorship hunks only, committed with `surgical_land --content` so the shared tree
was never swapped. Verified: receipt consistent, tree `16a15f546`, gate-rc 0; pushed to origin.
Every file loses nothing from HEAD, checked by symbol set rather than by diffstat, because
`isolate_hunks --keep /survivorship/` on the producer also reverted `_the_level_legs_family` — a
symbol `ea6101870` had just landed — and a diffstat cannot see that.

**What a reader meets today is the refusal branch, not the table.** The live feed's split is
`available: false` with its own named reason, so item 1 below is still the next increment. The
block distinguishes that state from the third one — a feed predating the producer entirely — which
is why the refusal names which absence it is.

## What is next, unchanged from the parent finding

1. **No run carries the split.** Both `value_cycle_ab_s1_three_arm.json` (08-31) and
   `..._20260908.json` were generated at 00:19 on 2026-09-08, before `_survivorship` landed at
   03:48. So the page correctly renders the absence and will go on doing so until an A/B run is
   taken with the current code. **That is the next increment, and it is a run, not an edit.**
2. **The page is also still a run behind** on its figures — `THREE_ARM_PATH` is the 08-31 run.
   Deliberately not moved here: `CURRENT_WORLD_THREE_ARM_PATH` publishes the 09-08 run beside it
   by design, and the figure and its bound (`NOISE_FLOOR_PATH`) move together or the page loses
   its error bar. One variable at a time.
3. **Pre-register the replacement estimand** before building it — fixed horizon from term start,
   counting a departure as the small-or-zero value it produced. The parent finding's prediction
   stands and is not re-stated here.
