**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `the-landed-binder-defaults-to-head-and-the-liveness-refusal-never-reaches-it`

# The item was spent 2h13m before it was drawn, and neither disposition could say so

*The work this id ordered had already landed and been published. Both verbs that exist to record
exactly that refused it, on the same clause, because the draw that handed it out wrote the claims
store and not the draw ledger. The refusal does not hold the row — it is swept at 100 minutes and
redrawn — so the clause that was protecting the books was the thing minting the duplicates.*

---

## 1. The premise, re-measured before starting

The drawn item cited `e5395902f` and the draw-time check confirmed it was an ancestor of
`origin/main`. That check asked about the **enabling** commit — `_window_hits`, the reader — and
never asked about the **enabled** work. The enabled work is `f382f8ace`, which is also an ancestor
of `origin/main`:

| the item's "FINISHED means" | state at HEAD | where |
|---|---|---|
| liveness refusal reaches the binder | **done** | `record_landing` calls `_is_liveness_only(paths, _liveness_surface_or_raise())` |
| a refusal that names its reason | **done** | `refusal_reason` names the class, the declared surface, and the `--commit` escape |
| the refusing branch provably reachable | **done** | `test_..._heartbeat_republish_is_not_a_landing...py`, 10 legs, whole-partition assertion on each side — **green at HEAD, re-run this turn** |
| the finding dispositioned | **done** | the 2026-09-19 `SEAT_FINDING` is gone from `docs/staging/`, replaced by the `SEAT_RESULT` form |
| no `"HEAD"` default on the function or the flag | **refused by design** | see §2 |

The item's line numbers (2847, 3861) are stale; the code sits at 2882 and 3929. The literals rotted
and the conclusion inverted with them.

## 2. The one unmet clause is a design that was considered and rejected on the record

`f382f8ace` weighed removing the default and rejected it, in the commit message and again in the
docstring: *"`HEAD` is the only spelling the executor's own instructions to an isolated turn give,
and `--landed` with no commit is what every tick in the machine runs; making that a refusal would
silence the ledger for every caller in order to close a hole that only the heartbeat class actually
walks through."*

**That rejection is right, and this turn is its own evidence.** The executor instructions that
opened this invocation say, verbatim, to run `python3 -m background.delivery_lane --landed <id>` —
the bare form, no commit. Removing the default would have refused the binding for this very turn.
The landed rule is keyed to the property (*does this commit carry work?*) rather than to how the
caller spelt it, which also catches an explicit `--commit <a-republish-sha>`. Nothing is owed here.

## 3. Three slugs, one subject

| slug | drawn | outcome |
|---|---|---|
| `the-landed-unbound-binder-counts-a-heartbeat-as-a-landing` | 2026-09-19 23:10:03 | no landing |
| `...-defaults-to-head-and-two-swept-rows-are-now-dispositionable` | 2026-09-21 12:36:03 | **landed `f382f8ace` at 12:51:53** |
| `...-defaults-to-head-and-the-liveness-refusal-never-reaches-it` | 2026-09-21 15:05:32 | this invocation |

The third was handed out **2h13m after the second had already landed and published the answer**.

## 4. A prediction, filed before measuring, and refuted

> *Predicted: all three live claims are absent from the draw ledger — the executor's draw path
> writes the claims store but not the ledger.*

**Refuted.** The ledger holds 400 rows; the other two live claims both have one. Only this id did
not. The systemic story was wrong and the defect is narrower: *a* draw reached the claims store
without reaching the ledger, not *every* draw. Kept here beside the result because the repair below
was designed against the refuted version first, and the narrower reading is what made it small.

## 5. The defect this turn repairs

Both dispositions refused, each on the same clause:

```
--landed-under  → credited NOTHING: ... was never drawn -- the ledger has no row for it
--premise-spent → recorded NOTHING: ... was never drawn -- the ledger has no row for it
```

`--landed-under` is **not** the missing verb and widening it would be wrong: its own rule refuses a
landing that is not newer than the id's first draw, and this landing predates the draw *by
definition* — that is what "spent" means. The fix belongs to `premise_spent` alone, which is the
only verb for "drawn after the work had already landed".

**"Nothing was handed out" is false while the claims store holds a live claim.** A live claim *is*
the thing that was handed out. `note_premise_spent` now falls back to the claim's `claimed_at` when
the ledger has no row — the same fallback `_binding_instant` twenty lines below already takes for
the same case, so this is the file's established reading of its two stores, not a new one.

**Why refusing cost more than it saved.** The refusal does not hold the row. The claim is swept at
100 minutes and returned to the pool; the seat re-orients every three hours. The row therefore goes
back out *before* it can be dropped. The clause meant to protect the books was minting the
duplicates — and a ledger wrong towards "done" is not symmetrical with one that is silent, but a row
that can never be *closed* is the same asymmetry running the other way.

**It still fails closed.** An id in *neither* store is refused exactly as before, and the refusal
now names both stores so a reader can tell the recoverable case from the unrecoverable one. Every
other guard is inherited unchanged: an unpublished spender is still refused as a claim about the
future.

## 6. The control

`tests/background/test_a_draw_the_ledger_never_recorded_is_still_dispositionable.py` — 4 legs.
The partition is one statement, for this family's usual reason: a disposition that fired on every
string would be the free eraser `note_landing_under` says this family must never become, and it
would pass every per-branch check of "does it record a ledger-backed row?" written alone.

Mutations run this turn, both fired on the leg written for them, and the partition statement reds in
**both** directions:

| mutation | result |
|---|---|
| (a) delete the claims-store fallback (restore the bare refusal) | **3 failed** — ledgerless leg reds |
| (b) make the fallback unconditional (drop the `claimed_at <= 0.0` guard) | **2 failed** — neither-store leg reds |

Siblings green: `test_delivery_lane.py` + the heartbeat suite, 52 passed.

## 7. What is owed

Nothing on the item's own subject. One thing remains open and is **not** repaired here, because it
is a different subject and guessing at it would be the third mint again:

**Why did this draw write the claims store and not the ledger, when its two neighbours wrote both?**
That is the upstream cause of the duplicate slug. This finding repairs the *consequence* — the row
can now be closed — and deliberately leaves the cause named rather than assumed.
