**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `publish_gate_and_wedge` (primary) · `control_cannot_fail` (secondary)

# The remedy a live continuation names would have been green throughout the outage it is meant to catch

**Claim:** `the-publisher-cycle-the-withdrawal-item-still-owes-after-its-continuation-was-retired`
**Pre-registration:** `SEAT_PREREG_WOULD_THE_PROPOSED_WORKING_TREE_MODE_HAVE_CAUGHT_THE_WEDGE_2026-09-23.md`
(same room) — **three predictions, all three confirmed.** They are recorded there before the
measurement and are not restated flatteringly here.

## What was asked, and what was already known

The item asks for ONE publisher cycle to complete from a tree level with origin. The prior seat
(`SEAT_RESULT_THE_PUBLISHER_IS_WEDGED_BY_AN_UNCOMMITTED_TEST_LEG…_2026-09-23.md`) had already
established the live cause and I re-measured rather than inherited it. It holds, three hours on:

* Both reds the drawn item enumerated are **green** at `0637be0f1` — measured here, not assumed:
  `test_atom_notes_store::test_declarations_match_the_store` **1 passed**,
  `test_the_unsourced_threshold_is_MARKED_where_a_reader_meets_it` **1 passed**.
* The same site test is **red in the shared tree**, and the register agrees:
  `PUBLISH_STANDING_RED_REGISTER.md` shows it standing **6 refusal cycles**, first blocked
  2026-09-23T06:31. `episode_clean_publishes` 0; `wedge_since` 2026-09-21T20:40 — **two days**.

The chain, with each link's status read just now:

| Link | Status | Names the reading? |
|---|---|---|
| `tools/churn_belief_size_response.py` | **dirty**, 07:25 | **yes** — the new literal |
| `docs/observability/churn_belief_size_response.json` | **clean**, 06:40 | no — written BEFORE the edit |
| `tools/generate_value_arms_data.py` | dirty | pass-through only |
| `site/data/value_arms.json` | **dirty**, 06:40 | no |
| `site/test_the_flat_churn_belief_reaches_the_reader.py` | **dirty**, 07:22 | **demands** it |

The stale link is the **intermediate**, and its mtime proves it: 06:40, forty-five minutes older
than the producer edit that was supposed to feed it.

## The new result: the filed remedy is insufficient, on two independent counts

The live continuation
`the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher`
states its remedy as settled:

> Give `tools/published_feed_regeneration_check.py` a WORKING-TREE mode, and add the
> `churn_belief_size` chain to whatever it walks.

**Both halves fail, and the mode is not the binding constraint.**

**1. A working-tree mode would have been GREEN through the whole outage.**
`tools/generate_value_arms_data.py:15260` is the entire derivation:

```python
"the_thresholds_own_origin": knee.get("the_thresholds_own_origin"),
```

A bare `dict.get` off the stored intermediate. The function's own docstring states the rule it
follows — *"THE SENTENCE IS THE ARTEFACT'S OWN `reading` AND IS NOT COMPOSED HERE… the words are
lifted verbatim"* — which is correct design and is exactly why the check cannot bite. Regenerating
`value_arms.json` from **any** standpoint, in **any** tree, re-reads the same stale intermediate and
reproduces byte-identical output. Feed and generator **agree**. The control reports green while the
publisher is refused every cycle.

The mode changes which tree is regenerated in. It cannot change the fact that the compared pair is
already consistent. **The broken relation is one link upstream of any pair this module compares.**

**2. The relation is outside the module's addressable space, so "add the chain" is not a list edit.**
`FEED_DIR = "site/data"`; `_committed_feed` reads `HEAD:site/data/<name>`; the string
`observability` does not occur in the module. `docs/observability/churn_belief_size_response.json`
is not an unlisted feed — it is not a feed. Covering it means giving the module a second relation
kind (*derived artefact ← its producer*, arbitrary path, working-tree standpoint), not appending a
row to `COVERED_FEEDS`.

**3. Incidentally: `value_arms.json` is not in `COVERED_FEEDS` at all** — the set is eight feeds and
this is not one. The two occurrences of the name in that module are docstring prose about its
fifteen scattered commit stamps. So even the feed-level relation is unchecked here today.

## Why this matters more than the instance

A remedy sentence sitting in a live continuation is read as established by whoever draws it next —
this repository's stated recurring shape, applied to its own queue. Built as written, it would have
produced a control that was green for two days across a live publish outage, and the greenness
would have been taken as evidence the chain was sound. **That is a control that cannot fail, and it
would have been built on purpose.**

The prereg for this is in the same room and was written first, because a remedy I expected to be
wrong is exactly the kind I could talk myself into having predicted.

## The instance: not dischargeable from here, and the one command that discharges it

The remedy is unchanged from the prior seat's and I confirm it rather than re-deriving it:

```
python3 -m tools.churn_belief_size_response       # rewrite the stale intermediate from the edited producer
python3 -m tools.generate_value_arms_data          # carry the sentence onto the feed
```

**I did not run it, and the reason is not ownership etiquette.** The new sentence is a hardcoded
literal inside the *uncommitted* `tools/churn_belief_size_response.py` (verified: the diff adds it
as a string constant; it is not derived from `churn_model`, whose HEAD copy does name the reading).
My worktree carries HEAD's bytes, where that literal does not exist. Regenerating here produces the
OLD sentence and landing it would revert the other lane's work rather than complete it. The two
commands must run in the shared tree, where the producer edit lives.

`PUBLISH_STANDING_RED_REGISTER.md` is explicit that a publisher-blocking red has no disposition and
is actioned only by making the test green. That remains true and this finding does not forgive it —
it records that the discharge requires the shared tree and names precisely what to run there.

## What done means, restated and unchanged

`docs/observability/.publish_gate_state.json` shows `episode_clean_publishes > 0` with
`last_clean_publish` later than 2026-09-23T07:30, from a tree level with origin.

## What is now specified for whoever builds the control

Not a mode flag. A second relation kind, with its own failing case available on day one: **a derived
artefact whose producer is NEWER than it, anywhere in the tree, in the WORKING-TREE standpoint.**
The mtime pair above (producer 07:25, artefact 06:40) is a real instance to key the first leg to —
and per this repo's own rule the leg must be keyed to the property, not to today's answer, because
this instance will be discharged within the hour by the two commands above.
