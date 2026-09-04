**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING: every deploy red for three days was the verifier, never the publication

LATENT, not BLOCKING: the control is sound in direction and wrong in what it says. No reader was
ever served stale bytes — all 19 directory-index pages were verified byte-identical by hand. What
is broken is the one signal that would tell us if they had been, which is why this cannot be left
merely recorded.

Filed 2026-09-04 ~10:25Z by the delivery seat, working the Lane 0 direction
*"the figures stopped reaching the reader and no direction ever named the path"*.

## What the direction assumed, and what was actually true

The direction said the publish path had been down ~4 hours with eight `run_complete_*` files
queued, wedged on untracked site-lane controls. **None of that was still true at this
orientation.** `docs/observability/.publish_gate_state.json` read `{"alerted_at": null,
"failures": []}`, `git status --porcelain site/` was empty, the staging root held zero
`run_complete_*` files, and `site/harness/{test_the_deployment_reading_reaches_the_reader.py,
_render_harness.mjs,index.html}` were all tracked at HEAD. Another lane had already landed the
unwedge in `7d33c1986`.

The direction's own acceptance test — *"a figure on the live site visibly moves and the run queue
is empty"* — was then met and watched:

| | 10:07Z | 10:10Z |
|---|---|---|
| live `proof.json` `generated_at` | `09:20:22Z` | `09:53:14Z` |
| deployment reading, daemons `stale` | 7 | **3** |
| `unincorporated_for_s` across daemons | `97646.4` on **every** behind daemon | `[1725.6, 2413.2, 216459.3]`, 0.0 for the rest |

That constant was the pre-fix reducer; the per-daemon figures are `53d775b04` reaching the
reader. So the queue is empty and the figure moved.

## The finding

Chasing why the live feed had been 47 minutes behind turned up a different, live defect.

`poesys.net` is Cloudflare Pages (`server: cloudflare`, project `poesys-net`); the
"Deploy GitHub Pages" workflow is a mirror the reader never meets. Over the 60 most recent
Cloudflare Pages runs (2026-09-01 22:28Z → 2026-09-04 10:00Z): **50 green, 10 red.**

**In all 10 reds, `wrangler pages deploy` exited success and only the
`Assert the deployed commit is what a reader gets` step failed.** The upload has not failed once
in three days. Every red on the deploy path has been a verification failure wearing the costume
of a publication failure — and it did that during an incident about publication.

The failure is not random. It is exactly one class:

* Across the 462 `serving the deployed bytes after Ns` observations those runs printed,
  **zero are a `/`-terminated URL.** `url_for` maps `site/<dir>/index.html` → `/<dir>/`, and this
  control has **never once** confirmed such a URL.
* Direct file routes are fast and the 8-minute clock is 3.8× what they have ever needed:
  min 0s, median 25s, p90 91s, **max 126s**.
* Of the 10 reds, 4 have a head commit that directly changed a `site/**/index.html`
  (`site/harness/index.html` ×2, `site/capabilities/index.html` ×2). The other 6 are merge
  commits whose push RANGE contained one — confirmed for `ded79e205` from its own
  `DEPLOY_BASE_REF: 1b98c836…`, whose outstanding asset was `https://poesys.net/harness/`.
* **Not one of the 50 green runs changed a directory-index page at all.**

And the content was fine the whole time. All 19 directory-index pages fetched cache-busted at
10:20Z serve bytes **byte-identical** to the repo, each with `cache-control: no-cache,
must-revalidate`.

## Hypotheses I ran and had refuted

Recorded because the prediction was filed before the answer
(`SEAT_PREREG_WHICH_SITE_TOUCHING_COMMITS_GOT_NO_CLOUDFLARE_DEPLOY_2026-09-04.md`).

* **A `paths:` filter gap** — *refuted.* Every `site/**`-touching commit sat in a push whose head
  got a run. H1 in the prereg was right.
* **The 8-minute clock is simply too short** — *refuted as stated.* It is 3.8× the observed
  maximum for the routes that do confirm. Widening it again is not supportable (below).
* **Overlapping deploys superseding each other's bytes** — *refuted.* 8 of the 10 reds had no
  concurrent run at all.
* **A caching gap in `site/_headers`** — *refuted.* `/*/` covers directory URLs and every route
  measured returns `no-cache, must-revalidate`.
* **Logs are pruned so no distribution can be built** — *refuted*, and worth recording as a trap:
  `gh run view <id> --log` exits **0 printing nothing** for older runs. The REST endpoint
  `/actions/runs/<id>/logs` returns the zip fine. I nearly filed "the evidence is discarded" off
  the silent-success.

## Why `ATTEMPTS` is not touched

The 2026-08-20 remedy for this same asymmetry was to widen the clock from 2m17s to 8m, under the
rule *"widen the clock, never the claim"*. It did not work. The reason it cannot be fixed by
widening again is that **there is no bound to widen to**: a clock is set from a distribution, and
the distribution of successful directory-URL promotions is **empty**. Picking a larger number
would be a number chosen because a number was needed — and it would be load-bearing within a week.
What is missing is an observation of a directory URL going live at all.

## What landed instead

The refusal now names which of two worlds it is in, because only one of them is about the reader:

* **REPLACED** — the edge is serving exactly the bytes this push overwrote. The defect this
  control was built for; actionable immediately.
* **UNCONFIRMED** — the edge serves neither the new bytes nor the old ones, or did not answer.
  This control cannot tell, and "we cannot tell" is a result. All ten reds were this.
* **RESOLVED** — arrived after the clock ran out; the window is the suspect, not the deploy.

**The exit code is unchanged in every case** — an unproven deploy stays red. Only the sentence
changes. A refusal that names its reason is how the refusal gets found to be wrong, and this one
was: it had been asserting something about the reader it had not established.

Mutation-proved, each caught by the test naming that defect: a constant `UNCONFIRMED` verdict
(4 fail, incl. the whole-partition reachability control); treating an unreadable base as a match,
the fail-open direction that would manufacture an incident from a missing ref (1 fail); dropping
the reason from the message (1 fail).

## Owed next

An observation of a directory URL promoting at all — the one number nothing here can supply.
The cheapest honest source is the `RESOLVED` verdict now emitted: the next red on a directory
route that later comes good will carry its own elapsed evidence, and a bound can be set from
several of those rather than from one anecdote. Until then the clock stays where it is and the
reds say what they actually know.
