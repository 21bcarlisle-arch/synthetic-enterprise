**Severity:** LATENT · **Lane:** H_harness

# FINDING — nothing fetches the published surface to check its own freshness

**Found by:** the disposition of
`WORKER_FINDING_THE_PUBLISH_COMMIT_STOPPED_LANDING_WHILE_RUNS_KEPT_ARCHIVING_2026-08-19`, whose
recommendation 3 this is. Filed rather than built, so the gap has a draw handle instead of
living inside a discharged document.
**Class:** every control that knows whether the live site is current reads LOCAL state; the one
question R11 says is the only real one — what does the fetch return — is asked by a human or
not at all.

## Observed, with evidence

Every claim `observed-with-evidence` (R9).

**The publish path's freshness controls are all inside-out.** `record_publish_gate_failure`
counts the publisher's own consecutive failures. `_green_is_on_record_for` reads
`.last_tested_hash`. `publish_provenance.record_verified` stamps what the publisher believes it
published. `_commit_and_push_paths` self-verifies its push with `git ls-remote` — the closest
thing to an outside check in the pipeline, and it stops at the git remote, one hop short of the
served object.

**Nothing fetches `poesys.net`.** `grep -rn "poesys.net" background/ tools/ --include=*.py`
returns no scheduled or gated consumer that fetches a published feed and compares it to local
state. On 2026-08-19 the only thing that noticed eleven and a half hours of stale public figures
was a `curl` typed by a worker turn drawn on an unrelated atom.

## Why it is still worth building after the parent finding's repair

The parent closed the cause it actually had: a refused commit exits 77 now, so the wedge
detector records a failure and pages on the third consecutive cycle. That covers staleness whose
cause is *the publisher knows it failed*. It does not cover staleness the publisher believes did
not happen:

* a push that reports success without advancing origin (this project has had one — the 3.5h
  origin freeze of 2026-07-24, which is why `_push_reached_origin` exists);
* origin advancing while the deploy that serves `poesys.net` does not run, or runs and fails;
* a cached or CDN-served object outliving the commit behind it;
* a generator wired into the publish path after the last successful commit, so its feed has
  never been carried by any commit at all — which is precisely how
  `site/data/projections.json` served 404 while every local record read green.

Each of those is invisible to every control listed above, because each one leaves local state
correct.

## What it should be, and the two ways it can be built wrong

A published-freshness control that fetches `https://poesys.net/data/dashboard.json` and reds when
its `meta.generated_at` is behind the newest local `run_output_*.json` by more than one cycle.

R15 says it must be able to fail on its own named defect, and today's tree is an unusually good
subject: the parent finding recorded the exact state (LIVE `2026-08-19T00:17:34Z` /
`5e0f964ab` against a local `2026-08-19T11:50:56Z` / `a8f602bf6`), so the control can be
mutation-tested against a fixture taken from a real outage rather than an invented one.

The two failure shapes to design against, both of which this project has filed before:

1. **FAIL-SILENT** — an unreachable host, a DNS failure or a timeout must read as RED, never as
   "check skipped". An unavailable check is a failed check, and a freshness monitor that goes
   quiet exactly when the site is down is worth less than none.
2. **TAUTOLOGY** — the local side of the comparison must not be read from anything the publisher
   writes to describe what it believes it published (`publish_provenance`, the gate state,
   `.last_tested_hash`). The honest local anchor is the newest run output on disk, which exists
   whether or not any publish succeeded.

## The wall it sits behind, which decides where it may live

`CLAUDE.md`'s network-isolation ruling: COMPANY may not open a socket, SIM may ingest published
sources, HARNESS may fetch published sources and the bytes may become documentation and never a
runtime input the company reads. A freshness monitor is HARNESS: it fetches a published surface
and produces an alert. It must not write anything the company layer reads, and
`tools/company_network_isolation.py` is a ratchet, so adding a new fetch route means adding it to
the frozen list deliberately rather than discovering it fails at commit time.

## Recommendation

Build it in the harness lane as a scheduled check feeding the existing `[ACTION NEEDED]`
register, not as a new alarm channel — the parent finding's whole lesson is that this pipeline
already had the alarm and the wrong thing was being fed to it.
