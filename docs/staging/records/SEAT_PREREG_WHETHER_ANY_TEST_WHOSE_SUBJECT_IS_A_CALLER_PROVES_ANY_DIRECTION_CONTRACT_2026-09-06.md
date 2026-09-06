**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: whether any test whose subject is a CALLER proves any `direction` contract

**Written 2026-09-06, delivery seat, shared tree at `d700de016`. Claim id
`direction-battery-four-columns-are-direct-importers`. Every prediction below is fixed BEFORE the
re-run and this file is landed ahead of the result, so the ordering is in the record and not in a
claim about the record.**

---

## 1. The question, and why the cells on disk cannot answer it

`tools/direction_contract_battery.py` scores eight contracts against four caller suites. All four
import `background.direction` at module level, and all four are legitimately the dedicated suite of
a module that calls it — which is why `b3938b313` ran the census before writing the caller-verdict
gate and shipped no gate on "imports the subject". `direction` is the only spec in the family where
every column is in that state.

The census this turn asked the sharper question — does the suite NAME a contract of the subject —
at the NODE grain rather than the file grain, by AST over the four files: a test is the subject's
own if its assertions run against `background.direction`'s API and it never calls the module the
file is named for. It finds **23 such tests in three of the four files**:

| file | tests naming a `direction` contract | tests that also call the file's own subject |
|---|---|---|
| `test_supervisor.py` | **0** — the only reference is the fixture's `monkeypatch.setattr(DIRECTION_PATH, ...)` | — |
| `test_delivery_lane.py` | 1 (`test_a_MISSING_or_BROKEN_record_offers_nothing`) | 1 (`test_EXPIRED_direction_offers_NOTHING`, calls `dl.`) |
| `test_delivery_seat.py` | 17 | 0 |
| `test_the_self_audit_...py` | 5 | 0 |

So the four columns are not four caller suites. Two are (`test_supervisor.py` entire,
`test_delivery_lane.py` less one node); two are files named for a caller that contain
`background/direction.py`'s own test suite, written with `MUTATION (must fire)` docstrings against
`direction`'s code and calling `d.focus_multiplier`, `d.validate`, `d.wrong_rows`, `d.focus_weights`
directly.

**And the recorded cells cannot settle what follows from that.** Every mutation cell was run under
`-x`; each records exactly one `FAILED` node and the tail says `stopping after 1 failures`. The one
node named in each killing cell is, in all six killing cells, one of the 23 — but `-x` means a
caller-subject test in the same file may also have gone red behind it and been never collected. The
question is genuinely open and only a re-run with the 23 deselected can close it.

## 2. The mechanism, fixed before the run

`BatterySpec` gains `direct_nodes`: node ids deselected from the CALLER columns only, hashed into
the fingerprint for the same reason `direct_suites` is — every cell measures what it measured
before and what `survived_all` MEANS changes. `direction` declares the 23 the census found.

## 3. The predictions

**P1 — the standing one.** All eight mutations survive all four caller columns: **8 of 8 unproved
by any caller**, against the two of eight published in
`SEAT_RESULT_THE_FOURTH_COLUMN_SURVIVED_ENTIRE_...2026-09-05.md`.

**P2 — per mutation.** Every one of the six published kills is by one of the 23 and disappears:

| # | published killed_by | predicted after deselection |
|---|---|---|
| M1 | seat | survives all four |
| M2 | — | survives all four (unchanged) |
| M3 | seat | survives all four |
| M4 | seat | survives all four |
| M5 | audit | survives all four |
| M6 | lane **and** seat | survives all four |
| M7 | — | survives all four (unchanged) |
| M8 | audit | survives all four |

**P3 — M6 is the one at risk, and it is named as such.** M6 is the only mutation with a kill in a
file that still has a caller-subject test using direction (`test_EXPIRED_direction_offers_NOTHING`,
which calls `dl.` and sets up a stale record). If any prediction here is wrong it should be this
one, and P1 falls with it.

**P4 — the supervisor column needs no re-run, and that is a proof rather than a saving.**
Deselecting tests can only remove failures, never add them, so a column already green on all eight
stays green a fortiori. Its 850s-a-pass cost is not paid and nothing is assumed by not paying it.

**P5 — direction of movement.** The caller answer is weaker than the published one and never
stronger. This is the third subject to move that way (`segment_vocabulary` 0→3 of 8 unproved,
`fuel_mix` 2→0 of 10 killed), and a mixed population is guaranteed to bias in that direction, so a
move the other way would mean the reduction is wrong rather than the publication.

## 4. What would refute the framing

If a caller-subject test kills any mutation, then "the file is named for a caller" and "the file
contains the subject's own suite" are not the clean split this proposes, the node grain buys
nothing over the file grain, and the published two-of-eight stands with only its wording corrected.

## 5. What this does NOT claim

Not that the 23 tests are misplaced or should move file. They are correct tests in a reasonable
home. The claim is only about which population may answer *"did anything other than the subject's
own tests prove this contract"* — and a test that calls `d.validate` and nothing else is the
subject's own test wherever it lives.
