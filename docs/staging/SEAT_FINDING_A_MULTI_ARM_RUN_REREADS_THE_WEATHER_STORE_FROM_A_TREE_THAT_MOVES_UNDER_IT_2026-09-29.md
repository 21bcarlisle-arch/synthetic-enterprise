**Severity:** LATENT · **Lane:** A_strategy_governance · **Class:** `measurements_that_mirror` · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING: a multi-arm A/B run re-reads the weather store from a working tree that can move under it, and nothing records that it did

**The defect.** `simulation/run_phase2b.py:1386` (`main`) calls `WeatherWorldSource.load()` on every arm. That call reads `sim/weather_world/*` from the working tree (`sim/weather_world.py:86`, `STORE_DIR`). A `run_value_cycle_ab --level-arm` run over two seeds makes six such reads over about 2.5 hours.

**What happened.** The run that produced `/var/tmp/se-arrears-lines-head/value_cycle_ab.json` was started in the executor worktree `/var/tmp/se-seat-executor`. That worktree is reset and landed into at every executor turn.
- At 02:25, `f0ba399a4` replaced the store under the running process.
- The last arm, seed 88888's level arm, therefore settled 42 premises on fabric physics.
- The five arms before it settled those 42 on the legacy provider.

Evidence and figures: `docs/staging/records/SEAT_RESULT_PROS_2024_0082_FIRST_BILL_PER_ARM_ON_SEED_88888_IS_NOT_REPRODUCED_BECAUSE_THE_WEATHER_STORE_WAS_SWAPPED_UNDER_THE_LAST_ARM_2026-09-29.md`. That included PROS-2024-0082 going from 16 issued bills to 5, and +£2,484 of the +£2,464 "moved where nothing was decided".

**Why nothing caught it.**
- `producing_commit` is stamped at process start. It records the code Python bound, and data read later is outside its scope.
- `book_identity` and the cross-arm same-book control compare the customer book, not the weather world.
- The six arms therefore passed every identity check while running in two different worlds.

**The smallest mechanism that can fail.** Put a digest of the three store files into each arm's identity block, beside `book_identity`, and have the existing cross-arm control raise when the digests differ. That is one leg, and it would have refused this artefact. Loading the store once per process would also fix it, but it would hide the next file that does the same thing. The digest names the problem.

**Standing practice until then.** Run long jobs in a worktree pinned to the commit under test, as the one-seed capture did (`/var/tmp/se-leak-88888`). Never run them in `/var/tmp/se-seat-executor`.

**Mechanism landed (2026-09-29, `weather-store-digest-in-each-arms-identity`).** `tools/run_value_cycle_ab.weather_store_digest()` hashes the three store files at `sim.weather_world`'s own paths. Each arm is digested just BEFORE and just AFTER it runs, because the arm reads the store once, somewhere in between. Both digests are carried in the arm's `book_identity` block. `same_book_across_arms` publishes `same_weather_store` over all brackets. It is `False` on any two distinct digests, including a swap inside one arm, and `None` when a bracket is unread. `run_value_cycle_ab` refuses on anything but `True`, at the same site as the book refusal. Both legs were mutation-proven: dropping the raise and pinning the verdict each red the new tests.

**Was open, closed 2026-09-29 (claim `noise-floor-seeds-reconcile-on-weather-store`).** The noise-floor path (`floor_book_identity`) reconciled seeds on the declared book only, so two seeds run in different weather worlds paired as one floor. It now reads every weather bracket of every seed: two digests refuse the floor ("N different weather stores"), agreement is published as `book_identity.weather_store`, and any unrecorded bracket (every floor seeded before c39e01693) blanks it with `weather_store_unavailable_because` instead of pairing on the seeds that did record one. The weather digest is deliberately NOT in `declared`, the pairing key `fold_noise_floor_family` and `generate_value_arms_data` compare, so old floors are not reclassified as a different book. Control: `test_the_weather_reconciliation_reaches_every_state_across_seeds`, which goes red when the refusal is removed and when a partial record is reported as agreement.
