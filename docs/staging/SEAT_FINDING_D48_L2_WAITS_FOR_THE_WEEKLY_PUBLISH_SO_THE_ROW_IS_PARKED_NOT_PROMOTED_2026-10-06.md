**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# D48: L2 waits for the weekly publish, so the row is parked, not promoted

## The ask

Drawn as `d48-records-the-level-its-reader-earned`. The ask was to record D48's level through
`tools/level_promotion_gate.py` now that it has a reader (`5063adeca`). If that could not be done,
the alternative was a finding that names the refusal.

## Why the level was not recorded

The refusal is not the gate's. The gate refuses only an *unrecorded* move, so it would have accepted
a self-certified record. The refusal comes from the rule "done means the rendered value changed".
L2 needs VERIFY evidence on a deployed surface, and the deployed surface still shows the absence:

- Live `site/data/billing_accuracy.json` (origin/main, 2026-10-06 04:40 BST): `"available": false`,
  with source `run_output_998814330_…`. That run output predates the key.
- The newest run output, `docs/reports/run_output_5063adeca_20261006T023117Z.json`, **does** carry
  `billing_accuracy`. I fed it through `published_view` in a worktree. The output is `available: true`,
  and the electricity snapshot is 2 of 48 (4.2%, 95% 1.2% to 14.0%) →
  `cannot_be_told_apart_from_the_median_supplier`. So the next publish will render the figures.
- That publish is held. `sim-runner-log.md` at 02:49 UTC reads: `HOLD (weekly publish window):
  this week's figures reached origin 2026-10-05T22:00Z; the next publish opens Mon 2026-10-12 04:00
  BST`. The window comes from the director's ruling of 2026-09-26 and is enforced in
  `background/process_run_complete.py`. Getting around it to put the figures on the page sooner
  would break that ruling.

So the rendered value cannot change before 2026-10-12, and the level is not recorded before then.

## What landed

D48's row went from `loop_stage: build` to `idle`, with a dated comment saying what un-parks it. The
reason for the draw was that D48 kept winning BUILD draws for work it had already done, and the BUILD
lane hands out every non-idle atom that is below target (`background/supervisor.py`
`_is_valid_candidate`). No build pass can move this level. Only the publish can. Parking it stops the
draws without claiming anything.

A seat continuation cannot carry this wait. Continuations expire after 6h
(`seat_continuation.STALE_AFTER_SECONDS`), and the wait is six days. The trigger is therefore this
finding plus the row's comment, and Monday's orientation reads both.

## Owed on or after Mon 2026-10-12 04:00 BST

1. Confirm the live `site/data/billing_accuracy.json` reads `available: true`, and that
   `/capabilities/` renders the snapshot.
2. Record L2 with `background.gate_authorization.record_level_up_self_certified`. Provenance:
   the published page, plus `site/test_the_billing_accuracy_reaches_the_reader.py` (four mutations
   proven), plus the four slices. Include this End-to-end clause: *the K2 12-month snapshot (48
   electricity / 27 gas accounts) cannot yet be told apart from the published median supplier
   (94.80% / 94.40% of consumers with a bill on a read in the past year, i.e. 5.2–5.6% without). The
   intervals are about ten times wider than the band, so the book is too small to say whether this
   read process is better or worse than a real supplier's.*
3. Set `loop_stage: harden`. The next step is the Expert Hour, with a revenue-assurance persona.
   The headline to put in front of it is the published K2 estimated share of billed electricity kWh,
   58% on this run. Slice 4's finding attributes that to the world's flat gas-heated homes. A
   revenue-assurance veteran will read 58% first, before the snapshot.
