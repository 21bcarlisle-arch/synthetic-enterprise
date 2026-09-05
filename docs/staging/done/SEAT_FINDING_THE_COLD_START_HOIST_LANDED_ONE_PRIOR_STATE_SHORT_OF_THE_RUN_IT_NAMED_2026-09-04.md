**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The cold-start hoist landed one prior state short of the run it was named after

*Delivery seat, 2026-09-04, claim
`decide-whether-the-episode-field-refusal-should-fire-on-a-cold-start-2026-09-04`.
Closing prediction **P5** of
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_UNSCREENED_PROPOSAL_SIDE_OF_A_SINCE_FIELD_ACTUALLY_DOES_2026-09-04.md`,
which pre-committed this as a SEPARATE decision before the proposal-side screen was measured.*

## Two lanes, one defect, and what that leaves

This turn and `90d7d3462` were in flight against the same defect at the same time —
`guard_episode`'s `EpisodeFieldTypeError` was written behind the prior screen, so the one refusal
protecting "wired this field in" from a no-op that reviews as protection was silent on a cold state
file. That lane landed first. **Its analysis and its decision are adopted, not re-litigated**, and
the rebuild this seat had ready was discarded rather than merged.

Two things are worth recording about the adoption, because a second lane arriving at the same fix
is the cheapest independent check this project ever gets:

* **Their harder call was the right one.** This seat's version exempted a *present-but-unreadable*
  prior from the refusal, on the reasoning that a carrier echoing its own disk value would meet the
  raise there. `90d7d3462` rejected that exemption on evidence instead of argument: every live
  `since_fields` carrier vets what it echoes with this module's own screen before proposing it.
  Re-checked here on the landed base — `_write_publish_gate_state`'s two callers pass either
  `prev_wedge_since if _is_episode_start(prev_wedge_since) else now` or a literal `None`. Their
  claim holds, the exemption bought nothing, and it is gone.
* **The two independent measurements agree on the defect**, table for table.

## What remains, and it is the run the fix is named after

The hoist went in at the top of the two **loops**. Both loops sit below
`if not isinstance(prev, Mapping): return out`. So on the landed base, measured:

    guard_episode({},   {"t": "banana"}, since_fields=("t",))    -> RAISES          (fixed)
    guard_episode({},   {"c": "banana"}, streak_fields=("c",))   -> RAISES          (fixed)
    guard_episode(None, {"t": "banana"}, since_fields=("t",))    -> {"t": "banana"} silently
    guard_episode(None, {"c": "banana"}, streak_fields=("c",))   -> {"c": "banana"} silently

**A missing KEY was covered; a missing FILE was not, and the missing file is the earlier state.**
The fix's own words are *"a field being wired in for the first time has no key in the state file at
all — that is not an edge case for a new field, it is the definition of one"*. A field wired into a
carrier that has never written is one state earlier than that, and it is not hypothetical:

* `sim_runner.record_run_outcome` — `guard_episode(previous or None, ...)`
* `process_run_complete._write_publish_gate_state` —
  `_read_publish_gate_state() if PUBLISH_GATE_STATE_FILE.exists() else None`

Both of the carriers most likely to gain a field meet the guard with `None`, not `{}`, on the write
that was supposed to surface a misdeclaration.

## Why it was missed, which is the transferable part

`None` was pinned green, deliberately, as one of *"the two doors that skip the loops entirely"* —
grouped with a non-Mapping prior. That grouping is the whole defect: it makes **"the guard cannot
read this"** and **"there is nothing to read"** one case, and this module turns on exactly that
difference everywhere else (`_absent` is "never a type error"; `_asserts_no_start` treats `None`
and a 1970 epoch as the same assertion; the fail direction is about a *corrupt* prior, not an
absent one).

A non-Mapping prior is data the guard cannot know — degrade, or it crashes the failure path of the
pipeline it monitors. `None` is the absence of data: nothing came off disk, so the proposal cannot
be an echo, and staying quiet protects nothing at all.

**The shape for the next session: when a hoist is described as "above the loop", ask what is above
the loop that it is still below.** An early return is invisible to a change reasoned about in terms
of statement order inside the body.

## The change

`prev is None` is read as `{}` — the cold start it is — before the loops. The non-Mapping door
stays exactly where it was, and `episode_closed` still returns first: a close is the caller's
evidenced claim that there is no episode left to protect.

## Evidence

`tests/background/test_the_type_refusal_was_silent_on_the_cold_start_that_needed_it.py`, extended
in place rather than forked into a rival file:

* `test_no_state_file_at_all_is_the_coldest_start_and_is_still_type_checked` — both loops refuse,
  and the SILENT half sits in the same control, because a check that refused a cold first write
  outright would pass the FIRES legs and break every carrier's first run.
* `test_the_two_doors_that_skip_the_loops_entirely_still_skip_them` — `None` removed from it and
  the non-Mapping door widened to three shapes, so the control now says what it means.
* `test_the_two_carriers_that_pass_none_still_write_on_their_very_first_run` — WIRED, not just
  built: `record_publish_gate_failure` and `record_run_outcome` driven with **no state file**, each
  asserting the file does not exist first, each required to persist a state its alarm can read.

Two mutations, neither survived:

| mutation | killed by |
|---|---|
| `prev is None` short-circuits again (the increment reverted) | `test_no_state_file_at_all_is_the_coldest_start...` |
| the non-Mapping door removed too (the over-reach this turn nearly shipped) | `test_the_two_doors_that_skip_the_loops_entirely...` |

158 tests green across the episode-guard family and the rung-1d draw before the increment; the full
suite after.

## Also recorded: the rung-1d control, fixed by the other lane

`test_rung_1d_still_fires_on_a_real_producer_outage` was red at HEAD, independently found by both
lanes within the hour: it pinned a 4h outage against `PRODUCER_STARVED_MIN_AGE_SECONDS`, which is
`_publish_cadence_seconds()` and moved to weekly in `78986f2aa`. The SILENT leg of a PRIORITY ZERO
rung was dead while the rung worked as designed. `90d7d3462` keyed it to the bar; verified here to
stay green at a 30-minute and a 30-day cadence. No further change needed.

## Class registration

Belongs to `publish_gate_and_wedge`.

*Declared 2026-09-05 by the delivery seat, on the director's instruction to fold findings into the class registers rather than leave them as individual documents. Classified on the MECHANISM THIS DOCUMENT DESCRIBES (its body), not on its title: the registered classifier greps titles, and the titles have outgrown its vocabulary — which is why 92 findings sat `unclassed` while the six classes held 138 instances. The body carries 5 matches for `publish_gate_and_wedge` against 1 for the runner-up, which is the threshold used; anything below it was left for a reader rather than graded from a sibling.*
