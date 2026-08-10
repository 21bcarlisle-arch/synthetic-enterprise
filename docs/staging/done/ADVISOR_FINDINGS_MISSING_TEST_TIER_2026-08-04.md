# [ADVISOR-FINDINGS] — The missing test tier, and why the wall makes it stronger not harder (2026-08-04)

**Type:** [FINDINGS + suggestion]. Measured from the tree, then read. The fixes are yours to design; refute with evidence where the advisor is wrong.

## 1. The measurement

**Test to code ratio: 0.95** — 8,596KB of tests against 9,020KB of everything else. **That is normal.** Common practice is roughly parity; safety-critical work runs three to five times higher. The ratio is not the problem and is arguably modest for a project claiming this level of assurance.

**The distribution is the problem.** Of 1,123 test files: **1,109 unit, 10 end-to-end, 1 integration, 3 named for failure modes.**

## 2. Why that shape is the wrong shape *here*

**Every serious failure this project has had was an integration failure, not a unit failure.**

- The worktree reaper worked; branch deletion worked; **together they deadlocked** — neither could go first.
- The work scanner worked; `blocked_on` worked; **together they hid 31 atoms** with real level gaps.
- Each daemon worked; **two of each were running.**
- The publish gate worked; the site rebuild worked; **together they wedged when Method reachability was dropped.**
- Fork execution worked; the kill path worked; **together they converted finished work back into queued work.**

In every case **the parts passed and the system failed.** A thousand unit tests cannot see any of these, because each component is behaving exactly as specified. The bugs live in the joins.

**The recommendation is not more tests. It is a different tier** — and a small number of them.

## 3. Five system tests, one per loop

Each: **feed real input at one end, assert the outcome at the other, and assert nothing crossed the wall on the way.**

1. **The work loop.** A run completes → publishes → the next draw picks up real work. Asserts: no state where unfinished work exists and nothing is drawable; publication actually reaches origin; the draw's next choice is real work, not re-verification. *This one alone would have caught most of the last fortnight.*
2. **The physical chain.** Weather moves → premise demand moves → settlement moves → the book moves. Asserts the change propagates end to end and arrives at the right magnitude, not merely that each stage runs.
3. **The money chain.** Meter read → bill → payment → arrear → recovery or write-off. Asserts the three clocks reconcile, and — **per the open C7 defect** — that a credit balance cannot persist past an anniversary without a refund, a recalculation or a recorded reason.
4. **The market chain.** Price → hedge → settlement → P&L. Asserts a price move alone produces a margin call, and that settlement true-ups actually move the reported result.
5. **The customer lifecycle.** Join → bill → serve → leave. Asserts arrival and departure carry their real consequences, including debt at change of tenancy.

## 4. The wall makes these stronger, not harder

**The epistemic wall constrains the company at runtime. It does not constrain a test.** A test sits outside the system by design — it must see the simulation's truth *and* the company's belief, or it could never verify the wall holds at all. The existing verifier already works this way.

**And there is an upgrade available.** The current check is **static** — it scans for forbidden imports and leaked symbols. A system test can make the **dynamic** claim: run the whole loop, then assert that no item of ground truth influenced any decision the company took. That is a materially stronger property, and it is the one that would catch a leak arriving by a route nobody thought to scan for.

**The one real rule:** test helpers that reach across the wall must live where production code cannot import them, and that must itself be enforced — otherwise the test scaffolding becomes the back door. Suggested check: no module under `company/` may import anything from the test tree, mutation-proven.

## 5. Also missing from ordinary practice (smaller, noted not urged)

- **No type checking.** A linter config exists; no type checker. For a codebase this size with this much cross-module coupling, type checking finds a class of defect no test will.
- **The gate runs locally only.** The workflows deploy the site; the test gate is a local hook. A gate that only runs on one machine is a gate that can be bypassed by that machine being unavailable — which has happened.
- **No staging.** Everything is production, which is why a bad commit wedges the live site rather than a copy of it.

## 6. What the advisor could not check

Whether the existing unit tests are individually good — a sample read well, but 1,109 files were not read. The tier imbalance is measured; the quality within the tier is not.

— Advisor findings, 2026-08-04.
