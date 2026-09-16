**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `PB3_book_growth_as_earned_outcome`

*Born archived: a new instance of the existing class `figures_on_a_superseded_clock`, filed to
`done/` rather than staged live. The one part of it that is NOT an instance of a known class —
§3 — was fixed in the same tick and its control landed with it.*

# The book's belief-vs-truth gap sat five days on a superseded clock, and the check that grades whether a re-measurement is comparable could never have graded this row

Worker tick, 2026-08-30, at HEAD `357568b87`. All claims `observed-with-evidence`.

## 1. The instance

`docs/observability/coupled_gap_ledger.json` published `PB3_book_growth_as_earned_outcome` at
`gap = 1.2285`, measured `2026-08-25T17:31:02`, `run_git_commit d62a8e158`. On the Proof door that
value takes the chip `worse_than_blind`, severity **red** (`tools/generate_proof_data.py::_coupled_gaps`),
and it was one of the four rows behind the panel's published `worse_than_blind_count: 4`.

Re-measured this tick against the shipped campaign record, no code change:

    python3 -m tools.couple_pb3_book_growth
      scored (market-decided)  : 10   EXCLUDED (machine-bound) : 0   dropped : 0
      mean |err| LEARNED       : 0.025835
      mean |err| NO-SKILL (g0) : 0.031140
      GAP (normalised)         : 0.8296

**The door said the company's learned belief was worse than never updating. It was better.** The
supplier's own quote book beat holding the founding 0.20, over ten market-decided years, nine of
which planned on a learned rate. Ledger refreshed at `2026-08-30T10:45:26`, commit `357568b87`.

Nothing about the world changed to produce that: the number moved because
`tools/couple_pb3_book_growth.py` was re-keyed on 2026-08-29 (`_realised_rate` moved to
`funnel_wins`, and the headline learned to refuse itself when no scored year planned on a learned
rate), and **nothing re-ran it**. `--write-ledger` is opt-in and has no production caller.

## 2. The register saw it for five days — this half is already known, and is not new

`background/gap_ledger_reconciler.py` grades exactly this and would have said so on every tick:

    [stale] PB3_book_growth_as_earned_outcome: 3 commit(s) touched
            tools/couple_pb3_book_growth.py since d62a8e158; the published number was produced
            by code that has changed

It is **report-only by construction** and says so in its own docstring — *"it is deliberately NOT
a runner ... which surface should re-run a gap tool is a design pass this refuses to guess at."*
That refusal is defensible and it is not what this finding contests. What it costs is visible:
three rows are `[stale]` at HEAD right now — `EP1_clv_three_horizon` (`tools/couple_clv.py`),
`W1_11_fabric_physics_core` and `W1_12_premise_trace_generator` (`tools/couple_fabric.py`,
`background/fabric_gap_ledger.py`).

**Not attempted this tick, named rather than guessed at.** I re-ran PB3's coupler because it reads
one JSON file and costs seconds. I did not re-run the other three: `couple_fabric` runs a live
coupling judgement and `couple_clv` reads the account book, and re-measuring either without first
establishing what its support moved to is the `support_changed` trap next door in this same
register. They are the next tick's work, in that order.

## 3. What IS new: the population check could never have graded this row

When a row is re-measured, the register asks a second question — *did the population move, or is
this the same quantity re-taken?* — and refuses to hand a refresh command to a row whose
population moved. It answers it from `SUPPORT_DECLARATIONS`, which names, per metric family, which
component keys are the support.

The `belief` family declared `("n_customers", "n_cells_total")`. **PB3's population is campaign
YEARS.** Its components carry `n_years_in_record`, `n_scored_market_decided`,
`n_scored_planning_on_learned_rate` — and none of the declared candidates. So the moment PB3 was
re-measured, the register returned:

    [support_ungradeable] PB3_book_growth_as_earned_outcome: the committed row records none of
            its family's support keys (n_customers, n_cells_total) ... an unavailable check is a
            failed check -- record a support descriptor before landing

Permanently. Not for this measurement — for every measurement of this row that will ever be taken.
And the blindness is on precisely the wrong row: **PB3 is the one live `belief` row whose
population is KNOWN to have moved.** The settlement ceiling took its scored partition from ten
years to `{2016}` — the state in which the published `gap = 1.0` was an arithmetic identity rather
than a measurement, reported on 2026-08-29 — and the uniform-sample repair took it back to ten.
That is the exact `support_changed` event this register exists to catch, on the exact row it could
not see.

The shape is one already in the catalogue from the other side: a control whose declared scope does
not reach its subject reads as a clean refusal rather than as a miss. `support_ungradeable` fails
CLOSED, which is why this cost five days rather than a wrong number — but a fail-closed verdict
that can never clear is a control that will be routed around, not obeyed.

**Fixed in this tick.** `SUPPORT_DECLARATIONS["belief"]` now also carries
`n_scored_market_decided` and `n_years_in_record`. Both are support and neither is an outcome:
the campaign's length and the denominator the mean is taken over are moved by the run, never by
the measurement — which is the discrimination the declaration exists to make, and the reason it is
declared per metric rather than inferred from `n_*` names.

Three tests in `tests/background/test_gap_ledger_reconciler.py`, all mutation-proven against
reverting the declaration:

- `test_a_PB3_shaped_belief_row_is_GRADEABLE_for_support` — able to pass; reads the key names out
  of `couple_pb3_book_growth.measure` itself rather than hand-typing them, so a rename on either
  side of the contract reds the test instead of silently re-opening the hole.
- `test_the_PB3_partition_collapsing_to_ONE_YEAR_reads_SUPPORT_CHANGED` — able to fail, at the
  shape that actually happened, and asserts no refresh command is offered for it.
- `test_the_LIVE_PB3_row_carries_its_support_descriptor` — the live reading.

## 4. One thing I got wrong inside this tick, kept beside the result

The live test's first draft called `glr.load_ledger()` with no argument. `tests/background/conftest.py`
has an autouse fixture that pins `LEDGER_PATH` at an **absent** tmp file, so the test read an empty
ledger, took its absent-row branch, and **passed under the mutation it was written to catch** — two
of the three tests fired, and I only found the third because the mutation run reported `2 failed, 1
passed` where it should have reported three. A live test the directory's own isolation has emptied
asserts nothing at all. It now reads the shipped ledger by explicit path and says why, and asserts
the row's presence instead of returning on its absence.

## 5. What landed

- `docs/observability/coupled_gap_ledger.json` — PB3 re-measured, 1.2285 → 0.8296.
- `background/gap_ledger_reconciler.py` — the `belief` family's support declaration.
- `tests/background/test_gap_ledger_reconciler.py` — the three tests above.
- `docs/design/maturity_map.yaml` — PB3 `level_current 0 → 2`, with its L3 residue named in the
  atom rather than left in a document nobody points at.
