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
