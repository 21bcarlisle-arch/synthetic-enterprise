**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The "PUBLISHING IS FAILING" line was a landed publish whose failure episode never closed, and today's four "failed" deploys deployed (2026-10-22)

*Answers items 1–3 of `advisor/DIRECTOR_STEER_THE_FRONT_DOOR_SAYS_PUBLISHING_IS_FAILING_AND_IT_IS_NOT_2026-10-22.md`
and the deploy item of `advisor/DIRECTOR_READING_USAGE_27PCT_THURSDAY_2026-10-22.md`. Written by the
seat executor while landing the fixes.*

## What the banner read, and a correction to the advisor's diagnosis

The advisor wrote that the banner read the site's own heartbeat snapshot, frozen at 07:56Z on 19 Oct.
**That is only half right.** `site/assets/freshness-banner.js` reads two copies and uses whichever
was written later. The liveness-branch copy was fresh: written 2026-10-22T13:40:45Z, it is the one
every reader got. That fresh copy *also* read `publisher.state: failing`, `consecutive_failures: 2`,
`failing_for_seconds: 288700` (80.2 h) and `clean_publishes_this_episode: 0`. The 80 h was not the
browser extrapolating. The publisher wrote it, and it was wrong.

## The cause: a landed publish that never closed the episode

`docs/observability/.publish_gate_state.json`, read at 16:20Z on 22 Oct:

| field | value | read as |
|---|---|---|
| `wedge_since` | 1792387744.9 | the episode opened 2026-10-19T05:29:04Z |
| `episode_failures` | 2 | two gate refusals |
| `citation_at_head` | `dead` | the cited red, `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`, passes at HEAD |
| `last_landed_publish` | 1792401343.0 | **the publish landed 2026-10-19T09:15:43Z**, after the episode opened |
| `failures_since_landed_publish` | 0 | no failure since that landing |
| `episode_clean_publishes`, `last_clean_publish` | 0, 13 Oct | the success recorder never ran for Monday's landing |
| `publish_hold.next_opens` | 2026-10-26T04:00Z | the weekly window held every cycle since |

So **Monday's two failures** were two gate refusals at about 05:29Z on 19 Oct. Each named one red
test that passes when re-run at HEAD, so it was flaky or already fixed. The third attempt landed at
09:15Z. It landed by a route that does not call `record_publish_gate_success`, so `episode_failures`
stayed at 2. After that, the weekly hold meant no further attempt was made that could close the
episode. `publish_freshness.publisher_refusal` read `failing` from `episode_failures` alone. The
record already held the landing-keyed count (`landed_publish_count`, 2026-10-05) that refutes it,
but nothing read that count.

## The fixes, landed or landing in this turn

1. **The front door has no banner** (the 14:57 steer, section 1). Its only clock is a line written at
   publish: "Figures from the run of 19 Oct 2026 · published every Monday". The banner-adoption rule
   accepts that line in place of the banner, but only between the generator's markers.
2. **At the source:** `publisher_refusal` no longer reads `failing` when a publish landed after the
   episode began and no failure has followed it. It reads the hold instead ("Publishing is held by
   the weekly window — the next publish opens Mon 2026-10-26 04:00"). It also carries
   `superseded_by_landed_publish`. On today's real state file it reads `held`.
3. **In the browser:** a failure record written before the verified publish that shipped the page
   makes no failure claim. This is the deployed-copy fallback the advisor described.

Each of these is mutation-proven in its test file.

## Today's four "failed" Cloudflare deploys: every one deployed

The advisor counted three. `gh run list` shows four: 07:32Z, 07:58Z (`420a5b67d`), 09:49Z
(`989ce4f1c`) and 11:55Z (`02659d155`). **In every one, `wrangler pages deploy` printed
"Deployment complete".** The red step is the next one, `tools/assert_deployed_bytes_are_served.py`.
In each case `https://poesys.net/` was still serving older bytes (`STALE`, or `UNCONFIRMED` on 11:55Z)
after the check's 8-minute window, while other assets of the same push were already new. At 16:25Z,
the live `/` was byte-identical to `origin/main:site/index.html`.

**Did readers ever see a broken page? No.** A Pages deployment is atomic, so for a few minutes past
the window they saw the previous front door. Every failing push changed `site/index.html`, and every
passing push today left it alone. That pattern is consistent with the front door's own route
propagating more slowly than the 8-minute window, but **I cannot yet say that this is the cause**.

**Owed:** measure how long `/` takes to turn over on the next front-door push, then either widen the
window for `/` with that measurement or find what holds it. Also, nothing on the seat's own surface
reads a red deploy run. A served-bytes failure should reach the stretch brief, because today only the
advisor saw it.

## Still owed from the steer (handed on, not done here)

- Item 2's full sweep: every site element that reads a snapshotted runtime file, with counts, plus a
  check that every freshness or failure claim carries the age of its source.
- Publisher state as an operational line on How it's built (14:57 steer, section 1, second bullet).
- Item 4: the garbled settlement sentence, and the dual-fuel mover drawn as world work, K8 first.
- Item 5: the Claude Code package. Updating the builder's toolchain is not one of the G5 walls, but
  the seat's last stretch chose against folding it into item 1. It is left for the seat.

## Measured on this turn's own push (2406226c8, run 39811209357, 16:07Z): the window is not the cause

This push changed `site/index.html`. From this machine, polling `https://poesys.net/?cb=<nonce>`
every 10 s, the new front door (with its `BUILD-STRIP` markers) was served at **16:08:45Z, about 90 s
after the push**. Fetched with the check's own urllib and its User-Agent `poesys-deploy-assert`, it
was byte-identical to `origin/main:site/index.html` (`cf-cache-status: DYNAMIC`). On the GitHub
runner, the same check went red again. `/` returned HTTP 500 on attempt 0 and then **served neither
the new bytes nor the old for the full 8 minutes**, while `/assets/freshness-banner.js` from the same
push matched after 16 s. One deployment, so the window explains neither 90 s here nor more than 8
minutes there. A per-edge cached resolution of the path route `/` does explain both: it is the
hypothesis the check itself recorded on 2026-09-04 (`classify` docstring), and the runner's edge is
not this machine's. I have only run one push, so I cannot yet say whether readers near the runner's
edge are served the stale `/` for that long. Widening the window is refuted as the remedy. The next
step is to read what that edge serves at `/` (its bytes against the last few commits'
`site/index.html`), and to fetch `/index.html` beside `/` in the check, so the two routes can be told
apart.

## Disposition (2026-10-22, worker)

Everything this finding listed as owed was landed in the commit that archives it. The sweep: five
runtime-feed readers plus `proof.deployment`, each now stating its source's age or fed fresh, under
one mutation-proven control. Publisher state on How it's built: the freshness layer already renders
it there, under the same bound. A red deploy now reaches the seat's brief (`deploys_red`) with the
check's refusal line.

**One question is still open: why `/` is stale on the runner's edge.** It is now instrumented rather
than parked. `/index.html` 308s to `/`, so it cannot serve as a second route. Instead, a STALE or
UNCONFIRMED verdict now names which of the path's last 30 commits the served bytes match, or none,
together with the edge's status, colo, cache status and title. That line reaches the brief through
`deploys_red`. The next red run settles it. The full account is in the steer's `## Done`.
