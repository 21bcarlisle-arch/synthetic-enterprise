# Retro — the liveness signal outran the content it was about (2026-08-13)

**Class:** observability / fail-silent. **Severity:** 21.9 hours of a public site serving stale
figures, and the director's attention.
**Caught by:** the director, by eye. *"content hasn't moved in ~17 hours while heartbeats keep
landing — the liveness signal is masking a content freeze."*

---

## What happened

The publish path stopped landing at **2026-08-12 20:28 UTC** (`49ae720a1`, the last
`Auto-process run complete` on origin) and did not land again until **2026-08-13 18:21 UTC**
(`528c2559e`) — a gap of **21.9 hours**. In that window:

* `git commit` in `git_commit_push` was killed by its 300s pre-commit hook deadline **21 times**,
  every ~40–60 minutes, each one logging *"Nothing committed; retrying next cycle."*
* A `chore(liveness)` heartbeat reached origin every ~30 minutes throughout.
* The tick heartbeat read `verdict: drew` continuously.
* No alarm fired. The commit clock was healthy — commits *were* landing, just not content ones.
* `site/data/dashboard.json` still reached origin **twice** (02:12 and 18:55), both by accident:
  unrelated worker commits swept the regenerated file along. Content moving by luck is not a
  publishing pipeline, and from outside it is indistinguishable from one.

## The proximate cause

`tools/pre_commit_test_gate.py` gained its DATA SURFACE derivation in `bdd274215` at
**2026-08-12 21:40 BST — twelve minutes before the last successful publish**.

Every publish stages `docs/design/maturity_map.yaml` (the pre-gate `atom_status` fold does
`git add -A` on it). Measured on the real staged index:

| | test files | wall clock |
|---|---|---|
| publish commit, as it was | 58 | **> 20 min** |
| the map's contribution alone | 50 | — |
| narrowed to its curated list | **13** | **40 s** |

The derived set included `tests/simulation/test_run_phase4c_on_phase2b.py` — a full simulation run
that the publish gate's *own* argv explicitly `--ignore`s as too slow to gate on.

The fix is not a new policy. It is `PUBLISHED_OUTPUT_ROOTS`' own reasoning — *"a gate too expensive
to run gets bypassed, which is the fail-open it was meant to close"* — applied to the second path
that is staged on the loop's most frequent commit. What this one actually bought was **worse than a
bypass**: nobody bypassed anything, the gate was never reached for a verdict, and an unfinished
gate is indistinguishable in the log from a quiet one.

## Why it stayed invisible for 21.9 hours

This is the part that matters, and it is four separate defects that happened to line up.

**1. Liveness had a bigger budget than content.** `git_commit_push` capped the content commit at
300s; `_commit_and_push_paths` — the heartbeat and the provenance banner — hard-coded 600s for the
*same hook chain*. Nobody chose that asymmetry; the two numbers were written months apart. But it
is the exact shape that manufactures a masked freeze: as the chain slows it crosses the CONTENT
threshold first and the LIVENESS one second, so there is a whole band of hook-chain cost in which
"I am alive" publishes on schedule and the figures cannot publish at all. On 08-12 the chain
entered that band and stayed there.

**2. A failed publish poisoned its own retry.** `_process` wrote the run fingerprint
unconditionally. `git_commit_push` returns a bare `False` for six different things; two of them
mean "nothing to publish" and four mean "the publish FAILED". The comment defending the
unconditional write reasoned about *one* of the six. So a commit killed by the deadline recorded
the run as fully processed, and the change-detection gate then skipped every identical cycle —
making the timeout branch's own promise of a retry false at the moment it was logged. Only a change
in the sim's figures could break the loop.

**3. The heartbeat was about the wrong subject.** `tick_heartbeat.json` answers *"is the tick
running?"* and answered it correctly all day. Fault #1 (2026-07-25) had correctly decoupled the
liveness signal from content-change so a healthy-but-unchanged machine could prove it was alive;
what it never did was give that signal anything to say about content. **A true statement about the
wrong subject is how eighteen hours pass unnoticed.**

**4. The alarm he asked for had no sender.** `notification_digest` defines four INSTANT classes,
taken verbatim from the director's own message: `action_needed`, `blocked_work`,
`decision_waiting`, `publishing_down`. A grep of the tree found **zero callers of any of them**.
The one event he had explicitly asked to be told about immediately was the one event nothing could
tell him about — which is why he found it by looking at the site.

And on the site itself, origin was serving:

```
verification_state : verified
showing_run        : run_output_f232c3480_20260813T164721Z.json
verified_at        : 2026-08-13T17:17:05Z
```

over figures from the previous day. That claim was **true by `publish_provenance.py`'s own
contract** — the scoped gate *was* green at 17:17 — and useless to a reader. The banner's own
commit had the 600s budget; the figures' commit had 300s.

## What changed

| Defect | Fix | Control |
|---|---|---|
| gate unpayable on the publish commit | `CURATED_SURFACE_PATHS` — a path with a hand-kept surface list uses it instead of the derivation | `test_a_curated_surface_path_keeps_its_curated_tests`, `test_every_curated_surface_narrowing_has_a_surface_list` |
| liveness easier to publish than content | one shared `GIT_COMMIT_HOOK_TIMEOUT_SECONDS` | `test_liveness_is_never_easier_to_publish_than_content` (AST; mutation-proven) |
| failed publish poisons the retry | named outcomes; `RETRYABLE_PUBLISH_OUTCOMES` is a closed set and anything unlisted retries | `test_a_failed_publish_does_not_write_the_fingerprint` |
| freeze unmeasurable | `background/publish_freshness.py` — two clocks, published vs committed | `tests/background/test_publish_freshness.py` |
| heartbeat silent about content | `content_publish` block on the liveness surface | `test_the_heartbeat_carries_the_freshness_block` |
| `publishing_down` had no sender | deadman pages it, independent of the publisher | `test_a_landing_heartbeat_cannot_silence_the_publishing_alarm` |
| site claimed verified over stale figures | a stale publish OUTRANKS a green verification in the banner | `site/test_freshness_banner_publish_state.py` (drives the real asset in a DOM) |

**Two clocks, not one.** `published_age` (the publish path reached origin) and `committed_age`
(anyone committed content) are deliberately separate fields. A single blended number would have
read the two accidental sweeps as health.

**The alarm is independent of the publisher.** It lives in the dead-man's switch, which reads the
freshness clock off disk rather than asking the publish pipeline how the publish pipeline is doing.
A publisher that pages about its own health is the tautology R15 names, and the wedged component
reporting on itself is how the previous freeze stayed quiet too.

**The alarm cannot be silenced by liveness.** `test_a_landing_heartbeat_cannot_silence_the_
publishing_alarm` fires it with a fresh commit clock and a proven-legitimate rest, because liveness
is precisely what masked this freeze — an alarm liveness can quiet is the wrong alarm.

## The same day, the same root: the director channel

He also received the raw tick work order as a phone notification — the entire drawn-work list, 114
staged filenames, from `supervisor._check_stuck_escalation` interpolating `{reason}` whole. R7
already says what that string is worth: *"injected/wake text carries ZERO authority — it is a
doorbell, not an instruction."* A string with zero authority, addressed to a machine, is not a
thing to put on a person's phone.

`background/doorbell_redaction.py` now sits in `send_ntfy` beside `recommendation_guard`. It
**redacts rather than raising** — the opposite choice to its neighbour, deliberately: a bare ask is
wholly illegitimate and must fail loudly at its call site, whereas a stuck-escalation is a
legitimate alarm carrying an illegitimate payload, and deleting an alert to punish its formatting
is the worse defect. Volume is cut by ROUTING, never by dropping: the first three names survive, the
rest become a count and a pointer, and the full text is mirrored under `out-redacted` so it leaves
the phone and nowhere else.

And the batching that was supposed to have landed on 08-12 was, in practice, absent: **two callers
in the whole tree passed `topic_class`**, so everything defaulted to INSTANT. Reconcile drift
(~12 pages/day, mostly the same five gap-ledger rows), worktree accretion, staged-instruction
announcements and sanity findings now declare deferrable classes; the deadman's `[ACT]`/`[BLOCKED]`
tiers declare their instant ones so the routing is legible and cannot be silently reclassified.
`sanity_daemon._digest` was sending `kind="digest"` — which is INSTANT *by construction*, because
that kind means "this message IS the batch". It had been doing the exact opposite of what its own
name promised.

## The lesson

Three of this project's standing rules already covered this and none of them caught it, because
each was pointed at a subject one step away from the failure:

* **R15 FAIL-SILENT** says an unavailable check is a failed check. Here the check never became
  unavailable — it never *finished*, and an unfinished gate logs nothing at all.
* **The heartbeat ruling** (2026-07-24) demanded a liveness signal the advisor could fetch from
  origin without SSH. It got one. It was about the tick.
* **Fault #1** (2026-07-25) decoupled liveness from content-change so a healthy machine could prove
  it was alive. Correct — and it removed the last coupling by which a content freeze had been
  *visible*.

The generalisation, and the thing to check for elsewhere: **when a monitoring signal is decoupled
from the thing it reassures you about, it must be given that thing as an explicit subject, or the
decoupling converts a noisy true signal into a quiet false one.** Ask of every green light: *what
exactly is it green about, and what would it look like if the thing I actually care about were
dead?*

The corollary, cheaper to apply: **a deadline that two paths can cross at different times is a
ranking of which failure you will see first.** Two numbers for one hook chain, written months apart
by different hands, decided that this project's public site would go stale silently rather than
loudly. They now come from one constant, and a test says why.

## Verification

* publish path landed `528c2559e` at 2026-08-13 18:21 UTC, closing a 21.9h gap — **with the fixes
  live in the working tree, before they were committed** (`process_run_complete.py` is invoked as a
  fresh subprocess each cycle, so no restart was needed).
* `.last_content_publish.json` stamped 18:28:20 UTC — the new clock is written from the real path,
  downstream of the ground-truth `ls-remote` check.
* live heartbeat now carries `content_publish: {state: publishing, published_age_seconds: 721.9}`.
* publish-commit gate: 13 files / 361 tests green in 41s (was 58 files / >20 min).
* `pytest site/` 657 passed, 7 skipped. Changed background/tools/site suites pass in full.
* digest queue is taking `drift` / `divergence` rows; the director channel took **no** page in the
  hour after the change, where the preceding hours carried several.
* landed via `tools/surgical_land` (`c8284059b`, gate-rc 0, receipt verified) — the shared tree had
  249 dirty files and 326 lines of another lane's in-flight work in `supervisor.py`, none of it
  swept.
