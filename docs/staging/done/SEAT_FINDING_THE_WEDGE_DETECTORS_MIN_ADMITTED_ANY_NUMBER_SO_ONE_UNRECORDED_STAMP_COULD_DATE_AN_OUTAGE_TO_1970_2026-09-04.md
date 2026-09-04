**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

*LATENT and not BLOCKING on the evidence: Q1 below shows no unrecorded stamp on the live state file
at 15:28 today, so nothing is mis-dated right now. The repair and its controls are landed; what is
latent is the reachability, which is a decodable file token away.*

# The wedge detector's `min()` admitted any number, so one unrecorded stamp could date an outage to 1970 — and a `NaN` killed the whole draw ladder

Subject: `background/supervisor._publish_gate_wedge_active`, the age block (was
`background/supervisor.py:3789-3794`). Preregistered before measurement in
`docs/staging/records/WORKER_PREREGISTRATION_WHAT_A_NON_POSITIVE_FAILURE_TIMESTAMP_MEANS_IN_THE_WEDGE_DETECTOR_2026-09-04.md`
(written 15:28:29 BST, sha256 `142c48ca…`, before any of the numbers below were read).

## What it was

The detector measures how long the publish gate has been wedged as a `min()` over three sources —
each `failures[].ts`, plus `wedge_since` and `alerted_at` — and every one of them was admitted by a
hand-rolled `isinstance(v, (int, float))` with **no positivity, no bool refusal and no finiteness
screen**. It was the fourth hand-rolled copy of a question `background/episode_monotonic.py` now
answers in one place, and the only copy with nothing behind the type test.

On a `min()` the error is not proportional to its size. **One** unrecorded stamp beside any number
of honest ones wins outright and dates the outage to 1970 — older than any threshold — so RUNG 1
fires permanently, at priority zero, above every product and HARDEN lane, on a gate that is fine.

## What was measured, against what was predicted

| Q | Predicted | Found |
|---|---|---|
| Q1 — non-positive value on the live state file now? | no (writer closed; `alerted_at` the least certain) | **no.** `wedge_since` 1788501449.3, `alerted_at` 1788528090.1, both failure stamps positive floats. The defect is **latent, not live**, and this finding claims no outage. |
| Q2 — is RUNG 1 firing now? | no | no — 2 failures, below the threshold of 3. |
| Q3 — what does a `NaN` do? | `ValueError` out of the ladder | **confirmed**, and worse than predicted in one respect (below). |
| Q4 — only unscreened copy? | no, expect three siblings | **confirmed**, and two of the siblings carry the same defect live. |

### Q3, precisely

`json.loads` parses a bare `NaN` token, so this arrives from a **file**, not from a caller's
mistake. `NaN` fails every comparison, so `age < PUBLISH_GATE_WEDGE_MIN_AGE_SECONDS` is `False` and
`int(age // 60)` twelve lines later raises `ValueError`. `_self_refill_draw_ladder` does **not**
catch, so the whole ladder dies — every rung, not the wedge rung. That is strictly worse than the
thing this rung draws: a permanent fire is loud, a dead ladder is the silent tick-stall of
2026-07-23/24 that the rung exists to prevent. The detector's own docstring promised callers
"never an exception into the draw ladder".

The sharp edge: `min([nan, 5.0])` is `nan` but `min([5.0, nan])` is `5.0`. **The crash's
reachability turned on list order** — so a control that poisoned one slot would have been green
half the time with the crash standing. The new control asserts both orderings for that reason.

## Why `failures[].ts` was NOT folded into the landed `wedge_since` repair, and is now

Because the argument differs even though the verdict coincides, and a borrowed argument is how a
clause written about one field silently acquires authority over another. Of an **episode start**,
`0` is the same fact as `None` — nobody recorded one. Of a **failure timestamp**, `0` does not mean
"a failure was observed in 1970"; no clock here can produce it. It means the stamp is **missing**,
and a missing stamp is not evidence about when anything happened. Both arguments are now carried in
`episode_monotonic.recorded_instant_seconds`, so the next reader does not have to reconstruct which
one applies where.

## The repair

`background/episode_monotonic.recorded_instant_seconds(v)` — the value-level door. The centralised
form (`episode_age_seconds`) only ever fitted a *named field of a mapping*; `failures[].ts` is an
element of a list with no episode reading at all, which is **why** the fourth copy got hand-rolled.
That is the shape it needed. `episode_age_seconds` is now expressed in terms of it, so there is one
path and not two. Called from three sites:

* `supervisor._publish_gate_wedge_active` — the named subject.
* `publish_cause.publish_cause` (was `background/publish_cause.py:211`) — **live fail-open**. `0`
  and `False` fell into the stale branch by luck, but `now - NaN > max_age` is `False`, so an
  unaged cause record would have been cited as attribution for **every** cycle forever — the
  carried-forward-blocking-list defect this function exists to stop, arriving through the age bound
  instead of the hash check.
* `ntfy_utils` (was `background/ntfy_utils.py:249`) — the landed zero-episode-start finding, one
  file over, on the director's **only** channel. `guard_episode` screens the *prior* side of a
  low-water field and not the *proposal*, by design — and the proposal here is
  `previous.get("since_epoch", now)`, echoed straight off disk. A persisted `0` is re-proposed,
  wins because the prior was screened out, and renders `1970-01-01T00:00:00Z` as the deafness
  episode's start. `time.gmtime(NaN)` raises, inside `send_ntfy`, on the path whose job is to
  report that the channel is broken.

## Controls, and the prediction they refuted

`tests/background/test_publish_gate_wedge_draw.py`, +7 controls (129 pass). Reachability first —
`test_the_honest_wedge_still_draws_and_reports_its_real_age` — because everything else asserts a
refusal and a screen that ate the wedge entirely would satisfy all of them.

The fixture caught the control's own first draft: poisoning `wedge_since` in the obvious fixture
does not test the screen, it **deletes the only evidence of age**, and the resulting `None` is the
detector correctly saying it cannot tell. `_three_honest_signals` attests the age from all three
sources so removing one leaves two.

Mutation-proven, three ways:

| Mutation | Result |
|---|---|
| M1 — restore the pre-repair hand-roll | **33 red** |
| M2 — hand-rolled `v > 0` instead of the shared screen | **2 red** |
| M3 — screen refuses everything | **107 red** (the reachability leg) |

**M2 refuted a claim I had already written into the code comments.** I asserted the finiteness
screen was what stopped the raise and what a hand-rolled positivity test would lose. It is not:
`NaN > 0` is `False`, so a bare `v > 0` screens `NaN` too, by accident of IEEE semantics. The
reasons that survive measurement are duller: `+Infinity` **passes** `v > 0` and turns an age into
`-inf`, which reads as "too young" and suppresses the alarm silently; an ISO-8601 value — which
`guard_episode` may legitimately write back, since the winner is returned in its own representation
— is dropped entirely by a numeric test, silently under-measuring the age; and a fifth copy is a
fifth thing to keep in step. The correction is kept beside the claim in both files. The two
controls that told M2 apart are the only two in 129 that could:
`test_an_iso_stamp_is_read_rather_than_discarded` and
`test_the_screen_is_the_shared_one_and_not_a_fourth_hand_rolled_copy`.

## What is left, deliberately

`ntfy_utils` still persists a non-recordable `since_epoch` to disk — the render no longer asserts
1970 from it, but the carrier is not repaired. Screening the **proposal** side of a low-water field
is a change to `guard_episode`'s stated contract ("of the proposal the guard asks *can I order
this?*"), and that contract is load-bearing for the misdeclared-field refusal. It needs deciding on
its own evidence, not as a rider here. Handed on.
