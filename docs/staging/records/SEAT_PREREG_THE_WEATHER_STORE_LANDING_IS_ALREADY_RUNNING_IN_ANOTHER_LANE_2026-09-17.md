**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# PREREGISTRATION: my drawn item is being landed by another lane while I read it

Delivery seat, 2026-09-17 04:06 BST. Claim `land-the-per-cell-weather-store-and-wire-its-reader`.
**Written before any of the measurements below were run**, and before the other lane's process had
exited.

## The situation this registers

At 04:06 I found PID 1092137, started 03:43, running `python3 -m tools.surgical_land` on the shared
tree with the paths of my drawn item: `simulation/fabric_demand_path.py`,
`simulation/run_phase2b.py`, `tools/build_weather_world.py`, `docs/design/orphan_baseline.json`,
`sim/weather_world/{cells.json,daily.csv.gz,regimes.json}`, plus a WORKER_RESULT document, with
`--drops tools/fabric_settlement_gap.py`.

This is the live-concurrent-repair shape: the queue drew me onto work a worker lane had already
started. The item's own closing paragraph warns against spending an invocation re-deriving work
already done, so what I register here is **what I expect to find, so that what I actually deliver is
judged against a prediction rather than against whatever turns out to be left.**

## Predictions, numbered so they can be refuted individually

**P1 — the other lane's landing succeeds and reaches origin/main.** It has been running 23 minutes,
which is inside the normal nine-gate cycle, and its message is a finished one. If it succeeds, the
*wiring* half of my item is spent and re-doing it would be the waste the item warns of.

**P2 — the ERA5 pull is NOT finished by that landing, and that is the half left for me.** Its own
commit message says so under a heading `KNOWN INCOMPLETE, AND IT FAILS CLOSED`: *"52 of 221 cells
hold temperature only: Open-Meteo rate-limited the ERA5 pass (60/120/180s backoff) after 31 of 83
cells."* My item's first clause — *pull the 18 temperature-only cells and the 65 book cells the
store never held* — is therefore **not** spent; it is larger than when the item was written, because
the book cell count went from 156 to 221.

**P3 — `validate_weather_world` against the landed store will report exactly `52 of 221` cells
holding temperature only.** This is the claim I am least willing to adopt on trust: it is a number
in a commit message written by its own author, and a WHAT-LANDED-style receipt is this project's
least re-checked claim surface. If the validator says a different number, the commit message is
wrong and that is the finding.

**P4 — resuming `--build` will skip the already-complete cells rather than re-pulling all 221.**
`_existing_rows` was repaired on 2026-09-16 to read the regime key correctly; if the resume is still
broken it will try to re-pull everything and I will see 221 fetches, not ~52. A broken resume is a
defect worth more than the pull.

**P5 — Open-Meteo rate-limits me too, and I finish fewer than 52 cells.** I am predicting this
because the other lane hit 429s an hour ago and the limit is per-source-address, not per-process. If
I am refuted and the whole remainder completes, good; if I am confirmed, the increment I land is
partial and `available()` refusing an incomplete cell is what keeps that honest rather than
dangerous.

**P6 — my item's instruction to remove ALL THREE rows from `orphan_baseline.json` is wrong on the
tree, and the other lane's one-row judgement is right.** `tools.build_weather_world` and
`tools.validate_weather_world` are CLI entry points that nothing imports, and the ratchet does not
count test files as entrypoints, so removing their rows asserts a reachability the tree does not
have. **A drawn item's remedy is an un-re-asked prediction like any other factual claim it makes.**
I will ask `orphan_ratchet`, not the item.

## What "done" means for this turn, decided before I know the answer

The store is an artefact whose value is coverage, so done is **more cells carrying all six variables
than when I started, landed, with the validator's verdict published beside it** — not "the FAIL is
gone", which depends on a rate limiter I do not control. A partial pull that fails closed is a real
increment; a full pull I cannot finish is not a reason to land nothing.
