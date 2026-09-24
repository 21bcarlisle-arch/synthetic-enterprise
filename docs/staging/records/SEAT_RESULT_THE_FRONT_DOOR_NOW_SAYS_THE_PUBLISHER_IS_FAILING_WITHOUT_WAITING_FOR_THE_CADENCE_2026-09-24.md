# SEAT RESULT — the front door now says the publisher is failing, without waiting for the cadence

**Severity:** RESOLVED (was: a confidently healthy page over a 60-hour publish outage)
**Date:** 2026-09-24
**Claim:** `land-the-built-and-unlanded-publisher-refusal-sentence-before-it-is-lost`
**Landed:** `199743f80`

## What was landed

Three files, as one unit, because the door boots the **committed** copies and scores the renderer
against the feed in the same commit:

| path | what |
|---|---|
| `background/publish_freshness.py` | `publisher_refusal()` — reads `.publish_gate_state.json`, never writes it; carried beside the two content ages and into `describe()` |
| `site/assets/freshness-banner.js` | `publisherIsFailing()` / `publisherFailureSentence()` — the sentence, above the as-at line |
| `site/test_freshness_banner_publish_state.py` | the door — 7 new cases on the rendered DOM, 28 passed |

`site/data/tick_heartbeat.json` was **not** landed and did not need to be: it is generated on every
tick, and at the prior HEAD it already carried `content_publish.publisher.state: "failing"` with 46
consecutive failures — a field no committed producer wrote and no committed renderer read. That
inversion is what this landing closes.

## The defect, stated once

Every fault the banner could name was an **age against a threshold**, and an age cannot become a
fault until its threshold comes due. At the weekly cadence that threshold is eight days. So while
the publisher refused every attempt for two and a half days the page rendered its ordinary healthy
branch — *"Figures as at 2026-09-21 18:15"* — and the "PUBLISHING IS DOWN" wording could not have
fired for another five days, however many attempts died in between.

Nothing on the page was false. **"Not due yet" and "tried and failed" are different facts, and only
one of them had a sentence.** That is the same shape CLAUDE.md names under *before measuring a
thing, say what it is*: one word, `state`, was carrying two distinct questions.

## Two judgements worth keeping

**It does not move `state`.** `state` is the content clock's verdict and it is what the deadman
pages on. Folding a self-report into it would put the wedged component in charge of reporting its
own wedge — the tautology R15 names, and the reason
`deadmans_switch._check_content_publishing` already refuses it by design. The refusal rides
*beside* the verdict with its own name; the alarm keeps its independent clock.

**It is trusted in exactly one direction.** A `failing` reading is an admission against interest
and is believed. A clean reading is no evidence at all — a publisher wedged before it can write and
a state file that was lost both read clean. Hence three states, with `unknown` never folded into
`no_open_episode`: FAIL-SILENT is the failure mode this class dies of. Neither non-failing state
renders a reassurance *or* an alarm; the content clocks keep the currency verdict, and they cannot
be faked by an absent file.

## Two readings that would have gone quiet on the real outage

- **`episode_failures`, not the `failures` list.** The list is trimmed to a one-hour window
  (`supervisor._publish_gate_wedge_active`), so a two-day outage whose last attempt was 70 minutes
  ago has an **empty list** and a count of 46.
- **A missing `wedge_since` does not veto the failure.** The count establishes that attempts died;
  the stamp only says since when, and it is legitimately absent on an episode's first cycle.
  Vetoing on it is the fail-open shape, and `test_a_failure_with_no_recorded_duration_still_says_it_failed`
  fires on it.

## The control that matters is the null

`test_a_working_publisher_leaves_the_healthy_banner_alone`. Without it every other new case passes
on a banner that shouts on every visit — which is a banner nobody reads on the visit it means
something.

## Disposition of the duplicate claim

The draw flagged `the-front-door-cannot-say-publishing-is-failing-while-the-weekly-cadence-is-not-yet-due`
as possibly this work under another name. It is **the same subject and different work**: that claim
*built* these bytes (mtimes 08:25–08:28 local, matching its `claimed_at` of 08:21) and ended without
landing them, binding no paths. No live process named it at draw time, so the sweep would have
returned the item to the pool with the files still loose on disk, one stray pathspec from being
swept. This claim landed them. Nothing was done twice.

## What this does not fix

**The publisher is still refusing.** This landing changes what the page *says* about the outage, not
the outage. The open cause is the sixth in the series — the `rc=1` exit in
`background/process_run_complete.py` recording `cause='unattributed'` while `total_red` is 0 and
every cited red is dead at HEAD — held under
`the-publishers-rc1-exit-names-no-cause-while-total-red-is-zero-and-every-citation-is-dead`.
That is the right split: the fail-closed rule says the reader is told now, whether or not we have
yet found why.
