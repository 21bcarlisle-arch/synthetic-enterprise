**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `the-census-times-out-before-it-says-anything`)

# Pre-registration: the census's time is the company's forward price re-scanning the whole price history on every call

Written 21 Oct 2026 BEFORE the change was built or timed. Parent:
`SEAT_PREREG_THE_TWO_CENSUS_SPIKES_MEASURED_ALONE_2026-10-21.md` (the peak is fixed; the
17,400 s timeout is now what stops the census saying anything).

## Where the time is, read before predicting

- The next nightly census after `d12ebda3c` has not run yet (that commit landed 11:02 BST on
  10-21; the timer fires 03:30). Its peak and duration stay owed to 10-22's journal.
- Wall clock, from systemd: 10-16 3h49m, 10-17 4h02m, 10-18 3h40m (complete); 10-19 and 10-21
  killed at 4h50m. 10-19 used 2h17m CPU in 4h50m wall (starved, not compute-bound); 10-21 used
  6h31m CPU (more work than any complete night's 4h46m-5h12m).
- The 10-18 SLOW table: one fixture setup (`test_a_save_is_not_paid_for_by_the_stayers`) 1,346 s;
  three `test_the_svt_origin_household_can_reach_a_fixed_term` calls ~374 s each; many more
  simulation setups at 100-400 s.
- Profiled one `build_renewal_schedule` for one SVT-origin household (2016-06 to 2023-12):
  **11.0 s, of which 10.6 s is `CompanyTariffEngine.get_forward_price`** over 38 calls. Each call
  scans the full 140k-168k SSP record list seven times (`_daily_means_for_window` x4,
  `_chronological_means` x2, the lookback filter x1), calling `date.fromisoformat` per record:
  37.3M parses for one household. The window it wants is a few hundred days.

So the lever is not any test. It is a production function that is O(history) per call where it
could be O(window). Every simulation run prices every term through it, which is why the cost
shows up as simulation fixture setups across the whole suite rather than in one place.

## The change

Index each price-record list once (per day: date, record count, prices in record order), keyed
on the list's identity and checked against its length and end elements, and answer each window
by bisection. Daily means are still `statistics.mean` over the same floats. `statistics.mean`
and `stdev` are exact (Fraction) sums, so they do not depend on order. Any list whose keys are
not canonical `YYYY-MM-DD` falls back to the original scan. A string sort and a date sort agree
only on that form.

## Predictions

1. **Equality:** `get_forward_price` for both fuels, across monthly delivery dates 2016-2025, and
   for 12/24-month terms, returns floats `==` to HEAD's. That includes on a shuffled copy of the
   records. **Refuted (and the change does not land)** if any one differs.
2. **One household's schedule:** 11.0 s -> **< 1.0 s**.
3. **The svt-origin test module:** ~1,200 s in the census -> **< 120 s** measured alone.
4. **The census as a whole:** I predict a large share of the simulation fixture setups is this
   function, so the next complete census should fall by **>= 25%** against 10-18's 13,190 s.
   This is inferred and NOT measured here. The nightly journal measures it, and other lanes'
   landings move it too, so I can attribute only a fall that is far larger than night-to-night
   noise (10-16..18 spread: ~1,300 s).

## Result (21 Oct 2026, worktree off `d12ebda3c`, box load ~5 throughout)

| prediction | measured | verdict |
|---|---|---|
| 1. equality | 1,000 cases (both fuels, 2016-2025 twice monthly, 12/24 m, plus a shuffled list): **0 differences**, ValueError messages included | HOLDS |
| 2. one household | 11.0 s -> **0.09-0.21 s** | HOLDS |
| 3. svt-origin module | ~1,200 s in the census -> **37 s** alone | HOLDS |
| 5. whole fixture, one variable | `test_a_run_reaches_the_svt_contact_response`: index on **614 s**, off **742 s**, so -17% | **REFUTED** (predicted <= 50% of off) |
| 4. census >= 25% faster | not measured here; owed to the nightly journal | OPEN |

**Prediction 5 is refuted, and that weakens prediction 4.** The forward price dominates a
schedule built household by household. It is a minority of a whole `run_phase2b`, which is what
most simulation fixtures run. Taken alone, the forward-price fix buys the svt-origin module
(~1,150 s) and ~17% of each run-based fixture. That is real, but it is not the census's whole
excess over 17,400 s. Where a whole run spends its time is the next measurement (profile below).

**A second source, found on the way: `tools/capability_index.py`.** One run costs 33.0 s at HEAD,
and the census runs it ~25 times (`test_capability_index.py`, `test_knife_hotspot_measure.py`,
`test_orphan_ratchet.py`, ...). Its `_offset_of` walked each source from the start for every
comment and docstring position (179k calls over 3,389 files, so quadratic). Now it uses a
line-start table: **17.8 s**, and the `--json` output is byte-identical (2.7 MB, `cmp`).

**A standing red, cleared because it blocks this landing.** Since W2_36 wired the theft screen
(10-17), `test_the_live_register_rules_on_every_live_orphan` has been red with two stale
dispositions: `company.billing.theft_indicator` and `company.crm.next_best_action`. Both are now
wired. The finding's own remedy is to delete the rows, and they are deleted.

### Added before the second measurement (still before any number)

5. **One-variable arm on a whole simulation fixture.** `tests/simulation/test_a_run_reaches_the_svt_contact_response.py`
   is run in one tree, first with the index on and then with `_daily_index` forced to `None`, which
   is the old scan. I predict the index-on arm is **<= 50%** of the index-off arm.
