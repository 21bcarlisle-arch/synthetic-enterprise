**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION: does a directory URL ever confirm through the deploy check's own fetch?

Filed 2026-09-04 ~12:10 BST by the delivery seat, before running the measurement, working the
Lane 0 direction *"the figures stopped reaching the reader and no direction ever named the path"*.

## Why this measurement, and why now

`SEAT_FINDING_EVERY_DEPLOY_RED_FOR_THREE_DAYS_WAS_THE_VERIFIER_AND_NEVER_THE_PUBLICATION`
(2026-09-04) established, over the 60 most recent Cloudflare Pages runs:

* 50 green, 10 red; `wrangler pages deploy` exited success in **all 10 reds**;
* across the 462 `serving the deployed bytes after Ns` observations, **zero** are a
  `/`-terminated URL — a directory URL has never once been confirmed by this control;
* every push that changed a `site/**/index.html` went red; not one of the 50 greens changed one.

It closed with **"Owed next: an observation of a directory URL promoting at all"**, and proposed
to wait for a `RESOLVED` verdict to accumulate. That is passive, and it presumes the answer is
latency. **The presumption has never been tested against the tool's own fetch.**

The finding's own contrary evidence is that all 19 directory-index pages, fetched cache-busted at
10:20Z, served bytes **byte-identical** to the repo. That check was made **by hand**, not through
`tools/assert_deployed_bytes_are_served.py:fetch()`. So two incompatible readings are both on the
record and nothing has separated them.

**The tree is quiet right now** — last publish `75f2614d8` at 11:51, HEAD == `origin/main` ==
`881debc8b`, publish gate state `{"alerted_at": null, "failures": []}`, zero queued
`run_complete_*`. No deploy is in flight. Any promotion latency has had ~20 minutes to finish,
which is 2.5× the 8-minute clock. So a directory URL that does not confirm NOW cannot be
explained by latency at all.

## The measurement

Call `tools/assert_deployed_bytes_are_served.py`'s **own** `url_for()` and `fetch()` — imported,
not reimplemented, so the thing measured is the thing that runs in CI — against the live
`poesys.net`, for:

* every `site/**/index.html` in the tree (the directory-URL population, ~19 pages), and
* a direct-file control (`site/data/proof.json`, `site/_headers`-exempt paths excluded),

comparing sha256 of the served body to the **working-tree** bytes, which equal HEAD's (site/ is
clean). Record for each: HTTP status, the final URL after redirects, body sha256, and whether it
matches.

## Predictions, recorded before the answer

Ranked, and I hold H3 and H2 close enough that I would not bet either way — which is why this is
worth running rather than reasoning about.

* **H1 — the direct-file control confirms.** Near-certain; it is the 462 observations' own
  population. If this fails the measurement is invalid (no network, wrong host) and nothing below
  is readable. *This is the validity check, not a finding.*
* **H2 — LATENCY: the directory URLs all confirm now.** Then the 10 reds really were a window too
  short, the finding's reading stands, and `ATTEMPTS` is the honest subject after all — with the
  bound still unobtainable, because a confirmation 20 minutes after a quiet tree gives no
  promotion latency. Owed-next stands as written.
* **H3 — THE FETCH: the directory URLs do NOT confirm, even now.** Then latency was never the
  cause, `Owed next` is aimed at a number that does not exist, and the defect is inside
  `url_for`/`fetch` — permanently, for every future directory-index deploy. Candidate mechanisms,
  each distinguishable from the recorded status and final URL:
  * **H3a — trailing-slash redirect.** Pages canonicalises `/harness/` → `/harness`. If it answers
    308, `urllib` may not follow it, and the raised `HTTPError` is caught as `URLError` by both
    `main()` and `classify()` — surfacing as *"the edge did not answer"*, not as a wrong body.
  * **H3b — the cache-buster.** `?cb=<nonce>` on a `/`-terminated path misses Pages' path
    resolution and 404s, where the same path without a query resolves. The hand-check would not
    have caught this if it fetched differently.
  * **H3c — a genuinely different body** (an injected or error page): status 200, sha mismatch,
    matching neither the new bytes nor the old.
* **H4 — MIXED:** some directory URLs confirm and some do not. Then the split is the finding and
  the population, not the route class, is what needs naming.

## What must NOT happen, stated in advance

* **No `ATTEMPTS` change on this evidence.** A quiet-tree confirmation is not a promotion-latency
  observation and cannot set a clock. If H2 holds, the clock stays where it is.
* **No deleting or weakening the control.** If H3 holds the repair is to the fetch, and the exit
  code stays red for an unproven deploy either way.
* **The 10 reds' `classify()` verdicts are NOT evidence.** The tri-state landed in `b0bceffae`,
  *after* those runs — `classify` never executed on any of them. The finding's "all ten reds were
  UNCONFIRMED" is an inference from the hand-check, and I must not cite it as an observation.

## How this is graded

The result is written beside this file whichever way it goes, and this prediction is not revised
after the fact. If H3 is right the finding above is partly wrong and says so beside itself; if H2
is right, this prereg is the refuted one.
