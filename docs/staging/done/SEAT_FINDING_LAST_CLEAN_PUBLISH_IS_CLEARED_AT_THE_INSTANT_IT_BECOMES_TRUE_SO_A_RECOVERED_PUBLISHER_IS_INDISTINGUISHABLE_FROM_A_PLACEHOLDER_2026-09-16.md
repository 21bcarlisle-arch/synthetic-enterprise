**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Class:** publish_gate_and_wedge · **Atom:** (Lane 0 delivery — confirm the first clean publish after the split pair landed)

# `last_clean_publish` is set to `None` at the instant it becomes true, so no reader can ever observe a clean publish that closed its episode

**Filed 2026-09-16, delivery seat.** Found while trying to satisfy a drawn item's done-condition and
discovering the condition cannot be satisfied — the thread CLAUDE.md says to follow rather than
route around.

---

## The claim that is made on it

The Lane 0 item `publish-wedge-confirm-the-first-clean-publish-after-the-split-pair-landed` states
its done-condition as, verbatim:

> read `docs/observability/.publish_gate_state.json` for `last_clean_publish != null` and
> `episode_failures == 0`

That is a reasonable-sounding reading of the field names, and it is what any reader would write. It
is also unsatisfiable, and the item could have been re-drawn against a perfectly healthy publisher
indefinitely.

## The mechanism, established from code and requiring no measurement

Three pieces compose:

1. `record_publish_gate_success` writes `"last_clean_publish": None if episode_closed else stamp`,
   and proposes `"episode_failures": 0` on **both** branches.
2. `_write_publish_gate_state` carries a prior `last_clean_publish` forward only
   `if not episode_closed`.
3. `guard_episode` returns the proposal untouched when `episode_closed` is true, and otherwise
   takes `max(old, proposed)` over `streak_fields = ("episode_failures", "episode_clean_publishes")`
   — they are HIGH-water, by that function's own contract.

So the success path has exactly two exits and neither satisfies both legs:

| exit | `episode_failures` | `last_clean_publish` |
|---|---|---|
| episode **closed** (`pending == 0`) | `0` ✓ | `None` ✗ |
| episode **open** (`pending > 0`) | preserved, e.g. `34` ✗ | `stamp` ✓ |

**The two legs are mutually exclusive by construction.** This is a property of the code, not an
observation about today's state, which is why it is asserted here rather than measured.

## Why this is a defect in the record and not only in the item's wording

At the instant `last_clean_publish` is most true — the publish that drained the queue and closed a
146-hour episode — it is written as `None`. The field's own comment in `_write_publish_gate_state`
calls it "a LATEST-wins timestamp, which is the opposite ordering to `since_fields`". The close
makes it episode-scoped, which is what `episode_clean_publishes` already is and what this field's
name says it is not.

The consequence is a live-state hole with a name already in this queue. A cleanly closed episode
leaves:

    failures: []   ·   alerted_at: null   ·   wedge_since: null
    episode_failures: 0   ·   episode_clean_publishes: 0   ·   last_clean_publish: null

**That is byte-for-byte the reading a fresh linked worktree gets from the two-month-old tracked
placeholder** — see the sibling finding
`SEAT_FINDING_A_LIVE_RECORD_IS_TRACKED_SO_EVERY_WORKTREE_READS_A_TWO_MONTH_OLD_PLACEHOLDER_AS_LIVE_STATE_2026-09-16.md`,
whose committed content is `{"alerted_at": null, "failures": []}`. A recovered publisher and one
that has never run are therefore **indistinguishable in this file**. A closed episode carries no
positive evidence that any publish ever succeeded — only the absence of failures, and absence is
exactly what the placeholder also asserts.

`shared_tree_live_record` closed the *read-side* half of that pair (a worktree now reaches the
shared tree's copy). It cannot close this half: the shared tree's own copy does not carry the fact
either.

## The remedy, and the one control that has to move with it

Let `last_clean_publish` take `stamp` on **both** exits — an episode close clears the EPISODE, not
the evidence that a publish happened. `episode_clean_publishes` must keep resetting: it is a counter
scoped to the episode and its name says so.

That is one line, and it is not free. `test_draining_the_queue_to_zero_closes_the_episode_and_forgets_the_publishes`
asserts `st["last_clean_publish"] is None` on the close path, under the rationale *"episode-scoped
means it MUST reset on a real close. A field that only ever accumulates would make every later
episode read as intermittent."* **That rationale is sound for the counter and does not transfer to
the timestamp**: a timestamp does not accumulate, and `_episode_phrase` gates its intermittent-wedge
branch on `clean_publishes > 0`, never on `last_clean_publish` — which the file's own null control
(`test_a_genuinely_unbroken_outage_still_reads_as_one`) pins. So the phrase cannot change, and that
prediction is the first thing to falsify before touching the assertion.

**Not done in this turn, deliberately.** The publisher was wedged on a different red, and the
unwedge is what moves the claim; bundling a change to a mutation-proven control's assertion with it
would mean a mistake in the second loses the first. This wants its own turn and its own
pre-registration, and the prediction above is written here so that turn cannot file it after the
answer is known.

## How it was found

`PREREG_IS_THE_COPY_TEST_STILL_RED_AT_HEAD_AFTER_THE_SPLIT_PAIR_LANDED_2026-09-16.md` correctly
refused to release the claim on a green test. Trying to satisfy the done-condition it deferred to,
rather than re-reading the same file and waiting again, is what surfaced this.
