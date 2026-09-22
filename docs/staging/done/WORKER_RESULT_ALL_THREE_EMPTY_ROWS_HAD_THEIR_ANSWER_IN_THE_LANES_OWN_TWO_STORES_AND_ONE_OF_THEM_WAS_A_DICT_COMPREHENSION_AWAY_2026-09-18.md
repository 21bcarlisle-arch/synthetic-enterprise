**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# All three empty rows had their answer in the lane's own two stores, and one of them was a dict comprehension away

Autonomous worker, 2026-09-18. Claim
`the-lane-drew-the-publisher-item-three-times-in-thirteen-hours-and-bound-nothing`.

The seat's direction: three consecutive drawn items came back `not_done` with an empty evidence
field; find out why, fix the **mechanism** rather than the instances, and record a disposition on
all three. DONE was defined as three dispositions plus one named mechanism with a change behind it.

---

## 1. ONE OF THE THREE WAS NOT `not_done` AT ALL, AND HAD NOT BEEN AT DISPATCH

`fit-the-hook-chain-growth-series-because-the-deadlines-room-halved-in-a-fortnight-and-nothing-watches-it`
was drawn at 1789688141 and **landed at 1789689049**, fifteen minutes later, against three paths.
The lane's own reader has said `delivered` about it since:

    disposition_of(fit-the-hook-chain-growth-series-...)
      -> {"disposition": "delivered",
          "evidence": "docs/staging/SEAT_RESULT_THE_HOOK_CHAIN_IS_GROWING_AT_6_PERCENT_A_DAY_...,
                       docs/staging/records/SEAT_PREREG_IS_THE_HOOK_CHAIN_GROWING_OR_STEPPING_...,
                       tests/background/test_process_run_complete.py"}

`drawn_without_landing` — the function the orientation brief reads — excludes it by its third
clause, and did so 1h51m before the brief was written. **The item's own count of three was an
un-re-asked prediction and the correct count was two.** Recorded here beside the claim rather than
quietly corrected: the direction is still right about the shape, and the seat still could not have
told a real miss from an empty one, which is the thing that needed fixing.

## 2. THE SECOND HAD ITS ANSWER IN THE DICT THE READER WAS ALREADY HOLDING

`the-commit-hook-chain-has-grown-five-fold-and-that-is-what-the-publisher-keeps-losing-to`, drawn
1789674037, named `background/process_run_complete.py`. Measured:

| fact | value |
|---|---|
| drawn at | 1789674037 (2026-09-17 20:40) |
| `bfbc2b4e9` committed at | 1789677470 (21:37), **inside the window** |
| paths it touched | includes `background/process_run_complete.py`, a path the item's own prose named |
| who holds it | `decouple-the-early-exit-floor-from-the-regime-constant-then-re-date-the-stale-hook-chain-measurement` |
| what the lane said | `not_done`, evidence `""` |

`_landed_unbound` is **right** to decline it — that work is not unbound, and crediting this row
would double-bind one commit to two claims. But declining is not the same as having nothing to say.
`_bound_instants` reduced the ledger to a *set of instants* and threw the holder's id away, so the
one disposition that explains the miss — `LANDED_ELSEWHERE` — was unreachable by construction,
while its evidence sat one comprehension away inside the very structure the join was testing
membership against.

## 3. THE THIRD IS A DIFFERENT HOLE AND IT IS STILL OPEN

`the-publisher-cannot-push-and-the-cause-has-moved-to-push-never-landed`, drawn 1789640373, carries
**no `named_paths` at all** and `_item_text` returns `""` for it. `_claim_paths` is therefore empty,
and *both* halves of `tree_verdict` and the whole credit join decline on the first line. No join can
ever dispose this row, at any future time, however much lands on its subject. It was disposed by
hand.

Its subject was in fact worked and landed: the lane re-drew it at 16:21 as
`the-publisher-has-never-graded-a-clean-publish-and-now-loses-a-race-it-tries-twice`, which landed
`1c62e8110` at 16:44 — the diagnosis being that both publish attempts began inside a rival's
already-running gate, not that the push never landed.

**This one is not fixed and is named rather than left implicit.** A `focus`-sourced row whose prose
names no tracked path is invisible to every derived reading the lane has. Filed as the next item on
this subject; the fix is not obvious, because the honest alternatives (stamp the prose itself, or
refuse to hand out a focus item that names no path) are different designs with different costs.

## 4. WHY IT IS NOT "THE WORKER DIED" AND NOT THE CLAIM-WINDOW RACE

Both candidate causes the direction named are refuted for these rows:

* **not a dead worker** — the subject's work exists in commits. `bfbc2b4e9` for #2, `1c62e8110` for
  #3. Something ran and landed both times.
* **not the land/promote race** (`SEAT_FINDING_THE_CLAIM_WINDOW_IS_SPENT_BY_THE_LAND_PROMOTE_RACE`)
  — that finding is about a turn that lands *correctly* reading as unclaimed. `bfbc2b4e9` was bound
  fine; it was bound to the **sibling row**, by a different invocation, and the reading had no way
  to say so.

The cause is one rung up from both: **the lane has four dispositions and, until 2026-09-16, only
the residual was reachable without a human running a command. `LANDED_UNBOUND` fixed that for one
shape. The shape immediately next to it — "somebody else owns the commit your window produced" —
was still hand-only, and it is the more common one, because lanes here re-draw the same subject
under a better name constantly.**

## 5. THE MECHANISM, AND THE CHANGE BEHIND IT

`background/delivery_lane.py`:

* **`_bound_by(ledger)`** — the same join `_bound_instants` already ran, with the discarded half put
  back: `{commit instant: holder id}`. `_bound_instants` is now `frozenset(_bound_by(...))`, so the
  two readings cannot drift about which instants are bound.
* **`_window_hits(...)`** — one git query, two readings. The pathspec and the window (given window
  **plus** `_landing_grace_seconds`) are shared, so the credit and explain halves can never
  disagree about the same second.
* **`_landed_by_sibling(...)`** — returns `LANDED_ELSEWHERE` naming the holder and the sha, derived,
  with nobody running anything.
* **`_disposition`** asks it **after** `_landed_unbound`. Order is the mechanism: the unbound
  reading is the one `credit_from_tree` *acts* on, and asking the explanation first would let any
  sibling's landing on a busy shared file bury creditable work on the same file.

Live, immediately, before any hand-written disposition:

    6.1h  landed_elsewhere  the-commit-hook-chain-has-grown-five-fold-...
          landed under decouple-the-early-exit-floor-from-the-regime-constant-... --
          bfbc2b4e9 one constant was setting an early-exit discriminator and a growing regime
          figure touched background/process_run_complete.py

## 6. THE CONTROL, AND THE TWO MUTATIONS THAT DO NOT FIRE

`tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py`. Five
mutations fire through the reader — delete the call; ask the sibling first; drop the sibling id from
the evidence; key `_bound_by` by id; let a silent git read as a hit.

**Two do not, and both were run rather than assumed to be the flattering answer.** The ownership
test and the self-guard inside `_landed_by_sibling` are *equivalences through `disposition_of`*:
the function is reached only after `_landed_unbound` declined, which happens only when every hit is
owned; and a row that owned an in-window instant would have been answered `DELIVERED` branches
earlier. They are not dead code — a direct caller exercises both — so they are graded at the
function, and both mutations fire there. The module docstring says which are which and why.

## 7. A HEAD RED REPAIRED ON THE WAY, AND IT IS THE SAME SHAPE ONE FILE OVER

`test_A_COMMIT_OUTSIDE_THE_WINDOW_IS_NOT_IN_IT_whichever_side_it_falls` has been red at HEAD since
`_landing_grace_seconds` was added on 2026-09-17. The fixture pinned `WINDOW_ENDS + 60` as "outside"
— the *pre-grace* edge — so a commit that is now correctly inside the window read as a failing test
rather than as a subject that had become more honest. Keyed to today's answer, exactly the thing
this repository keeps paying for. Repaired to derive both edges from the same two quantities the
subject derives them from, **plus a third leg asserting a commit inside the grace IS credited**, so
the repair cannot be "widen until green".

The same correction was made to
`test_A_COMMIT_ANOTHER_ROW_IS_CREDITED_WITH_IS_NOT_THIS_ONES_unbound_is_the_word`, whose first leg
asserted `== NOT_DONE` when the property it is named for is `!= LANDED_UNBOUND`. It went red on a
module that had become more honest. Both corrections are written beside the original claim.

## 8. DISPOSITIONS RECORDED

| item | disposition | evidence |
|---|---|---|
| `fit-the-hook-chain-growth-series-...` | **`delivered`** | landed 1789689049 under its own name; the item's premise about it was already false at dispatch |
| `the-commit-hook-chain-has-grown-five-fold-...` | **`landed_elsewhere`** | `decouple-the-early-exit-floor-from-the-regime-constant-...`, `bfbc2b4e9` — derived first, then written by hand so the row carries it |
| `the-publisher-cannot-push-...` | **`landed_elsewhere`** | `the-publisher-has-never-graded-a-clean-publish-and-now-loses-a-race-it-tries-twice`, `1c62e8110` — hand-written, because no derived route can ever reach this row (§3) |

`drawn_without_landing` now returns **one** row, and it is a genuine open window
(`read-the-next12-twelve-alone-once-the-0358-run-settles`, waiting on a long job).

## 9. WHAT IS STILL OWED

The §3 hole. A `focus`-sourced row whose prose names no tracked path can never be disposed by any
join, and the two honest fixes — stamp the item's own prose onto the row at draw, or refuse to hand
out a focus item that names no path — are different designs. The first is cheap and makes the reach-
back unnecessary; the second is a refusal on the seat's own path and would need the director. **The
recommendation is the first**, and it is the next item on this subject.
