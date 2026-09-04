**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION: which `site/**`-touching commits on main got no Cloudflare Pages deploy?

RECORDED: this is the prediction, filed 2026-09-04 ~10:10Z BEFORE the measurement, kept so the
result beside it is evidence the experiment was designed before its answer was known. The defect
it led to is filed separately as
`SEAT_FINDING_EVERY_DEPLOY_RED_FOR_THREE_DAYS_WAS_THE_VERIFIER_AND_NEVER_THE_PUBLICATION_2026-09-04.md`.

## Why this is being asked

`poesys.net` is served by Cloudflare Pages (`server: cloudflare`, project `poesys-net`). The
"Deploy GitHub Pages" workflow succeeds on every commit and is a mirror the reader never meets.
The reader's bytes come from `.github/workflows/deploy-pages.yml`, which fires only on

```yaml
on:
  push:
    branches: [main]
    paths: [site/**, docs/PROJECT_STATE.md]
```

At 10:07Z the live feed's `generated_at` was `2026-09-04T09:20:22Z` — 47 minutes stale — while the
corrected feed (`09:53:14Z`) had been committed to origin/main at 09:54Z in `b2031daa5`. In the
`gh run list` window, six commits produced a "Deploy GitHub Pages" run and **no** "Deploy to
Cloudflare Pages" run at all.

## The question

For every commit on `main` in the last ~4 hours that changed a file under `site/`, is there a
"Deploy to Cloudflare Pages" workflow run whose `headSha` is that commit *or* a later commit that
also deployed the tree?

## What I predict, before looking

**H1 (the one I think is true).** There is no per-commit hole in *content*. GitHub evaluates a
`paths:` filter against every commit in a push, and `wrangler pages deploy site` uploads the whole
`site/` directory at the checked-out head — so a push that contains any `site/**` change deploys
the whole tree, and intermediate commits needing no run of their own is correct behaviour, not a
gap. On this hypothesis the 47-minute staleness is fully explained by *push batching plus deploy
latency*: `b2031daa5` was pushed inside the push headed by `53d775b04` at 10:00:33Z, and that run
was still executing `wrangler pages deploy` at 10:08Z.

**H2 (the failure mode that would be real).** A commit touching `site/**` is pushed in a batch, and
the deploy that covers it fails or is cancelled, and nothing retries — so the reader keeps the old
bytes until the *next* site-touching push. On this hypothesis the two failed Cloudflare runs
(`33857591488`, `33858118312`) each left the tree they deployed unverified, and the gap is real but
is a *retry* gap, not a `paths:` gap.

**H1 and H2 are not exclusive.** H1 explains today's 47 minutes; H2 would still be a live hole.

## What would refute H1

A commit whose diff touches `site/**`, which is the **head of its own push**, and for which no
"Deploy to Cloudflare Pages" run exists with that `headSha`. That would mean the `paths:` filter
is not matching what I think it matches.

## What I will NOT claim

That `wrangler pages deploy` succeeded merely because the workflow step exited 0 — the two failed
runs failed at the *assert* step, which runs **after** wrangler has already uploaded. A red run
therefore does **not** mean the reader got nothing. Deploy success and assert success are two
different facts and I will report them separately.

## RESULT, written after the measurement (2026-09-04 ~10:25Z)

**H1 held.** Every `site/**`-touching commit sat in a push whose head got a Cloudflare run; no
commit that was the head of its own push touched `site/**` without one. There is no `paths:`
gap, and the 47 minutes were push batching plus deploy latency exactly as predicted.

**H2 held, and is larger than I framed it.** It is not a retry gap. Across the 60 most recent
runs, all 10 reds had `wrangler pages deploy` succeed and only the assert step fail, and the
failures are confined to one class: directory-index URLs, which the control has never once
confirmed (0 of 462 observations). Written up in
`SEAT_FINDING_EVERY_DEPLOY_RED_FOR_THREE_DAYS_WAS_THE_VERIFIER_AND_NEVER_THE_PUBLICATION_2026-09-04.md`.

**What I got wrong, kept here rather than revised.** Reading the first failure log I judged its
output mislabelled — the "serving the deployed bytes" lines looked like successes filed under a
FAILED heading. They are: they are the per-asset successes, and "are still not what / poesys.net
serves after 8 minutes" is one sentence wrapped across two lines. The message was fine. I also
predicted the 8-minute clock was simply too short for a new route; the distribution refuted that
(max 126s, budget 480s), which is why the fix names the reason instead of moving the number.

## Constraint on this turn

This measurement is read-only: `gh run list`, `git log`, `git show --stat`, `curl`. It must not
push, must not restart a daemon, and must not modify `.github/workflows/`.
