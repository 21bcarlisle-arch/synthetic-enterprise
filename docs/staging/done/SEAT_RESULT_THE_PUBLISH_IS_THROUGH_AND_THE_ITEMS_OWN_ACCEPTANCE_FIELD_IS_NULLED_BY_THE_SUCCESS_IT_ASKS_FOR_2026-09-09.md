**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — land-the-w2-28-level-claim-or-lower-it-then-publish-and-take-the-next-refusal) · **Class:** publish_gate_and_wedge

# RESULT — the publish is through, and the item's own acceptance field is nulled by the success it asks for

The wedge is cleared: 36 hours dark, 34 consecutive failures, `last_clean_publish: null`. The publish
landed as `a2f0d07ca` and reached origin, the episode is CLOSED, and the figures on the live page are
from this morning. The item's stated acceptance test is still not met — and cannot be, by this
outcome or any other.

---

## What the tick did

| step | outcome |
|---|---|
| level-promotion gate | `rc=0` at draw — the item's named cause landed in `31aff7abd` before this tick |
| the real blocker | the shared **index** held the failed 04:44 cycle's pre-landing blobs — [finding](SEAT_FINDING_THE_SHARED_INDEX_STILL_HELD_THE_FAILED_CYCLES_PRE_LANDING_BLOBS_SO_THE_NEXT_PLAIN_COMMIT_WOULD_HAVE_REVERTED_THE_CONTROL_2026-09-09.md) |
| repair | `git reset HEAD --` on the four paths; disk already equalled HEAD, so all four went clean, and 206 other staged paths were left as their lanes staged them |
| finding landed | `5006fa1dd`, bound to the claim |
| publish | **LANDED `a2f0d07ca`**, 128 paths, gated in a clean extract of the tree the commit created |
| origin | `origin/main = a2f0d07ca`; `5006fa1dd` is an ancestor, so both reached origin |
| wedge | `episode_failures` 34 → **0**, `wedge_since` → **null**, episode CLOSED, alarm re-armed |
| figures at origin | `site/data/publish_provenance.json` `written_at: 2026-09-09T06:38:18Z`, 251 accounts, 10,924 bills, £677,289.18 |

The publisher hit `fatal: cannot lock ref 'HEAD': is at a2f0d07ca … but expected 5006fa1dd` on the
way — the base-moved race, caused by my own landing going in underneath it. It auto-retried and
landed. Not hand-retried, and it must not be.

## The correction, beside the claim

The item defined done as *"a publish with a non-null `last_clean_publish` and a figure at origin
whose timestamp is from tonight"*. The second half is met. **The first half cannot be met by a
publish that clears the wedge**, and that is by design, not by defect:

```python
"last_clean_publish": None if episode_closed else stamp,     # process_run_complete.py:7516
```

and the carry is gated the same way (`if not episode_closed and … is None: out[…] = prior[…]`, line
6508). Both fields are **episode-scoped**, and the control that pins it says why —
`test_draining_the_queue_to_zero_closes_the_episode_and_forgets_the_publishes`: *"episode-scoped
means it MUST reset on a real close. A field that only ever accumulates would make every later
episode read as intermittent."*

So `last_clean_publish` is non-null only on a clean publish that did **not** drain the queue. The
publish that fully recovers the gate is precisely the one that erases the timestamp saying so.
Measured after this cycle: `last_clean_publish: None`, `episode_failures: 0`, `wedge_since: None`.

**This is not a defect to fix in the publisher.** The control is keyed to the property, not to
today's answer, and its reason is sound. The defect is in reading the field from outside the episode
it is scoped to.

## Why this costs a re-drawn item every time

`last_clean_publish: null` has two disjoint meanings and no way to tell them apart from the field
alone:

| state | `last_clean_publish` | `wedge_since` | `episode_failures` |
|---|---|---|---|
| wedged, nothing clean this episode | `null` | a timestamp | > 0 |
| **recovered, episode closed** | `null` | `null` | 0 |

Code never confuses them — the only read is inside `_episode_phrase`, gated on
`clean_publishes > 0`, so it is consulted only while an episode is open. **Prose does.** The Lane 0
item, the doorbell that carried it, `background/origin_reconcile.py` (lines 543 and 887) and three
test docstrings all cite `last_clean_publish: null` as evidence of a wedge. It is evidence of a
wedge only when read together with `wedge_since`, and this item has now been drawn twice with an
acceptance test that success cannot satisfy — which is exactly how a cleared wedge gets re-drawn as
an open one.

Same class as the memory's *"publishing the newest artefact unsatisfies every control keyed to the
staleness it fixes"*, reached from the other side: here the field is correct and episode-scoped, and
the readers quoting it have dropped the scope.

## What is next

- **The wedge signal is the pair, never the field.** `wedge_since is not None` is the reading that
  means wedged; `last_clean_publish` alone means nothing outside an open episode. Anything that
  builds a Lane 0 item, an alarm line or a doorbell from this state file should say
  `wedge_since`/`episode_failures`, and the item's done-test should be
  *`wedge_since` is null and a figure at origin carries tonight's date* — both of which this cycle
  now satisfies.
- The three prose sites that read the field as a wedge indicator (`origin_reconcile.py:543`, `:887`,
  and the test docstrings citing "`last_clean_publish: null` and N consecutive failures") are
  accurate about the episodes they describe and wrong as a general rule. They are worth a one-line
  qualification rather than a rewrite.
- Not done this tick, and named rather than left implied: `W2_28` is still at `level_current: 1`
  against `level_target: 3`, and the `OUTSTANDING` debt row for `simulation.weather_cell_siting`
  stays — its declaration is still only another lane's uncommitted edit, so the row is load-bearing
  at HEAD. The item's instruction to delete it is refuted in the finding above.
