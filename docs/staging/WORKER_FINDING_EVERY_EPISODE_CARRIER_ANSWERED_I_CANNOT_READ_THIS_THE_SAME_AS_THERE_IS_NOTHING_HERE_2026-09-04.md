# WORKER FINDING — every episode carrier answered "I cannot read this" the same as "there is nothing here"

**Date:** 2026-09-04
**Class:** R10 (an absurdity is fixed as a class, not an instance) · R15 fail-silent
**Severity:** BLOCKING · **Lane:** H_harness — three of the carriers crashed on two members of the
partition, on the supervisor tick, the run-marker sweep, and every ntfy send.
**Status:** REPAIRED in this commit for the five carriers named below. The residual is named at the
bottom and is not repaired.

---

## What was drawn

The seat's direction, after `guard_episode`'s cold-start refusal was fixed twice by two lanes on
2026-09-04 and was **still** half a fix after both: sweep every guard the self-clearing-alarm
census enumerates for the same ABSENT-vs-PRESENT-BUT-UNREADABLE conflation, and print the verdict
across the WHOLE partition of prior states rather than the shapes the loop bodies happen to see.

## What the partition showed

`background/episode_monotonic.py` argues the distinction at length and turns on it in code — a
non-Mapping prior is *present and unreadable*, so the guard degrades; `None` is *absent*, so
nothing can be an echo. **The same conflation was one level UP, in the loader of every carrier, and
there it was not half a fix but a whole one missing.** Measured before the repair:

```
sim_runner.record_run_outcome(ok=False)   missing file       -> streak=1 outage=0.00h
                                          empty file         -> streak=1 outage=0.00h
                                          corrupt/truncated  -> streak=1 outage=0.00h
                                          OPEN EPISODE       -> streak=8 outage=10.00h

background_worker._check_zero_progress    corrupt/truncated  -> cycles=1   (from 8)
ntfy_utils.record_delivery_outcome        corrupt/truncated  -> failures=1 (from 5)
supervisor._record_atom_draw_and_check_stall  corrupt        -> count=1    (from 6)

supervisor._record_atom_draw_and_check_stall  json null      -> AttributeError
background_worker._check_zero_progress        json null      -> AttributeError
ntfy_utils.record_delivery_outcome            `[1, 2, 3]`    -> AttributeError
supervisor._load_stuck_state  (-> dict)       json null      -> returned None
```

Two distinct defects across one partition.

**1. An unreadable prior silently reset the episode.** A ten-hour open episode collapsing to a fresh
one because its own state file could not be parsed is the 2026-08-09 shape verbatim — the failure
silencing its own alarm — and it is the shape the census exists to enumerate. `sim_runner`'s guard
comment names *"a truncated read"* as exactly what its `guard_episode` call protects against.
Measured, it does not and cannot: the loader had already flattened the truncated read to an absent
prior one level above the guard, so **the guard's argued degrade door is not reachable from that
call site at all.** Mutation-proved and never able to run — R15's own subject.

**2. Four members of the partition did not reach a guard, they raised.** `json.loads` accepts `null`
and `[1, 2, 3]`. Both *parse*, so both walked past every `except (json.JSONDecodeError, OSError)`
and left through a loader annotated `-> dict` into the next line's `state.get(...)`. An observer
must never break the observed; an alarm's own writer crashing on the state it keeps its alarm in is
that rule inverted.

## The repair

`background/episode_prior.py` — the seam above `episode_monotonic`. It classifies once and returns
both halves: a mapping the caller can index without crashing, and the verdict on where that mapping
came from (`absent` / `readable` / `unreadable`). It deliberately does **not** choose an escalation:
what an alarm should DO about a lost episode memory is a per-control judgement, the same one PW4
refused to make by reflex, and guessing it here would produce five controls escalating for a reason
nobody picked.

Wired into the five carriers that lacked it:

| carrier | state path | what changed |
|---|---|---|
| `sim_runner.record_run_outcome` | `.sim_producer_state.json` | classified prior; `prior_unreadable` on the record |
| `background_worker._check_zero_progress` | `.run_marker_sweep_state.json` | classified prior; `prior_unreadable` on the record |
| `ntfy_utils.record_delivery_outcome` | `.ntfy_delivery_state.json` | classified prior; `prior_unreadable` on the record |
| `supervisor._check_stuck_escalation` | `.supervisor_stuck_state.json` | **an unreadable prior is no longer an evidenced close** |
| `supervisor._record_atom_draw_and_check_stall` | `.atom_stall_tracker.json` | **an unreadable prior is no longer progress** |

The last two are behaviour changes, not just bookkeeping. `episode_closed` is a *caller's
assertion*, and `episode_monotonic` is explicit that asserting it from a path that did not
demonstrate a close is still a defect. A corrupt file demonstrates nothing — it read as `{}`, so
the episode key compared unequal, so a stall running for hours closed its own episode and
re-stamped `first_seen_at` at now. For the stall tracker the same read made *every* atom's
fingerprint `None` at once, so the livelock detector cleared its whole register on a file it could
not read.

Where a counter genuinely cannot be recovered, `prior_unreadable: true` goes on the record so the
alarm reading it for severity knows the number is a **floor, not the episode**. "We cannot tell" is
a result and belongs on the surface.

## The control

`tests/background/test_episode_prior_partition.py`, 52 legs. Two properties it was deliberately
built NOT to have:

* It asserts absent and unreadable **DIFFER**, never that they take one branch. A control asserting
  sameness would pin the defect green while reading as deliberate — which is precisely how
  `prev=None` survived two lanes' repairs.
* Its subject is **derived** from the census's own `real` rows, not hand-listed, so a sixth carrier
  of this class fails here rather than joining it quietly. The two exempt readers are named with
  their reason *and the exemption is itself checked* (`_read_publish_gate_state` and
  `_read_operational_layer_state` really do report `state_unavailable` across the partition — they
  are the shape `episode_prior` generalises).
* `test_the_open_episode_control_can_reach_a_different_answer` is the reachability leg: without it
  every "differs" assertion is satisfiable by a carrier that answers the same thing to everything.

Mutation-proved both halves. `unreadable -> absent` in the classifier → 6 failures; letting a
non-mapping escape as-is → 11 failures, including all three crash legs.

## Residual, named rather than glossed

**A recovered episode is not recovered — only its loss is now visible.** When a counter's prior is
unreadable there is no earlier value to remember, so `cycles`/`consecutive_failures`/
`consecutive_unchanged` still restart at 1. What changed is that the record no longer *claims* a
cold start it never observed. Making an alarm act on `prior_unreadable` — escalate, or report the
count as a floor on the surface it pages from — is per-control judgement work and is **not done
here**. That is the next item on this class, and it is deliberately not guessed.

## Also landed on the way

`episode_monotonic`'s module docstring ended `Used by: process_run_complete._write_publish_gate_state`.
There are eighteen call sites across six modules and had been for weeks. A stale "used by" is worse
than none: it tells the next reader the blast radius of a change is one call site. Replaced with the
six modules and the grep that cannot go stale.

## Unrelated red observed, not mine

`tests/background/test_doorbell_redaction.py` — two `real_ntfy` legs fail in the shared tree
(`record_sent_id` writes `docs/observability/.sent_ntfy_ids.json`, a protected surface). Proven
pre-existing by running HEAD's own `background/ntfy_utils.py` in place: same two failures. Note
that a `git archive HEAD` extract is **not** a valid control for this one — `SENT_IDS_FILE` is a
hardcoded absolute path into the real tree, so the extract's guard never matches it and the test
passes there for the wrong reason.
