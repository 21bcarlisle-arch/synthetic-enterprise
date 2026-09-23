**Severity:** RECORDED · **Lane:** H_harness · **Class:** `publish_gate_and_wedge` · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The orientation writes a published feed and never commits it, so the publish gate is the first reader

**Claim:** `publish-the-withdrawal-the-belief-leg-did-not-survive`

## The three reds, and that one of them was already green

`.publish_gate_state.json` named three blocking tests, all of the here-relative-pointer family, all
measured at `git=32010eeb2` against a HEAD of `c50ea7f0b` — so `red_at_head: "not_established"` was
the honest reading and it was carried, again, from the state the previous record described.

Run at the merged base `d93c76825`, **two were red and one was already green**:

| named by the state file | at `d93c76825` |
|---|---|
| `test_a_here_relative_pointer_has_one_home.py::test_no_here_relative_pointer_is_composed_into_more_than_one_region` | **RED** |
| `test_a_producers_here_relative_pointer_has_one_home.py::test_no_feed_FIELD_that_reaches_two_regions_carries_a_here_relative_sentence` | **RED** |
| `test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer.py::...` | **already green** |

A state file's red list is a claim about the commit it was measured at, and a third of this one had
rotted. Worth saying because the count is what gets quoted: `total_red: 3` was the number in the
record, and three reds and two reds are different amounts of work.

## One cause, and it is a sentence

Both live reds name the same string: `site/data/delivery.json .what_it_decided.focus[2].why`,
carrying *"why it sits above the item below it rather than at the bottom"* and, later in the same
sentence, *"a machine item above a thesis item"*.

`site/harness/index.html` renders `what_it_decided.focus[].why` **twice** — at `#delivery-decided`
as an unordered "Chose" card (line 574) and at `#delivery-next` as a ranked `<ol>` (line 630). The
direction is true in the ranked list and means nothing in the card block. The rule is right and the
sentence was wrong.

Repaired at the source, `docs/direction/DIRECTION.yaml`, by naming the landmark rather than pointing
at it: *"ranked ahead of `say-what-the-ceiling-is-and-price-what-this-book-can-settle` rather than
last"*. `_LANDMARK` in the sweep only admits headline-relative wordings, which is correct for that
page and no use here, so the repair is to name the item — which is also what makes the claim
checkable by a reader in either region. Regenerated `site/data/delivery.json` through
`tools.generate_delivery_page`; the only payload delta is that sentence. All 17 tests across the
three files green.

## THE STRUCTURAL FINDING: every focus `why` is a two-home string by construction

`focus[].why` reaches two regions for every item, always. So **any** here-relative phrase a seat
writes into a direction record's `why` wedges the publish gate — this was not a one-off wording slip
and the next orientation can re-arm it in a sentence.

And the reason it reaches the gate rather than a commit hook is the part worth keeping:

> **The orientation writes `docs/direction/DIRECTION.yaml` and regenerates `site/data/delivery.json`,
> stages both, and never commits them.** Both sat `M ` in the index for hours.

The site lane runs the whole `site/` tree on any commit that touches it — so this family *would*
have been caught at write time by the ordinary route. It was not, because the orientation never
takes that route. The first thing in the architecture able to see the defect is the publisher, which
reads the WORKING tree, forty minutes per cycle, and wedges publishing when it finds one.

That is the same shape as the parent claim's own finding — a producer writing the working tree while
every control asks HEAD — arriving from the other direction. **Not repaired here, and deliberately
not repaired by adding a watcher:** the check already exists and already runs; what is missing is
that the orientation's own writes never reach it. The cheap move is for the orientation to commit
what it writes, not for a new gate to notice that it didn't. Filed for the seat that next touches
`background/delivery_seat.py`'s write path.

## AND THE WITHDRAWAL HAD ALREADY BEEN UN-PUBLISHED AGAIN, in the working tree, four hours later

This is the larger finding of the turn and it was not what I came for.

`site/data/value_arms.json` at HEAD carries `the_verdict_survives_pooling` and
`the_leg_holds_across_draws`. **The working copy carried neither** — `renewal_churn_belief` had
degraded to `available: False`, rendering the producer's own *"this grade was taken before the
reading carried its own stratification"* refusal in place of the withdrawal.

The clock cleared it, which is why the draw-time path check graded it only `[dirty]`:

| | |
|---|---|
| working copy mtime | `01:32:19` |
| last commit to that path (`e5e57c19a`) | `01:18:48` |

**The copy is NEWER than the landing and still carries LESS.** No stale-copy rule in the tree can
see that, because every one of them is a clock or a content-overlap question and this is neither:
it is a fresh regeneration from a stale INPUT. `docs/observability/svt_drift_belief_grade.json` —
the artefact carrying the `stratification` block both clauses derive from — was not refreshed to
HEAD until `01:40:01`, eight minutes after the publisher regenerated the feed from it.

So the previous record's warning was exactly right and arrived eight minutes too late to prevent
the thing it named: *"A publish taken before this would have degraded the withdrawal to
`available: False` on the live page."* It had already happened.

Repaired by re-running `tools.generate_value_arms_data` with the correct input in place:
`available: True`, both clauses back, and the headline sentence a reader meets now reads *"AND IT
DOES NOT SURVIVE POOLING ... AND IT DOES NOT SURVIVE A SECOND DRAW"*.

**The shape worth keeping: a producer run is only as fresh as its oldest input, and nothing here
grades that.** A regenerated artefact gets a new mtime, which exempts it from the clock rule, and
its content is a legitimate output of the producer — so it is invisible to both halves of the
stale-copy machinery while being, in substance, a revert. Filed as a class, not an instance.

## A second merge residue: two door tests were absent from the working tree

`site/test_the_renewal_belief_reaches_the_reader.py` and
`site/test_the_flat_churn_belief_reaches_the_reader.py` were present at HEAD and **absent from the
working tree** — arrived at HEAD through this turn's `--merge origin/main`, which advances the
commit without materialising new files into the shared working tree. The publisher runs the working
tree, so the door that grades the withdrawal would not have run at all.

`refresh_to_head` refuses both `refused_no_base` — it is built for a stale copy and has no branch
for an absent one. Restored from HEAD's blobs directly, guarded on non-existence so nothing could
be overwritten. Both green: 13 and 14 legs.

**And both read the INDEX, not the working tree** — `test_no_subject_of_this_file_is_read_from_the_working_tree` is an explicit relapse guard in the first of them. So those 27 green legs grade HEAD's feed and say nothing about the regenerated working copy above; what makes them grade it is `git add`, which is the commit below.

Worth noting for the tool: `refused_no_base` on a path that EXISTS at HEAD and not on disk is the
one case where writing HEAD's bytes is unambiguously safe, and it is the case the tool declines.

## What this leaves

`last_clean_publish` is still `2026-09-21 19:15`, `episode_clean_publishes: 0`. The two reds this
record clears were the ones the state file named; the gate runs 258 blocking files and a red it
never reached is still a red, which is the same caveat the previous record ended on and it has not
been retired. `tools/enumerate_publish_gate_reds.py` is the instrument that would settle it in one
pass at a clean HEAD, and it has not been run at this base.
