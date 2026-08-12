# [WORKER-FINDING] The episode-monotonic guard is numeric-only and fails SILENTLY on an ISO timestamp — wiring it on one would look like protection and be none (2026-08-10)

**Severity:** RECORDED · **Lane:** H_harness

> **CLOSED 2026-08-12** (worker tick, RUNG 1c blocking-finding draw). Severity moved BLOCKING ->
> RECORDED because the guard was REPAIRED, not because the limitation was accepted: this line is
> what the class document's "what is owed" list is derived from, so leaving it BLOCKING would
> keep an owed item that is discharged, and changing it without the repair would be the
> laundering OPS9 fails closed against. The proposed atom below (`OPS_episode_guard_typed_fields`)
> is BUILT: `_episode_key` orders epoch AND ISO-8601 (naive read as UTC) and
> `EpisodeFieldTypeError` refuses a field it cannot order, scoped to the CALLER's own proposed
> value and to a representation mismatch so a corrupt persisted prior still degrades silently
> (it provably cannot under-report -- with no readable earlier value there is nothing to
> remember). The winner is returned in its own representation. `episode_age_seconds` reads both.
>
> R15 BOTH WAYS, mutations RUN and their red sets recorded in
> `tests/background/test_episode_monotonic_guard.py`: (1) drop the ISO branch from `_episode_key`
> -- 4 red, including this document's own driven case; (2) turn each `_refuse` into a silent
> `continue` -- 5 red. Every pre-existing numeric test stays green under both, and a vacuity
> guard pins the numeric contract bit-identical. 27 pass.
> **Not** wired onto `publish_provenance.paused_since`: that path's real guard is transition-only
> stamping and remains so; what changed is that wiring it is now possible and would no longer be
> the no-op this document warned about. The stale workaround comment in `background/ntfy_utils.py`
> -- which carried a duplicate numeric `since_epoch` *because* of this defect -- is corrected, and
> `since` is now DERIVED from the guarded epoch so one episode cannot have two starts.

**Found:** dispositioning `site/data/publish_provenance.json` into the self-clearing-alarm census
after the publish decoupling landed. Not a defect in what shipped — a trap laid for whoever wires
this guard next, which on current evidence is the natural thing to do.

## Observed, with evidence

`background/episode_monotonic.guard_episode` protects an episode START by low-watermarking it. Its
field test is `_is_num`. Driven, not read:

```
prev  {'paused_since': '2026-08-09T14:30:09Z'}
new   {'paused_since': '2026-08-10T17:40:00Z'}     # a failure moving the episode start 27h LATER
guard_episode(prev, new, since_fields=('paused_since',))
  -> '2026-08-10T17:40:00Z'                        # SILENT NO-OP, the later start passed through

numeric control: prev 1000.0 / new 2000.0 -> 1000.0   # the guard works, on numbers
```

Every existing `real` entry stores epoch floats (`.publish_gate_state.json` carries
`wedge_since = 1786285809.3788102`), so the guard is doing its job today and nothing is currently
broken. That is precisely why this is worth filing rather than fixing quietly: the class is
**invisible while every member happens to be numeric**.

## Why it matters here specifically

`publish_provenance.json` carries `paused_since` as **ISO-8601**, because the field is rendered
verbatim on the public banner ("Verification paused since 2026-08-09T14:30:09Z"). It is a genuine
episode start — a reset would publish "paused since 30 seconds ago" through a 25-hour outage, the
ruling's own cardinal sin wearing the opposite coat.

So the obvious move — add `since_fields=("paused_since",)` — produces a call that reads as guarded
in review, passes any test that only asserts the call happens, and protects nothing. The guard's
own contract makes this worse: it "is never blocked and never raises… every other field passes
through untouched", so a no-op is indistinguishable from a successful guard at the call site.

**What was done instead:** the path is dispositioned `real` with its ACTUAL guard named —
transition-only stamping inside `publish_provenance.record_paused`, mutation-proven in
`tests/background/test_publish_provenance.py` (forty `record_paused` calls leave the freshness
fields byte-identical and do not restamp `paused_since`). `episode_monotonic` is deliberately not
wired, and the disposition says why, so the absence is a recorded decision rather than an omission.

## Proposed atom (queued, not built — SELF_INTERRUPT_DISCIPLINE)

**`OPS_episode_guard_typed_fields`** — make `guard_episode` either (a) parse ISO-8601 alongside
numerics, or (b) **refuse loudly** on a field it cannot order. (b) is the better default by this
project's own doctrine: an unavailable check is a FAILED check, and a guard that silently declines
to guard is the fail-silent pattern R15 names. R15 both ways: the guard must hold the ISO case above
(mutation: revert to `_is_num`, the later start passes and the test reds), and must still pass every
numeric caller untouched.

**Recommendation:** normal priority. Nothing is unguarded today, so this is not urgent — but it
should land before any second ISO episode field appears, because the failure is silent and the
register would still read fully dispositioned while one entry was protected by nothing.
