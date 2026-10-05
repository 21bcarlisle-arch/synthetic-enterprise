**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality` · **Claim:** `w2-36-second-slice-wire-estimated-reads-into-the-run-and-size-persistence`

# W2_36 second slice: the world's read process now lets an estimated run outlast the back-billing limit

## Where the work came from

The duplicate-work note at draw time named this same id as already held. That holder was this
invocation's own draw. It was written at 19:15:54, and the draw ran at 19:15. No rival seat or
`surgical_land` on W2_36 was running.

What the draw did not say: the shared tree already held this slice, unlanded. It was written at
17:45 by a tick that is no longer running. That tick had rewritten `simulation/meter_reads.py` and
`tests/simulation/test_meter_reads.py`, deleted `simulation/unbilled_energy.py` and its test, taken
the module off `docs/design/orphan_baseline.json`, and repointed the Q2 solver in
`docs/market_research/assumption_toggles.yaml`. This invocation took that pile into an isolated
worktree, read it, finished it and landed it. The shared tree's copies are now superseded by
origin.

## The decisions

1. **The persistent process replaces the read draw in `meter_reads.py`; `unbilled_energy.py` goes.**
   The item's step (1) asked whether it should. Two implementations of one read process is the VAT
   shape, and `meter_reads.py` is the one the run already uses. It reaches the company through
   `company/interfaces/bill_assembly.py`'s `ReadArrivalFeed` and `_resolve_catchup`. The
   first-slice module had no caller. Its unsized chain is superseded by the director's ruling of
   2026-10-05 on practitioner questions.
2. **The process is the register's Q2 model, not the item's p-sweep.** The item asked for
   `MONTHLY_ESTIMATE_PERSISTENCE` to be swept from 0.80 to 0.99. By draw time the register
   (`q2_persistent_unread_share`, `q2_no_read_12m_share`) had already replaced that framing with a
   different model. A small hard-to-read class is read about once in four years. Everyone else is
   read memorylessly, at the rate solved to give Ofgem's 7% with no actual-read bill in 12 months.
   That is now what the world runs.
3. **There is no forced read at 12 months.** The 12-month rule is the company's (SLC 21BA, in
   `company/billing/back_billing.py`), not physics. With the old forced read, every estimated run
   ended at 12 months, so the cap could never bind from an ordinary run. A new run-level control,
   `test_an_estimated_run_past_12_months_is_not_forced_and_its_final_read_meets_the_cap`, shows
   both halves. Sixteen estimated months stay estimated, and the closing read is an undercharge
   that the cap writes off.
4. **Step (4) of the item needs no new seam.** The company already observes the read basis of
   each bill and resolves a catch-up when an actual read arrives. Used energy does not cross.

## The sweep (pre-registered before it ran)

Pre-registration, written before the run. The settings were π ∈ {0, 0.01, 0.03} for the
hard-to-read share, with the 12-month no-read share held at 0.07, over traditional meters.

- P1: the 12-month no-read share is about 0.07 at every π.
- P2: the barred share is invariant in π to within 0.005. The barred share is the months more than
  12 back at their catch-up, divided by all months.
- P3: the share of catch-ups that end a run of 24 months or more rises with π.
- P4: the easy-class rate falls slightly as π rises.

The first run used 60-month histories and 4,000 households. It was confounded: hard-class runs
average about 50 months, so most of them were cut off by the window. The second run used
600-month histories and 600 households.

| π | easy-class monthly rate | 12-month no-read | barred share | share of catch-ups ≥24 months | share of barred months in runs ≥24 months | longest run |
|---|---|---|---|---|---|---|
| 0 | 0.1988 | 0.0702 | 0.0545 | 0.0055 | 0.263 | 57 |
| 0.01 | 0.2060 | 0.0701 | 0.0546 | 0.0054 | 0.339 | 177 |
| 0.03 | 0.2237 | 0.0720 | 0.0575 | 0.0051 | 0.502 | 316 |

- **P1 held.**
- **P2 held**, with a spread of 0.003.
- **P3 was wrong.** The per-catch-up share falls slightly. A hard-to-read household has very few
  catch-ups, and the easy class is read more often. The shape moves in a different place: the share
  of barred energy that comes from runs of two years or more goes from 26% to 50%.
- **P4 was wrong in direction.** The easy-class rate rises with π, because the hard class absorbs
  part of the unread share.

**Verdict for the item's step (3).** No current company decision reads the tail. The total that the
back-billing limit bars does not move with π, so pricing and the accrual are unaffected. That
matches the register: DOESNT_MATTER for aggregates. What π moves is the shape: fewer, larger,
older back-bills. That becomes decision-relevant once D48 or W2_37 builds read-chasing or complaint
handling, and it should be swept again there.

The control
`tests/simulation/test_meter_reads.py::test_the_hard_to_read_share_moves_the_shape_of_back_bills_and_not_their_total`
holds both legs. Two mutations were tried, and each turned it red:
- `is_hard_to_read` always returns False.
- The hard-class rate is ignored.

## Open, not done here

- `tools/assumption_toggle_sensitivity.py` is named five times by the register and exists on no
  branch. Its only copy is in a `fork_salvage` commit, `99694ad9a`.
- `meter_reads.py` is in the value-cycle run's import closure. The current-world arms block was
  already refused at HEAD, on `company/analytics/forward_clv.py` and
  `company/carbon/half_hourly_footprint.py`. This change adds a path to that refusal and withdraws
  no headline that is live now. The next arms re-take runs on the new read process.
- W2_36's `file_scope` now points at `simulation/meter_reads.py` and its test.
