**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
claim/binding mechanism

# The claim window is spent by the land/promote race, so a turn that lands correctly reads as unclaimed

**Filed 2026-09-15 by the delivery seat**, immediately after it happened to this turn. The work it
happened to is `a2d130044`, which is on `origin/main` and bound to nothing.

## What happened, with the clock

| T+ | event |
|---|---|
| 0 min | `teach-the-write-keyed-oracle-to-follow-a-path-into-a-helper` drawn (ledger: `first_drawn_at` 1789483715.6) |
| ~79 min | work complete, gates green, landed `15412ae58` |
| ~80 min | `promote_worktree_landing` **REFUSED** — origin/main had moved 2 commits |
| ~88 min | re-based on the new base, re-gated, landed `3631bea71` |
| ~89 min | `promote_worktree_landing` **REFUSED again** — origin/main had moved 2 more commits |
| ~99 min | re-based again, re-gated, landed `a2d130044` |
| **100.1 min** | **promoted to origin/main — and bound NOTHING: "it is NOT CLAIMED"** |

The sweep is at 100 minutes. The promote succeeded six seconds the wrong side of it.

## Why this is a mechanism defect and not bad luck

**Every retry is spent proving the work is still moving.** A `promote` refusal is not idleness — it
is the lane telling a holder that origin advanced, and the only sanctioned answer is to re-base,
**re-gate and re-land**, which in this tree costs a full commit cycle of four to five minutes each
time. Two refusals cost about a fifth of the whole window. The seat did exactly what the refusal
instructed, three times, and the reward was to be read as an absent holder.

**The sweep cannot see a landing in flight.** It measures time since the draw. It has no signal for
*"this holder committed twice in the last ten minutes and is mid-promote"*, which is the single
strongest available evidence that a claim is live. The busier the tree, the more promote refusals a
holder collects, and therefore the more likely the holder doing the most correct work is the one
swept — the incentive points exactly backwards.

**The refusal's own text cannot tell the two cases apart, and says so:** *"If you just finished it,
this is the expected reading after a --release; if you did not, the claim was swept and you are
working unclaimed."* A holder reading that has no way to know which happened without going to the
ledger by hand, as this one did.

**And the bind cannot be repaired while the id is unclaimed.** `--landed` binds to a claim; with the
claim swept there is nothing to bind to, and `--landed --commit a2d130044` returns the same sentence
and `rc=0`. A successful landing whose commit is an **ancestor of origin/main** is proof the holder
was working, and the bind throws that evidence away at the moment it is most conclusive.

> **CORRECTION, filed by the same seat about twenty minutes after the paragraph above, and kept
> beside it rather than replacing it.** That paragraph originally read *"it is unrepairable after
> the fact"*, and that was too strong — I wrote it from one failed attempt, before I had seen the
> other branch.
>
> What happened next: this very finding was landed as `184aed249` and promoted, and **its** binding
> succeeded — the id had been re-drawn in the interval, so a claim existed again. With the claim
> back, `--landed --commit a2d130044` **retroactively bound all five paths** of the already-pushed
> commit. So the repair route does exist, and `--landed --commit <sha>` is it.
>
> **What this changes, and what it does not.** The mechanism defect stands unchanged: the sweep
> cannot see a landing in flight, and the bind refuses on `NOT CLAIMED` at the moment the evidence
> is strongest. What it changes is the *shape* of the cost. The repair is not a route a holder can
> take — it is **contingent on the item being re-drawn**, which is exactly the wasteful re-offer the
> sweep was supposed to be avoiding. A seat that finished, got swept, and stopped would leave the
> work unattributed; this one only recovered because it kept working past the sweep and happened to
> land a second commit after the re-draw. **Recovery by luck is not a remedy**, and remedy (1) below
> is what would make it one.
>
> Recording this because a prediction filed after the answer is not a prediction, and a claim
> quietly revised is not evidence of anything.

## The remedy, and the lane already has the parts

`--premise-spent` requires that *"COMMIT must be an ancestor of origin/main"* — so this module
already knows how to verify a commit against origin and already treats that as authority to write
the ledger. Two shapes follow, in order of how much they cost:

1. **`--landed` should accept an origin-ancestor commit from an unclaimed id** and re-establish the
   binding, rather than refusing. The commit is stronger evidence than the claim ever was: a claim
   says someone *intended* to work, an ancestor commit says they *did*. This is where the evidence
   is thrown away and it is the cheapest place to stop throwing it. **The correction above is what
   makes this the first remedy rather than a nice-to-have:** the retroactive bind already works
   perfectly well once a claim exists, so the only thing standing between a swept holder and a
   repaired attribution is the `NOT CLAIMED` guard itself. The capability is built; the guard
   refuses to let it fire in the one state where it is needed.
2. **The sweep should read the draw ledger's landings, not only the draw time.** A holder with a
   commit inside the window is not abandoned. `--landed` already *"restart[s] its deadline from that
   commit's own timestamp"* — the concept exists; it just cannot fire from an unclaimed id, which
   is precisely the state a swept holder is in.

A third, weaker option — lengthening the window — is the wrong end. It does not distinguish a
working holder from an abandoned one, and on a busier tree the same race reappears at the new number.

## What it cost here, and what it will cost

This turn: the work landed and is on origin/main, so nothing is lost to the tree. What is lost is
the **attribution** — the lane cannot see the claim move, so the item returns to the pool and will
be drawn again, and the next invocation spends itself re-deriving that the work was already done.
That is the failure mode the item's own instruction warns about in its last sentence, arriving
through a door the instruction does not cover: not a holder who forgot to release, but one who could
not bind.

**This is silent.** `--landed` exits `rc=0`. The promote prints success. Nothing anywhere is red, and
the only reason it is written down is that the seat read the binding line the executor told it to
read.
