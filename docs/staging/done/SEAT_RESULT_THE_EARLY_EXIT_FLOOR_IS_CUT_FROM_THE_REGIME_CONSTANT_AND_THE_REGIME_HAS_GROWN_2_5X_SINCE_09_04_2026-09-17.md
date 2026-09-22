**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`decouple-the-early-exit-floor-from-the-regime-constant-then-re-date-the-stale-hook-chain-measurement`)

**Knowledge:** none new from outside. Two constants in `background/process_run_complete.py` are
re-derived from this machine's own ledger and four prose claims in the same file that the
re-derivation falsifies are corrected beside their replacements. No published source is involved
and none is claimed.

# The early-exit floor is cut from the regime constant, and the regime it was tied to has grown 2.5x since 09-04

Delivery seat, 2026-09-17. Scores
`docs/staging/records/SEAT_PREREG_CAN_THE_EARLY_EXIT_FLOOR_BE_CUT_FROM_THE_REGIME_CONSTANT_WITHOUT_MOVING_A_SINGLE_ROW_2026-09-17.md`,
written before any of the numbers below were run and unedited. **P1–P4 hold. P5 held only after
its own first version was found unable to fail — recorded below rather than quietly fixed.**

---

## The disposition checks first

**PREMISE — NOT SPENT.** The item cites `8cb9a6b96`, which is indeed already an ancestor of
`origin/main`. It is the item's PRECONDITION, not its subject: that commit landed the `chains`
field on the row and handed off, in its own message, the two pieces this item names. Re-measured
at draw time: `_recent_hook_chain_seconds` still read `prc.MEASURED_... / 4.0`, and still read
`duration_seconds` alone. Both pieces were outstanding.

**DUPLICATE — NOT THIS WORK.** `the-commit-hook-chain-has-grown-five-fold-and-that-is-what-the-
publisher-keeps-losing-to` is a HEAD_RED_REGISTER / unprocessed-staging item (67 owed reds, the
`CLASS_PUBLISH_GATE_AND_WEDGE` file) that shares the words *chain* and *hook* and nothing else. It
holds no paths and names no constant. Different work on a neighbouring subject; carried on, as the
note allows.

## What was wrong

`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04 = 134` had two derivatives whose gradients point
opposite ways:

| use | must | why |
|---|---|---|
| `1.25 * MEASURED` — the committed headroom floor | **RISE** with the regime | or the deadline reports room that is not there |
| `MEASURED / 4` — `floor_of_a_real_chain` | stay **BELOW the smallest real chain** | it separates a hook that refused early from one that ran the gate |

The second is not a property of the regime at all. An early exit is the hook *deciding not to run
the suite*; it costs about a second whatever the suite costs. So every honest re-measurement of the
first dragged the second up through the population it was supposed to sit under — and the failure
mode is not a red. **It is the whole live half SKIPPING**, silently, in the colour of health.

That is why the refusal on `test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_
today` has spent a fortnight instructing the reader to re-measure a constant that could not safely
be re-measured.

## The measurements

All from `docs/observability/commit_hook_duration.jsonl` on the shared tree, n=195, 2026-08-25 →
2026-09-17 12:40 UTC.

**The two populations, and the empty band between them:**

| | n | span |
|---|---|---|
| early exits | 9 | 0.93 – 1.58s |
| real chains | 186 | 67.44 – 1381.52s |
| **between them** | **0** | **a 42.7x gap** |

`REAL_CHAIN_FLOOR_SECONDS_2026_09_17 = 10.0` — the round number nearest the band's geometric
centre (`sqrt(1.58 × 67.44) = 10.3`), 6.3x above every early exit ever recorded and 6.7x below
every real chain ever recorded. It is not derived from the regime and nothing in the regime moves
it.

**The regime, re-taken (P2 holds):**

| window | reading |
|---|---|
| 2026-08-25 | 837s, 674s — the incident, machine loaded |
| 2026-08-26 → 08-31 | 390–425s (~60 runs, ±4%) |
| 2026-08-31 19:28 → | 101–134s (~40 runs, ±13%) ← the 09-04 reading |
| 2026-09-08 → 09-10 | 91–218s, the climb back |
| 2026-09-15 → 09-17 | 253–333s (9 runs, ±12%) ← **the reading here** |

`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17 = 333`. **The worst row in the window is 666.95s
and that is deliberately NOT the figure**, because 666.95 is a row whose *unit is unstated*:
`b55667741` lost the landing race and its stopwatch spans two chains, as the publisher's own record
says. Setting a per-chain constant from a row that counts two of them would put the exact inference
that wedged the tree on 2026-09-16 into a committed number. The worst row in the window that is not
one of the two the publisher's record names as a multi-chain landing is `770497ddd` at **333.22s**,
a clean `pass`.

**P1 HOLDS — the decoupling is inert on today's data.** Windows compared directly:

| reading | kept | worst |
|---|---|---|
| as found (floor 33.5, no `chains`) | 19 | 666.95 |
| as shipped (floor 10.0, `chains` read) | 19 | 666.95 |

Byte-identical, and the whole-series census is identical too: 9 rows below the floor and 186 above
it at **both** 33.5 and 10.0. Zero rows change class.

**And a correction to my own framing of the harm.** I wrote the coupling up as if re-dating to 333
would have broken the live reading. Measured: at floor 83.25 the current window is *also*
unchanged, because its minimum is 90.68s. The 7 rows a coupled floor would have re-labelled
(67.44, 68.43, 70.70, 71.40, 72.12, 72.69, 72.82) are all older than the window. So this was a
**latent** fail-open, not a live one — armed, not yet fired. That is a weaker claim than the one I
started with and it is the true one.

**P3 HOLDS — and this is the part worth reading.** The live half is RED right now (`worst 666.95 >
0.75 × 880 = 660`) and **nothing here turns it green.** `MEASURED` appears only in that assert's
message, never in its predicate. The red clears when the 666.95 row ages out of the twenty-row
window, exactly as `8cb9a6b96` said, and not a commit sooner. A design that had cleared it today
would have been keyed to today's answer.

**P4 HOLDS.** 0 of 195 rows carry a `chains` count — the field began being written at 19:24 UTC
today and no commit has been recorded since. The stated-unit reading is therefore inert, and stays
inert for twenty commits.

## The reader's new rule

* a **stated** row (`chains` a positive int, and a bool is not one — the same predicate the
  producer writes under) has a per-chain `duration_seconds` and is **not divided again here**;
* a **silent** row is UNKNOWN-UNIT: an upper bound on the per-chain cost, never a measurement;
* the transition is **a full window or nothing.** `max` is monotone in the sample, so preferring
  the stated rows can only ever LOWER what this control demands — the fail-open direction.
  Switching on the first stated row would grade an 880s deadline against a one-row window and call
  it a regime. The stated reading engages at `HOOK_CHAIN_WINDOW_ROWS` stated rows and reads
  exactly that many, so the sample never shrinks at the changeover and **there is no threshold
  between "one row" and "a window" for anyone to pick.**

The cost is that `chains` buys nothing for twenty commits. Accepted rather than worked around.

## P5 — and the version of it that could not fail

Six mutations, each applied to the file, verified to have changed the bytes, run, and reverted.

| mutation | fires |
|---|---|
| floor `= 70.0` (above the smallest real chain) | 2 red |
| floor `= 0.5` (below the worst early exit) | 2 red |
| re-couple: `floor = prc.MEASURED_... / 4.0` | 1 red |
| a silent row read as a stated one chain | 1 red |
| transition threshold dropped to `>= 1` | 1 red |
| a stated row divided again by its own count | 1 red |

**THE THIRD ONE FIRED NOTHING ON ITS FIRST RUN, AND SO DID THE FIRST.** My independence control
called `_recent_hook_chain_seconds` bare. Under the coupled floor the reader **skips** — which is
its correct behaviour and which pytest reports in a colour indistinguishable from a pass. The
battery printed `8 passed` against the single mutation that control is named for. A skip silencing
a leg is a class already in this file's history and I wrote another one into it. `_must_grade`
converts the skip into the failure it always was; both mutations then fire. Recorded here rather
than quietly repaired, because from the outside a control that skips and a control that passes are
the same colour, and the only evidence the difference was found is this paragraph.

## What else this falsified, and was corrected in place

The re-measurement makes four claims in the same file untrue. Correcting them is the point of the
interconnection pass, and the file already carries a scar for exactly this — one refuted claim read
as current inside the file that disproved it.

* *"the commit hook chain ~134s"* → **~333s**.
* *"the second run is a FIFTH of the first"* → **roughly two fifths**. The publisher's own scoped
  gate has grown too: full runs in the last 60 rows of `publish_gate_duration.jsonl` span
  563–1004s, median **837s** (the sub-200s rows are early failures, not gate runs). The throughput
  conclusion *"there is no headroom in this lever"* survives — halving the gate returns ~7 min of
  a ~19.5 min cycle rather than the ~5 min claimed — but it now rests on a measurement rather than
  on a ratio that had rotted.
* *FLOOR 168s* → **416s** (`1.25 × 333`).
* *"the room is 732 seconds"* → **484 seconds.** Worth stating plainly: the floor rises with the
  chain, and at the growth observed since 09-04 it reaches the 900s ceiling
  (`PUBLISH_PATH_ALLOWANCE_SECONDS`, which the director has ruled may not grow) **in about a
  month**. That, and not 880, is the wall this deadline is walking toward.

## Done, against the bar set in the prereg

1. ✅ `floor_of_a_real_chain` reads a constant `MEASURED_...` cannot move, carrying its own date,
   band and placement argument.
2. ✅ `MEASURED_...` re-measured, re-dated `2026_09_04` → `2026_09_17`, 134 → 333.
3. ✅ `_recent_hook_chain_seconds` reads `chains`, prefers stated rows, treats silence as unknown
   unit, and cannot return a degenerate window at the transition.
4. ✅ Six mutations applied, observed, reverted — in this isolated worktree, never the shared tree.
5. ✅ Landed and promoted by the ordinary route.

## Still owed — and it is a prediction, not a finding

**The 484-second room is the next thing to look at, and I have not looked.** The floor is
`1.25 × MEASURED` and `MEASURED` has gone 134 → 333 in thirteen days. If that continues, the
committed half of the headroom control and
`test_the_deadline_leaves_room_for_the_publish_path_after_the_gate` intersect emptily again — the
identical shape as 2026-09-04 and 2026-09-16, reached a third way. I have **not** established that
the growth is linear, or that it is growth rather than a regime step like 08-31's; two readings do
not make a trend and I am not going to claim one. The honest statement is that the room halved in a
fortnight and nothing is watching it. Whoever takes that should fit the series, not the endpoints.
