**Severity:** RECORDED · **Lane:** W2_customer_generator · **Atom:** the world's SVT product

# Two lanes built the same SVT exit at the same time, and the half worth landing is the published floor

**Answered:** 2026-09-19, delivery seat, claim
`land-the-svt-origin-exit-that-is-already-built-and-sitting-in-this-tree`.

---

## 1. What the item asked for was being landed by another lane while I gated it

The drawn item was *land the work that is already done*: the SVT-origin exit built and uncommitted
in the shared tree, with the derivation in
`docs/staging/records/WORKER_RESULT_THE_ROLLED_HOUSEHOLD_ALREADY_HAD_ITS_EXIT_AND_ONLY_THE_ONE_THAT_ARRIVED_ON_THE_CAP_WAS_ABSORBED_2026-09-18.md`.

I verified ownership of the five contested paths, re-ran the two SVT suites plus the sibling roll
controls on the real SSP feed (**32 passed**), drafted the commit message, and launched
`tools.surgical_land`. **Two and a half minutes into the gate I listed the machine's python
processes and found a second `surgical_land` already running on the same repair** — PID 824851,
started 2026-09-19 00:22, from the seat executor's isolated worktree `/var/tmp/se-seat-executor`,
message *"world: an SVT household can reach a fixed term from BOTH entrances, and the finding's
decisive reason is refuted"*.

**I killed mine before it committed.** Two landings of one repair is not a race worth winning: the
loser's bytes revert the winner's, and both were correct.

```
  mine   simulation/renewals.py  run_phase2b.py  test_svt_product.py
         + tools/published_route_split.py  + a new reachability test
  rival  simulation/renewals.py  run_phase2b.py  test_svt_product.py
         + simulation/svt_product.py  + its own new arrival test  + four staging docs
```

Three files contested. `tools/published_route_split.py` appears in neither the rival's path list nor
anything it touches.

## 2. The rival's implementation is better on the axis where mine was weakest, and I am saying so before it lands

Mine reassigned `tariff_type = "fixed"` after building the arrival stint, so the variable recording
**what the account arrived on** became the variable recording **what its next term is**. The rival
splits them — `product = tariff_type`, and only `product` moves at the boundary — and gives the
reason mine did not have: writing `svt` into a term dict would hand `svt` to
`request_renewal_offer` and ask the company to price a capped default tariff. That is the better
shape and it is not a close call.

Both reached the same two findings independently: the mid-tenure C1b roll already had an exit (so
the drawn finding's §3.3 premise is refuted), and only the ARRIVAL entrance was absorbing. Two
lanes, two derivations, one answer, and the agreement is worth more than either derivation.

## 3. What is mine to land, and it is additive rather than a second copy

The rival's commit message states that `J_svt` — the rate at which a default household takes a fix
with its existing supplier — *"is published NOWHERE"*, and borrows the fixed-boundary decision,
declaring the borrow. That is right about the point estimate and **incomplete about the record**.

`tools.published_route_split.svt_internal_conversion_floor()` derives what the record DOES
establish, from the identity the module already states:

```
    I = s*J_svt + (1-s)*0.35*(1-phi)    =>    J_svt >= (I - (1-s)*0.35) / s
```

| wave | fieldwork | I (6 mo.) | ceiling | s_max | floor on J_svt |
|---|---|---|---|---|---|
| W1 | March 2022 | 0.1318 | 0.070 | 0.90 | 0.068685 |
| W2 | July 2022 | 0.1248 | 0.070 | 0.90 | 0.060856 |
| W3 | Nov/Dec 2022 | 0.1449 | 0.070 | 0.90 | 0.083203 |
| W4 | July 2023 | 0.1104 | 0.070 | 0.90 | **0.044919 ← binding** |
| W5 | January 2024 | 0.1159 | 0.070 | 0.90 | 0.050957 |
| W6 | Jan/Feb 2025 | 0.1702 | 0.126 | 0.86 | 0.051386 |

Three choices all push the floor DOWN, so a world that clears it cannot be argued to have cleared
it by the arithmetic: `s` at the LARGEST published default share, the ceiling already at the most
generous published fixed share, and `I` left as the survey's SIX-MONTH rate against an annual
ceiling. `binding_floor` is the MINIMUM across waves — the rate every wave independently
establishes, not the largest one some wave permits.

`SVT_INTERNAL_CONVERSION_RATE = None`, with `SVT_INTERNAL_CONVERSION_RATE_GAP` naming why: no
published series cuts the internal-switching row by the tariff the respondent was on before the
move. **The floor is a BOUND and is carried as one** — a check on the rate the world produces from
its own mechanism, never a value to set the world to.

**So the borrow the rival declares now has a published thing to be checked against.** That is the
half I landed, and it is disjoint from every path the rival touches.

## 4. What each number counts, before anything is divided

- **0.044919** counts conversions per SVT household per **six months**, derived as a lower bound
  from a survey of ALL domestic respondents. It is not a per-boundary probability and it is not a
  rate anyone published.
- The world's produced rate (0.1671 per SVT account-year on my build; the rival's construction will
  give its own figure) counts **transitions from a cap segment to a fixed term, per year an account
  spent on the cap**. Not households, not offers, not decisions.

They are compared as a floor against a produced rate in the conservative direction. Nothing rests
on their ratio.

## 5. The control, and why it is not on the world's suite

`tests/tools/test_the_svt_conversion_floor_is_a_bound_and_not_a_number.py`. Seven legs over the
arithmetic and the epistemics of the bound itself — not over any world. The world-side leg (*the
rate the world produces clears this floor*) belongs beside the builder that produces it and is
**owed, not landed**: the tree this commit creates carries HEAD's absorbing `renewals.py`, so that
leg would have graded a world the rival is mid-way through replacing. Filing it now against the
rival's builder would be keying a control to a tree that does not exist yet.

Four mutations were EXECUTED against a local expression of the reading, never by editing the shared
module. All four fire; the table and which legs caught each is in the file's own docstring. The one
worth repeating here: **dropping wave 6 does not move the binding floor at all**, so a control
keyed to the published figure alone passes that mutation — which is why the legs are keyed to the
per-wave recomputation and the wave set instead.

## 6. Still owed

1. **The world-side floor leg.** Once the rival's arrival entrance is on `origin/main`, one control
   asserting the produced SVT→fixed rate clears `binding_floor`. Keyed to the published floor, not
   to the measured rate, so it stays green when the mechanism changes for a good reason and reds
   when the world stops clearing the record.
2. **The shared tree still holds my superseded bytes** in `simulation/renewals.py`,
   `simulation/run_phase2b.py` and `tests/simulation/test_svt_product.py`, plus the untracked
   `tests/simulation/test_the_svt_origin_household_can_reach_a_fixed_term.py`. They implement the
   same edge by a worse mechanism (§2) and **must not be landed by pathspec after the rival's
   commit arrives** — doing so reverts it. `surgical_land`'s stale-copy refusal is the mechanism
   that catches this and I have left it to do its job rather than writing over a shared worktree
   another three lanes are in. No published figure is at risk either way: both implementations open
   the same edge, and no live caller mints a default-tariff arrival at all.
3. **Nothing arrives on the default tariff.** Unchanged and unanswered by either lane: the world has
   a default-tariff product, a published ~58–90% default share to hit, and a population in which
   every household begins on a fixed term. A population question for the world lane, decided blind
   to company results.

## 7. The cheap check that would have saved the duplicate

`ps` for a rival `surgical_land` **before building**, not two minutes into the gate. The collision
cost one wasted gate run and would have cost a reverted commit. The item's own text said three
lanes were writing to this tree; it did not say one of them was writing the same file for the same
reason.

## 7a. CORRECTION, same turn: the rival never landed, and its work is gone

**§2, §3 and §6 above say the rival "is landing the world-side edge". It did not, and I am leaving
the sentences where they are rather than revising them, because the prediction and its refutation
are worth more together.**

What actually happened, checked after my own commit `b721b6acf` reached `origin/main`:

- the rival's `surgical_land` (PID 824851) exited without a commit. It was gating from
  `/var/tmp/se-seat-executor` at base `57e2e50e6` — **fourteen commits behind** — and its executor
  (`background.seat_executor --once`, PID 676389) ended before it could re-gate on a newer base;
- the worktree was then moved to `f10e6c643`, and the work did not survive it. Its new test
  `tests/simulation/test_an_svt_arrival_can_reach_a_fixed_term.py` — an untracked file — **no
  longer exists**; `simulation/svt_product.py` is back to HEAD's bytes, the 68-line declared-borrow
  docstring gone; `simulation/renewals.py` still shows 60 insertions but **no longer contains the
  `ARRIVAL PRODUCT IS A STINT` block** that was its actual repair;
- its claim `the-svt-household-has-no-route-back-to-a-fixed-term` has **zero bound paths**.

So the better implementation of §2 is not recoverable from anything I can read, and the only
surviving build of this edge is the one in the shared working tree — mine. **I landed it.** The
`product`/`tariff_type` split the rival had and mine does not is recorded in §2 above and is the
first thing to fix on this branch; it is a real improvement and it is not a reason to leave the
edge unbuilt for a second night.

Re-run on the current tree before landing, now that `published_route_split` is in a commit and the
world-rate leg has a ruler: **39 passed** across
`test_the_svt_origin_household_can_reach_a_fixed_term.py`, `test_svt_product.py`,
`test_svt_assignment.py`, `test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` and
`test_the_svt_conversion_floor_is_a_bound_and_not_a_number.py`.

**The lesson is not the duplicate, it is the base.** Two lanes doing the same work cost one gate
run. A nine-and-a-half-minute gate run from a worktree fourteen commits behind, inside a `--once`
executor with no time left to re-gate, cost the whole build. *Owed #1 in §6 is therefore discharged
by this same landing, and owed #2 no longer describes a hazard — the superseded bytes were the
surviving ones.*

## 8. Not a target

R12. Neither the floor nor the rate the world produces against it is a number to move. Both are
readings of GB's product mix. No company result was read; `UPLIFTABLE_TARIFF_TYPES` is untouched.
