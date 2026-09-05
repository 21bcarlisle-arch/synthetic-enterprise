**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: what a standing-red ledger would have escalated, replayed over the real runner log

**Filed 2026-09-05 by the delivery seat from an isolated worktree at `origin/main` = `48e0f20b4`,
BEFORE the replay was written or run.** The mechanism it describes is being built in the same turn;
this fixes what its historical replay is allowed to say before the answer is visible.

---

## Why this is pre-registered when the turn's brief says "do not re-measure"

The brief is right: the four measurements that named the subject compose, and none of them is being
re-run. But the mechanism being built has a number in it — the escalation threshold — and one
question about it is genuinely open: **replayed over the log that already exists, what would this
ledger have escalated, and how often?** That answer is not in any of the four findings. It is a new
measurement, so it gets a pre-registration, and the ledger's design is fixed here first so the
threshold cannot be quietly tuned to make the replay flattering.

## What is being built (fixed here so the replay cannot redefine it afterwards)

`background/publish_standing_red.py` — a ledger of the node ids the pre-commit HOOK CHAIN named at
publish-commit refusal, with an age, a discharge rule, and a route into the draw.

**The population, named before it is counted.** `cycles_blocked` for a node id is *the number of
publish commit-refusal cycles, since the last observed landing, in which the hook chain named that
node id*. It is **not** "consecutive": the hook chain runs fail-fast, so a later refusal naming a
different test does not prove this one green. Gaps are not breaks, and that asymmetry is the whole
design.

**Discharge has exactly one form and absence is not it.** A node leaves the ledger when the hook
chain PASSES — a `git commit` that returns 0 through the same chain. Nothing else discharges: not
absence from a later refusal, not a green scoped gate (a different suite), not age. A ledger that
let absence discharge would read a fail-fast refusal naming test B as proof that test A was fixed,
which is the fail-open twin of the fail-silent this replaces.

**The threshold is 2, and its origin is a measurement, not a preference.** `e0cc653c9` established
that **0 of 7 same-test re-arrivals demonstrably re-broke** — every one was persistence — and
`988270c2e` that 77.8% of same-gate re-refusals carry the identical complaint. So the second
refusal naming the same node id with no landing between it and the first is, by the only evidence
we have, persistence and not a fresh break. Two is where the observed base rate of "this is a new
failure" is zero out of seven.

## The predictions

Made before the replay exists. Threshold fixed at 2 above; **no prediction below may be used to
move it.**

1. **The ledger escalates at least one node id over the retained log.** The log holds a red retried
   24 times; if nothing escalates, the parse or the fold is broken, not the log.
2. **The largest `cycles_blocked` for a single node id is ≥ 7.** Seven same-test re-arrivals were
   already counted, so a maximum below that means the fold is losing subjects.
3. **The ledger is not monotonic: at least one landing discharges a non-empty ledger to zero.** If
   nothing ever discharges, the discharge leg is unreachable and "zero means zero" is a claim with
   no evidence — this is the one prediction I most expect to catch a defect.
4. **At least one refusal in the log names NO node id and folds nothing.** Non-test gates
   (orphan-ratchet, finding-class, level-promotion) refuse without a test verdict; if every refusal
   folds something, the parser is finding tests where there are none, which is worse than finding
   none.

## What would refute the mechanism rather than the replay

If prediction 2 fails **and** prediction 1 passes, the ledger works but under-counts, and the
threshold of 2 is then firing on a population smaller than the one the finding measured — that is a
subject-loss defect in the fold and it is reported as such, not smoothed.

If prediction 3 fails, the escalation is a ratchet with no exit and **the mechanism must not ship in
that form**, whatever the other three say.

## Where the answer will be written

Beside this file, in the finding the same turn files, with the replay's derivation in the module's
own `--replay` so it is re-derivable rather than quoted.
