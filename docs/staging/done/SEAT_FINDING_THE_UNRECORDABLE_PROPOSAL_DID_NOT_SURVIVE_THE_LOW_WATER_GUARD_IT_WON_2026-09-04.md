**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The unrecordable proposal did not survive the low-water guard. It won.

*Delivery seat, 2026-09-04, claim `decide-the-proposal-side-of-a-low-water-episode-field-2026-09-04`.
Pre-registered before measurement:
`SEAT_PREREGISTRATION_WHAT_THE_UNSCREENED_PROPOSAL_SIDE_OF_A_SINCE_FIELD_ACTUALLY_DOES_2026-09-04.md`.*

---

## The question I was given, and the sentence in it that was backwards

`guard_episode` screens the PRIOR side of a `since_field` and deliberately not the PROPOSAL side.
The direction asked me to decide whether that should change, and named the risk in doing it:

> Screening the proposal could turn a data-dependent value into a silent field-clear, which is the
> under-reporting the whole class exists to cure.

That is a good reason to be careful and it is the wrong way round. `since_fields` is **LOW-water** —
earliest wins. An unrecordable proposal is not a weak value the guard tolerates; `0` is the
**earliest instant orderable**, so the guard *preferred* it:

```
guard_episode({"t": 1.7e9},                {"t": 0},                    since_fields=("t",))
    -> {"t": 0}
guard_episode({"t": "2026-09-04T10:00:00"}, {"t": "1970-01-01T00:00:00"}, since_fields=("t",))
    -> {"t": "1970-01-01T00:00:00"}
```

A single bad write took the field off a live 2026 episode and dated it to 1970. Screening the
proposal is therefore not a field-clear — **it makes the prior stand.** It is strictly *more*
remembering than what was there. The direction called this "a durability question, not an outage,
because both call sites are already safe at the render". Two of those three words held.

## The three carriers, and the reader nobody screened

| where | its proposal / read | measured, before |
|---|---|---|
| `ntfy_utils.record_delivery_outcome` | `previous.get("since_epoch", now)` — no screen | persisted `0` → written `0`, `since` stayed `1970-01-01T00:00:00Z` |
| `sim_runner.record_run_outcome` | `first if isinstance(first, (int, float)) else stamp` | `0` → `0`, `-1` → `-1`, **`True` → `True`** |
| `process_run_complete.record_publish_gate_failure` | `_is_episode_start(prev)` — screened | correct already |
| **`supervisor._producer_starved_active`** | `outage = (now - first_ts) if isinstance(first_ts, (int, float)) else 0.0` | **fires at 496,815.1h for `0`, `-1` and `True`** |

`isinstance(True, (int, float))` is `True` in Python. `episode_monotonic._is_num` has a docstring
about refusing exactly that value, for exactly this reason — and `True` walked in through a door
two modules away and came out the other side as a 496,815-hour outage.

### The reader is a live PRIORITY ZERO defect, not durability

The silly figure in the RUNG 1d prose is not the harm. The line under it is:

```python
if (streak >= PRODUCER_STARVED_MIN_FAILURES
        and outage > PRODUCER_STARVED_MIN_AGE_SECONDS   # 30 minutes
        and not superseded):
```

`outage > 30min` was satisfied by the **broken stamp alone**. A producer that had failed three
times in two minutes cleared the bar and drew a PRIORITY ZERO producer-starvation page. That is a
false page at the top of the ladder, on a rung explicitly built to outrank every product lane.

The direction's premise — *"the render is now closed (`recorded_instant_seconds`), so nothing
PUBLISHES 1970 from it any more"* — is true of `_episode_phrase` and of the publish-gate door, and
false here. This was the **fifth** hand-roll of one question and the sweep did not cover it. It is
the same shape memory already records: *a grep for a concept's NAME is blind to the MECHANISM
implemented without it*. Nothing in the timestamp-screen landing mentioned `first_failure_ts`.

## What landed

1. **`episode_monotonic._asserts_no_start`** — a proposed value that is orderable but names no
   recorded instant asserts the same thing `None` asserts. With a start on the prior side the
   **prior stands**; with none, the field is written as the `None` it means, so the echo loop stops
   refuelling itself. `_refuse` is untouched: the screen is asked only of values `_episode_key`
   could already order, so a misdeclared field still raises and a data-dependent value still cannot
   raise into the failure path being monitored. `True` and `NaN` were never in this set — they are
   unorderable and were already refused.
2. **`sim_runner`, `supervisor`, `ntfy_utils`** now ask `recorded_instant_seconds` instead of
   hand-rolling `isinstance`. One definition, five call sites, one answer.
3. **`ntfy_utils`'s rendered `since`** is derived from the carrier or is `None`, never inherited
   from disk. The first draft of that block claimed leaving it alone was "the honest branch"; it
   was not, because `since`'s own proposal is echoed off disk too. Corrected beside the claim.

Six mutations, each reverting one repair, are each killed by a named control in
`tests/background/test_an_unrecordable_proposal_beat_the_start_it_guarded.py`. The
rendered-string leg's first mutation **survived** — established as an equivalence, not a missing
test, and then made reachable by injecting the condition rather than left unprovable.

## Left open, deliberately, and it is the next item

**`EpisodeFieldTypeError` is silent on a cold start.** The prior screen `continue`s *before* the
proposal is type-checked, so:

```
guard_episode({"t": None},  {"t": "banana"}, since_fields=("t",))  ->  {"t": "banana"}   # no raise
guard_episode({"t": 1.7e9}, {"t": "banana"}, since_fields=("t",))  ->  REFUSED
```

The guard's own docstring says a misdeclared field is "a deterministic property of the call site
that the first test run surfaces". It is not surfaced on the first run — a cold state file has no
prior, so the one defence against a field that "reads as protection and is not" is exactly
backwards in reachability: quiet when the field is new, loud once it is working.

Not fixed in this landing, on the reasoning pre-committed before I measured it: widening where
`_refuse` fires would let a value echoed off disk reach a raise **inside the failure path of the
pipeline the guard monitors**, which is the harm the guard's whole fail direction exists to
prevent. It needs its own evidence about which call sites could actually be handed a corrupt
proposal, and it deserves a decision, not a rider on this one.
