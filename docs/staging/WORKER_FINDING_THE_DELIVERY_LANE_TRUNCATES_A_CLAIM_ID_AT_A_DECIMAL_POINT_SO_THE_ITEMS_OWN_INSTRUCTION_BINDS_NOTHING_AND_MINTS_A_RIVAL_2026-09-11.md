**Severity:** BLOCKING · **Lane:** H_harness

# FINDING — the delivery lane truncates a claim id at a decimal point, so the item's own `--landed` instruction binds nothing AND mints a rival claim

**Found 2026-09-11, delivery seat, by following a drawn item's instruction literally and watching it
refuse.**

## What happened

The drawn Lane 0 item ends with, verbatim:

> IMMEDIATELY AFTER EACH COMMIT, run `python3 -m background.delivery_lane --landed
> the-third-arm-separates-fewer-accounts-from-different-accounts-in-p6s-2.45-percent` ... Skip it
> and the claim is swept back into the pool in 100 minutes however much you landed.

Run exactly as written, against a commit landed minutes earlier, it refuses:

```
bound NOTHING to the-third-arm-...-in-p6s-2.45-percent: b3ab3877f is OLDER than this id was
FIRST drawn (1789100794 <= 1789101333) -- ... An older commit here is genuinely somebody else's work
```

The commit is not somebody else's work. It is this turn's, landed 539 seconds *before* the id in
the message was "first drawn" — **because the `--landed` invocation itself minted that id**, at the
moment it ran.

## The mechanism

`docs/observability/.delivery_lane_claims.json` holds **two** ids for one piece of work:

| id | `claimed_at` | paths |
|---|---:|---|
| `the-third-arm-...-in-p6s-2` | 1789100128 | (the real claim, drawn by the tick) |
| `the-third-arm-...-in-p6s-2.45-percent` | 1789101333 | `[]` — minted by my own `--landed` |

**The id the lane actually registered at draw time is truncated at the decimal point** — `p6s-2`,
not `p6s-2.45-percent`. The slug normaliser stops at the `.` in "2.45". The item's prose quotes the
untruncated form, so the id in the instruction **cannot be the id in the store**.

Binding against the truncated id works first time:

```
bound 1 path(s) to the-third-arm-...-in-p6s-2:
  docs/staging/records/PREREG_DOES_P6S_..._2026-09-11.md
```

## Why this is BLOCKING and not a cosmetic slug bug

The refusal is **fail-closed and correctly reasoned** — an older commit really would usually be
another lane's — but its premise is manufactured by the same command that then fails on it. Three
consequences, and the third is the expensive one:

1. **The work looks unbound.** The real claim keeps `paths: []` and is swept back into the pool
   after 100 minutes however much landed, which is exactly the outcome the instruction exists to
   prevent.
2. **A rival claim is left in the store**, with an empty path list and a `claimed_at` newer than the
   real one, looking like a fresh unstarted claim of the same work.
3. **The refusal's text sends the reader the wrong way.** "An older commit here is genuinely
   somebody else's work" invites the conclusion that another lane landed it, which is
   [the shape where a control's message lets the alert invent a cause]. A seat that believed it
   would go looking for a rival lane that does not exist.

## The remedy, and what it must NOT be

**Not** "quote the truncated id in future items" — that keys the fix to today's answer and the next
id with a `.` in it breaks the same way.

The bind should **resolve the id the way the draw did**: normalise the argument through the same
slug function that wrote the store, so `p6s-2.45-percent` and `p6s-2` land on one claim. Failing
that, `--landed` must **refuse to mint an id that does not already exist** — minting on a
write-path whose whole job is to attach to an existing claim is what turns a typo into a rival
record. Either is a one-leg change in `background/delivery_lane.py`.

**A control that would have caught it:** land a commit, bind it with an id containing a `.`, and
assert the claim the tick drew has a non-empty `paths`. The current behaviour passes no such test
because no such test exists — the binding's success is only ever read from its own stdout.

*Reproduced this turn against `b3ab3877f`. The workaround used was the truncated id; the finding is
the mechanism, not the instance.*
