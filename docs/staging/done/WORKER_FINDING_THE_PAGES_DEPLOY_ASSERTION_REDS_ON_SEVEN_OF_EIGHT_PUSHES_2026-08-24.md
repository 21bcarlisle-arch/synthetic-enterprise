**Severity:** LATENT · **Lane:** H_harness

# The post-deploy assertion reds on almost every push that changes an HTML page, so nobody can tell a real stale-serve from the routine one

**Found by:** diagnosing the director's "the site is showing 05:36Z, eleven hours stale",
2026-08-24 ~15:20Z. The staleness had a different cause (publishing was paused on a red
publish-path gate from 07:52Z and recovered at 15:15Z on its own). This is what the diagnosis
walked into on the way.

## Observed, with evidence (R9)

`gh run list --workflow=deploy-pages.yml`, today:

| run | commit | result | duration |
|---|---|---|---|
| 32744312579 | publisher 15:15Z | in_progress | — |
| 32742709352 | Explore stage 3 | **failure** | 8m50s |
| 32741583893 | win-rate caveat | **failure** | 8m46s |
| 32736541757 | Knowledge index | **failure** | 8m42s |
| 32735028884 | Capabilities growth | **failure** | 8m53s |
| 32733793718 | growth curve | success | 54s |
| 32720247638 | B4 ceiling | **failure** | 8m44s |
| 32715513649 | publish gate | **failure** | 8m45s |

**Seven of eight.** In every one, `wrangler pages deploy` SUCCEEDED and the step after it —
`tools/assert_deployed_bytes_are_served.py` — failed after its full 8-minute wait. The one
success took 54 seconds.

The failing asset is always a DIRECTORY URL. From 32742709352, quoted whole:

```
serving the deployed bytes after 0s: https://poesys.net/_live_harness.mjs
serving the deployed bytes after 0s: https://poesys.net/data/explore_hh_days.json
serving the deployed bytes after 1s: https://poesys.net/test_explore_second_clock.py
FAILED: 1 of 4 changed asset(s) are still not what
poesys.net serves after 8 minutes:
  https://poesys.net/explore/
```

Direct files: 0–1 seconds. `/explore/`: not after 8 minutes. Measured by hand afterwards, the
same URL served byte-identical content at **15:22:41Z**, roughly 16 minutes after that deploy —
so the bytes were right and the window was wrong, which is exactly what the control's own
docstring says happened once before on `/harness/`.

## Why this matters more than a red tick

The control exists because eight deleted pages served 200 for a day. It is the only thing that
would catch that again. But it now reds on essentially every push that touches a page, so its
signal is indistinguishable from its noise — and its own comment says why that ends badly: *"a
control that cries wolf gets bypassed, which costs more than the false red."*

## What is NOT established

The 8-minute figure came from two measurements on 2026-08-20. Today falsifies it for directory
URLs, but **does not establish the real distribution** — one hand-measurement between 8 and 16
minutes, confounded by a second deploy (32744312579) landing at 15:21 which may itself be what
promoted the asset. Do not simply raise the number to 16 and call it measured; that would be
replacing one guessed window with another.

## Where to look, in order

1. **Measure the real promotion time for a directory URL**, cleanly: push a change to exactly
   one HTML page, then poll that URL alone until it flips, with no other deploy in flight.
   Several samples, because the failure being guarded against is *indefinite*, not slow.
2. **Ask whether the window is the right instrument at all.** Pages exposes deployment status
   via its API; "is the deployment that contains this commit live on the custom domain" is a
   question with an answer, and polling a URL for a fixed duration is a proxy for it.
3. Only then set a number, and record the samples beside it.

## Not fixed here (SELF_INTERRUPT_DISCIPLINE)

Queued, not fixed on sight. The machine is not blocked — deploys are landing, and the site is
current as I write this. What this costs is the trustworthiness of the one control that watches
the last hop to a reader, which is worth a measurement rather than a guess.
