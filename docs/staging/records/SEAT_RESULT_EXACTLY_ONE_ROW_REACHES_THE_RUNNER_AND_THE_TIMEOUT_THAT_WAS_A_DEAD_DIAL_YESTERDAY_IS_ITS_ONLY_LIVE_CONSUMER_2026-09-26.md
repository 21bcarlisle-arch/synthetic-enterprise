**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — exactly one row reaches the runner, the 60s timeout is its only live consumer, and raising it buys nothing

Drawn on the scheduled tick of 2026-09-26 as LANE 0 DELIVERY, claim
`does-the-level-zero-pass-reach-a-runner-at-all`. The item instructed: *partition the population by
which leg of the pass each row dies at, with `budget_s=0` (free), BEFORE touching a timeout.*

## The premise was half spent, and the half that was live has moved

`d01283d58` had already run that partition and published it in
`SEAT_FINDING_NO_ROW_IN_THE_LEVEL_ZERO_POPULATION_EVER_REACHES_A_RUNNER_..._2026-09-25.md`, whose
headline is **"Not one row in the population reaches the pytest invocation"** and whose conclusion
is that `DEFAULT_TIMEOUT_S` and `background/delivery_seat._LEVEL_ZERO_TIMEOUT_S` are **dead dials**.

Re-measured on the live map one day later, both are false. Correction filed beside the claim in
that file.

Free partition, `--budget 0`, 2026-09-26 — the `>= budget` check sits after every cheap leg and
before the only expensive call, so a row returned by it is a row that WOULD have reached the runner:

| leg | 2026-09-25 | 2026-09-26 |
|---|---|---|
| `NO_CONTROL_NAMED` | 20 | 14 |
| `CONTROL_PREDATES_ROW` | 5 | 8 |
| `NAMED_CONTROL_ABSENT` | 2 | 4 |
| silenced by the HEAD-red register | 1 | 1 |
| **reaches the runner** (`BUDGET_EXHAUSTED` under the free probe) | **0** | **1** |
| population | 28 | 28 |

And in the seat's own production configuration (`timeout_s=60`, `budget_s=300`):
`reached_the_runner: 1`, `clears_every_cheap_leg: 1`.

## The one row, and why its dial is live and still not worth turning

`OPS6_scoped_publish_path_suite` names `tests/background/test_publish_scope.py` and
`tests/background/test_process_run_complete.py`. Measured, not reasoned:

- the named set costs **109s** wall clock (`1 failed, 134 passed in 108.97s`)
- production caps each atom at **60s**, so the row returns `RUN_UNAVAILABLE — timed out after 60s`
- at `--timeout 600` it runs to a verdict, and the verdict is **SILENT**: the set does not all pass
  (`test_a_root_unavailable_scope_stops_the_gate_instead_of_running_it` is red), and `CONTRADICTED`
  needs the whole named set

So `_LEVEL_ZERO_TIMEOUT_S` is not a dead dial — it is the sole live consumer in the partition, and it
bites the only row that gets that far. **Raising it is still the wrong move**, and that is now a
measurement rather than a preference: 109s against a 300s pass budget in a three-hourly orientation,
bought in exchange for a verdict we can already derive — the set holds a red, so silence is the only
answer it can return. The dial was not turned. What was missing was never the number; it was that
nothing on any surface said which of the two worlds the census was in.

## What was built

`graded` counts rows the pass did not refuse. A row silenced by the HEAD-red register satisfies that
with no control executed, so `graded: 1 of 28` and "a runner weighed a row and found it wanting" are
the same sentence for two unlike worlds — and on the live map the graded row (`KNIFE3_wall_crossing_paydown`,
silenced) is not even the row that reaches a runner (`OPS6`). Two different rows behind one `1`.

1. **`assess(..., leg_log=[])`** — an out-parameter, not a third return element, because twenty-one
   call sites unpack the two-tuple. Written at the single point each row leaves the loop, never
   re-derived by a second reader: a leg added in one place and not the other would silently stop
   being counted, which is the exact defect the log exists to make visible. Two leg names no
   `reason` string covered, because neither is a refusal: `SILENCED_AT_HEAD` and `REACHED_THE_RUNNER`.
2. **Two numbers on both surfaces** (`--json`, stderr, and the seat's `self_contradicting_levels`
   brief): `reached_the_runner`, and `clears_every_cheap_leg` = reached + budget-exhausted.
   Publishing only the first would be a trap: under the free probe `--budget 0` a row that would
   reach the runner is returned by the budget check, so `reached` reads 0 for a reason about the
   probe and not about the map. The second is budget-independent and is the number to read.
3. **When nothing reaches a runner the surface says so in those words** — `NO RUNNER WAS ASKED
   ABOUT ANY OF THE N ROW(S) … NO CONTROL WAS EXECUTED`, above the `graded` line that was misread.
4. **A repair to `test_every_verdict_names_a_live_atom_actually_in_the_partition`**, which was
   RED in the shared working tree and is the same defect one level up: it asserted
   `contradicted | ungradable == candidates`, true until the HEAD-red leg landed on 2026-09-25 and
   gave the pass a third outcome the test did not know about. Repaired by asking the leg log, not
   by pinning today's silent id — which would have gone green and stayed green when a second row
   started being silenced for another reason.

Nine mutations run, all fire, each on the leg written for it: dropping any of the three logged legs,
`reached` hardcoded to 0, `reached = len(legs)`, `cleared` dropping the budget term, the banner made
unconditional, and the brief dropping `leg_log=`.

## What is still owed

Nothing in this claim. The adjacent repair filed on 2026-09-25 — whether `controls_older_than_the_row`
can be taught to see a control an atom EXTENDED rather than created, which is the 8 rows now in
`CONTROL_PREDATES_ROW` — remains filed and unbuilt, with the measurement that refuses the obvious
version of it (commit subjects naming the full atom id: **zero**).
