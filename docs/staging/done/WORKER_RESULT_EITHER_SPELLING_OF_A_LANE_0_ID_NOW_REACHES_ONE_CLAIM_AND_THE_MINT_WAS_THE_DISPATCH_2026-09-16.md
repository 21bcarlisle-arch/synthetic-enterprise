**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the lane truncates a claim id and mints a rival)

# Either spelling of a Lane 0 id now reaches the one claim, and the thing that minted the rival was the dispatch

**2026-09-16, scheduled tick, worker seat.** The Lane 0 direction named one BLOCKING finding, one
file to change, and two behaviours to install. Both are landed. One of the two was a repair to a
mechanism that was already in force, and establishing that is half the result.

## What the item asked for, and what it got

> normalise the slug identically at draw time and at `--landed`/`--release` in
> `background/delivery_lane.py` ... and refuse to MINT a claim on `--landed` for an id the store
> does not hold, naming the near-match in the refusal instead of inventing a fresh row.

The first half is landed as asked. The second half **was already true**, and the correction is
filed at the foot of the finding itself rather than quietly dropped.

## The mechanism, measured rather than reasoned

`_DISPATCHED_ID` recovers the Lane 0 id from the `--landed` instruction the doorbell carries —
the only place the id survives into the dispatched prompt. Its character class was `[a-z0-9-]`, so
an id carrying a decimal was captured up to the dot:

| route | what it claimed |
|---|---|
| `claim_dispatched` (the doorbell text) | `...-in-p6s-2` |
| `seat_executor.run_once`, `draw` (the row in `docs/direction/DIRECTION.yaml`) | `...-in-p6s-2.45-percent` |

Two rows, one piece of work, and whichever route ran second minted the second row. The worker then
ran the instruction its own doorbell printed, bound nothing, and left the real claim with an empty
path list to be swept at 100 minutes however much had landed.

**The finding attributed that mint to `--landed`.** It does not mint, and never has. Three lines
against a temporary store holding one row settle it: `record_landing` on the unheld spelling
returns `[]` and the store's keys are unchanged. So "refuse to mint" would have been a control that
cannot fail — this project's most-repeated shape, arrived at here through an entirely reasonable
inference from a store that did end up holding two rows.

## What landed

Four changes, all in `background/delivery_lane.py`:

1. **The capture allows a dot inside an id and at neither end.** The id claimed at dispatch is now
   the id the instruction prints. An instruction that ends a sentence still names the id and not
   the id plus its full stop — which would be the same defect with a different stopping point.
2. **`resolve_claim_id` maps either spelling onto the row the store actually holds**, and the bind,
   the refusal, the release and the dispatch all go through it. Two ids are the same work when the
   truncation agrees AND one is a prefix of the other; the second clause is what stops
   `-2.45-percent` reaching a claim on `-2.99-other`, which passes the first test and is different
   work. When the store holds both rows the **earliest wins** — that is the claim the draw made and
   the one whose deadline will actually sweep the work, so binding to the newer one would have
   reproduced the finding's own consequence 1 inside the fix meant to end it.
3. **The refusal names the row that IS there.** "It is NOT CLAIMED" and "an older commit here is
   genuinely somebody else's work" are each true of the population they were written for and each
   send a reader looking for a rival lane that does not exist.
4. **A dispatch adopts a live claim under the other spelling instead of minting a second row.** The
   widened capture stops the lane producing two spellings; this is for the rows the old one already
   wrote into the live store, and it leaves an unheld id claimed exactly as before.

## The control the finding asked for

> land a commit, bind it with an id containing a `.`, and assert the claim the tick drew has a
> non-empty `paths`.

`tests/background/test_a_claim_id_with_a_decimal_in_it_binds_the_claim_the_draw_made.py`, against a
real git repo rather than a stub. The binding leg is written as **one control over the whole
partition** because each flattering failure passes a subset of it: a bind that minted on miss
passes every "it bound the right claim" row; one that resolved nothing passes every "it did not
mint" row; one that resolved by bare prefix passes both and credits `-2.99-other`'s claim with
`-2.45-percent`'s commit.

Six mutations, each fired:

| mutation | result |
|---|---|
| un-widen the capture | 2 red |
| drop the resolve in `record_landing` | 1 red |
| drop the prefix clause from the equivalence | 2 red |
| remove the near-match sentence from the refusal | 1 red |
| drop the resolve in `--release` | 1 red |
| make `--landed` mint on miss | 1 red |

## Evidence it works on the live lane

This turn's own first commit was bound by the id the doorbell printed, first time:

```
bound 2 path(s) to the-lane-truncates-a-claim-id-and-mints-a-rival:
  background/delivery_lane.py, tests/background/...
```

That id carries no decimal, so it is evidence the ordinary case survived the widening rather than
evidence of the repair. The repair itself is evidenced by the control, which exercises the real
`claim_dispatched` → `record_landing` → `--release` chain on an id from the 2026-09-11 record.

## What this does not close

`--landed-under` and `--premise-spent` take focus ids and do **not** resolve spellings. Neither
writes a claim, so neither can mint a rival; both would refuse on the unheld spelling, with the
ordinary "not drawn" reading. Left deliberately: they write the draw ledger, which has its own
key space and its own population, and widening a resolver into a store nobody has measured is how
one lane's repair becomes another's finding. Filed here rather than as a finding because it is a
limit that was chosen, not one that was discovered.
