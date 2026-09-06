**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: what the re-run at fingerprint `95c9da4db380` will show

**Written 2026-09-06 03:2x BST, delivery seat, worktree `/var/tmp/se-seat-executor` at `e20d5a2dc`,
claim id `fuel-mix-return-annotation-and-battery-anchor`. Recorded BEFORE reading rows M10 and M11,
which were not yet written when this was typed: the in-flight run had recorded M1..M9.**

The run is not mine. It is PID 1448564, launched 03:06:22 BST from the SHARED tree
(`/home/rich/synthetic-enterprise`), writing the engine's default fingerprint-keyed path
`/var/tmp/grid_intensity_fuel_mix_battery_95c9da4db380.json`. I did not start it and I will not
start a second one — see the finding filed beside this.

## The predictions

1. **M1 and M2 are killed; every other contract is killed by nobody.** Rows M3..M9 already read
   `killed_by: []`, so the live prediction is over **M10 and M11 only: both survive.** M11 is
   predicted to survive on the spec's own stated grounds — it is M2 with `series = {}` in place of
   `series = []`, and the spec says in prose that it survives where M2 dies. M10 has no such prior
   and is the genuinely open cell.

2. **`survived_all` is `false` for all eleven rows, and that is NOT a survivor count of zero.**
   `tools/contract_battery.py:374` scores it as `len(callers) == len(spec.suites) and ...`, and
   `spec.suites` is all ten declared. The run was launched with `--suites` naming nine. So every
   row is structurally barred from the verdict, for a reason that has nothing to do with any
   contract. The engine prints this honestly
   (`NOT YET GRADED ON EVERY SUITE (no verdict)`), and the danger is only at the JSON layer,
   where `survived_all: false` on all eleven rows reads as "nothing survived" — the flattering
   reading — when the truth is "no row has a verdict".

3. **The tenth suite, `tests/tools/test_ep13_embedded_generation_bound.py`, has no cell in any
   row, and this is a stated bound rather than a silent cap.** It costs 655.1s per round against
   ~90s for the other nine together. Predicted: it is absent from `baseline`, `poison`,
   `null_round` and every `per_suite`.

4. **The reachability column stays at three of nine.** The poison round has already stamped
   `reaches_subject: true` on exactly `test_elexon_fuel_outturn`,
   `test_grid_intensity_feed_and_explore_carbon` and `test_process_run_complete`. Predicted: the
   six `ep13_*` suites remain non-reaching, because the spec's own null-round comment records that
   six of the eight callers read the subject as TEXT and walk it as an AST rather than executing
   it. If that holds, the tenth suite is very likely non-reaching too, which would mean the
   two-hour run the previous result reserved as "a separate, budgeted run" would buy eleven
   green cells that prove nothing. **That is a prediction about a measurement nobody has bought
   yet, and it is the cheap thing worth buying first: one poison round on that suite alone
   (~11 min) settles whether the remaining 2.5 hours is worth spending.**

5. **Both control suites stay green under the poison**, so the floor still discriminates.

## What would refute each

1 is refuted by any non-empty `killed_by` on M10 or M11. 2 is refuted by any row with
`survived_all: true`. 3 is refuted by the suite appearing in any `per_suite`. 4 is refuted by any
`ep13_*` suite carrying `reaches_subject: true`. 5 is refuted by
`tests/background/test_delivery_lane.py` or `tests/design/test_atom_notes_store.py` reddening.
