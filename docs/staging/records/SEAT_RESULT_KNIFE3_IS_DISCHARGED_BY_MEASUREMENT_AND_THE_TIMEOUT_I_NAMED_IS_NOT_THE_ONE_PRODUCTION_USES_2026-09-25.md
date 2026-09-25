**Severity:** INFORMATIONAL · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# KNIFE3 is discharged by measurement — its verdict is SILENCE — and the timeout I told the next reader to price is not the one production uses

Result record for
`SEAT_FINDING_THE_RECONCILER_THREW_AWAY_NINE_ATOM_OWN_CONTROLS_FOR_THREE_OLDER_ONES_AND_TWO_ROWS_NAME_AN_ABOLISHED_SUBJECT_2026-09-25.md`,
landed in `8a1269101`. That finding left two things open and named a third wrongly. All three are
settled here, beside the claims rather than instead of them.

## 1. I named the wrong constant, and the correction matters more than the slip

The finding says *"`DEFAULT_TIMEOUT_S` is NOT edited here… what the twelve suites cost is being
measured and the change is made against that"*, and lists pricing the 900s timeout as owed work.

**`DEFAULT_TIMEOUT_S` is not the binding constant.** The only production caller is
`background/delivery_seat.py:1038`, and it passes its own bounds:

```
_LEVEL_ZERO_TIMEOUT_S = 60      # per atom
_LEVEL_ZERO_BUDGET_S  = 300     # whole pass
```

900s is the standalone default. At orientation the cap is **60 seconds**, and the comment above it
already says why, naming this very row: *"the other two — `D27…` and `KNIFE3_wall_crossing_paydown`
(twelve architecture suites) — exceed any cap worth setting and simply consume it. So the per-atom
cap's job is to give up on those two QUICKLY rather than to let them finish."*

That reasoning is sound and I am not proposing to undo it. But it has a consequence nobody had
written down: **the instrument, as it actually runs, cannot grade any row whose named set costs more
than 60 seconds** — and the rows that name the most controls, which is to say the rows carrying the
most evidence, are exactly the ones it can never afford to weigh. `graded` at orientation is bounded
by COST, not by evidence. Raising `DEFAULT_TIMEOUT_S` would have changed nothing in production, and
a reader following my "owed next" line would have spent a turn discovering that.

## 2. What KNIFE3's twelve suites actually cost

Run as one invocation, exactly as `assess` runs them, on this machine:

| | |
|---|---:|
| elapsed | **1078.5 s (17 min 58 s)** |
| peak RSS | 2,562,740 KB (**2.44 GB**) |
| collected | 224 tests |
| standalone default cap | 900 s → **times out** |
| orientation cap | 60 s → **times out, 18× over** |

Measured under concurrent load (a sibling lane's `surgical_land` gate run held several cores
throughout), so this is the contended cost rather than the clean one. Stated because it is the
wrong direction to quote as a clean figure — but it is also the condition the instrument actually
runs in at orientation, where daemons are live by definition.

## 3. The verdict, established: KNIFE3 is SILENT, not contradicted

**2 of its 224 tests fail**, both in `tests/simulation/test_home_move_undeliverable_win.py`:

- `test_a_won_home_mover_with_no_successor_still_goes_to_market`
- `test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market`

**They reproduce in isolation** — that suite alone is 2 failed / 4 passed in 536.8 s — so this is
not the full-suite pollution class (`H40`, itself one of the 28). The cause is a
`LiveLedgerWriteUnderTest` refusal: the test process attempts to write
`docs/observability/coupled_gap_ledger.json`, a live observability record, and the choke point
refuses it by design.

**And it is already known.** `docs/staging/reference/HEAD_RED_REGISTER.md` carries both node ids at
**19 consecutive census runs, first seen 2026-09-02** — red at HEAD for 19 days, among 41 owed.

So the named set does not all pass, and under `assess`'s three verdicts that is **(silent)** — "the
map and the controls agree that something is unbuilt. Nothing to say." `KNIFE3_wall_crossing_paydown`
at `level_current: 0` is **right**, and no level move is owed.

**One of the 28 is now weighed.** Not by the instrument — by hand, because the instrument cannot
afford to. That is the discharge the drawn item asked for, and it lands on the un-flattering side:
the row is honest. For this row, cause A holds.

## 4. Which corrects the finding's P4 properly

The finding recorded P4 (*"≥1 row, once gradable, comes back CONTRADICTED"*) as REFUTED because no
row became gradable — true, but it left open whether a row WOULD have. It would not. With an
unbounded timeout KNIFE3 returns silence, and it is the only mixed-set row in the partition. **P4 is
refuted on the merits, not on a technicality.**

## 5. The mechanism this points at, and why it is not built here

A row naming a suite that is **red at HEAD** cannot possibly be CONTRADICTED — contradiction
requires the whole named set to pass. The register already knows which suites those are. So the
expensive run is skippable for exactly the rows that are too expensive to run: resolve to silence in
microseconds, and `graded` moves without the 18-minute pass.

It is not built in this turn, and the reason is the direction it fails in. Silence is the
NON-refusing verdict, so keying it off the register means **a stale register silences a genuinely
contradicted row** — a fail-open on the precise defect this instrument exists to catch. The register
is currently stamped `2026-09-22T04:23:51+00:00 at HEAD f705248ae`, three days and many commits
behind. Any such short-circuit must therefore fail CLOSED on a stale or unreadable register (run the
suites), and that requires its own control proving the stale arm is reachable. That is a designed
change with its own evidence, not a thing to append to a turn.

## What is owed, corrected

1. **Strike "price the 900s timeout"** from the previous finding's owed list — wrong constant, and
   the right one (`_LEVEL_ZERO_TIMEOUT_S = 60`) is deliberate and should stay.
2. **The red-at-HEAD short-circuit**, fail-closed on register staleness, with a control proving the
   stale arm fires. This is the piece that actually moves `graded` for the expensive rows.
3. Unchanged from the finding: `SITE3_wall_exhibit_url_rename` closed as superseded;
   `C_supply_start_consumer_routing`'s unsatisfiable R11 wall ruled on; a cause for an abolished
   subject in `ungradable_causes`.
