**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** a53-the-supplier-cm-charge-reaches-nothing

# The anti-theft guard refused the turn's own landed work, because the executor's hand-out never wrote the draw ledger

**Found:** 2026-09-07, 16:42, by a53's own promotion. The work is on `origin/main` as `f716b6eac`;
**nothing is bound to the claim, and the turn will be logged LANDED NOTHING.**

---

## What happened

```
promoted f716b6eac -> origin/main (12 path(s), from 4a56ebfe8)
bound NOTHING to a53-the-supplier-cm-charge-reaches-nothing: f716b6eac... is OLDER than
this id was FIRST drawn (1788795517 <= 1788795691) -- not merely older than the current
claim, which a re-draw no longer puts out of reach. An older commit here is genuinely
somebody else's work
```

The commit is 174 seconds older than the instant the guard believes a53 was first drawn. It is not
somebody else's work; it is this turn's, and it is the only commit for this claim.

## The mechanism, established rather than guessed

`_binding_instant` reads `first_drawn_at` from the draw ledger beside the claims store
(`docs/observability/.delivery_lane_claims.draws.json`), falling back to `claimed_at`. The a53 row
reads:

```json
{"first_drawn_at": 1788795691.0052803,   // 16:41:31
 "last_drawn_at":  1788795691.0052803,   // identical -- this row was CREATED at 16:41
 "source": "continuation", "source_self_issued": true,
 "source_written_at": 1788790975.5230021}
```

`first_drawn_at == last_drawn_at` means the row was born at 16:41. **But a53 was handed to this
executor turn about two hours forty-five minutes earlier** — the turn had already read the work,
oriented, pre-registered, measured and landed twice by then.

**The obvious explanation is refuted.** `record_draw` writes `first_drawn_at` once and never moves
it (the docstring calls this "the whole mechanism"), so a re-draw cannot reset it — but the ROW is
capped by `MAX_REMEMBERED_DRAWS`, and an evicted row would be recreated with a fresh
`first_drawn_at`, silently restoring the trap. **Measured: 144 rows against a cap of 400, with rows
surviving from 2026-08-29.** No eviction. That is not the cause.

**What is left is that the ledger was never written for this turn's draw at all.** The executor's
hand-out of a Lane 0 item and `delivery_lane.draw()` are two different doors, and only the second
calls `record_draw`. So for an executor turn, `first_drawn_at` is not when the seat was given the
work — it is whenever some *other* route next touches the id, which can be, and here was, **after
the turn's own commit.**

## Why this is BLOCKING rather than an annoyance

The guard exists to stop a claim being credited with another writer's older commit. Against an
executor turn it does the opposite of its purpose:

* It is **keyed to a ledger the executor's own door does not write**, so its reference instant is
  unrelated to when this seat received the work.
* Its refusal is **unrepairable after the turn ends** — the promotion route says so itself — and it
  fires at the one moment nothing can be done about it.
* **The longer and more expensive the turn, the more likely it fires.** a53 took nine gate cycles
  of roughly ten minutes each; `CLAIM_STALE_SECONDS` is 100 minutes. Any Lane 0 item whose gated
  landing outlasts the sweep is swept, re-drawn by another route, and its own landed work then
  reads as theft. **The guard is hardest on the work it most needs to see.**
* The consequence is not cosmetic: an unbound claim is re-offered, so the lane hands the same
  finished work out again. **The correct number nobody reads — which is the defect a53 itself was
  about — reproduced one layer up, in the machinery that tracks whether a53 was done.**

The ledger's oldest surviving row is, verbatim,
`bind-a-reissued-claim-to-the-work-that-already-landed`. This class has been worked before.

## What would fix it, in preference order

1. **The executor's hand-out should call `record_draw`.** One line, and it makes
   `first_drawn_at` mean what the guard already assumes it means. Everything else is a workaround
   for this absence.
2. **A row created AFTER a live claim's `claimed_at` cannot be that claim's first draw.** When
   `first_drawn_at >= claimed_at` the ledger is telling you it did not witness the draw;
   `_binding_instant` already spots this case and falls back to `claimed_at`, which here is the
   SAME 16:41 instant and so is no fallback at all. The honest answer in that state is **"I cannot
   tell"**, not "somebody else's work" — and a guard that cannot tell should say so on the surface
   and let the seat record the binding with a named reason, rather than fail into the accusation.
3. **Compare against the claim the commit was made under, not the claim that exists now.** The
   sweep is silent by design; nothing in the record distinguishes "a rival landed something old"
   from "we recycled the id under the writer while it was gating".

## What is true regardless

`f716b6eac` is on `origin/main`. a53's substance is done: `compute_cm_obligation` has a production
caller, the charge reaches the annual report as the supplier's own statutory position, and unwiring
it now reds the orphan ratchet. **A re-draw of a53 will find its premise spent** — the remaining
work is the "what is next" section of
`SEAT_FINDING_THE_SUPPLIER_CM_CHARGE_NOW_REACHES_THE_STATUTORY_RETURN_AND_THE_TWO_READINGS_DISAGREE_ONLY_ABOUT_JANUARY_2026-09-07.md`,
not the wiring.
