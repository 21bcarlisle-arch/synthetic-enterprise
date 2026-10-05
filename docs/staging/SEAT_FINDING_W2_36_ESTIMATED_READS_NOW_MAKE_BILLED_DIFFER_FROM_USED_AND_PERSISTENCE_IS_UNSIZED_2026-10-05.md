**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` · **Claim:** `w2-36-first-slice-estimated-reads-make-billed-differ-from-used`

# W2_36 first slice: estimated reads now make billed differ from used, and the one rate that sizes them is not established

At draw time the duplicate-work note named this same id as already held. The holder was this
invocation's own draw (no rival seat or `surgical_land` on W2_36 was running).

## The stray draft is superseded

`.claude/worktrees/agent-ab1767e2116083819/docs/market_research/unbilled_energy_and_revenue_assurance.md`
(untracked) was diffed against origin's copy. Both have 416 lines. The only difference is one path:
the draft cites `docs/staging/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`, and origin cites the
same file under `done/` after it was archived. Nothing to fold in, so the draft is superseded. It was
not deleted, because that worktree's owner pid (2197437) is alive.

## What was built

`simulation/unbilled_energy.py` adds K2 from the research doc, one kind of unbilled energy. Each
household carries a read state (actual or estimated) from month to month. Estimated months bill the
average use of the last read interval, so used and billed drift apart. The next actual read trues
up: the gap closes to zero, and the catch-up can be a debit or a credit.
`tests/simulation/test_unbilled_energy.py` has 6 tests. It includes the partition control
(`branches == {actual, estimated, true_up}`) that proves the rare true-up branch can be reached. Four
mutations were tried (no true-up, broken hazard, branch label collapsed, refusal replaced by a
number). Each turned at least one test red.

## What sizes it, and what does not

The doc establishes one figure: Ofgem 2017, 5.2–5.6% of customers with no read-based bill in a year.
A two-state chain needs two rates. Under stationarity the share = π_E·p¹¹, so the entry hazard q
follows from the share **only once persistence p is given**. Persistence is the doc's §6 gap 1, a
practitioner question. `MONTHLY_ESTIMATE_PERSISTENCE = None`, and the sourced leg refuses with that
reason.

**Measured, not assumed:** printing q against p showed what the published share requires.
- **Floor:** p ≥ **0.781** (0.778–0.783 across the range). Any lower and q would exceed 1.
- **At and above the floor:** the derived q reproduced the share in simulation (0.054–0.056 at
  p = 0.8–0.99).

**Correction:** my first draft bounded only π_E < 1 (floor 0.767) and returned q = 5.14 at
p = 0.77. The printed table caught it before any test was written.

**What the floor says about today's world:** `simulation/meter_reads.py` reads a traditional meter
with independent probability 1/6 a month, so p = 5/6 ≈ 0.83. That is just above the floor, i.e. it
sits near the shortest spells the published share allows. The doc's reading (a minority almost never
read) would put p much higher (0.95+ gives π_E ≈ 6–9%).

## Not done (continuation)

- **Wiring:** this module is not wired into the run loop or settlement, and nothing crosses the seam.
  It is recorded as deliberately dormant in `docs/design/orphan_baseline.json` until that wiring lands.
- **Persistence:** the value is a question for the director. Recommendation: ask the practitioner
  for "how long does a household that has gone unread typically stay unread", and sweep p over
  0.80–0.99 until it is answered.
