**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `the-census-peak-chunked-by-directory`)

# Pre-registration: does the census's peak belong to its process lifetime or to a few tests?

Written 21 Oct 2026, ~07:10 BST, BEFORE the probe below ran. The parent prediction is in
`SEAT_FINDING_THE_NIGHTLY_CENSUS_ALREADY_ASKS_ADMISSION_AND_ITS_ONLY_LEVER_ON_THE_ARMS_IS_ITS_PEAK_2026-10-21.md`
(landing under `the-nightly-test-census-holds-the-box-through-the-arm-window`). This note adds
what tonight's reading says and what the probe will decide.

## What tonight's log can and cannot say

`/var/tmp/census_mem_20261021.log` started at 05:47Z, which is 3h15m into the run. The cgroup's
`memory.peak` was already 9,350 MB by then. At every sample after that, anon was 3,545–3,546 MB
and file (page cache) was 1,546–1,724 MB, for 5,278–5,465 MB in total. **So the log cannot split
the peak.** It does show one thing: late in the run, the single pytest process holds about
3.6 GB anon, and that is all the "whole-process cache" there is at that point. That leaves about
4 GB of the 9,350 MB peak not accounted for by the late-run state. It was either page cache from
an earlier phase or a transient (a child process, or one test's working set).

That cuts against the parent's stated reason ("caches that live for the whole process"). I record
it here before the probe, rather than after.

## The probe

One long job, `census-chunk-probe-company-tools`, declared at 11,981 MB. It does the following:

- It builds a clean checkout of HEAD, using the census's own helpers.
- It runs `tests/company/` and then `tests/tools/`, the two largest directories (~15,000 and
  ~7,400 test functions), each as a separate pytest process. Each run uses the census's own
  marker expression and ignores.
- Every 2 s it samples its own cgroup's anon, file and current, together with the test that is
  running at that moment.

The unit's journal peak is the maximum over both chunks. The sampler separates them.

## Predictions

1. **P1 (the parent's refutation condition).** The larger of the two chunk peaks, measured as
   cgroup current, is ≤ 8,900 MB. **Refuted if** either chunk alone exceeds 8,900 MB.
2. **P2.** At each chunk's peak, anon is less than 70% of current. I predict that page cache
   plus transients, not resident Python heap, make up most of the peak. **Refuted if** anon is
   ≥ 70% of current at the peak sample.
3. **P3.** The peak sample of each chunk is attributable to a named test (or a few), not to a
   slow ramp. A slow ramp would mean anon rising steadily across the chunk. **Refuted if** the
   anon series rises monotonically by more than 2 GB over the chunk and the peak is at its end.

## What each result changes

- **P1 holds and P3 is refuted** (a ramp): chunking is the lever. Build the chunked
  `run_suite`, with the control the direction item names.
- **P1 holds and P3 holds** (a spike): chunking alone will not move the peak. It moves
  whichever chunk holds the heavy test. The remedy is that test's own handling.
- **P1 refuted:** chunking is not the lever, as the parent says.
- **P2 holds:** the census's declared weight is a cgroup peak inflated by reclaimable cache.
  The definition of "the census's weight" goes back to the knowledge layer before anyone
  re-derives a number.

## Result (21 Oct 2026, 10:23 BST; the probe ran 08:22-10:23 in one cgroup, HEAD `f762d3ca1`)

| chunk | wall | tests | peak current | anon at peak | file at peak | test running at the peak |
|---|---|---|---|---|---|---|
| `tests/company/` | 29m34s | 1 failed, 15,727 passed | 2,924 MB | 2,176 MB | 754 MB | `test_the_flat_supplier_policy_makes_no_retention_offer.py::test_a_run_under_the_flat_supplier_makes_no_retention_offer` |
| `tests/tools/` | 1h31m22s | 6 failed, 7,993 passed | **9,510 MB** | **8,259 MB** | 1,038 MB | `test_weather_cell_joint_partition.py::test_the_CELL_COUNT_IS_AN_OUTPUT_of_the_draw_and_the_SAMPLE_is_not_what_bounds_it` |

systemd's own peak for the unit: 9.3G. The sampler ran every 2 s and named the running test.

- **P1 is REFUTED.** `tests/tools/` alone peaks at 9,510 MB, above the 8,900 MB line. **Chunking
  by directory is not the lever,** as the parent finding's refutation condition says. The
  chunked runner was built and mutation-tested (all six mutations fired), and then **not
  landed**. A landing was in its gate when the probe answered, and it was stopped before it
  committed, because its message said P1 held. The diff is kept at
  `/var/tmp/census_chunked_runner_unlanded_20261021.patch`. What it would buy is real but too
  small: the one-process run's late base was ~4 GB anon plus ~3.6 GB cache, against ~2.9 GB anon
  and ~1-2 GB cache per chunk.
- **P2 is REFUTED at the peak.** Anon is 87% of current (8,259 / 9,510). The peak is resident
  heap, not reclaimable cache. The declared weight is therefore not inflated by cache, and
  `CLASS_WEIGHTS_MB` stays a fair reading.
- **P3 HOLDS. The peak is two named tests, not a ramp.** Across `tests/tools/`, anon only rose
  from 17 to 2,895 MB. Taking the peak sample with each test excluded:
  - all tests: **9,510 MB**;
  - without the weather-cell test: 6,939 MB, which is
    `test_the_pages_artifact_is_the_manifest_not_the_docs_tree.py::test_every_published_link_is_in_the_manifest`;
  - without both: 5,606 MB.

  The weather-cell test calls `weather_cell_joint_partition.derived_cell_count`, which builds
  `space_filling_sample.output_space(sample=200_000)` over the 39.3m (cell, case) pairs. That
  build is a ~5.4 GB transient over the base.

**What this changes, as filed above:** the remedy is those two tests' own handling, not the
runner. Remove the two spikes and a one-process census would sit near base plus cache (~7.7 GB
late in the night, read from the 10-21 log). That is under 8.9 GB, but this is an inference from
a different run and **not measured**. The next step is to measure `output_space(sample=200_000)`
alone. Then either make the test's sample smaller while keeping its `> 10 x landed[987]` bound
honest, or memoise the space across the module. The choice belongs to whoever owns W1_28's
claim. It is handed on as a continuation.

**Two readings on the side.**
- `tests/tools/` alone took 91 minutes. The census has produced no verdict for three nights:
  10-19 and 10-21 timed out at 17,400 s, and 10-20 was deferred by the governor. Its timeout,
  not its peak, is what currently stops it from saying anything.
- The prereg's own reading of the 05:47Z log said "~4 GB unaccounted, either earlier cache or a
  transient". It was a transient: the peak is a test's working set.
